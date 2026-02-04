import pandas as pd
from sqlalchemy import create_engine
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path to allow importing 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

# Configuración interna (solo variables que no son de DB si fueran necesarias)
# DB connection now handled by database.py

from database import get_db_engine

def load_to_sql():
    print("Cargando datos a PostgreSQL...")
    
    # Obtener conexión (dev o prod según .env)
    engine = get_db_engine()
    
    # Leer el CSV limpio
    df = pd.read_csv('data/river_cleaned.csv')
    
    # Cargar a la tabla (reemplaza si existe)
    df.to_sql('partidos_river', engine, if_exists='replace', index=False)
    
    print("¡Carga completada exitosamente!")

if __name__ == "__main__":
    load_to_sql()