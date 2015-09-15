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

if __name__ == "__main__":
    unittest.main()
    
