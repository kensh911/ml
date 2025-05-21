import pandas as pd
from extractor import ProductExtractor
from database import Database
import time
import os
import json
import random
from tqdm import tqdm

class BatchProcessor:
    def __init__(self, url_file, database_path, max_workers=1):
        self.url_file = url_file
        self.database = Database(database_path)
        self.extractor = ProductExtractor()
        self.max_workers = max_workers
        
    def load_urls(self):
        """Загрузка URL из CSV-файла"""
        try:
            df = pd.read_csv(self.url_file)
            if 'max(page)' in df.columns:
                urls = df['max(page)'].tolist()
                return urls
            else:
                print(f"Ошибка: отсутствует колонка 'max(page)' в файле {self.url_file}")
                return []
        except Exception as e:
            print(f"Ошибка при загрузке URL из {self.url_file}: {e}")
            return []
    
    def process_url(self, url):
        """Обработка одного URL"""
        try:
            print(f"Обработка: {url}")
            products = self.extractor.extract_products(url)
            self.database.save_products(url, products)
            return {
                'url': url,
                'status': 'success',
                'products_count': len(products),
                'products': products
            }
        except Exception as e:
            error_message = str(e)
            self.database.save_error(url, error_message)
            return {
                'url': url,
                'status': 'error',
                'error': error_message
            }
    
    def process_batch(self, batch_size=None, start_index=0):
        """Пакетная обработка URL"""
        urls = self.load_urls()
        
        if not urls:
            print("Нет URL для обработки")
            return []
        
        # Если указан batch_size, обрабатываем только часть URL
        if batch_size:
            end_index = min(start_index + batch_size, len(urls))
            urls = urls[start_index:end_index]
        
        results = []
        
        # Последовательная обработка URL с tqdm для отображения прогресса
        for url in tqdm(urls, desc="Пакетная обработка"):
            result = self.process_url(url)
            results.append(result)
            # Пауза между запросами для избежания блокировки
            time.sleep(1)
        
        return results
    
    def create_test_set(self, sample_size=30, output_file='data/test_set.json'):
        """Создание тестового набора для оценки качества"""
        urls = self.load_urls()
        
        if not urls:
            print("Нет URL для создания тестового набора")
            return False
        
        # Берем случайную выборку URL
        sample_urls = random.sample(urls, min(sample_size, len(urls)))
        
        test_data = []
        
        for url in tqdm(sample_urls, desc="Создание тестового набора"):
            try:
                products = self.extractor.extract_products(url)
                
                if products:
                    test_data.append({
                        'url': url,
                        'products': [p['name'] for p in products],
                        'confidence': [p['confidence'] for p in products]
                    })
                
                # Пауза между запросами
                time.sleep(1)
            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
        
        # Сохраняем тестовый набор
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"Тестовый набор создан и сохранен в {output_file}")
        return True