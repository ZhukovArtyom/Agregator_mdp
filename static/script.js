document.addEventListener('DOMContentLoaded', function() {

    // Получаем элемент заголовка
    const uniTitleElem = document.getElementById('uniTitle');
    if (uniTitleElem) {
        const uni = new URLSearchParams(window.location.search).get('uni');
        if (uni && uni !== 'all') {
            uniTitleElem.textContent = decodeURIComponent(uni);
        } else {
            uniTitleElem.textContent = 'Новости всех университетов';
        }
}

    const startBtn = document.getElementById('startScan');
    const loadingDiv = document.getElementById('loading');
    const progressText = document.getElementById('progressText');

    // Инициализация только на главной странице
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            startBtn.disabled = true;
            startBtn.hidden = true;
            loadingDiv.style.display = 'block';
            progressText.textContent = 'Идёт сбор новостей...';

            fetch('/start_scan', { method: 'POST' })
                .then(() => checkScanStatus())
                .catch(error => {
                    console.error('Ошибка:', error);
                    progressText.textContent = 'Ошибка при запуске сканирования';
                });
            setTimeout(fetchProgress, 500);
        });

        
    }

    // Инициализация на странице новостей
    if (document.getElementById('newsGrid')) {
        const uni = new URLSearchParams(window.location.search).get('uni') || 'all';
        loadNewsData(uni);
    }
});


function fetchProgress() {
    fetch('/progress.json')
        .then(response => response.json())
        .then(data => {
            document.getElementById("university").textContent = data.university;
            document.getElementById("progress").style.width = data.progress + "%";
            document.getElementById("progress").textContent = data.progress + "%";
            document.getElementById("status").textContent = data.status;

            setTimeout(fetchProgress, 500);
        })
        .catch(error => console.log("Ошибка:", error));
}

// Единая функция проверки статуса
function checkScanStatus() {
    fetch('/check_status')
        .then(response => response.json())
        .then(data => {
            if (data.ready) {
                window.location.href = '/select_university'; // Переход только если данные готовы
            } else {
                setTimeout(checkScanStatus, 2000);
                const progressText = document.getElementById('progressText');
                if (progressText) progressText.textContent += '.';
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            setTimeout(checkScanStatus, 2000);
        });
}

function selectUni(uni) {
    // Двойное кодирование для корректной передачи кириллицы
    const encodedUni = encodeURIComponent(encodeURIComponent(uni));
    window.location.href = `/university_news?uni=${encodedUni}`;
}

function loadNewsData(uni) {
    // Декодируем один раз при загрузке
    const decodedUni = decodeURIComponent(uni);
    fetch(`/get_news_data?uni=${encodeURIComponent(decodedUni)}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            updateCategories(data);
            renderNews(data);
        })
        .catch(error => {
            console.error('Error loading news:', error);
            document.getElementById('newsGrid').innerHTML = 
                '<p class="error">Ошибка загрузки новостей. Попробуйте обновить страницу.</p>';
        });
}

function updateCategories(newsData) {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;
    
    const categories = [...new Set(newsData.map(item => item.Категория))];
    categoryFilter.innerHTML = '<option value="all">Все категории</option>';
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

function renderNews(newsData) {
    const newsGrid = document.getElementById('newsGrid');
    if (!newsGrid) return;

    newsGrid.innerHTML = newsData.length ? '' : '<p class="no-news">Новости не найдены</p>';

    // Используем объект для группировки новостей по заголовку
    const groupedNews = {};

    

    newsData.forEach(item => {
        if (!groupedNews[item.Заголовок]) {
            groupedNews[item.Заголовок] = {
                ...item,
                Категории: [] // Создаём массив для категорий
            };
        }
        groupedNews[item.Заголовок].Категории.push(item.Категория); // Добавляем категорию к массиву
    });

    // Теперь отображаем сгруппированные новости
    Object.values(groupedNews).forEach(item => {
        const categoriesText = item.Категории.join(', '); // Объединяем категории в строку

        const newsCard = document.createElement('div');
        newsCard.className = 'news-card';

        newsCard.innerHTML = `            
            <img src="${item.Изображение}" 
                    alt="${item.Заголовок}">
            
            <div class="news-content">
                <h3>${item.Заголовок}</h3>
                <div class="University_name">${item.Университет}</div>
                <div class="news-category">${categoriesText}</div>
                <p><small>${item.Дата}</small></p>
                <a href="${item.Ссылка}" target="_blank" class="news-link">
                    Читать далее
                </a>
            </div>
        `;

        newsGrid.appendChild(newsCard);
    });
}

function filterNews() {
    const university = new URLSearchParams(window.location.search).get('uni') || 'all';
    const category = document.getElementById('categoryFilter').value;

    fetch(`/get_news_data?uni=${encodeURIComponent(university)}`)
        .then(response => response.json())
        .then(data => {
            let selectedTitles = [];

            // Если выбрана конкретная категория, отфильтруем заголовки новостей
            if (category !== 'all') {
                selectedTitles = data
                    .filter(item => item.Категория === category) // Фильтруем по выбранной категории
                    .map(item => item.Заголовок); // Составляем список заголовков
            } else {
                // Если выбрана категория "Все", просто получаем все заголовки
                selectedTitles = data.map(item => item.Заголовок);
            }

            // Теперь отбираем все новости, заголовки которых входят в список отобранных заголовков
            const filteredData = data.filter(item => selectedTitles.includes(item.Заголовок));

            renderNews(filteredData);
        })
        .catch(error => console.error('Filter error:', error));
}