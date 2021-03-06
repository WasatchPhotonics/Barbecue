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
        self.assertTrue(self.model.assign("single"))
        self.assertTrue(self.model.close_model())

    def test_result(self):
        # result object has expected default values
        res = model.Result()
        self.assertEqual(res.gain, -1)
        self.assertEqual(res.offset, -1)
        self.assertEqual(res.linetime, -1)
        self.assertEqual(res.integration, -1)
        self.assertEqual(len(res.data), 0)
        

    def test_scan_result(self):
        scan = self.model.scan
        # Attempt to scan before device assignment, fail
        self.assertRaises(ValueError, scan, gain=None, offset=None,
                          linetime=None, integration=None)

        self.model.assign("single")

        # Attempt to scan with no gain, offset, fail
        self.assertRaises(ValueError, scan, gain=None, offset=None,
                          linetime=None, integration=None)

        # Run a succesful scan, make sure the results list is populated
        result = scan(gain=1, offset=10, linetime=100, integration=98)
        self.assertEqual(len(self.model.results), 1)

        # Make sure the results list data items match expected values
        last_result = self.model.results[-1]
        self.assertEqual(last_result.gain, 1)
        self.assertEqual(last_result.offset, 10)
        self.assertEqual(last_result.linetime, 100)
        self.assertEqual(last_result.integration, 98)
        self.assertEqual(len(last_result.data), 2048)

    
if __name__ == "__main__":
    unittest.main()
    
