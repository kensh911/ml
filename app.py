from flask import Flask, render_template, request, jsonify
from extractor import ProductExtractor
from database import Database
from metrics import Evaluator
from batch_processor import BatchProcessor
import os
from config import Config

app = Flask(__name__)
config = Config()

# Пути к файлам
database_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
os.makedirs(database_dir, exist_ok=True)
database_path = os.path.join(database_dir, 'products.db')

# Инициализация
extractor = ProductExtractor()
db = Database(database_path)

@app.route('/')
def index():
    """Главная страница приложения"""
    recent_urls = db.get_recent_urls(5)
    stats = db.get_products_stats()
    return render_template('index.html', recent_urls=recent_urls, stats=stats)

@app.route('/extract', methods=['POST'])
def extract_products():
    """API для извлечения товаров с URL"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL не указан', 'success': False}), 400
    
    # Нормализация URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Извлекаем продукты с таймаутом
        products = extractor.extract_products(url)
        
        # Сохраняем в базу
        db.save_products(url, products)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        # Обработка ошибок и информативное сообщение
        error_message = str(e)
        db.save_error(url, error_message)
        
        # Формируем понятное сообщение об ошибке
        if 'timeout' in error_message.lower():
            friendly_error = "Превышено время ожидания. Сайт не отвечает."
        elif 'connection' in error_message.lower():
            friendly_error = "Не удалось подключиться к сайту. Проверьте URL."
        else:
            friendly_error = f"Ошибка при обработке: {error_message}"
            
        return jsonify({
            'error': friendly_error,
            'success': False
        }), 500

@app.route('/stats')
def get_stats():
    """API для получения статистики"""
    stats = db.get_products_stats()
    return jsonify(stats)

@app.route('/recent')
def get_recent():
    """API для получения недавних URL"""
    recent = db.get_recent_urls(10)
    return jsonify(recent)

@app.route('/batch', methods=['POST'])
def run_batch_processing():
    """API для запуска пакетной обработки URL"""
    data = request.get_json()
    batch_size = data.get('batch_size', config.BATCH_SIZE)
    start_index = data.get('start_index', 0)
    
    processor = BatchProcessor(
        url_file=config.URL_LIST_PATH,
        database_path=config.DATABASE_PATH,
        max_workers=config.MAX_WORKERS
    )
    
    # Запускаем обработку в отдельном потоке
    import threading
    thread = threading.Thread(
        target=processor.process_batch,
        kwargs={'batch_size': batch_size, 'start_index': start_index}
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Запущена обработка {batch_size} URL начиная с индекса {start_index}',
        'total_urls': len(processor.load_urls())
    })

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """API для получения метрик качества модели"""
    try:
        # Проверяем наличие тестового набора
        if not os.path.exists(config.TEST_SET_PATH):
            return jsonify({
                'error': 'Тестовый набор не найден. Сначала создайте его.',
                'success': False
            }), 404
        
        # Создаем экземпляр оценщика и получаем метрики
        evaluator = Evaluator(config.TEST_SET_PATH)
        metrics = evaluator.evaluate_model(extractor)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при расчете метрик: {str(e)}',
            'success': False
        }), 500

@app.route('/create_test_set', methods=['POST'])
def create_test_set():
    """API для создания тестового набора"""
    data = request.get_json()
    sample_size = data.get('sample_size', 30)
    
    processor = BatchProcessor(
        url_file=config.URL_LIST_PATH,
        database_path=config.DATABASE_PATH
    )
    
    # Запускаем создание тестового набора в отдельном потоке
    import threading
    thread = threading.Thread(
        target=processor.create_test_set,
        kwargs={'sample_size': sample_size, 'output_file': config.TEST_SET_PATH}
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Запущено создание тестового набора из {sample_size} URL'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)