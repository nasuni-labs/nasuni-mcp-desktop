""" App package. """
import logging
from .config import Config
from .file_system import FileSystem

def init_logger(config:Config):
    """
    Initialize the logger.
    """
    logging.basicConfig(level=logging.CRITICAL,
                        handlers=[logging.NullHandler()])
    
    log = logging.getLogger("nasuni_file_system")
    log_level = config.get_log_level()

    if log_level == logging.NOTSET and config.log_destination != "":
        log_level = logging.INFO

    log.setLevel(log_level)

    if config.log_destination:
        handler = logging.FileHandler(config.log_destination)
    else:
        handler = logging.NullHandler()
        
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.info("Logger initialized")
    return log

def get_file_system_client(config:Config, log:logging.Logger) -> FileSystem:
    """
    Get FileSystem instance.
    """

    if not config.file_system_path:
        raise ValueError("File system path is not set in the config")

    return FileSystem(config, log)