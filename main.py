import logging 
import pygame
from pathlib import Path 

from src import AppConfig, PathFinderApp

def configure_logger():
    # define absolute path of the log file 
    BASE_DIR = Path(__file__).resolve().parent  # points to directory where main.py resides 
    
    # / joins directory and file name, works cross-platform
    LOG_FILE = BASE_DIR / "errors.log"

    # configure the root logger using the absolute path 
    # all loggers in the project are children of the root 
    # and automatically inherit settings 
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - [%(filename)s: %(funcName)s: %(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(str(LOG_FILE), mode="w"),
            logging.StreamHandler()  # print to console
        ]
    )

    logger = logging.getLogger(__name__) # create logger for this file 
    logger.info(f"Log file at {LOG_FILE}")


def main():
    
    configure_logger() 
    
    try:
        config = AppConfig()
        app = PathFinderApp(config=config)
        app.run()
    finally:
        pygame.quit() 


if __name__ == "__main__":
    main()
