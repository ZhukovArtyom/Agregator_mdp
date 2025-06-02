import json
from flask import Flask, render_template, jsonify, send_from_directory, request
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
        # Инициализируем прогресс
        with open('progress.json', 'w') as f:
            json.dump({
                "university": "Подготовка...",
                "current": 0,
                "total": 100,
                "progress": 0,
                "status": "Запуск сканирования"
            }, f)
        
        # Запускаем ваш скрипт сбора данных
        subprocess.run(['python', 'main.py'], check=True)
        data_ready = True
        
        # Финальный статус
        with open('progress.json', 'w') as f:
            json.dump({
                "university": "Все университеты",
                "current": 100,
                "total": 100,
                "progress": 100,
                "status": "Завершено!"
            }, f)
            
    except Exception as e:
        print(f"Ошибка: {e}")
        with open('progress.json', 'w') as f:
            json.dump({
                "university": "Ошибка",
                "current": 0,
                "total": 100,
                "progress": 0,
                "status": f"Ошибка: {str(e)}"
            }, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress.json')
def get_progress():
    try:
        return send_from_directory('.', 'progress.json')
    except FileNotFoundError:
        return jsonify({"error": "Прогресс не доступен"}), 404

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