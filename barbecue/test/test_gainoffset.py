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

from barbecue import controller

# All the classes below will reuese this qapplication
app = QtGui.QApplication([])


class TestGainOffsetControllerView(unittest.TestCase):

    def setUp(self):
        self.form = controller.GainOffset()

    def tearDown(self):
        app.closeAllWindows()
       
    def test_gain_start_and_end_move_together(self):
        # Verify that signals have been setup that link gain start can
        # never be before the gain end, limits are in place, etc.
        gain_start = self.form.ui.spinBoxGainStart.value()
        gain_stop  = self.form.ui.spinBoxGainEnd.value()
        self.assertEqual(gain_start, 0)
        self.assertEqual(gain_stop, 255)
        
if __name__ == "__main__":
    unittest.main()
