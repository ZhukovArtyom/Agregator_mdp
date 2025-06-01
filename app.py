from flask import Flask, render_template, jsonify, request
import subprocess
import pandas as pd
import os
import threading
from urllib.parse import unquote

app = Flask(__name__)

# Флаг завершения сбора данных
data_ready = False

def run_data_collection():
    global data_ready
    try:
        # Запускаем ваш скрипт сбора данных
        subprocess.run(['python', 'main.py'], check=True)
        data_ready = True  # Устанавливаем флаг после завершения
        print("Сбор данных завершён успешно!")
    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scan', methods=['POST'])
def start_scan():
    global data_ready
    data_ready = False  # Устанавливаем флаг в False перед началом сбора данных
    threading.Thread(target=run_data_collection, daemon=True).start()
    return jsonify({'status': 'scan_started'})

@app.route('/check_status')
def check_status():
    return jsonify({'ready': data_ready})

@app.route('/select_university')
def select_university():
    if not data_ready:
        return "Данные ещё не готовы", 400
    return render_template('select.html')

# Новый маршрут для страницы университета
@app.route('/university_news')
def university_news():
    if not data_ready:
        return "Данные ещё не готовы", 400
    
    uni = unquote(request.args.get('uni', 'all'))
    return render_template('news.html', university=uni)

@app.route('/get_news_data')
def get_news_data():
    if not os.path.exists('news_categories.csv'):
        return jsonify([])
    
    df = pd.read_csv('news_categories.csv')
    uni = request.args.get('uni', 'all')
    category = request.args.get('category', 'all')
    
    if uni != 'all':
        uni = unquote(uni)  # Декодируем URL-параметр
        df = df[df['Университет'] == uni]
    if category != 'all':
        category = unquote(category)
        df = df[df['Категория'] == category]
    
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    data_ready = False  # Изначально данные не готовы
    app.run(debug=True)