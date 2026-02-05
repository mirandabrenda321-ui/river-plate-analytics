import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from scripts.extract import extract_river_scraping
from scripts.extract_players import extract_river_players
from scripts.transform import transform_data
from scripts.transform_players import transform_players
from scripts.load import load_to_sql
from database import get_db_engine
from datetime import datetime

# DB Connection handled by database.py
def get_engine():
    return get_db_engine()

st.set_page_config(page_title="River Plate Analytics", page_icon="⚪🔴", layout="wide")

# --- Estilo CSS Identidad River ---
st.markdown("""
    <style>
    /* Título principal: Letras Blancas */
    h1 { 
        color: #ffffff !important; 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Títulos secundarios en Rojo */
    h2, h3 { color: #FFFFFF !important; }

    /* Pestañas: Fondo Blanco + Letra Roja (Inactiva) | Fondo Rojo + Letra Blanca (Activa) */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: #ffffff; 
        color: #ED1C24; 
        border: 2px solid #ED1C24;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ED1C24 !important; 
        color: #ffffff !important; 
        border: 2px solid #ED1C24 !important;
    }

    /* Estilo de métricas */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 8px solid #ED1C24;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    [data-testid="stMetric"] > * {
        color: rgb(14, 17, 23);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚪🔴 RIVER PLATE - TEMPORADA 2026")

with st.sidebar:
    # URL del escudo oficial (usando la imagen de la web que estamos scrappeando)
    url_escudo = "https://cdn.resfu.com/img_data/equipos/593.png?size=120x"
    
    # Mostramos el escudo centrado
    st.image(url_escudo, width=150)
    
    st.markdown("---") # Una línea divisora para separar el logo de los botones
    
    # Aquí iría tu botón de ETL
    if st.button('🚀 Actualizar Datos (ETL)'):
        with st.spinner('Procesando datos...'):
            # Match Data
            extract_river_scraping()
            transform_data()
            
            # Feature: Squad/Plantel Data
            extract_river_players()
            transform_players()
            
            # Load all
            load_to_sql()
            st.success('¡Datos actualizados!')

# --- Lógica de Datos ---
try:
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM partidos_river", engine)
    
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        tab1, tab2, tab3 = st.tabs(["📅 AGENDA POR COMPETICIÓN", "📊 ANÁLISIS ESTADÍSTICO", "⚽ PLANTEL"])

        with tab1:
            st.header("Calendario River Plate 2026")
            competencias = df['competicion'].unique()
            
            for comp in competencias:
                with st.expander(f"🏆 {comp.upper()}", expanded=True):
                    df_comp = df[df['competicion'] == comp].sort_values('fecha').copy()
                    
                    # Renombrar columnas
                    df_view = df_comp.rename(columns={
                        'fecha': 'FECHA', 'local': 'LOCAL', 'visitante': 'VISITANTE',
                        'g_river': 'GOLES DE RIVER', 'g_rival': 'GOLES DEL RIVAL',
                        'resultado_final': 'RESULTADO'
                    })
                    df_view['FECHA'] = df_view['FECHA'].dt.strftime('%d/%m/%Y %H:%M')

                    # Función Semáforo
                    def color_semaforo(val):
                        if val == 'Ganó': return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                        if val == 'Empató': return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
                        if val == 'Perdió': return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                        return ''

                    cols = ['FECHA', 'LOCAL', 'VISITANTE', 'GOLES DE RIVER', 'GOLES DEL RIVAL', 'RESULTADO']
                    st.dataframe(df_view[cols].style.applymap(color_semaforo, subset=['RESULTADO']), 
                                 use_container_width=True, hide_index=True)

        with tab2:
            st.header("Análisis de Rendimiento")
            df_jugados = df[df['resultado_final'] != 'Pendiente'].copy()

            if not df_jugados.empty:
                # 1. PUNTOS POR COMPETICIÓN
                st.subheader("Puntos Obtenidos por Torneo")
                df_jugados['Puntos'] = df_jugados['resultado_final'].map({'Ganó': 3, 'Empató': 1, 'Perdió': 0})
                puntos_comp = df_jugados.groupby('competicion')['Puntos'].sum().reset_index()
                
                c_met = st.columns(len(puntos_comp))
                for i, row in puntos_comp.iterrows():
                    c_met[i].metric(row['competicion'], f"{row['Puntos']} Pts")

                st.divider()

                # 2. GRÁFICO DE BARRAS POR COMPETICIÓN (NUEVO - Con tus colores)
                st.subheader("Resultados Detallados por Competición")
                df_barras = df_jugados.groupby(['competicion', 'resultado_final']).size().reset_index(name='Cantidad')
                
                fig_bar = px.bar(
                    df_barras, 
                    x='competicion', 
                    y='Cantidad', 
                    color='resultado_final',
                    barmode='group',
                    text_auto=True,
                    color_discrete_map={
                        'Ganó': '#b0d3b4',   # Tu verde pastel
                        'Empató': '#e6d89f', # Tu amarillo pastel
                        'Perdió': '#e0bfc2'  # Tu rojo pastel
                    }
                )
                
                fig_bar.update_layout(
                    xaxis_title="", 
                    yaxis_title="Cantidad de Partidos",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                st.divider()

                # 3. DISTRIBUCIÓN TOTAL Y KPIs
                col_izq, col_der = st.columns(2)
                
                with col_izq:
                    st.subheader("Distribución Total de Resultados 2026")
                    fig_pie = px.pie(
                        df_jugados, 
                        names='resultado_final', 
                        color='resultado_final',
                        color_discrete_map={
                            'Ganó': '#b0d3b4', 
                            'Empató': '#e6d89f', 
                            'Perdió': '#e0bfc2'
                        },
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_der:
                    st.subheader("Métricas de Eficacia")
                    # Convertimos a numérico para evitar errores en el promedio
                    df_jugados['g_river_num'] = pd.to_numeric(df_jugados['g_river'], errors='coerce')
                    prom_g = df_jugados['g_river_num'].mean()
                    vallas = len(df_jugados[df_jugados['g_rival'].astype(str) == '0'])
                    
                    st.metric("Promedio Goles de River", f"{prom_g:.2f}")
                    st.metric("Partidos con Valla Invicta", vallas)
            else:
                st.warning("No hay datos de partidos jugados para generar estadísticas.")

        with tab3:
            st.header("Plantel 2026")
            try:
                df_players = pd.read_sql("SELECT * FROM plantilla_river", engine)
                
                if not df_players.empty:
                    # Configuración de columnas
                    st.dataframe(
                        df_players[['dorsal', 'imagen', 'nombre', 'posicion', 'edad', 'bandera', 'altura', 'peso', 'goles', 'amarillas', 'rojas']],
                        column_config={
                            "imagen": st.column_config.ImageColumn("Foto", width="small"),
                            "dorsal": st.column_config.TextColumn("N°", width="small"),
                            "nombre": st.column_config.TextColumn("Jugador", width="medium"),
                            "posicion": "Posición",
                            "edad": "Edad",
                            "bandera": st.column_config.ImageColumn("Nacionalidad", width="small"),
                            "altura": "Altura (cm)",
                            "peso": "Peso (kg)",
                            "goles": "⚽ Goles",
                            "amarillas": "🟨 Amarillas",
                            "rojas": "🟥 Rojas"
                        },
                        hide_index=True,
                        use_container_width=True,
                        height=600
                    )

                    st.divider()
                    
                    # --- Dimensiones Físicas (Histogramas) ---
                    st.subheader("📊 Físico y Edad")
                    
                    # Limpieza de datos visuales
                    df_stats = df_players.copy()
                    df_stats['edad'] = pd.to_numeric(df_stats['edad'], errors='coerce')
                    df_stats['altura'] = pd.to_numeric(df_stats['altura'], errors='coerce')
                    df_stats['peso'] = pd.to_numeric(df_stats['peso'], errors='coerce')
                    
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        fig_edad = px.histogram(df_stats, x="edad", title="Edad", 
                                              nbins=10, color_discrete_sequence=['#ED1C24'],
                                              labels={'count':'Cantidad'})
                        fig_edad.update_layout(bargap=0.2, yaxis_title="Cantidad")
                        st.plotly_chart(fig_edad, use_container_width=True)
                        
                    with c2:
                        fig_alt = px.histogram(df_stats, x="altura", title="Altura (cm)", 
                                             nbins=10, color_discrete_sequence=['#333333'],
                                             labels={'count':'Cantidad'})
                        fig_alt.update_layout(bargap=0.2, yaxis_title="Cantidad")
                        st.plotly_chart(fig_alt, use_container_width=True)

                    with c3:
                        fig_peso = px.histogram(df_stats, x="peso", title="Peso (kg)", 
                                              nbins=10, color_discrete_sequence=['#B0B0B0'],
                                              labels={'count':'Cantidad'})
                        fig_peso.update_layout(bargap=0.2, yaxis_title="Cantidad")
                        st.plotly_chart(fig_peso, use_container_width=True)

                    st.divider()

                    # --- Rendimiento (Donut Charts) ---
                    st.subheader("⚽ Rendimiento: Goles y Tarjetas")
                    
                    # Convertir a numérico por seguridad
                    df_stats['goles'] = pd.to_numeric(df_stats['goles'], errors='coerce').fillna(0)
                    df_stats['amarillas'] = pd.to_numeric(df_stats['amarillas'], errors='coerce').fillna(0)
                    df_stats['rojas'] = pd.to_numeric(df_stats['rojas'], errors='coerce').fillna(0)

                    # Total por equipo
                    total_goles = df_stats['goles'].sum()
                    total_amarillas = df_stats['amarillas'].sum()
                    total_rojas = df_stats['rojas'].sum()

                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric("Goles Totales", int(total_goles))
                    kpi2.metric("Tarjetas Amarillas", int(total_amarillas))
                    kpi3.metric("Tarjetas Rojas", int(total_rojas))

                    # Gráficos de Torta/Anillo - Top Jugadores
                    row_charts = st.columns(3)
                    
                    # Definir paleta River: Rojo, Negro, Gris Oscuro, Gris Claro, Rojo Oscuro
                    palette_river = ['#ED1C24', '#333333', '#808080', '#B0B0B0', '#8B0000']

                    # 1. Goles (Top goleadores)
                    df_goles = df_stats[df_stats['goles'] > 0].sort_values('goles', ascending=False)
                    if not df_goles.empty:
                        fig_gol = px.pie(df_goles, values='goles', names='nombre', title='Distribución de Goles',
                                         hole=0.4, color_discrete_sequence=palette_river)
                        row_charts[0].plotly_chart(fig_gol, use_container_width=True)
                    else:
                        row_charts[0].info("Sin goles registrados")

                    # 2. Amarillas
                    df_am = df_stats[df_stats['amarillas'] > 0]
                    if not df_am.empty:
                        fig_am = px.pie(df_am, values='amarillas', names='nombre', title='Tarjetas Amarillas',
                                        hole=0.4, color_discrete_sequence=['#FFD700', '#F0E68C', '#BDB76B'])
                        row_charts[1].plotly_chart(fig_am, use_container_width=True)
                    else:
                        row_charts[1].info("Sin amarillas registradas")

                    # 3. Rojas
                    df_rj = df_stats[df_stats['rojas'] > 0]
                    if not df_rj.empty:
                        fig_rj = px.pie(df_rj, values='rojas', names='nombre', title='Tarjetas Rojas',
                                        hole=0.4, color_discrete_sequence=['#FF0000', '#8B0000'])
                        row_charts[2].plotly_chart(fig_rj, use_container_width=True)
                    else:
                        row_charts[2].info("Sin rojas registradas")

                else:
                    st.info("No hay datos de plantilla disponibles.")
            
            except Exception as e:
                # Si la tabla no existe aún
                st.error(f"Error cargando plantilla: {e}")

    else:
        st.info("La base de datos está vacía. Ejecuta el ETL en la barra lateral.")

except Exception as e:
    st.error(f"Error en la aplicación: {e}")