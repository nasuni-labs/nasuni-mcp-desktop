""" Config class """
import logging
import os
import sys
from dotenv import load_dotenv

class Config:
    """
    Configuration class for the application. For new features, please add 
    configuration options here.
    """
    def __init__(self, env_file_path : str = "") -> None:
        self.error_traceback = False

        # config keys
        self.file_system_path = ""

        self.log_destination = ""
        self.log_level = ""

        # Max items to scan in a folder
        self.max_scan_items: int = 10000
        # Max size of a file to return
        self.max_return_file_size: int = 1 * 1024 * 1024  # 1 MB
        # Max size of a file to read
        self.max_read_file_size: int = 20 * 1024 * 1024  # 20 MB
        # Array of folders to exclude from access
        self.exclude_folders: list[str] = []
        # Expression to ignore certain files by a name
        self.ignore_files_exp: str = ""
        # Expression to ignore certain folders by a name
        self.ignore_folders_exp: str = ""

        self._set_values(env_file_path)

    def _set_values(self, env_file_path: str) -> None:
        """
        Set configuration values from environment variables.
        """
        if env_file_path != "":
            load_dotenv(env_file_path)
        
        # ENV has highest priority. It can overwrite values from static .env file
        self._parse_env()
        self._merge_command_line_args()

        # some post processing.

        # remove trailing slashes for each value in exclude_folders
        self.exclude_folders = [folder.rstrip("/") for folder in self.exclude_folders]

    def _merge_command_line_args(self):
        """
        Merge command line arguments into the configuration.
        Arrays are represented as --config_var VAL1 VAL2 ... till
        the next config_var is found or till the end.
        """
        possible_command_line_args = {
            "exclude_folders": list[str],
        }
        for arg in sys.argv[1:]:
            if arg.startswith("--"):
                current_key = arg[2:]
                if current_key in possible_command_line_args:
                    current_type = possible_command_line_args[current_key]
                    current_values = []
                    while True:
                        try:
                            next_arg = sys.argv[sys.argv.index(arg) + 1]
                        except IndexError:
                            break
                        if next_arg.startswith("--"):
                            break
                        current_values.append(next_arg)
                        sys.argv.remove(next_arg)
                    if len(current_values) > 0:
                        if current_type == list[str] and current_values[0]:
                            setattr(self, current_key, current_values)
                        elif current_type is str:
                            setattr(self, current_key, current_values[0] if current_values else "")
                        elif current_type is int:
                            setattr(self, current_key, int(current_values[0]) if current_values else 0)

    def get_log_level(self) -> int:
        """
        Get the log level for the application.
        """
        if self.log_level == "DEBUG":
            return logging.DEBUG
        if self.log_level == "INFO":
            return logging.INFO
        if self.log_level == "WARNING":
            return logging.WARNING
        if self.log_level == "ERROR":
            return logging.ERROR
        if self.log_level == "CRITICAL":
            return logging.CRITICAL
        return logging.NOTSET

    def _parse_env(self) -> None:
        """
            Set values from ENV. Overwrite values for config
        """
        for attr, current_value in vars(self).items():
            env_value = os.environ.get(attr.upper())

            if env_value is not None and env_value != "":
                # Convert string environment values to appropriate types
                if isinstance(current_value, bool):
                    # Convert string to boolean
                    setattr(self, attr, env_value.lower() in ('true', '1', 'yes', 'on'))
                elif isinstance(current_value, int):
                    # Convert string to integer
                    try:
                        setattr(self, attr, int(env_value))
                    except ValueError:
                        # Keep original value if conversion fails
                        pass
                elif isinstance(current_value, float):
                    # Convert string to float
                    try:
                        setattr(self, attr, float(env_value))
                    except ValueError:
                        # Keep original value if conversion fails
                        pass
                elif isinstance(current_value, list):
                    # Convert string to list. This kind of config variables must be list[str]
                    env_value = env_value.split(",") if env_value else []
                    setattr(self, attr, env_value)
                else:
                    # String values - set directly
                    setattr(self, attr, env_value)

        
