import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config
from main import configure_logging


class TestLogging(unittest.TestCase):
    def test_configure_logging_creates_log_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "errors.log")
            original_log_file = getattr(config, "LOG_FILE", None)
            config.LOG_FILE = log_file
            try:
                logger = configure_logging()
                logger.error("test error message")
            finally:
                config.LOG_FILE = original_log_file

            self.assertTrue(os.path.exists(log_file))


if __name__ == "__main__":
    unittest.main()
