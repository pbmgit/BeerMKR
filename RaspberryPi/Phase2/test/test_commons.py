import unittest
import sys
import os
from unittest.mock import mock_open, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MyTestCase(unittest.TestCase):
  def setUp(self):
    from commons import logger
    self.logger = logger

  def test_something(self):
    # Mock the file writing to avoid actual file I/O
    with patch('builtins.open', mock_open()) as mocked_file:
      # Call the logger function
      self.logger('test.log', True, 'This is a test log message')
      # Check if the file was opened correctly
      mocked_file.assert_called_once_with('test.log', 'a')
      # Check if the correct message was written to the file
      import re
      argument_string = mocked_file().write.call_args[0][0]
      pattern = re.compile(".*This is a test log message\n")
      assert pattern.match(argument_string)


if __name__ == '__main__':
    unittest.main()