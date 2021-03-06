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
import sys
import logging
import unittest

from PyQt4 import QtGui, QtTest, QtCore

from barbecue import gain_offset_controller
from barbecue import GainOffset

# All the classes below will reuese this qapplication
app = QtGui.QApplication([])

log = logging.getLogger()
log.setLevel(logging.DEBUG)

strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)

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

    def test_image_widget_populated(self):
        # Make sure the image widget is available at a useful size
        imgd = self.form.ui.image_dialog
        self.assertGreater(imgd.width(), 100)
        self.assertGreater(imgd.height(), 100)
 
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

    def test_result_in_list_widget(self):
        # Set a 1-iteration of the offset value.
        # Gain value is the internal range 
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(1)
        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(1)

        # Click the scan button
        self.form.ui.toolButtonStart.click()

        # verify that the datamodel increases in size
        QtTest.QTest.qWait(1000)
        dm = self.form.datamod
        self.assertEqual(dm.rowCount(), 2)

        # Append another scan group, verify the result size
        self.form.ui.spinBoxOffsetEnd.setValue(16)
        self.form.ui.toolButtonStart.click()
        QtTest.QTest.qWait(1000)
        self.assertEqual(dm.rowCount(), 19)

    def test_summary_display_updates(self):
        # Set offset and gain to very short values, verify the display
        # text updates
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(1)

        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(1)

        ref_txt = "System will process 4 combinations."
        lbl_txt = self.form.ui.labelProcessing.text()
        self.assertEqual(ref_txt, lbl_txt)

    def test_save_results(self):
        # Create a small scan range, make sure the file is written to
        # disk
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(1)

        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(1)

        self.form.ui.toolButtonStart.click()
        log.info("Post tool button")

        # There has to be an easier way to find the cancel button
        #bb = self.form.file_dialog
        #parts = bb.findChildren(QtGui.QDialogButtonBox)
        #cancel_button = parts[0].button(QtGui.QDialogButtonBox.Cancel)
       
        # Any of these options trigger a modal, blocking popup of the
        # filedialog
        #self.form.ui.actionSave.trigger()
        #QtTest.QTest.mouseClick(self.form.ui.actionSave)
        #QtTest.QTest.keyEvent(QtTest.QTest.Click, self.form, 
        #                       QtCore.Qt.Key_S, QtCore.Qt.ControlModifier)
       
        # instead, break out the action into save dialog, which should
        # be testable elsewhere. Or make a custom save widget that wraps
        # the file dialog so you can add an auto-close timer or a
        # default value. For now just ignore that portion

        QtTest.QTest.qWait(1000)
        self.form.save_file("test_file.csv")

        # Now look at the file, make sure it is the correct length
        self.assertTrue(self.file_lines(), 2)

        # Make sure header is at the top of the file
        file_str = self.get_header()
        head_str = "Offset,Gain,Line Time,Integration Time,Data\n"
        self.assertEqual(file_str, head_str)

        # Make sure first line matches set values of gain/offset, ltm,
        # etc.
        first_line = self.get_line(1)
        first_str = "0,0,100,98"

        self.assertEqual(first_line[0:10], first_str)
        
    def get_line(self, line_num, name="test_file.csv"):
        """ Helper function to get specific line of file.
        """
        my_file = open(name)
        count = 0
        for line in my_file.readlines():
            if count == line_num:
                return line
            count += 1
 
    def get_header(self, name="test_file.csv"):
        """ Helper function to return header of csv file.
        """
        my_file = open(name)
        return my_file.readline()
   
    def file_lines(self, name="test_file.csv"):
        """ helper function to return number of liens in the file
        """
        my_file = open(name)
        count = 0
        for line in my_file.readlines():
            count += 1
        return count 

    def test_build_image_from_result(self):
        # Build a small scan group, run it. Make it cover the whole
        # widget area so the cilck below can just be in the middle
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(11)
        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(1)
        self.form.ui.toolButtonStart.click()

        # Store the first data values
        QtTest.QTest.qWait(1000)
        plot = self.form.ui.image_dialog.get_plot()
        # Apparently get_default_item is not supported by the python xy
        # implementation of guiqwt. 
        #start_data = plot.get_default_item().get_data(0,0)
        start_data = plot.get_items()[1].get_data(0,0)

        # Click the first entry in the tree widget, verify that the
        # image data changes

        # Why do I have to specify application level coordinates, get
        # the child, then click the button? If you do mouseclick on the
        # treeview widget directly it does nothing.
        treeview_pos = QtCore.QPoint(140, 500)
        child = self.form.childAt(treeview_pos)
        QtTest.QTest.mouseClick(child, QtCore.Qt.LeftButton)

        QtTest.QTest.qWait(1000)
        # Apparently get_default_item is not supported by the python xy
        # implementation of guiqwt. 
        #start_data = plot.get_default_item().get_data(0,0)
        end_data = plot.get_items()[1].get_data(0,0)
        self.assertNotEqual(start_data, end_data)

    def test_progress_bar(self):
        # On startup, progress bar is disabled
        pg = self.form.ui.progressBar
        self.assertFalse(pg.isVisible())

        # Set a small scan parameter, 
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(1)
        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(1)

        
        # Trigger the scan, verify that the progress bar updates
        self.form.ui.toolButtonStart.click()
        QtTest.QTest.qWait(1000)
        self.assertTrue(pg.isVisible())
        self.assertEqual(pg.value(), 100)

    def test_stop_button(self):
        # Setup a long scan
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(1)
        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(255)

        first_pg_val = self.form.ui.progressBar.value()
        # Trigger the scan, verify the progress bar updates
        self.form.ui.toolButtonStart.click()
        QtTest.QTest.qWait(100)

        # Click stop, verify that the progress bar has stopped
        self.form.ui.toolButtonStop.click()
        second_pg_val = self.form.ui.progressBar.value()
        self.assertNotEqual(first_pg_val, second_pg_val)

        # Wait, check the progress bar again to make sure it actually
        # stopped
        QtTest.QTest.qWait(1000)
        third_pg_val = self.form.ui.progressBar.value()
        self.assertEqual(second_pg_val, third_pg_val)
        log.info("Values: %s, %s " % (first_pg_val, second_pg_val))

    def test_save_results_use_progress_bar(self):
        # setup a long scan for saving data
        self.form.ui.spinBoxOffsetStart.setValue(0)
        self.form.ui.spinBoxOffsetEnd.setValue(2)
        self.form.ui.spinBoxGainStart.setValue(0)
        self.form.ui.spinBoxGainEnd.setValue(55)

        # Trigger the scan
        self.form.ui.toolButtonStart.click()
        QtTest.QTest.qWait(1000)
        
        # trigger the save action with specified file
        self.form.save_file("test_file.csv")
        QtTest.QTest.qWait(100)

        # Get the progress bar
        first_val = self.form.ui.progressBar.value()

        # wait, get progress bar again, verify they are different
        QtTest.QTest.qWait(800)
        second_val = self.form.ui.progressBar.value()
        self.assertNotEqual(first_val, second_val)

    def test_load_results_use_progress_bar(self):
        file_name = "barbecue/test/100samples.csv" 

        # Choose the file, make sure the summary text is updated
        self.form.load_file(file_name)
        QtTest.QTest.qWait(100)
    
        # get the read from the progress bar near the start
        start_progress = self.form.ui.progressBar.value()
        
        # as the file loads, read the progress bar , make sure they are
        # different. It's a 7 meg file, wait for the load
        QtTest.QTest.qWait(1000)
        mid_progress = self.form.ui.progressBar.value()

        self.assertNotEqual(start_progress, mid_progress)

        # Make sure the total entries is two
        QtTest.QTest.qWait(1000)
        dm = self.form.datamod
        self.assertEqual(dm.rowCount(), 2)
            
        # verify the offset value is read from the file to the datamodel
        # correctly
        new_offset = self.form.datamod.item(0, 0).text()
        self.assertEqual(new_offset, "0")

        # Verify that the image data changes when the entry is clicked

        # Why do I have to specify application level coordinates, get
        # the child, then click the button? If you do mouseclick on the
        # treeview widget directly it does nothing.
        plot = self.form.ui.image_dialog.get_plot()

        # Apparently get_default_item is not supported by the python xy
        # implementation of guiqwt. 
        #start_data = plot.get_default_item().get_data(0,10)
        first_item = plot.get_items()[1]
        start_data = first_item.get_data(0, 10)

        treeview_pos = QtCore.QPoint(140, 500)
        child = self.form.childAt(treeview_pos)
        relative_move = QtCore.QPoint(20, 10)
        QtTest.QTest.mouseClick(child, QtCore.Qt.LeftButton,
                                pos=relative_move
                               )

        first_item = plot.get_items()[1]
        end_data = first_item.get_data(0, 10)
        self.assertNotEqual(start_data, end_data)
        
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
