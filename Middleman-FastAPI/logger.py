import logging
from pathlib import Path
from datetime import datetime

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


# Setup logging
def setup_logger():
    logger = logging.getLogger("middleman_api")
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(
        log_dir / f"api_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
