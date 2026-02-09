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
    if os.path.exists('data/river_cleaned.csv'):
        df = pd.read_csv('data/river_cleaned.csv')
        df.to_sql('partidos_river', engine, if_exists='replace', index=False)
        print("✅ Tabla 'partidos_river' actualizada.")
    
    # Cargar Plantilla
    if os.path.exists('data/river_players_cleaned.csv'):
        df_players = pd.read_csv('data/river_players_cleaned.csv')
        df_players.to_sql('plantilla_river', engine, if_exists='replace', index=False)
        print("✅ Tabla 'plantilla_river' actualizada.")

    print("✅ Carga a base de datos exitosa.")

    # --- Metadata: Last Update ---
    from sqlalchemy import text
    from datetime import datetime
    import pytz

    try:
        with engine.connect() as conn:
            # Create table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS metadata_etl (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP
                );
            """))
            
            # Upsert timestamp
            ahora = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
            timestamp_str = ahora.strftime('%Y-%m-%d %H:%M:%S')
            
            conn.execute(text("""
                INSERT INTO metadata_etl (key, value, updated_at)
                VALUES ('last_execution', :ts, :ts_obj)
                ON CONFLICT (key) DO UPDATE 
                SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at;
            """), {"ts": timestamp_str, "ts_obj": ahora})
            
            conn.commit()
            print(f"🕒 Metadata actualizada: {timestamp_str}")
            
    except Exception as e:
        print(f"⚠️ Error actualizando metadata: {e}")

if __name__ == "__main__":
    load_to_sql()