import unittest
import os
import tempfile
from unittest.mock import mock_open, patch
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBeerMKR(unittest.TestCase):
  @staticmethod
  def setup_test_environment():
    # Create temp directory with mock files
    test_dir = tempfile.mkdtemp()

    # Create mock status file
    with open(os.path.join(test_dir, 'statusfile'), 'w') as f:
      f.write("2024-01-01 12:00:00\n")
      f.write("BREWING\n")
      f.write("Temps grain:65 bag:70\n")

    return test_dir

  def setUp(self):
    # Setup test environment
    self.test_filepath = '/tmp/test_beerpi'
    self.test_log = os.path.join(self.test_filepath, 'test_brewlog.log')
    self.test_marlin = os.path.join(self.test_filepath, 'test_marlin.cmd')
    self.test_recipe_data = (
      "monitor:on:30\n"
      "bag:set:65:wait\n"
      "grain:set:70\n"
      "wait:300"
    )

    # Multiple status entries to simulate temperature changes
    self.status_entries = [
      "2024-01-01 12:00:00\nBREWING\nTemps grain:65.0 extra:0 bag:60.0\n",
      "2024-01-01 12:00:00\nBREWING\nTemps grain:65.0 extra:0 bag:62.0\n",
      "2024-01-01 12:00:00\nBREWING\nTemps grain:65.0 extra:0 bag:64.0\n",
      "2024-01-01 12:00:00\nBREWING\nTemps grain:65.0 extra:0 bag:65.0\n"
    ]
    self.status_index = 0

    # Create mock files dictionary with content
    self.mock_files = {
      'recipe.bmkr': self.test_recipe_data,
      'statusfile': self.status_entries[0],
      'marlinqueue.cmd': '',
      'brewlog.log': '',
      'buttonfile': ''
    }

    # Create a custom mock_open that handles multiple files and changing status
    def mock_file_handler(filename, mode='r'):
      if filename == 'statusfile':
        content = self.status_entries[self.status_index]
        self.status_index = (self.status_index + 1) % len(self.status_entries)
        return mock_open(read_data=content).return_value
      return mock_open(read_data=self.mock_files.get(filename, '')).return_value

    # Setup the mock before importing BeerMKR
    self.patcher = patch('builtins.open', side_effect=mock_file_handler)
    self.mock_file = self.patcher.start()

    # Add sleep patch to prevent delays
    self.sleep_patcher = patch('time.sleep', return_value=None)
    self.sleep_patcher.start()

    # Now we can safely import BeerMKR
    from BeerMKR import recipe, logger, marlincmd
    self.recipe = recipe
    self.logger = logger
    self.marlincmd = marlincmd

  def tearDown(self):
    self.patcher.stop()
    self.sleep_patcher.stop()

  @patch('builtins.open', new_callable=mock_open)
  def test_marlincmd(self, mock_open_func):
    self.marlincmd("M104 S60")
    mock_open_func.assert_called_with('marlinqueue.cmd', 'a')
    mock_open_func().write.assert_called_with("M104 S60\n")

  def test_recipe_parsing(self):
    test_recipe = [
      "monitor:on:30",
      "bag:set:65:wait",
      "grain:set:70",
      "wait:300"
    ]
    self.assertEqual(self.recipe, test_recipe)


if __name__ == '__main__':
  unittest.main()
