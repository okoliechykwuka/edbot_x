import shutil
import os
import logging

def cleanup_database():
    """Clean up the ChromaDB database directory"""
    db_path = "db"
    try:
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            os.makedirs(db_path)
            logging.info("Successfully cleaned up database directory")
        else:
            print("Database does not exist")
    except Exception as e:
        logging.error(f"Error cleaning up database: {e}")
        raise

if __name__ == "__main__":
    cleanup_database()