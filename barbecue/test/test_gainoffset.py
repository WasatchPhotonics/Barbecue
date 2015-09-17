""" multiple tests for the gainoffset portion of the barbecue project.

Unlike individual test files, this has many classes in one file. This is
so you can just run nosetests from the project root. The tests will then
all use the qapplication created below. You can get around the apparent
fact that there can be only one qapplication per nosetest run by
splitting into multiple runs, then compiling the coverage report. This
approach makes it easy to just run:

nosetests --with-coverage --cover-package=barbecue

"""

import os
import unittest

from PyQt4 import QtGui, QtTest, QtCore

from barbecue import gain_offset_controller
from barbecue import GainOffset

# All the classes below will reuese this qapplication
app = QtGui.QApplication([])


class TestGainOffsetControllerView(unittest.TestCase):

    def setUp(self):
        self.form = gain_offset_controller.GainOffset()

    def tearDown(self):
        app.closeAllWindows()
      
    def test_application_defaults(self):
        # Verify controller sets the start parameters
        gain_start = self.form.ui.spinBoxGainStart.value()
        gain_stop  = self.form.ui.spinBoxGainEnd.value()
        self.assertEqual(gain_start, 0)
        self.assertEqual(gain_stop, 255)

        offset_start = self.form.ui.spinBoxOffsetStart.value()
        offset_stop  = self.form.ui.spinBoxOffsetEnd.value()
        self.assertEqual(offset_start, 0)
        self.assertEqual(offset_stop, 255)

        lt_box = self.form.ui.spinBoxLineTime
        self.assertEqual(lt_box.value(), 100)

        in_box = self.form.ui.spinBoxIntegrationTime
        self.assertEqual(in_box.value(), 98)

 
    def test_gain_start_and_end_move_together(self):
        # Verify that signals have been setup that link gain start can
        # never be before the gain end, limits are in place, etc.

        gain_start = self.form.ui.spinBoxGainStart
        gain_stop  = self.form.ui.spinBoxGainEnd

        # Move the start to 100, make sure end doesn't move
        gain_start.setValue(100)
        self.assertEqual(gain_stop.value(), 255)

        # Move end to 99, make sure it moves to the minimum
        gain_stop.setValue(99)
        self.assertEqual(gain_stop.value(), 101)

        # Move start to 98, move end to 99, make sure the minimum is
        # always 1 more than the start
        gain_start.setValue(98)
        gain_stop.setValue(99)
        self.assertEqual(gain_start.value(), 98)
        self.assertEqual(gain_stop.value(), 99)
      
    def test_offset_start_and_end_move_together(self):
        # Verify that signals have been setup that link gain start can
        # never be before the gain end, limits are in place, etc.

        offset_start = self.form.ui.spinBoxOffsetStart
        offset_stop  = self.form.ui.spinBoxOffsetEnd

        # Move the start to 100, make sure end doesn't move
        offset_start.setValue(100)
        self.assertEqual(offset_stop.value(), 255)

        # Move end to 99, make sure it moves to the minimum
        offset_stop.setValue(99)
        self.assertEqual(offset_stop.value(), 101)

        # Move start to 98, move end to 99, make sure the minimum is
        # always 1 more than the start
        offset_start.setValue(98)
        offset_stop.setValue(99)
        self.assertEqual(offset_start.value(), 98)
        self.assertEqual(offset_stop.value(), 99)

    def test_line_time_integration_time_move_together(self):
        lt_box = self.form.ui.spinBoxLineTime
        in_box = self.form.ui.spinBoxIntegrationTime

        # move the integration time to 90, make sure the line time does
        # not move
        in_box.setValue(90)
        self.assertEqual(in_box.value(), 90)
        self.assertEqual(lt_box.value(), 100)

        # Move the line time to 80, make sure the integration time drops
        # too 
        lt_box.setValue(80)
        self.assertEqual(lt_box.value(), 80)
        self.assertEqual(in_box.value(), 78)

        # Move line time back up, make sure integration time does not
        # change
        lt_box.setValue(100)
        self.assertEqual(lt_box.value(), 100)
        self.assertEqual(in_box.value(), 78)

        # Attempt to set an integration time higher than 2-line time,
        # expect it does not move
        in_box.setValue(99)
        self.assertEqual(in_box.value(), 98)
        in_box.setValue(105)
        self.assertEqual(in_box.value(), 98)

         
class TestGainOffsetScript(unittest.TestCase):

    def tearDown(self):
        # This cleans up old windows from rapid tests
        app.closeAllWindows()

    def test_parser(self):
        # Accept one option: testing, which causes the form to close
        # itself which should only be used with the unittest as the
        # controller. 
        goapp = GainOffset.GainOffsetApplication()

        # Fail with more than just -t
        with self.assertRaises(SystemExit):
            goapp.parse_args(["-t", "-s"])
            
        args = goapp.parse_args(["-t"])
        self.assertTrue(args.testing)

    def test_main_options(self):
        # Verify that main run with the testing option auto-closes the
        # application
        result = GainOffset.main(["unittest", "-t"])
        self.assertEquals(0, result)
        
if __name__ == "__main__":
    unittest.main()
