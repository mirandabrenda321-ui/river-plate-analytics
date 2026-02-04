import pandas as pd
import numpy as np
import os

def transform_data():
    print("🚀 Transformando datos con fechas y horarios...")
    input_path = 'data/river_raw_data.json'
    output_path = 'data/river_cleaned.csv'

    if not os.path.exists(input_path):
        print("❌ No se encontró el archivo raw_data.json")
        return

    # Cargamos el JSON
    df = pd.read_json(input_path)

    meses = {
        'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 
        'May': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08', 
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'
    }
    
    def procesar_fecha_completa(row):
        f = str(row['fecha'])
        h = str(row.get('horario', '00:00')) # Si no hay hora, ponemos medianoche
        
        # Si la hora parece un marcador (tiene un '-'), no es una hora válida
        if '-' in h or not ':' in h:
            h = "00:00"

        # Reemplazamos el nombre del mes por su número
        for mes_txt, mes_num in meses.items():
            if mes_txt in f:
                f = f.replace(mes_txt, mes_num)
                break
        
        # Combinamos fecha y hora: "24 01 26 21:00"
        try:
            string_final = f"{f} {h}"
            return pd.to_datetime(string_final, format='%d %m %y %H:%M', errors='coerce')
        except:
            return pd.to_datetime(f, format='%d %m %y', errors='coerce')

    # Aplicamos la transformación fila por fila
    df['fecha'] = df.apply(procesar_fecha_completa, axis=1)



    # Limpieza final de columnas
    # Aseguramos que cualquier valor nulo, None o vacío se convierta en '-'
    df['g_river'] = df['g_river'].replace([np.nan, None, 'None', ''], '-')
    df['g_river'] = df['g_river'].fillna('-')
    
    df['g_rival'] = df['g_rival'].replace([np.nan, None, 'None', ''], '-')
    df['g_rival'] = df['g_rival'].fillna('-')

    # Ordenar cronológicamente
    df = df.sort_values('fecha', ascending=True)

    # Exportar a CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Transformación exitosa: {len(df)} partidos procesados con horarios.")

if __name__ == "__main__":
    transform_data()