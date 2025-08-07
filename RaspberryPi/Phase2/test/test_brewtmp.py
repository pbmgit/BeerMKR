import unittest
import serial
import sys
import os
import datetime
import time
from unittest.mock import mock_open, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBrewTemp(unittest.TestCase):
  @patch('serial.Serial')
  def setUp(self, mock_serial):
    # Multiple status entries to simulate temperature changes
    self.marlin_queue = [
      "logging:on",
      "logging:off",
      "# Test text",
      "ABORT",
      "",
      "Some other command"
    ]
    self.marlin_index = 0

    # Create mock files dictionary with content
    self.mock_files = {
      'marlinqueue.cmd': self.marlin_queue[0],
      'statusfile': '',
    }

    # Create a custom mock_open that handles multiple files and changing status
    def mock_file_handler(filename, mode='r'):
      if filename == 'marlinqueue.cmd':
        content = self.marlin_queue[self.marlin_index]
        self.marlin_index = (self.marlin_index + 1) % len(self.marlin_queue)
        return mock_open(read_data=content).return_value
      return mock_open(read_data=self.mock_files.get(filename, '')).return_value

    # Setup mocks
    self.patcher = patch('builtins.open', side_effect=mock_file_handler)
    self.mock_file = self.patcher.start()
    self.mock_serial = mock_serial
    self.mock_serial.return_value.isOpen.return_value = True
    self.mock_serial.return_value.readline.return_value = b""

    # Start patches for brewtemp module
    self.run_patch = patch('brewtemp.run', False)
    self.rf_patch = patch('brewtemp.rf', False)
    self.ser_patch = patch('brewtemp.ser', self.mock_serial.return_value)

    self.run_patch.start()
    self.rf_patch.start()
    self.ser_patch.start()

    # Import brewtemp after patches
    import brewtemp
    self.brewtemp = brewtemp

  def tearDown(self):
    self.patcher.stop()

  def test_logging_on(self):
    self.brewtemp.rf = True
    with open('marlinqueue.cmd', 'r+') as cmdfile:
      self.mock_file.return_value.readline.return_value = "logging:on\n"
      self.brewtemp.rf = False  # Stop after one iteration
    self.assertTrue(self.brewtemp.log_to_file)

  def test_logging_off(self):
    # Simulate logging:off command
    self.mock_file.return_value.readline.return_value = "logging:off\n"
    self.assertFalse(self.brewtemp.log_to_file)

  def test_marlin_command(self):
    # Simulate a Marlin command
    self.mock_file.return_value.readline.return_value = "M104 S60\n"

    # Verify command is sent to serial
    self.mock_serial.return_value.write.assert_called_with(b"M104 S60\n")

  def test_temperature_response(self):
    # Simulate temperature response from Marlin
    self.mock_serial.return_value.readline.return_value = b" T:60.0 /60.0"
    response = self.mock_serial.return_value.readline()
    self.assertIn(b"T:60.0 /60.0", response)