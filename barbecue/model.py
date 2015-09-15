""" Datamodel classes for the barbecue.
"""

import logging

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
