
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os

def extract_river_players():
    print("🚀 Iniciando scraping de Plantilla...")
    url = "https://www.resultados-futbol.com/equipo/plantilla/ca-river-plate/2026"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.select_one('table.sdata_table')
        if not table:
            print("❌ No se encontró la tabla de plantilla.")
            return pd.DataFrame()

        players = []
        current_position = "Desconocido"
        
        rows = table.select('tbody tr')
        
        for row in rows:
            # Check if it's a header row for position (e.g. "Portero", "Defensa")
            header_th = row.select_one('th.axis')
            if header_th:
                current_position = header_th.get_text(strip=True)
                continue
            
            # Check if it's a player row
            if not row.has_attr('itemprop'):
                continue
                
            try:
                # 1. Number / Dorsal
                dorsal_tag = row.select_one('td.num')
                dorsal = dorsal_tag.get_text(strip=True) if dorsal_tag else "-"
                
                # 2. Name
                name_tag = row.select_one('th.sdata_player_name span[itemprop="name"]')
                name = name_tag.get_text(strip=True) if name_tag else "Desconocido"
                
                # 3. Image
                img_tag = row.select_one('td.sdata_player_img img')
                img_url = img_tag['src'] if img_tag else None
                
                # 4. Age & Birthdate
                age_tag = row.select_one('td.birthdate')
                age = age_tag.get_text(strip=True) if age_tag else "-"
                birthdate = age_tag['content'] if age_tag and 'content' in age_tag.attrs else None
                
                # 5. Nationality & Flag
                nat_tag = row.select_one('td.ori span[itemprop="name"]')
                nationality = nat_tag['content'] if nat_tag and 'content' in nat_tag.attrs else "ar"
                
                # Flag scraping
                flag_tag = row.select_one('td.ori img')
                flag_url = flag_tag['src'] if flag_tag else "https://cdn.resfu.com/media/img/flags/st3/small/ar.png"

                # 6. Stats (Height, Weight, Goals, Cards)
                # The columns after nationality are: Height, Weight, Goals, Yellow, Red
                # We iterate data cells
                dat_cells = row.select('td.dat')
                height = dat_cells[0].get_text(strip=True) if len(dat_cells) > 0 else "-"
                weight = dat_cells[1].get_text(strip=True) if len(dat_cells) > 1 else "-"
                goals = dat_cells[2].get_text(strip=True) if len(dat_cells) > 2 else "0"
                # Corregido: Index 3 es Rojas, Index 4 es Amarillas (según reporte de usuario)
                red_cards = dat_cells[3].get_text(strip=True) if len(dat_cells) > 3 else "0"
                yellow_cards = dat_cells[4].get_text(strip=True) if len(dat_cells) > 4 else "0"
                
                players.append({
                    "dorsal": dorsal,
                    "nombre": name,
                    "posicion": current_position,
                    "edad": age,
                    "nacimiento": birthdate,
                    "nacionalidad": nationality,
                    "bandera": flag_url,
                    "altura": height,
                    "peso": weight,
                    "goles": goals,
                    "amarillas": yellow_cards,
                    "rojas": red_cards,
                    "imagen": img_url
                })
                
            except Exception as e:
                print(f"⚠️ Error procesando fila de jugador: {e}")
                continue

        df = pd.DataFrame(players)
        
        # Guardar en raw_players.json
        os.makedirs('data', exist_ok=True)
        df.to_json('data/river_raw_players.json', orient='records', force_ascii=False)
        
        print(f"✅ Scraping plantilla finalizado. {len(df)} jugadores guardados.")
        return df

    except Exception as e:
        print(f"❌ Error en el scraping de plantilla: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    extract_river_players()
