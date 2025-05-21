import json
import os

class Evaluator:
    def __init__(self, test_data_path):
        """Инициализация с путем к тестовому набору данных"""
        self.test_data_path = test_data_path
        self.load_test_data()
    
    def load_test_data(self):
        """Загрузка тестовых данных"""
        try:
            if os.path.exists(self.test_data_path):
                with open(self.test_data_path, 'r', encoding='utf-8') as f:
                    self.test_data = json.load(f)
                print(f"Загружено {len(self.test_data)} тестовых примеров")
            else:
                print(f"Файл {self.test_data_path} не найден")
                self.test_data = []
        except Exception as e:
            print(f"Ошибка при загрузке тестовых данных: {e}")
            self.test_data = []
    
    def evaluate_model(self, extractor, max_samples=None):
        """Оценка модели на тестовых данных"""
        if not self.test_data:
            return {
                'error': 'Нет тестовых данных для оценки'
            }
        
        # Ограничиваем количество тестовых примеров, если указано
        test_samples = self.test_data[:max_samples] if max_samples else self.test_data
        
        all_true_products = []
        all_predicted_products = []
        url_results = []
        
        for test_case in test_samples:
            url = test_case['url']
            true_products = set(test_case['products'])
            
            # Извлекаем продукты
            try:
                extracted = extractor.extract_products(url)
                predicted_products = set([p['name'] for p in extracted])
                status = 'success'
            except Exception as e:
                predicted_products = set()
                status = f'error: {str(e)}'
            
            # Сохраняем результаты для этого URL
            url_results.append({
                'url': url,
                'true_count': len(true_products),
                'predicted_count': len(predicted_products),
                'correct_count': len(true_products & predicted_products),
                'status': status
            })
            
            all_true_products.append(true_products)
            all_predicted_products.append(predicted_products)
        
        # Вычисляем метрики
        metrics = self.calculate_metrics(all_true_products, all_predicted_products)
        metrics['url_results'] = url_results
        
        # Сохраняем результаты оценки
        self.save_evaluation_results(metrics)
        
        return metrics
    
    def calculate_metrics(self, true_sets, predicted_sets):
        """Вычисление метрик качества"""
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for true_set, predicted_set in zip(true_sets, predicted_sets):
            true_positives += len(true_set & predicted_set)
            false_positives += len(predicted_set - true_set)
            false_negatives += len(true_set - predicted_set)
        
        # Рассчитываем precision, recall и F1
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Рассчитываем дополнительные метрики
        total_true_products = sum(len(true_set) for true_set in true_sets)
        total_extracted_products = sum(len(pred_set) for pred_set in predicted_sets)
        accuracy = true_positives / total_true_products if total_true_products > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'accuracy': accuracy,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'total_true_products': total_true_products,
            'total_extracted_products': total_extracted_products
        }
    
    def save_evaluation_results(self, metrics):
        """Сохранение результатов оценки в JSON"""
        output_dir = os.path.dirname(self.test_data_path)
        results_path = os.path.join(output_dir, 'evaluation_results.json')
        
        # Создаем копию метрик без больших списков URL
        metrics_summary = {k: v for k, v in metrics.items() if k != 'url_results'}
        
        try:
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_summary, f, ensure_ascii=False, indent=2)
            
            print(f"Результаты оценки сохранены в {results_path}")
        except Exception as e:
            print(f"Ошибка при сохранении результатов: {e}")