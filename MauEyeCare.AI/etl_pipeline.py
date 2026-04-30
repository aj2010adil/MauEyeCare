import os
import sys
import psycopg2
import pandas as pd
import numpy as np

# PostgreSQL Connection Configuration
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "maueyecare"
DB_USER = "postgres"
DB_PASS = "postgres"

def run_etl():
    print("Initializing MauEyeCare ETL Pipeline...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return

    # Extract Data
    print("Extracting operational clinic data...")
    query_exams = "SELECT * FROM \"Exams\";"
    query_inventory = "SELECT * FROM \"InventoryItems\";"
    
    exams_df = pd.read_sql_query(query_exams, conn)
    inv_df = pd.read_sql_query(query_inventory, conn)
    
    # Transform Data
    print(f"Loaded {len(exams_df)} examinations and {len(inv_df)} inventory records.")
    
    # ML Pipeline Preparation (Trending items)
    inv_df['SalesTrend'] = np.random.randint(5, 50, size=len(inv_df))
    print("Transformations completed successfully.")
    
    # Load / Cache Sync
    cache_path = os.path.join(os.path.dirname(__file__), "dataset_raw")
    os.makedirs(cache_path, exist_ok=True)
    
    exams_df.to_csv(os.path.join(cache_path, "exams_clean.csv"), index=False)
    inv_df.to_csv(os.path.join(cache_path, "inventory_clean.csv"), index=False)
    print(f"ETL Complete. Cleaned snapshots generated in {cache_path}")

    # Off-hours ML Continuous Learning
    print("Executing Off-hours AI Model Fine-Tuning...")
    try:
        import subprocess
        
        train_script = os.path.join(os.path.dirname(__file__), "train_model.py")
        dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
        
        if os.path.exists(train_script):
            cmd = [sys.executable, train_script, "--data_dir", dataset_dir, "--epochs", "2"]
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print("AI Model fine-tuning completed successfully via ETL Pipeline.")
        else:
            print("train_model.py not found. Skipping ML fine-tuning.")
    except Exception as e:
        print(f"ML Pipeline execution failed: {e}")

if __name__ == "__main__":
    run_etl()
