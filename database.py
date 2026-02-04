
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_engine():
    """
    Returns a SQLAlchemy engine based on the 'ENVIRONMENT' variable.
    - 'dev': Uses local Docker credentials.
    - 'prod': Uses Supabase/Cloud credentials.
    """
    env = os.getenv("ENVIRONMENT", "dev").lower()
    
    if env == "prod":
        # Supabase / Production Credentials
        user = os.getenv("SUPABASE_USER")
        password = os.getenv("SUPABASE_PASSWORD")
        host = os.getenv("SUPABASE_HOST")
        port = os.getenv("SUPABASE_PORT", "5432")
        message = "🌍 Connecting to Production Database (Supabase)..."
        
        # Supabase specific: Connection pooling requires 'postgresql' dialect
        db_name = "postgres"  # Supabase default DB is usually 'postgres'
        
        # Construct connection string
        # Note: sqlalchemy < 1.4 uses postgres://, but we use postgresql:// for compatibility
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        
    else:
        # Local / Development Credentials
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "admin123")
        host = os.getenv("DB_HOST", "localhost") # Default to localhost for running scripts outside docker
        # NB: Inside docker, DB_HOST should be 'db'. Outside, it is 'localhost'.
        # We handle this by letting the .env or docker-compose override DB_HOST.
        
        port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "river_plate_db")
        message = "💻 Connecting to Local Database (Docker)..."
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    print(message)
    
    try:
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        print(f"❌ Error creating database engine: {e}")
        raise e
