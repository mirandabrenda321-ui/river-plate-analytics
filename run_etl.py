import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import ETL modules
try:
    from scripts.extract import extract_river_scraping
    from scripts.extract_players import extract_river_players
    from scripts.transform import transform_data
    from scripts.transform_players import transform_players
    from scripts.load import load_to_sql
except ImportError as e:
    logger.error(f"Failed to import ETL modules: {e}")
    sys.exit(1)

def main():
    logger.info("🎬 Starting River Plate Analytics ETL Process")

    try:
        # Step 1: Extract Match Data
        logger.info("--- Step 1: Extracting Match Data ---")
        df_matches = extract_river_scraping()
        if df_matches.empty:
            logger.warning("⚠️ No match data extracted.")
        else:
            logger.info(f"✅ Extracted {len(df_matches)} matches.")

        # Step 2: Transform Match Data
        logger.info("--- Step 2: Transforming Match Data ---")
        transform_data() # This functions reads from json and writes to csv, doesn't return df in current impl
        
        # Step 3: Extract Player Data
        logger.info("--- Step 3: Extracting Player Data ---")
        df_players = extract_river_players()
        if df_players.empty:
            logger.warning("⚠️ No player data extracted.")
        else:
            logger.info(f"✅ Extracted {len(df_players)} players.")

        # Step 4: Transform Player Data
        logger.info("--- Step 4: Transforming Player Data ---")
        transform_players() # Reads from json, writes to csv

        # Step 5: Load Data to SQL
        logger.info("--- Step 5: Loading Data to Database ---")
        load_to_sql()
        
        logger.info("🎉 ETL Process Completed Successfully!")

    except Exception as e:
        logger.error(f"❌ ETL Process Failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
