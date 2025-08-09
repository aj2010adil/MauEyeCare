import sqlite3
from contextlib import closing

DB_PATH = "src/eyecare.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            contact TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_name TEXT,
            medicines TEXT,
            dosage TEXT,
            eye_test TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            medicine TEXT PRIMARY KEY,
            quantity INTEGER
        )''')
        conn.commit()

def add_patient(name, age, gender, contact):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO patients (name, age, gender, contact) VALUES (?, ?, ?, ?)", (name, age, gender, contact))
        conn.commit()
        return c.lastrowid

def get_patients():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM patients")
        return c.fetchall()

def add_prescription(patient_id, doctor_name, medicines, dosage, eye_test):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO prescriptions (patient_id, doctor_name, medicines, dosage, eye_test) VALUES (?, ?, ?, ?, ?)", (patient_id, doctor_name, medicines, dosage, eye_test))
        conn.commit()
        return c.lastrowid

def get_prescriptions(patient_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM prescriptions WHERE patient_id=? ORDER BY date DESC", (patient_id,))
        return c.fetchall()

def update_inventory(medicine, qty):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO inventory (medicine, quantity) VALUES (?, ?) ON CONFLICT(medicine) DO UPDATE SET quantity=quantity+?", (medicine, qty, qty))
        conn.commit()

def reduce_inventory(medicine, qty):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("UPDATE inventory SET quantity=quantity-? WHERE medicine=? AND quantity>=?", (qty, medicine, qty))
        conn.commit()

def get_inventory():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM inventory")
        return c.fetchall()
