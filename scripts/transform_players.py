
import pandas as pd
import os

def transform_players():
    print("🚀 Transformando datos de plantilla...")
    input_path = 'data/river_raw_players.json'
    output_path = 'data/river_players_cleaned.csv'

    if not os.path.exists(input_path):
        print("❌ No se encontró el archivo river_raw_players.json")
        return

    df = pd.read_json(input_path)

    # 1. Limpieza de Edad (extraer solo número si es necesario, o dejar como está si ya es limpio)
    # En el scraping ya lo sacamos limpio si era texto, pero por seguridad:
    df['edad'] = df['edad'].astype(str).str.replace(' años', '', regex=False)

    # 2. Limpieza de Altura y Peso
    # Altura "184 cm" -> 184
    # Peso "77 kg" -> 77
    def clean_metric(val):
        if not isinstance(val, str): return val
        return val.lower().replace('cm', '').replace('kg', '').strip()

    df['altura'] = df['altura'].apply(clean_metric)
    df['peso'] = df['peso'].apply(clean_metric)

    # 3. Manejo de nulos (Dorsal a '-')
    df['dorsal'] = df['dorsal'].replace([None, 'None', '', float('nan')], '-')
    df['dorsal'] = df['dorsal'].fillna('-')

    # 4. Asegurar que bandera exista, si no, poner placeholder
    if 'bandera' not in df.columns:
        df['bandera'] = "https://cdn.resfu.com/media/img/flags/st3/small/ar.png"
    
    df['bandera'] = df['bandera'].fillna("https://cdn.resfu.com/media/img/flags/st3/small/ar.png")

    # 5. Limpieza de Goles y Tarjetas
    cols_stats = ['goles', 'rojas', 'amarillas']
    for col in cols_stats:
        if col in df.columns:
            # Convertir a cero si hay guiones o nulos
            df[col] = df[col].astype(str).replace(['-', '', 'nan', 'None'], '0')
            # Extraer solo numeros
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0

    # Manejo general de nulos
    df = df.fillna('-')

    # Guardar
    df.to_csv(output_path, index=False)
    print(f"✅ Transformación de plantilla exitosa: {len(df)} jugadores procesados.")

if __name__ == "__main__":
    transform_players()
