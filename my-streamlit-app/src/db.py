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
        # Drop and recreate prescriptions table to ensure schema is correct (WARNING: this deletes all prescription data)
        c.execute('DROP TABLE IF EXISTS prescriptions')
        c.execute('''CREATE TABLE prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_name TEXT,
            medicines TEXT,
            dosage TEXT,
            eye_test TEXT,
            issue TEXT,
            money_given REAL DEFAULT 0,
            money_pending REAL DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            medicine TEXT PRIMARY KEY,
            quantity INTEGER
        )''')
        # Pre-populate with common eye specialist medicines and spectacles if not already present
        default_items = [
            ("Tobramycin Eye Drops", 20),
            ("Moxifloxacin Eye Drops", 15),
            ("Carboxymethylcellulose Eye Drops", 25),
            ("Atropine Eye Drops", 10),
            ("Prednisolone Acetate Eye Drops", 10),
            ("Timolol Eye Drops", 12),
            ("Latanoprost Eye Drops", 8),
            ("Brimonidine Eye Drops", 8),
            ("Acetazolamide Tablets", 30),
            ("Fluorescein Strips", 50),
            ("Eye Ointment (Erythromycin)", 10),
            ("Contact Lens Solution", 15),
            ("Reading Glasses +1.00", 10),
            ("Reading Glasses +1.50", 10),
            ("Reading Glasses +2.00", 10),
            ("Single Vision Spectacles", 10),
            ("Bifocal Spectacles", 8),
            ("Progressive Spectacles", 6),
            ("Protective Eye Shields", 12),
            ("Eye Patch", 20)
        ]
        for med, qty in default_items:
            c.execute("INSERT OR IGNORE INTO inventory (medicine, quantity) VALUES (?, ?)", (med, qty))
        conn.commit()

def add_patient(name, age, gender, contact):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        # Check for existing patient with same name and contact
        c.execute("SELECT id FROM patients WHERE name=? AND contact=?", (name, contact))
        row = c.fetchone()
        if row:
            return row[0]
        c.execute("INSERT INTO patients (name, age, gender, contact) VALUES (?, ?, ?, ?)", (name, age, gender, contact))
        conn.commit()
        return c.lastrowid

def get_patients():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM patients")
        return c.fetchall()

def get_prescriptions(patient_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM prescriptions WHERE patient_id=? ORDER BY date DESC", (patient_id,))
        return c.fetchall()

def add_prescription(patient_id, doctor_name, medicines, dosage, eye_test):
    # New version: add issue, money_given, money_pending
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO prescriptions (patient_id, doctor_name, medicines, dosage, eye_test, issue, money_given, money_pending) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (patient_id, doctor_name, medicines.get('medicines', ''), medicines.get('dosage', ''), medicines.get('eye_test', ''), medicines.get('issue', ''), medicines.get('money_given', 0), medicines.get('money_pending', 0)))
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
