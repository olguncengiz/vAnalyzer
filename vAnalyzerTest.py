import unittest
import os
import vAnalyzer


class TestvAnalyzer(unittest.TestCase):
    def testBlankArguments(self):
        vAnalyzer.checkArguments([])


    def testSingleArgument(self):
        vAnalyzer.checkArguments(["vAnalyzer"])


    def testBootVm(self):
    	vAnalyzer.checkArguments(["vAnalyzer", "boot"])


"""
    def testCreateHeatTemplate(self):
        vAnalyzer.createHeatTemplate("Dummy_VM", "cirros-0.3.3", "m1.tiny", "net04")
        self.assertTrue(os.path.exists(vAnalyzer.HEAT_YAML_FILE))
            

    def testDeleteHeatTemplate(self):
        self.assertTrue(os.path.exists(vAnalyzer.HEAT_YAML_FILE))
        vAnalyzer.deleteHeatTemplate()
        self.assertFalse(os.path.exists(vAnalyzer.HEAT_YAML_FILE))
"""

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestvAnalyzer)
	unittest.TextTestRunner(verbosity=2).run(suite)
	