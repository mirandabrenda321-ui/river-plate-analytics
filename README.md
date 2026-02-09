
# ⚪🔴 River Plate Analytics Dashboard ⚪🔴

Este proyecto es un dashboard de análisis de datos interactivo construido con **Python (Streamlit)**, **SQL** y **Docker**, enfocado en seguir el rendimiento del Club Atlético River Plate durante la temporada 2026.

La aplicación integra datos de partidos (fixture y resultados) y del plantel profesional, proporcionando visualizaciones avanzadas y KPIs de rendimiento.

## Vista previa:
⚪🔴 https://river-plate-analytics-brenda-miranda.streamlit.app/

## ✨ Características Principales

### 📅 Agenda y Resultados
- **Calendario Completo:** Visualización de partidos por competición (Liga, Copas, Amistoso, etc).
- **Semáforo de Resultados:** Identificación rápida (✅ Ganó, ⚠️ Empató, ❌ Perdió).
- **KPIs:** Promedio de goles, vallas invictas y puntos por torneo.

### ⚽ Plantel Profesional
- **Fichas de Jugadores:** Tabla interactiva con fotos, dorsales, posición y nacionalidad.
- **Estadísticas de Rendimiento:**
  - Goles, Tarjetas Amarillas y Rojas.
  - Gráficos de torta/anillo con los goles y amonestados.
- **Datos Biométricos:**
  - Distribución de Edad, Altura y Peso del equipo.
- **Identidad Visual:** Gráficos personalizados con la paleta de colores oficial del club.

### 🚀 Ingeniería de Datos (ETL)
- **Web Scraping:** Scripts en Python (`Match` y `Player` scrapers) que extraen datos en tiempo real.
- **Base de Datos:** Almacenamiento estructurado en **PostgreSQL**.

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.11
- **Frontend:** Streamlit
- **Base de Datos:** PostgreSQL 15
- **Infraestructura:** Docker & Docker Compose
- **Librerías Clave:**
  - `pandas` (Manipulación de datos)
  - `plotly` (Gráficos interactivos)
  - `beautifulsoup4` (Web Scraping)
  - `sqlalchemy` (ORM SQL)

## 🚀 Cómo Empezar

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/river-plate-analytics.git
cd river-plate-analytics
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz (podés usar `.env.template` como base):
```env
DB_HOST=db
DB_NAME=river_plate_db
DB_USER=postgres
DB_PASSWORD=admin123
DB_PORT=5432
```

### 3. Ejecutar con Docker

Construye y levanta los servicios (App + Base de Datos):

```bash
docker-compose up -d --build
```

- **Dashboard:** http://localhost:8501
- **Base de Datos:** localhost:5432

### 4. Cargar Datos Iniciales

Al iniciar por primera vez, la base de datos estará vacía.
1. Ve al dashboard en el navegador.
2. En la barra lateral, presiona el botón **🚀 Actualizar Datos (ETL)**.
3. Espera a que finalice el proceso de scraping y carga.

## 📂 Estructura del Proyecto

```
/river-plate-analytics
├── .env                # Credenciales (no versionado)
├── docker-compose.yml  # Orquestación de servicios
├── Dockerfile          # Imagen de la app
├── main.py             # App principal de Streamlit
├── database.py         # Conexión a DB
├── scripts/            # Módulos ETL
│   ├── extract.py            # Scraping de Partidos
│   ├── extract_players.py    # Scraping de Plantel
│   ├── transform.py          # Limpieza de Partidos
│   ├── transform_players.py  # Limpieza de Plantel
│   └── load.py               # Carga a SQL
└── sql/
    └── init_db.sql     # Script inicial
```

---
*Vamos River Plate⚪🔴⚪*

## 🤖 Automatización con GitHub Actions

Este proyecto incluye un flujo de trabajo de GitHub Actions para ejecutar el proceso ETL automáticamente todos los días.

### Configuración de Secretos

Para que la automatización funcione, necesitas configurar las siguientes credenciales en los "Secrets" de tu repositorio en GitHub (Settings > Secrets and variables > Actions):

| Nombre del Secreto | Descripción |
|--------------------|-------------|
| `DB_HOST`          | Host de tu base de datos (ej. Supabase) |
| `DB_NAME`          | Nombre de la base de datos (ej. `postgres`) |
| `DB_USER`          | Usuario de la base de datos (ej. `postgres`) |
| `DB_PASSWORD`      | Contraseña de la base de datos |
| `DB_PORT`          | Puerto de la base de datos (ej. `5432` o `6543`) |

El workflow se ejecutará automáticamente todos los días a las 00:00 UTC, o puedes ejecutarlo manualmente desde la pestaña "Actions" en GitHub.