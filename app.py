from flask import Flask, render_template, request, jsonify, send_from_directory
import database
import json
import os
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Главная страница редактора - доступна всем"""
    return render_template('editor.html')

@app.route('/save', methods=['POST'])
def save():
    """Сохранение сценария - доступно всем"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Нет данных'}), 400
            
        name = data.get('name', 'Новый сценарий')
        scenario_data = data.get('scenario', [])
        
        if not scenario_data:
            return jsonify({'error': 'Нет сцен в сценарии'}), 400
        
        scenario_id = database.save_scenario(name, 'public', scenario_data)
        
        return jsonify({
            'id': scenario_id, 
            'status': 'ok',
            'message': f'Сценарий сохранён с ID {scenario_id}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load/<int:scenario_id>')
def load(scenario_id):
    """Загрузка сценария - доступна всем"""
    try:
        scenario = database.get_scenario(scenario_id)
        if scenario:
            return jsonify(scenario)
        return jsonify({'error': 'Сценарий не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Загрузка фото - доступна всем"""
    print("\n" + "="*50)
    print("📸 ПОЛУЧЕН ЗАПРОС НА ЗАГРУЗКУ ФАЙЛА")
    print("="*50)
    
    try:
        if 'file' not in request.files:
            print("❌ Нет файла в запросе")
            return jsonify({'error': 'Нет файла'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("❌ Имя файла пустое")
            return jsonify({'error': 'Файл не выбран'}), 400
        
        print(f"📁 Получен файл: {file.filename}")
        
        if not allowed_file(file.filename):
            print(f"❌ Неподдерживаемый формат: {file.filename}")
            return jsonify({'error': 'Неподдерживаемый формат. Используйте JPG, PNG, GIF'}), 400
        
        # Сохраняем файл с уникальным именем
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(file_path)
        
        # Возвращаем путь к файлу для доступа через браузер
        file_url = f"/uploads/{unique_name}"
        
        return jsonify({
            'success': True,
            'file_url': file_url,
            'filename': unique_name,
            'message': 'Файл загружен!'
        })
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Отдаёт загруженный файл"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
    print("\n👥 ДОСТУПНО ВСЕМ!")
    print("📝 Любой может создавать сценарии")
    print("🎮 Проходить могут только те, кому назначил учитель")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
