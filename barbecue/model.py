""" Datamodel classes for the barbecue.
"""

import logging

from wasatchcameralink import DALSA
from wasatchcameralink import simulation

log = logging.getLogger(__name__)

class Model(object):
    """ Encapsulates the acquisition of data from a spectrometer, along
    with storage and results data structure.
    """
    def __init__(self):
        super(Model, self).__init__()
        #log.info("created")
        self.results = []
        self.device = None

    def assign(self, device_type):
        """ Designate and setup the specified device type
        """
        if device_type == None:
            raise(ValueError, "specify a device type")

        if device_type != "simulation" and \
           device_type != "cobra" and \
           device_type != "single":
            raise(ValueError, "specify a valid device type")
        
        self.device = device_type

        if self.device == "single":
            self._dev = simulation.SimulatedCobraSLED()

        elif self.device == "cobra":
            self._dev = DALSA.Cobra()

        # Yes, this order is correct. You have to setup, then grap from
        # the pipe, then open the port and then start the scan. You
        # might think this would cause a timeout in the sap net grab.
        # Apparently it does not. However, if you setup the pipe and/or
        # open the serial port first, everything will look fine. Until
        # you go to write to the serial port after a grab operation.
        # Then the write command will succeed, but reading back the
        # response will always result in '', and no changes appear to be
        # written to the device.
        result = self._dev.setup_pipe()
        result, data = self._dev.grab_pipe()
        forc_res = self._dev.open_port()
        forc_res = self._dev.start_scan()
        
        return True

    def scan(self, gain, offset, linetime, integration):
        """ Connect to a device, apply the settings, collect one line of
        data, store the results and exit.
        """
        if self.device == None:
            raise(ValueError, "Must assign device first")

        if gain == None or offset == None:
            raise(ValueError, "must specify gain, offset")

        result = self._dev.set_gain(gain)
        result = self._dev.set_offset(offset)
        result, data = self._dev.grab_pipe()

        store_result = Result(gain, offset, linetime, integration, data)
        self.results.append(store_result)
        return True

    def close_model(self):
        """ Helper function to close the pipe.
        """
        return self._dev.close_pipe()
            
class Result(object):
    """ holds stored data and device settings from a given scan.
    """
    def __init__(self, gain=-1, offset=-1, linetime=-1, integration=-1,
                 data=[]):
        super(Result, self).__init__()
        self.gain = gain
        self.offset = offset
        self.linetime = linetime
        self.integration = integration
        self.data = data
