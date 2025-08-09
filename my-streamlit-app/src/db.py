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
        
        # Medical tests table with change tracking
        c.execute('''CREATE TABLE IF NOT EXISTS medical_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            blood_pressure TEXT,
            blood_sugar TEXT,
            complete_blood_test TEXT,
            viral_marker TEXT,
            fundus_examination TEXT,
            iop TEXT,
            retinoscopy_dry TEXT,
            retinoscopy_wet TEXT,
            syringing TEXT,
            date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
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
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        # Handle both dict and string formats for medicines parameter
        if isinstance(medicines, dict):
            medicines_str = medicines.get('medicines', '')
            if isinstance(medicines_str, dict):
                medicines_str = str(medicines_str)
            dosage_str = medicines.get('dosage', dosage)
            eye_test_str = medicines.get('eye_test', eye_test)
            issue_str = medicines.get('issue', '')
            money_given = medicines.get('money_given', 0)
            money_pending = medicines.get('money_pending', 0)
        else:
            medicines_str = str(medicines) if medicines else ''
            dosage_str = dosage
            eye_test_str = eye_test
            issue_str = ''
            money_given = 0
            money_pending = 0
        
        c.execute("INSERT INTO prescriptions (patient_id, doctor_name, medicines, dosage, eye_test, issue, money_given, money_pending) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (patient_id, doctor_name, medicines_str, dosage_str, eye_test_str, issue_str, money_given, money_pending))
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

def add_medical_tests(patient_id, bp, sugar, cbt, viral, fundus, iop, retino_dry, retino_wet, syringing):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO medical_tests (patient_id, blood_pressure, blood_sugar, complete_blood_test, viral_marker, fundus_examination, iop, retinoscopy_dry, retinoscopy_wet, syringing) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (patient_id, bp, sugar, cbt, viral, fundus, iop, retino_dry, retino_wet, syringing))
        conn.commit()
        return c.lastrowid

def get_medical_tests(patient_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM medical_tests WHERE patient_id=? ORDER BY date_recorded DESC", (patient_id,))
        return c.fetchall()

def get_latest_medical_tests(patient_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM medical_tests WHERE patient_id=? ORDER BY date_recorded DESC LIMIT 1", (patient_id,))
        return c.fetchone()
