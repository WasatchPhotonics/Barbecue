""" Gain/Offset walkthrough with live visualization.
"""

import numpy
import logging

from PyQt4 import QtGui, QtCore

from guiqwt import plot
from guiqwt import builder

log = logging.getLogger(__name__)

class GainOffset(QtGui.QMainWindow):
    """ The main interface for the GainOffset application. Can be created
    from unittest or a main() for full test coverage.
    """
    def __init__(self):
        super(GainOffset, self).__init__()
        log.debug("creation")

        from barbecue.ui.GainOffset_layout import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setGeometry(450, 350, 1080, 600)

        # Make sure the system wide style sheet is applied before the
        # curve and image widgets style sheets overwrite
        #self.qss_string = utils.load_style_sheet("qdarkstyle.css")
        #self.setStyleSheet(self.qss_string)

        self.replace_widgets()

        # Align the image with the curve above it
        #self.main_image_dialog.setContentsMargins(17, 0, 0, 0)
#
#        self.add_manager_and_tools()
#    
#        # Timer to auto-close the application
#        self.close_timer = QtCore.QTimer()
#        self.close_timer.timeout.connect(self.closeEvent)
#
        self.set_app_defaults()
        self.setup_signals()
        self.show()

    def replace_widgets(self):
        """ From: http://stackoverflow.com/questions/4625102/\
            how-to-replace-a-widget-with-another-using-qt
        Replace the current placeholders from qt designer with the
        custom widgets.
        """

        # Create the new widget
        #options=dict(show_xsection=True, show_ysection=True,
                     #show_contrast=True)
        #self.ui.image_dialog = plot.ImageDialog(toolbar=True, edit=True,
                                                #options=options)
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

    def setup_signals(self):
        """ Configure widget signals.
        """
        spgs = self.ui.spinBoxGainStart
        spgs.valueChanged.connect(self.move_gain_range)

        spos = self.ui.spinBoxOffsetStart
        spos.valueChanged.connect(self.move_offset_range)

        splt = self.ui.spinBoxLineTime
        splt.valueChanged.connect(self.move_linetime)

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
        options=dict(show_xsection=True)
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
