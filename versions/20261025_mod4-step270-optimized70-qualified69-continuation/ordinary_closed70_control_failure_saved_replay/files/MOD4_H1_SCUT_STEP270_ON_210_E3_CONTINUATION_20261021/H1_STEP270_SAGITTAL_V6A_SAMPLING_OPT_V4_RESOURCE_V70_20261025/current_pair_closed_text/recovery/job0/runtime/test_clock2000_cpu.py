import unittest,math
from physics_clock2000 import validate_clock,fragments

class CrossBinContract(unittest.TestCase):
    def test_control_clock(self):
        c=validate_clock(.002);self.assertEqual(c['decimation'],5);self.assertIsNone(c['contact_bin_samples']);self.assertTrue(c['cross_bin_required'])
    def test_reject(self):
        for dt in (0,-.002,float('nan'),.003,.004):
            with self.assertRaises(ValueError):validate_clock(dt)
        with self.assertRaises(ValueError):validate_clock(.002,.02)
        with self.assertRaises(ValueError):validate_clock(.002,.01,.004)
    def test_exact_split(self):
        self.assertEqual([fragments(i,2000) for i in range(1,6)], [[(2000,False)],[(2000,False)],[(1000,True),(1000,False)],[(2000,False)],[(2000,True)]])
    def test_conservation_and_boundaries(self):
        for us in (500,1000,2000,2500,5000):
            flushed=0;elapsed=0
            for tick in range(1,10001):
                parts=fragments(tick,us);self.assertEqual(sum(d for d,_ in parts),us)
                for d,flush in parts:
                    self.assertGreater(d,0);elapsed+=d
                    if flush:self.assertEqual(elapsed%5000,0);flushed+=1
            self.assertEqual(flushed,10000*us//5000)
    def test_force_integral_independent_overlap(self):
        # Independently integrate force samples against a fixed time-bin grid.
        values=[3.,-7.,11.,5.,-2.,0.,9.,-1.,17.,2.]
        produced=[];acc=0
        for i,v in enumerate(values,1):
            for d,flush in fragments(i,2000):
                acc+=v*d
                if flush:produced.append(acc/5000);acc=0
        expected=[sum(v*max(0,min((i+1)*2000,(b+1)*5000)-max(i*2000,b*5000)) for i,v in enumerate(values))/5000 for b in range(4)]
        self.assertEqual(produced,expected);self.assertAlmostEqual(sum(produced)*5000,sum(values)*2000)
    def test_constant_force(self):
        acc=0;out=[]
        for i in range(1,101):
            for d,flush in fragments(i,2000):
                acc+=31*d
                if flush:out.append(acc/5000);acc=0
        self.assertEqual(out,[31.]*40)
    def test_aligned_old_mean(self):
        for us in (500,1000,2500,5000):
            count=5000//us;v=list(range(1,count+1));weighted=sum(x*fragments(i,us)[0][0] for i,x in enumerate(v,1))/5000
            self.assertEqual(weighted,sum(v)/count)
    def test_history_three_bins(self):
        history=[0.,0.,0.]
        for value in range(1,8):history=[float(value)]+history[:2]
        self.assertEqual(history,[7.,6.,5.])
    def test_partial_selected_reset(self):
        # A reset clears only selected rows; time phase remains global.
        rows=[[4.,1.,2.],[6.,3.,9.]];rows[0]=[0.,0.,0.]
        self.assertEqual(rows,[[0.,0.,0.],[6.,3.,9.]]);self.assertEqual(fragments(3,2000),[(1000,True),(1000,False)])

if __name__=='__main__':unittest.main(verbosity=2)
