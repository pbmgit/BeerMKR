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
    # Multiple status entries
    self.marlin_queue = [
      "logging:on",
      "logging:off",
      "# Test text",
      "Brew state test",
      "ABORT"
    ]
    self.marlin_index = 0

    # Create mock files dictionary with content
    self.mock_files = {
      'marlinqueue.cmd': self.marlin_queue[0],
      'statusfile': '',
    }

    self.mock_status_file = mock_open(read_data=self.mock_files.get('statusfile', ''))
    # Create a custom mock_open that handles multiple files and changing status
    def mock_file_handler(filename, mode='r'):
      if filename == 'marlinqueue.cmd':
        content = self.marlin_queue[self.marlin_index]
        self.marlin_index = (self.marlin_index + 1) % len(self.marlin_queue)
        return mock_open(read_data=content).return_value
        # Return the current status entry
      return self.mock_status_file.return_value

    # Setup mocks
    self.patcher = patch('builtins.open', side_effect=mock_file_handler)
    self.mock_file = self.patcher.start()
    self.mock_serial = mock_serial
    self.mock_serial.return_value.isOpen.return_value = True
    self.mock_serial.return_value.readline.return_value = b""

    # Import brewtemp after patches
    import brewtemp
    self.brewtemp = brewtemp
    self.brewtemp.ser = self.mock_serial

  def tearDown(self):
    self.patcher.stop()

  def test_check_marlin_queue(self):
    # Reset initial state, see mocked values line 16
    self.brewtemp.logstate = False
    self.brewtemp.run = True
    self.brewtemp.rf = True
    # Run the check_marlin_queue and capture the new logstate
    logstate, rf = self.brewtemp.check_marlin_queue(self.brewtemp.logstate, True)
    
    # Verify logging was turned on
    self.assertTrue(logstate)

    # Run the check_marlin_queue and capture the new logstate
    logstate, rf = self.brewtemp.check_marlin_queue(self.brewtemp.logstate, True)

    # Verify logging was turned off
    self.assertFalse(logstate)
    # Verify the serial write was called only to initialize
    self.mock_serial.assert_called_once()

    # Run the check_marlin_queue and capture the new logstate
    logstate, rf = self.brewtemp.check_marlin_queue(self.brewtemp.logstate, True)

    # Verify logging is still off
    self.assertFalse(logstate)
    # Verify the serial write was called only to initialize
    self.mock_serial.assert_called_once()

    # Run the check_marlin_queue and capture the new logstate
    logstate, rf = self.brewtemp.check_marlin_queue(self.brewtemp.logstate, True)
    self.brewtemp.check_reply(logstate, True)
    # Verify logging is still off
    self.assertFalse(logstate)
    self.mock_serial.write.assert_called_with(b"Brew state test")
    assert self.mock_serial.write.call_count == 1

    # ABORT line
    with self.assertRaises(SystemExit) as cm:
    # Run the check_marlin_queue and capture the new logstate
      logstate, rf = self.brewtemp.check_marlin_queue(self.brewtemp.logstate, True)
      self.assertEqual(cm.exception.code, 1)
      # Verify logging is still off
      self.assertFalse(logstate)

  def test_check_reply(self):
    # Multiple status entries
    self.mock_serial.readline.side_effect = [b" T:65.0\n", ""]

    self.brewtemp.check_reply(self.brewtemp.logstate, True)
    # Verify the status file was written
    self.mock_file.assert_called_with('statusfile', 'w')
    # verify the content written to statusfile
    self.assertEqual(self.mock_status_file.return_value.write.call_count, 3)