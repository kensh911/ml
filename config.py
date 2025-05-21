import os

class Config:
    # Пути
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'products.db')
    URL_LIST_PATH = os.path.join(DATA_DIR, 'URL_list.csv')
    TEST_SET_PATH = os.path.join(DATA_DIR, 'test_set.json')
    
    # Модели - используем готовые решения
    NER_MODEL = "Davlan/distilbert-base-multilingual-cased-ner-hrl"
    
    # Параметры скрапинга
    TIMEOUT = 15
    MAX_RETRIES = 3
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # Параметры пакетной обработки
    BATCH_SIZE = 50
    MAX_WORKERS = 5
    
    # Ключевые слова для мебели
    FURNITURE_KEYWORDS = [
        # Русские ключевые слова
        'диван', 'кресло', 'стол', 'стул', 'шкаф', 'кровать', 'комод', 'тумба',
        'полка', 'матрас', 'гарнитур', 'мебель', 'светильник', 'лампа', 
        # Английские ключевые слова
        'sofa', 'chair', 'table', 'desk', 'wardrobe', 'bed', 'dresser', 'cabinet',
        'shelf', 'mattress', 'furniture', 'lamp', 'couch', 'nightstand', 'bookcase'
    ]
    
    # Flask
    SECRET_KEY = 'furniture-extractor-key'
    DEBUG = True