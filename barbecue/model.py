""" Datamodel classes for the barbecue.
"""

import logging

from wasatchcameralink import simulation

log = logging.getLogger(__name__)

class Model(object):
    """ Encapsulates the acquisition of data from a spectrometer, along
    with storage and results data structure.
    """
    def __init__(self):
        super(Model, self).__init__()
        log.info("Model created")
        self.results = []
        self.device = None

    def assign(self, device_type):
        """ Designate and setup the specified device type
        """
        if device_type == None:
            raise(ValueError, "specify a device type")

        if device_type != "simulation" and \
           device_type != "single":
            raise(ValueError, "specify a valid device type")
        
        self.device = device_type
        return True

    def scan(self, gain, offset, linetime, integration):
        """ Connect to a device, apply the settings, collect one line of
        data, store the results and exit.
        """
        if self.device == None:
            raise(ValueError, "Must assign device first")

        if gain == None or offset == None:
            raise(ValueError, "must specify gain, offset")

        if self.device == "simulation":
            dev = simulation.SimulatedSpectraDevice()

        elif self.device == "single":
            dev = simulation.SimulatedCobraSLED()

        result = dev.setup_pipe()
        log.info("Setup result is: %s" % result)

        result = dev.set_gain(gain)
        result = dev.set_offset(offset)
        result, data = dev.grab_pipe()

        store_result = Result(gain, offset, linetime, integration, data)
        self.results.append(store_result)
        result = dev.close_pipe()
        return True
            
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
