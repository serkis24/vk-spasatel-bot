from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
import database
import json
import os
import requests
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Для сессий

# Настройки для загрузки файлов
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Токен ВК из .env
VK_TOKEN = os.environ.get("VK_TOKEN")
VK_GROUP_ID = os.environ.get("VK_GROUP_ID")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_group_manager(vk_id):
    """Проверяет, является ли пользователь руководителем группы"""
    try:
        url = "https://api.vk.com/method/groups.getMembers"
        params = {
            "access_token": VK_TOKEN,
            "v": "5.199",
            "group_id": VK_GROUP_ID,
            "filter": "managers",
            "fields": "id"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            print(f"Ошибка VK API: {data['error']}")
            return False
        
        for item in data['response']['items']:
            if item['id'] == vk_id:
                return True
        
        return False
        
    except Exception as e:
        print(f"Ошибка проверки прав: {e}")
        return False

@app.route('/')
def index():
    """Главная страница редактора"""
    teacher_id = request.args.get('teacher')
    
    if teacher_id:
        # Если пришли по ссылке от бота, сохраняем в сессию
        if is_group_manager(int(teacher_id)):
            session['vk_id'] = int(teacher_id)
            session['role'] = 'teacher'
            return render_template('editor.html', teacher_mode=True)
    
    # Проверяем сессию
    if 'vk_id' in session and session.get('role') == 'teacher':
        return render_template('editor.html', teacher_mode=True)
    
    # Если не авторизован, показываем страницу входа
    return render_template('login.html', group_id=VK_GROUP_ID)

@app.route('/auth/vk')
def vk_auth():
    """Обработка авторизации через ВК"""
    vk_id = request.args.get('vk_id')
    
    if not vk_id:
        return redirect('/')
    
    if is_group_manager(int(vk_id)):
        session['vk_id'] = int(vk_id)
        session['role'] = 'teacher'
        return redirect('/')
    else:
        return "❌ У вас нет прав учителя. Вы должны быть руководителем группы ВК."

@app.route('/save', methods=['POST'])
def save():
    """Сохранение сценария"""
    if 'vk_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Требуется авторизация учителя'}), 403
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Нет данных'}), 400
            
        name = data.get('name', 'Новый сценарий')
        scenario_data = data.get('scenario', [])
        
        if not scenario_data:
            return jsonify({'error': 'Нет сцен в сценарии'}), 400
        
        scenario_id = database.save_scenario(name, str(session['vk_id']), scenario_data)
        
        return jsonify({
            'id': scenario_id, 
            'status': 'ok',
            'message': f'Сценарий сохранён с ID {scenario_id}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load/<int:scenario_id>')
def load(scenario_id):
    """Загрузка сценария"""
    try:
        scenario = database.get_scenario(scenario_id)
        if scenario:
            return jsonify(scenario)
        return jsonify({'error': 'Сценарий не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка фото в ВК"""
    if 'vk_id' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Требуется авторизация учителя'}), 403
    
    # Здесь код загрузки фото (он у тебя уже есть, оставь как есть)
    # ... (я не копирую для краткости, но он остаётся)

@app.route('/logout')
def logout():
    """Выход из аккаунта"""
    session.clear()
    return redirect('/')

def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()
    print("="*50)
    print("🚀 РЕДАКТОР ЗАПУЩЕН!")
    print("="*50)
    print(f"\n📌 Локально: http://127.0.0.1:5000")
    print(f"📌 В сети: http://{local_ip}:5000")
    print("\n👥 Учителя = все руководители группы ВК")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
