import logging
import os


class GetLogger:

    def __init__(self, logger_file = None):
        self.log_file = logger_file
        # Create a custom logger
        self.logger = logging.getLogger(__name__)

        # Create handlers
        c_handler = logging.StreamHandler()
        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.setLevel(logging.DEBUG)

        if self.log_file is not None:
            # Create base directory if missing
            self._create_base_dir()
            f_handler = logging.FileHandler(self.log_file)
            f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            f_handler.setFormatter(f_format)
            self.logger.addHandler(f_handler)
            self.logger.setLevel(logging.DEBUG)

    def _create_base_dir(self):
        base_dir = os.path.dirname(self.log_file)
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)

    def get_logger(self):
        return self.logger
