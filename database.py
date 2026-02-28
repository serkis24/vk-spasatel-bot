import sqlite3
import json

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    
    # Таблица сценариев
    c.execute('''CREATE TABLE IF NOT EXISTS scenarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  author_id TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  data TEXT NOT NULL)''')
    
    # Таблица пользователей (учителя/ученики)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (vk_id INTEGER PRIMARY KEY,
                  role TEXT DEFAULT 'student',
                  first_name TEXT,
                  last_name TEXT,
                  last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Таблица назначений сценариев ученикам
    c.execute('''CREATE TABLE IF NOT EXISTS assignments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id INTEGER,
                  scenario_id INTEGER,
                  assigned_by INTEGER,
                  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(student_id, scenario_id))''')
    
    # Таблица прогресса учеников
    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id INTEGER,
                  scenario_id INTEGER,
                  current_state TEXT,
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(student_id, scenario_id))''')
    
    conn.commit()
    conn.close()

def save_scenario(name, author_id, scenario_data):
    """Сохраняет сценарий"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute("INSERT INTO scenarios (name, author_id, data) VALUES (?, ?, ?)",
              (name, author_id, json.dumps(scenario_data, ensure_ascii=False)))
    conn.commit()
    scenario_id = c.lastrowid
    conn.close()
    return scenario_id

def get_scenario(scenario_id):
    """Загружает сценарий по ID"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'name': row[1], 'author_id': row[2], 
                'data': json.loads(row[4])}
    return None

def get_user(vk_id):
    """Получает информацию о пользователе"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE vk_id = ?", (vk_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'vk_id': row[0], 'role': row[1], 'first_name': row[2], 'last_name': row[3]}
    return None

def update_user_role(vk_id, role):
    """Обновляет роль пользователя"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (vk_id, role, last_sync) VALUES (?, ?, CURRENT_TIMESTAMP)",
              (vk_id, role))
    conn.commit()
    conn.close()

def assign_scenario_to_student(student_id, scenario_id, teacher_id):
    """Назначает сценарий ученику"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO assignments (student_id, scenario_id, assigned_by) VALUES (?, ?, ?)",
              (student_id, scenario_id, teacher_id))
    conn.commit()
    conn.close()

def get_student_scenarios(student_id):
    """Получает список сценариев, назначенных ученику"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute('''
        SELECT s.id, s.name, s.data, a.assigned_at 
        FROM assignments a
        JOIN scenarios s ON a.scenario_id = s.id
        WHERE a.student_id = ?
        ORDER BY a.assigned_at DESC
    ''', (student_id,))
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'data': json.loads(r[2]), 'assigned_at': r[3]} for r in rows]

def save_progress(student_id, scenario_id, current_state):
    """Сохраняет прогресс ученика"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO progress (student_id, scenario_id, current_state, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (student_id, scenario_id, current_state))
    conn.commit()
    conn.close()

def get_progress(student_id, scenario_id):
    """Получает прогресс ученика"""
    conn = sqlite3.connect('scenarios.db')
    c = conn.cursor()
    c.execute("SELECT current_state FROM progress WHERE student_id = ? AND scenario_id = ?",
              (student_id, scenario_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# Инициализация при первом импорте
init_db()
