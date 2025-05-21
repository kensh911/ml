import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        # Проверяем, существует ли директория
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                product_name TEXT NOT NULL,
                confidence REAL,
                extraction_date TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                status TEXT,
                products_count INTEGER,
                scraping_date TIMESTAMP,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_products(self, url, products):
        """Сохранение продуктов в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product in products:
            cursor.execute('''
                INSERT INTO products (url, product_name, confidence, extraction_date, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                url,
                product['name'],
                product.get('confidence', 0.0),
                datetime.now(),
                json.dumps(product.get('metadata', {}))
            ))
        
        cursor.execute('''
            INSERT INTO scraping_history (url, status, products_count, scraping_date)
            VALUES (?, ?, ?, ?)
        ''', (url, 'success', len(products), datetime.now()))
        
        conn.commit()
        conn.close()
        
        return True
    
    def save_error(self, url, error_message):
        """Сохранение ошибки скрапинга"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraping_history (url, status, products_count, scraping_date, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, 'error', 0, datetime.now(), error_message))
        
        conn.commit()
        conn.close()
    
    def get_products_stats(self):
        """Получение статистики по продуктам"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_name, COUNT(*) as count 
            FROM products 
            GROUP BY product_name 
            ORDER BY count DESC 
            LIMIT 20
        ''')
        
        stats = cursor.fetchall()
        conn.close()
        
        return [{'name': row[0], 'count': row[1]} for row in stats]
    
    def get_recent_urls(self, limit=5):
        """Получение последних обработанных URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, status, products_count, scraping_date 
            FROM scraping_history 
            ORDER BY scraping_date DESC 
            LIMIT ?
        ''', (limit,))
        
        urls = cursor.fetchall()
        conn.close()
        
        return [{'url': row[0], 'status': row[1], 'count': row[2], 'date': row[3]} for row in urls]