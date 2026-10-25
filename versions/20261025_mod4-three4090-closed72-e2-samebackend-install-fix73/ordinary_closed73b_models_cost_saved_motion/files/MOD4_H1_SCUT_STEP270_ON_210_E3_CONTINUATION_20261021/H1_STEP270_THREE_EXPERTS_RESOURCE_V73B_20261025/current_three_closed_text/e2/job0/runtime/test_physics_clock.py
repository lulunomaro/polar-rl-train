import unittest
from physics_clock import validate_clock
class ClockContract(unittest.TestCase):
 def test_supported(self):
  for dt,dec,bins in [(.0005,20,10),(.001,10,5),(.0025,4,2),(.005,2,1)]:
   r=validate_clock(dt);self.assertEqual(r['decimation'],dec);self.assertEqual(r['contact_bin_samples'],bins)
 def test_unsupported(self):
  for dt in [0,-.001,.002,float('inf'),float('nan'),None]:
   with self.assertRaises(ValueError):validate_clock(dt)
 def test_time_window_not_misrepresented(self):
  for control,bin in [(.02,.005),(.01,.01),(.01,.004)]:
   with self.assertRaises(ValueError):validate_clock(.001,control,bin)
if __name__=='__main__':unittest.main()
