document.addEventListener('DOMContentLoaded', function() {
    // Элементы интерфейса
    const form = document.getElementById('extract-form');
    const urlInput = document.getElementById('url-input');
    const submitBtn = document.getElementById('submit-btn');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const recentLinks = document.querySelectorAll('.url-link');
    
    // Кнопки для работы с метриками
    const createTestSetBtn = document.getElementById('create-test-set-btn');
    const evaluateModelBtn = document.getElementById('evaluate-model-btn');
    const metricsResult = document.getElementById('metrics-result');
    
    // Кнопки для пакетной обработки
    const runBatchBtn = document.getElementById('run-batch-btn');
    const batchStatus = document.getElementById('batch-status');
    
    // Обработка отправки формы
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            extractProducts(urlInput.value);
        });
    }
    
    // Обработка кликов по недавним URL
    if (recentLinks) {
        recentLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('data-url');
                urlInput.value = url;
                extractProducts(url);
            });
        });
    }
    
    // Функция извлечения продуктов
    function extractProducts(url) {
        // Показываем загрузку
        loadingDiv.classList.remove('hidden');
        resultsDiv.innerHTML = '';
        submitBtn.disabled = true;
        
        // Отправляем запрос
        fetch('/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        })
        .then(response => response.json())
        .then(data => {
            // Скрываем индикатор загрузки
            loadingDiv.classList.add('hidden');
            submitBtn.disabled = false;
            
            // Обрабатываем результат
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Отображаем продукты
            displayProducts(data.products);
            
            // Обновляем статистику
            fetchStats();
        })
        .catch(error => {
            loadingDiv.classList.add('hidden');
            submitBtn.disabled = false;
            showError("Произошла ошибка при выполнении запроса");
            console.error('Error:', error);
        });
    }
    
    // Функция отображения ошибки
    function showError(message) {
        resultsDiv.innerHTML = `
            <div class="error-message">
                <p>${message}</p>
            </div>
            <p>Попробуйте другой URL или проверьте соединение с интернетом.</p>
        `;
    }
    
    // Функция отображения продуктов
    function displayProducts(products) {
        if (!products || products.length === 0) {
            resultsDiv.innerHTML = `
                <p>Не удалось найти товары на указанной странице.</p>
                <p>Попробуйте другой URL или проверьте, что это действительно страница мебельного магазина.</p>
            `;
            return;
        }
        
        // Сортируем по уверенности
        products.sort((a, b) => b.confidence - a.confidence);
        
        // Создаем HTML-список
        const list = document.createElement('ul');
        list.className = 'products-list';
        
        products.forEach((product, index) => {
            const item = document.createElement('li');
            item.className = 'product-item';
            item.style.animationDelay = `${index * 0.05}s`;
            
            const confidencePercent = Math.round(product.confidence * 100);
            
            item.innerHTML = `
                <span class="product-name">${product.name}</span>
                <span class="product-confidence">${confidencePercent}%</span>
            `;
            
            list.appendChild(item);
        });
        
        // Добавляем заголовок и статистику
        resultsDiv.innerHTML = `
            <div class="results-summary">
                <p>Найдено <strong>${products.length}</strong> товаров на странице:</p>
            </div>
        `;
        
        resultsDiv.appendChild(list);
    }
    
    // Функция получения статистики
    function fetchStats() {
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                const statsDiv = document.getElementById('stats');
                
                if (!data || data.length === 0) {
                    statsDiv.innerHTML = '<p>Статистика пока недоступна</p>';
                    return;
                }
                
                // Создаем HTML-список
                let html = '<ul class="stats-list">';
                
                data.forEach(item => {
                    html += `
                        <li>
                            <span class="product-name">${item.name}</span>
                            <span class="product-count">${item.count}</span>
                        </li>
                    `;
                });
                
                html += '</ul>';
                statsDiv.innerHTML = html;
            })
            .catch(error => {
                console.error('Error fetching stats:', error);
            });
            
        // Также обновляем список недавних URL
        fetch('/recent')
            .then(response => response.json())
            .then(data => {
                const recentDiv = document.getElementById('recent');
                
                if (!data || data.length === 0) {
                    recentDiv.innerHTML = '<p>История запросов пока недоступна</p>';
                    return;
                }
                
                // Создаем HTML-список
                let html = '<ul class="recent-list">';
                
                data.forEach(item => {
                    html += `
                        <li class="recent-item ${item.status === 'success' ? 'success' : 'error'}">
                            <a href="#" class="url-link" data-url="${item.url}">${item.url}</a>
                            <span class="url-count">${item.count} товаров</span>
                        </li>
                    `;
                });
                
                html += '</ul>';
                recentDiv.innerHTML = html;
                
                // Добавляем обработчики событий для новых ссылок
                const newLinks = recentDiv.querySelectorAll('.url-link');
                newLinks.forEach(link => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const url = this.getAttribute('data-url');
                        urlInput.value = url;
                        extractProducts(url);
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching recent URLs:', error);
            });
    }
    
    // Создание тестового набора
    if (createTestSetBtn) {
        createTestSetBtn.addEventListener('click', function() {
            const sampleSize = 30; // Можно сделать настраиваемым
            
            createTestSetBtn.disabled = true;
            createTestSetBtn.textContent = 'Создание...';
            
            fetch('/create_test_set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sample_size: sampleSize })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Создание тестового набора запущено. Это может занять несколько минут.');
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при запросе');
            })
            .finally(() => {
                createTestSetBtn.disabled = false;
                createTestSetBtn.textContent = 'Создать тестовый набор';
            });
        });
    }
    
    // Оценка модели
    if (evaluateModelBtn) {
        evaluateModelBtn.addEventListener('click', function() {
            evaluateModelBtn.disabled = true;
            evaluateModelBtn.textContent = 'Оценка...';
            
            fetch('/metrics')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Показываем результаты
                    metricsResult.classList.remove('hidden');
                    
                    // Обновляем значения метрик
                    document.getElementById('precision-value').textContent = 
                        (data.metrics.precision * 100).toFixed(2) + '%';
                    document.getElementById('recall-value').textContent = 
                        (data.metrics.recall * 100).toFixed(2) + '%';
                    document.getElementById('f1-value').textContent = 
                        (data.metrics.f1_score * 100).toFixed(2) + '%';
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при запросе');
            })
            .finally(() => {
                evaluateModelBtn.disabled = false;
                evaluateModelBtn.textContent = 'Оценить модель';
            });
        });
    }
    
    // Запуск пакетной обработки
    if (runBatchBtn) {
        runBatchBtn.addEventListener('click', function() {
            const batchSize = parseInt(document.getElementById('batch-size').value) || 50;
            const startIndex = parseInt(document.getElementById('start-index').value) || 0;
            
            if (batchSize < 1 || batchSize > 704) {
                alert('Размер пакета должен быть от 1 до 704');
                return;
            }
            
            if (startIndex < 0 || startIndex > 703) {
                alert('Начальный индекс должен быть от 0 до 703');
                return;
            }
            
            runBatchBtn.disabled = true;
            batchStatus.classList.remove('hidden');
            
            fetch('/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    batch_size: batchSize,
                    start_index: startIndex
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Пакетная обработка запущена. Это может занять некоторое время.');
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при запросе');
            })
            .finally(() => {
                runBatchBtn.disabled = false;
                batchStatus.classList.remove('hidden');
            });
        });
    }
});