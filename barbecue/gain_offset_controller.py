""" Gain/Offset walkthrough with live visualization.
"""

import csv
import numpy
import logging
import StringIO

from PyQt4 import QtGui, QtCore

from guiqwt import plot
from guiqwt import builder

from barbecue import model

log = logging.getLogger(__name__)

class GainOffset(QtGui.QMainWindow):
    """ The main interface for the GainOffset application. Can be created
    from unittest or a main() for full test coverage.
    """
    def __init__(self):
        super(GainOffset, self).__init__()
        #log.debug("creation")

        from barbecue.ui.GainOffset_layout import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setGeometry(450, 350, 1080, 600)

        self.replace_widgets()

        self.set_app_defaults()
        self.setup_signals()

        # It's necessary to create the dialog objects ahead of time so
        # the test scripts can click their buttons
        self.file_dialog = QtGui.QFileDialog()

        self.show()

    def replace_widgets(self):
        """ From: http://stackoverflow.com/questions/4625102/\
            how-to-replace-a-widget-with-another-using-qt
        Replace the current placeholders from qt designer with the
        custom widgets.
        """

        # Create the new widget
        self.ui.image_dialog = NoButtonImageDialog()

        # Remove the placeholder widget from the layout
        liph = self.ui.labelImagePlaceholder
        vli = self.ui.verticalLayout
        vli.removeWidget(liph)
        liph.close()

        # Add the new widget to the layout
        vli.insertWidget(0, self.ui.image_dialog)
        vli.update()

    def set_app_defaults(self):
        """ Setup preliminary values of all widgets.
        """
        # Hide the progress bar for better startup looks
        self.ui.progressBar.setVisible(False)

        self.ui.spinBoxGainStart.setMinimum(0)
        self.ui.spinBoxGainStart.setMaximum(254)
        self.ui.spinBoxGainStart.setValue(0)

        self.ui.spinBoxGainEnd.setMinimum(1)
        self.ui.spinBoxGainEnd.setMaximum(255)
        self.ui.spinBoxGainEnd.setValue(255)

        self.ui.spinBoxOffsetStart.setMinimum(0)
        self.ui.spinBoxOffsetStart.setMaximum(254)
        self.ui.spinBoxOffsetStart.setValue(0)

        self.ui.spinBoxOffsetEnd.setMinimum(1)
        self.ui.spinBoxOffsetEnd.setMaximum(255)
        self.ui.spinBoxOffsetEnd.setValue(255)

        self.ui.spinBoxLineTime.setMinimum(25)
        self.ui.spinBoxLineTime.setMaximum(1000)
        self.ui.spinBoxLineTime.setValue(100)

        self.ui.spinBoxIntegrationTime.setMinimum(2)
        self.ui.spinBoxIntegrationTime.setMaximum(98)
        self.ui.spinBoxIntegrationTime.setValue(98)

        # Create a datamodel, add it to the widget
        self.datamod = QtGui.QStandardItemModel()

        self.model_header = QtCore.QStringList()
        self.model_header.append('Offset')
        self.model_header.append('Gain')
        self.datamod.setHorizontalHeaderLabels(self.model_header)
        self.ui.treeView.setModel(self.datamod)

        # Trigger an update of the text
        self.update_summary()

        # Create the timer so the test controller can have access to the
        # various parts of the gain/offset loop control 
        self.processTimer = QtCore.QTimer()
        self.processTimer.setSingleShot(True)
        self.processTimer.timeout.connect(self.loop_process)

        # Progress indicators for data saving
        self.saveTimer = QtCore.QTimer()
        self.saveTimer.setSingleShot(True)
        self.saveTimer.timeout.connect(self.loop_save)

        self.loadTimer = QtCore.QTimer()
        self.loadTimer.setSingleShot(True)
        self.loadTimer.timeout.connect(self.loop_load)

        # When the save file action is activated, it needs to wait for
        # the filename selection dialog to close first. Signal is
        # connected with lambda function to filename below
        self.save_wait_timer = QtCore.QTimer()
        self.save_wait_timer.setSingleShot(True)

        self.load_wait_timer = QtCore.QTimer()
        self.load_wait_timer.setSingleShot(True)


    def setup_signals(self):
        """ Configure widget signals.
        """
        spgs = self.ui.spinBoxGainStart
        spgs.valueChanged.connect(self.move_gain_range)
        spgs.valueChanged.connect(self.update_summary)

        spos = self.ui.spinBoxOffsetStart
        spos.valueChanged.connect(self.move_offset_range)
        spos.valueChanged.connect(self.update_summary)

        splt = self.ui.spinBoxLineTime
        splt.valueChanged.connect(self.move_linetime)

        #self.ui.toolButtonStart.clicked.connect(self.start_process)
        self.ui.toolButtonStart.clicked.connect(self.setup_process)
        self.ui.toolButtonStop.clicked.connect(self.stop_process)

        # If start of end ranges change, update the summary text
        spge = self.ui.spinBoxGainEnd
        spge.valueChanged.connect(self.update_summary)

        spoe = self.ui.spinBoxOffsetEnd
        spoe.valueChanged.connect(self.update_summary)
      
        # Open/Save results
        self.ui.actionOpen.triggered.connect(self.open_process)
        self.ui.actionSave.triggered.connect(self.save_process)

        # Tree list widget updates image on click
        self.ui.treeView.clicked.connect(self.update_image)

    def update_image(self):
        """ Based on the tree view selected datamodel item, build an
        image in the dialog.
        """
        #log.info("Update image")
        # Get the currently selected item
        idx = self.ui.treeView.selectedIndexes()
        log.info("Clicked: %s" % idx)

        item = self.datamod.item(idx[0].row(), idx[0].column())
        #log.info("item: %s" % item.results)

        self.results_to_image(item)

    def results_to_image(self, item):
        """ given an item from the datamodel that has results of gain
        0-255, construct a numpy array and assign that to the image.
        """
        src_data = []
        for gain_row in item.results:
            src_data.append(gain_row.data)

        #log.info("How many rows: %s" % len(src_data))
        img_data = range(len(src_data))

        position = 0
        while position < len(img_data):
            img_data[position] = src_data[position]
            position += 1

         
        new_data = numpy.array(img_data).astype(float)
        
        plot = self.ui.image_dialog.get_plot()
        plot.get_default_item().set_data(new_data)

        plot.replot()
 
        #self.image_data.append(data)
        #if len(self.image_data) > self.image_height:
            #self.image_data = self.image_data[1:]
#
        #img_data = range(len(self.image_data))
#
        #position = 0
        #while position < len(img_data):
            #img_data[position] = self.image_data[position]
            #position += 1
#
        #new_data = numpy.array(img_data).astype(float)
#
        #mid = self.main_image_dialog
        #mid.image.set_data(new_data)

        # If you do autoscale here, it tends to jump around in appearing
        # to stretch to the window and be in 'normal' size
        #mid.get_plot().replot()


    def open_process(self):
        """ Get a filename to load.
        """
        file_name = self.file_dialog.getOpenFileName()
        
        # Trigger the timer after the dialog has had a chance to close
        self.load_wait_timer.timeout.connect(lambda: self.load_file(file_name))
        self.load_wait_timer.start(500)

    def load_file(self, file_name):
        """ Set the progress bar indicators and convert a csv file to
        datamodel.
        """
        total = self.get_line_total(file_name)

        msg = "Loading %s combinations from %s" % (total, file_name)
        self.ui.labelProcessing.setText(msg)

        self.ui.progressBar.total = total
        self.ui.progressBar.setValue(0)
        self.op_count = 0

        csv_header = ["Offset", "Gain", "Line Time", "Integration Time"]
        self.csv_file = csv.DictReader(open(file_name,'rb'),
                                       csv_header, 'Data')

        # Read past the header:
        header = self.csv_file.next()

        self.load_position = 0
        self.last_model = None
        self.loop_load()

    def loop_load(self):
        """ Iterate through the file data to be loaded inside a timer,
        update the interface progress.
        """

        line = None
        line_fail = 0
        try:
            line = self.csv_file.next()
            #log.info("File header: %s" % line['Offset'])
        except:
            line_fail = 1
            log.warn("Problem reading file")

        #log.info("read line: %s" % line)   
        self.load_position += 1 
        self.update_progress_bar()

        if line_fail:
            log.info("Load complete, add final")
            last_entry = self.last_model.results[0]
            offs_it = QtGui.QStandardItem(str(last_entry.offset))
            offs_it.results = self.last_model.results
            gain_it = QtGui.QStandardItem("Gain 0-255")
            self.datamod.appendRow([offs_it, gain_it])
            return

       
        new_data = [] 
        for item in line["Data"][0:2047]:
            new_data.append(float(item))

        new_result = model.Result(line["Gain"], line["Offset"], 
                                  line["Line Time"], 
                                  line["Integration Time"],
                                  new_data
                                 )

        # If it's the very first pass, just assign it
        if self.last_model == None:
            self.last_model = model.Model()


        # compare current line offset to last offset, if different, add last
        # item, start a new item
        new_offset = new_result.offset
        if len(self.last_model.results) == 0:
            old_offset = new_offset
        else:
            old_offset = self.last_model.results[0].offset

        if new_offset != old_offset:
            log.info("Offset change, add to model")
            offs_it = QtGui.QStandardItem(str(old_offset))
            offs_it.results = self.last_model.results
            gain_it = QtGui.QStandardItem("Gain 0-255")
            self.datamod.appendRow([offs_it, gain_it])

            self.last_model = model.Model()

        self.last_model.results.append(new_result)
 
        if self.load_position < self.ui.progressBar.total:
            self.loadTimer.start(0)

        
    def get_line_total(self, file_name):
        """ Make a pass through the file, read the total number of
        lines.
        """
        lfile = open(file_name)
        lcount = 0
        for line in lfile.readlines():
            lcount += 1
        lfile.close()
        return lcount

    def save_process(self):
        """ Select a filename to save the current results.
        """
        file_name = self.file_dialog.getSaveFileName()
        
        # Trigger the timer after the dialog has had a chance to close
        self.save_wait_timer.timeout.connect(lambda: self.save_file(file_name))
        self.save_wait_timer.start(300)

    def save_file(self, file_name):
        """ Write the current contents of the datamodel displayed in the
        tree widget to disk.
        """ 
        total = self.datamod.rowCount() * 255

        msg = "Saving %s combinations to %s" % (total, file_name)
        self.ui.labelProcessing.setText(msg)

        self.ui.progressBar.total = total
        self.ui.progressBar.setValue(0)
        self.op_count = 0
        self.csv_file = open(file_name, "wb")

        self.write_header(self.csv_file)

        self.save_position = 0
        self.loop_save()

    def loop_save(self):
        """ Iterate through the data to be saved in a timer to enable
        load inhibits and progress bar updates.
        """
            
        item = self.datamod.item(self.save_position, 0)
        log.info("Write item: %s" % item)

        self.write_results(self.csv_file, item)            
        self.save_position += 1

        if self.save_position >= self.datamod.rowCount():
            self.csv_file.close()
        else:
            self.saveTimer.start(0)

    def write_results(self, csv_file, item):
        """ Print the contents of the datamodel item to disk.
        """
        for result in item.results:
            csv_file.write("%s," % result.offset)
            csv_file.write("%s," % result.gain)
            csv_file.write("%s," % result.linetime)
            csv_file.write("%s," % result.integration)
            for pixel in result.data:
                csv_file.write("%s," % pixel)
            csv_file.write("\n")
            self.update_progress_bar()

    def write_header(self, csv_file):
        """ write the csv file format header to the passed in file.
        """
        head_str = "Offset,Gain,Line Time,Integration Time,Data\n"
        csv_file.write(head_str)

    def update_summary(self):
        """ Create a summary text showing how many iterations will be
        processed.
        """
        #log.info("update summary")
        offset_range = self.ui.spinBoxOffsetEnd.value() - \
                       self.ui.spinBoxOffsetStart.value() + 1

        gain_range = self.ui.spinBoxGainEnd.value() - \
                     self.ui.spinBoxGainStart.value() + 1

        total = offset_range * gain_range
        msg = "System will process %s combinations." % total
        self.ui.labelProcessing.setText(msg)

        # Store the current total combinations for use by the progress
        # bar update function
        self.ui.progressBar.total = total
        self.ui.progressBar.setValue(0)

    def setup_process(self):
        """ Configure the test iteration based on set parameters,
        trigger the loop timer to start the process.
        """
        log.info("Start setup")
        self.stop_scan = False
        self.ui.progressBar.setVisible(True)

        self.orig_gain_start = self.ui.spinBoxGainStart.value()
        self.orig_gain_end = self.ui.spinBoxGainEnd.value()

        self.orig_offset_start = self.ui.spinBoxOffsetStart.value()
        self.orig_offset_end = self.ui.spinBoxOffsetEnd.value()
        self.offset = self.orig_offset_start

        self.linetime = self.ui.spinBoxLineTime.value()
        self.integration = self.ui.spinBoxIntegrationTime.value()

        self.op_count = 0

        self.processTimer.start(0)

    def loop_process(self):
        """ Once the timer has been activated, loop through the test
        iteration structure until all offset/gain options have been
        processed.
        """
 
        #log.info("Process offset: %s" % self.offset)
       
        gain = self.orig_gain_start
        gain_group = []
        one_model = model.Model()
        one_model.assign("single")
        while gain <= self.orig_gain_end:
            #log.debug("Gain: %s" % gain)
            result = one_model.scan(gain, self.offset, self.linetime,
                                     self.integration)

            self.update_progress_bar()
            gain += 1

        offs_it = QtGui.QStandardItem(str(self.offset))
        offs_it.results = one_model.results
        #log.info("Store results: %s" % len(offs_it.results))
        gain_it = QtGui.QStandardItem("Gain 0-255")

        self.datamod.appendRow([offs_it, gain_it])

        self.offset += 1

        if self.offset <= self.orig_offset_end:
            if not self.processTimer.isActive():
                #log.info("Start timer: %s" % self.offset)
                self.processTimer.start(0)


    def stop_process(self):
        """ set the global variable to inhibit a running process, reset
        gui items.
        """      
        self.stop_scan = True
        self.processTimer.stop()
        self.saveTimer.stop()
 
    def update_progress_bar(self):
        """ Given a op_count value, assign the progress bar to the
        percentage of total operations. 
        """
        self.op_count += 1
        self.op_count = self.op_count * 1.0
        tot = self.ui.progressBar.total * 1.0
        perc = (self.op_count / tot) * 100.0
        self.ui.progressBar.setValue(perc)
        #log.info("progress: %s " % self.ui.progressBar.value())
        

    def move_linetime(self, event):
        """ Change the integration time range to make sure the user
        cannot set it more than 2 - line time.
        """
        lt_value = self.ui.spinBoxLineTime.value()
        self.ui.spinBoxIntegrationTime.setMaximum(lt_value - 2) 

    def move_gain_range(self, event):
        """ Make sure the end value is always at least 1 more than the
        start value.
        """
        gs_value = self.ui.spinBoxGainStart.value()
        self.ui.spinBoxGainEnd.setMinimum(gs_value + 1)

    def move_offset_range(self, event):
        """ Make sure the end value is always at least 1 more than the
        start value.
        """
        os_value = self.ui.spinBoxOffsetStart.value()
        self.ui.spinBoxOffsetEnd.setMinimum(os_value + 1)


class NoButtonImageDialog(plot.ImageDialog):
    """ An guiqwt imagedialog with the ok/cancel buttons hidden.
    """

    def __init__(self):
        options=dict(show_xsection=False)
        super(NoButtonImageDialog, self).__init__(toolbar=True,
                                                  edit=True, 
                                                  options=options)

        self.create_image()

        # Don't show the right side colormap axis
        local_plot = self.get_plot()
        local_plot.enableAxis(local_plot.colormap_axis, False)

    def create_image(self):
        """ Create a 2D test pattern image, apply it to the view area.
        """
        base_data = range(256)

        position = 0
        while position < len(base_data):
            base_data[position] = numpy.linspace(0, 100, 2048)
            position += 1

        new_data = numpy.array(base_data).astype(float)

        bmi = builder.make.image
        self.image = bmi(new_data, colormap="gist_earth")
        local_plot = self.get_plot()
        local_plot.add_item(self.image)
        local_plot.do_autoscale()

    def install_button_layout(self):
        """ Do not show the ok, cancel buttons, yet retain the right
        click editing capabilities.
        """
        pass
