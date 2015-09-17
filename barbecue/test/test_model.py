""" tests for datamodel of barbecue
"""

import unittest

from barbecue import model

class Test(unittest.TestCase):

    def setUp(self):
        self.model = model.Model()
        pass

    def test_creation(self):
        # new model creates empty results list and empty device
        self.assertEqual(len(self.model.results), 0)
        self.assertIsNone(self.model.device)

    def test_assignment(self):
        # Attempt to assign an invalid device, catch exception
        self.assertRaises(ValueError, self.model.assign, None)
        self.assertRaises(ValueError, self.model.assign, "KnownInvalid")
        
        # Pass with the simulation assignment
        self.assertTrue(self.model.assign("simulation"))

    def test_result(self):
        # result object has expected default values
        res = model.Result()
        self.assertEqual(res.gain, -1)
        self.assertEqual(res.offset, -1)
        self.assertEqual(len(res.data), 0)
        

    def test_scan_result(self):
        scan = self.model.scan
        # Attempt to scan before device assignment, fail
        self.assertRaises(ValueError, scan, gain=None, offset=None)

        self.model.assign("simulation")

        # Attempt to scan with no gain, offset, fail
        self.assertRaises(ValueError, scan, gain=None, offset=None)

        # Run a succesful scan, make sure the results list is populated
        result = scan(gain=1, offset=10)
        self.assertEqual(len(self.model.results), 1)

        # Make sure the results list data items match expected values
        last_result = self.model.results[-1]
        print "Result is: [%s]" % last_result
        self.assertEqual(last_result.gain, 1)
        self.assertEqual(last_result.offset, 10)
        self.assertEqual(len(last_result.data), 2048)

    def test_exam_creation(self):
        # Every time a new scan is created, the temporary working file
        # is overwritten with the contents of the scan. ScanGroup class
        # encapsulates this functionality

        sg = model.ScanGroup()
        self.assertTrue(sg.assign("simulation"))
        self.assertTrue(sg.offset_range(0, 1))

        self.assertTrue(sg.process())

        # Now look at the file, make sure it is the correct length

        # Make sure each line has the offset, gain, ltm, etc. header
        
    
if __name__ == "__main__":
    unittest.main()
    
