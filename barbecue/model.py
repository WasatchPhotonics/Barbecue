""" Datamodel classes for the barbecue.
"""

import logging

from wasatchcameralink import simulation

log = logging.getLogger(__name__)

class ScanGroup(object):
    """ Given a range of gains, create a data model for each, provide an
    interface for saving the data to disk in csv.
    """
    def __init__(self):
        super(ScanGroup, self).__init__()
        log.info("scangroup created")
        self.model = Model()
 
    def assign(self, device_type):
        """ pass-through the device assignment type.
        """
        return self.model.assign(device_type)
       
    def offset_range(self, start, end):
        """ initialize the range to be scanned.
        """
        self.offset_start = start
        self.offset_end = end


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

        if device_type != "simulation":
            raise(ValueError, "specify a valid device type")
        
        self.device = device_type
        return True

    def scan(self, gain, offset):
        if self.device == None:
            raise(ValueError, "Must assign device first")

        if gain == None or offset == None:
            raise(ValueError, "must specify gain, offset")

        self.device = simulation.SimulatedSpectraDevice()
        result = self.device.setup_pipe()
        log.info("Setup result is: %s" % result)

        result, data = self.device.grab_pipe()
        store_result = Result(gain, offset, data)
        self.results.append(store_result)
        return True
            
class Result(object):
    """ holds stored data and device settings from a given scan.
    """
    def __init__(self, gain=-1, offset=-1, data=[]):
        super(Result, self).__init__()
        self.gain = gain
        self.offset = offset
        self.data = data
