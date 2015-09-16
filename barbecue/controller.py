""" Gain/Offset walkthrough with live visualization.
"""
import logging

from PyQt4 import QtGui, QtCore

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

        #self.replace_widgets()

        # Align the image with the curve above it
        #self.main_image_dialog.setContentsMargins(17, 0, 0, 0)
#
#        self.add_manager_and_tools()
#    
#        # Timer to auto-close the application
#        self.close_timer = QtCore.QTimer()
#        self.close_timer.timeout.connect(self.closeEvent)
#
#        self.set_app_defaults()

        self.show()

