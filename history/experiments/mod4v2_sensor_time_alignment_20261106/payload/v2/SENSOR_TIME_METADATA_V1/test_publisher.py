"""NEW deterministic producer/clock stubs only; not real DR, sensors or physics."""
from pathlib import Path
from types import SimpleNamespace as NS
import io,json,random,unittest
from publisher import SensorTimeMetadataMixin
CALLS=0
ASSERTIONS=0
class Clock:
    def __init__(self,t):self.time=t
    def __getattr__(self,key):raise AssertionError('Forbidden non-clock state read: '+key)
class Poison:
    def __getattribute__(self,key):raise AssertionError('Disabled path touched producer clock: '+key)
def packet(stamp,arrival,token=1,valid=True):
    return NS(time_s=stamp,arrival_s=arrival,validity=valid,payload=(token,token+1,token+2))
class Source:
    def __init__(self,packets):
        self.packets=iter(packets);self.calls=0;self.rng=random.Random(19)
        self.d=Clock(0.);self.dt=.0005;self.imu_window_count=0
        self.total_highrate_IMU_samples=0;self.tick_phys=0;self.previous_torque=None
    def at(self,t,n,total=None):
        self.d=Clock(t);self.imu_window_count=n
        self.total_highrate_IMU_samples=round(t/.0005) if total is None else total
        self.tick_phys=self.total_highrate_IMU_samples
    def sensor_packet(self):
        global CALLS
        CALLS+=1;self.calls+=1;self.rng.random()
        self.previous_torque=object();self.imu_window_count=0
        return next(self.packets)
class Optional(SensorTimeMetadataMixin,Source):pass
def active(packets):
    p=Optional(packets);p.configure_sensor_time_metadata(True);return p
class Tests(unittest.TestCase):
    def test_default_off_is_literal_and_does_not_read_clock(self):
        a,b=packet(0.,0.),packet(.01,.01,2);p=Optional([a,b]);base=Source([a,b]);p.d=Poison()
        for expected in (a,b):
            self.assertIs(p.sensor_packet(),expected);self.assertIs(base.sensor_packet(),expected)
            self.assertEqual(p.rng.getstate(),base.rng.getstate())
        self.assertIsNone(p.last_sensor_time_metadata);self.assertNotIn('_sensor_time_publisher',vars(p))
    def test_enabled_call_once_values_and_rng_unchanged(self):
        packets=[packet(0.,0.),packet(.01,.01,5)];p=active(packets);base=Source(packets)
        for i,expected in enumerate(packets):
            p.at(i*.01,i*20);before=vars(expected).copy()
            self.assertIs(p.sensor_packet(),expected);base.sensor_packet()
            self.assertEqual(vars(expected),before);self.assertEqual(p.rng.getstate(),base.rng.getstate())
        self.assertEqual(p.calls,2)
    def test_boot_imu_unknown_qd_endpoint_and_alpha_unobserved(self):
        p=active([packet(0.,0.)]);p.sensor_packet();m=p.last_sensor_time_metadata;c=m['channels']
        self.assertIsNone(c['gyro_B']['timestamp_s']);self.assertIsNone(c['proper_imu_B']['timestamp_s'])
        self.assertEqual(c['encoder_qd4']['timestamp_s'],0.);self.assertEqual(c['encoder_qd4']['kind'],'endpoint')
        self.assertIsNone(c['motor_tau6']['timestamp_s']);self.assertIsNone(m['alpha_B']);self.assertFalse(m['force_input_ready'])
    def test_actual20_pre_mean_not_epoch_or_midpoint(self):
        p=active([packet(.01,.01)]);p.at(.01,20);p.sensor_packet();m=p.last_sensor_time_metadata
        for k in ('encoder_qd4','wheel_vel2','gyro_B','proper_imu_B'):
            c=m['channels'][k];self.assertAlmostEqual(c['timestamp_s'],.00475,15)
            self.assertEqual(c['sample_count'],20);self.assertAlmostEqual(c['window_start_s'],0.,15)
            self.assertAlmostEqual(c['window_end_s'],.0095,15);self.assertIsNone(c['clock_error_bound_s'])
        self.assertEqual(m['channels']['encoder_q4']['timestamp_s'],.01)
        self.assertAlmostEqual(m['channels']['motor_tau6']['timestamp_s'],.0095,15)
        self.assertIn('NOT_measured_output_torque',m['channels']['motor_tau6']['measurement_role'])
    def test_D3_first_sample_then_old_boot_then_old_mean(self):
        p=active([packet(0.,0.),packet(0.,.01),packet(.01,.02)])
        p.sensor_packet();p.at(.01,20);p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertEqual(m['source_frame_epoch_s'],0.);self.assertIsNone(m['channels']['gyro_B']['timestamp_s'])
        self.assertEqual(m['channels']['encoder_q4']['timestamp_s'],0.)
        p.at(.02,20);p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertEqual(m['source_frame_epoch_s'],.01);self.assertAlmostEqual(m['channels']['gyro_B']['timestamp_s'],.00475,15)
        self.assertAlmostEqual(m['channels']['motor_tau6']['timestamp_s'],.0095,15)
    def test_gap_fixed_D3_stamp_mismatch_not_current_relabel(self):
        p=active([packet(0.,0.),packet(0.,.01),packet(.02,.03),packet(.03,.04)])
        p.sensor_packet();p.at(.01,20);p.sensor_packet();p.at(.03,40);p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertTrue(m['packet_source_epoch_mismatch']);self.assertFalse(m['usable_for_alignment'])
        self.assertEqual(m['known_pipeline_source']['epoch_s'],.01)
        self.assertTrue(all(c['timestamp_s'] is None for c in m['channels'].values()))
        p.at(.04,20);p.sensor_packet();self.assertEqual(p.last_sensor_time_metadata['channels']['gyro_B']['sample_count'],40)
        self.assertAlmostEqual(p.last_sensor_time_metadata['channels']['gyro_B']['timestamp_s'],.01975,15)
    def test_duplicate_publication_does_not_borrow_an_older_matching_epoch(self):
        p=active([packet(0.,0.),packet(0.,.01),packet(0.,.01),packet(.01,.02)])
        p.sensor_packet();p.at(.01,20);p.sensor_packet();p.at(.01,0);p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertTrue(m['duplicate_publication_epoch']);self.assertTrue(m['packet_source_epoch_mismatch'])
        self.assertFalse(m['usable_for_alignment']);p.at(.02,20);p.sensor_packet()
        self.assertIsNone(p.last_sensor_time_metadata['channels']['gyro_B']['timestamp_s'])
    def test_rollback_clears_source_and_old_packet_clock(self):
        p=active([packet(.02,.02),packet(0.,0.),packet(.01,.01)])
        p.at(.02,20);p.sensor_packet();p.at(0.,0);p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertTrue(m['pipeline_history_reset_or_rollback']);self.assertFalse(m['usable_for_alignment'])
        self.assertTrue(all(c['timestamp_s'] is None for c in m['channels'].values()))
        p.at(.01,20);p.sensor_packet();self.assertTrue(p.last_sensor_time_metadata['usable_for_alignment'])
    def test_enable_midstream_old_source_missing_remains_unknown(self):
        p=active([packet(.49,.5)]);p.previous_torque=object();p.at(.5,20);p.sensor_packet()
        self.assertEqual(p.last_sensor_time_metadata['source_selection_reason'],'PREVIOUS_SOURCE_NOT_OBSERVED_BY_THIS_WRAPPER')
        self.assertIsNone(p.last_sensor_time_metadata['channels']['motor_tau6']['timestamp_s'])
    def test_same_object_held_keeps_old_labels_without_new_source_credit(self):
        a=packet(.01,.01);p=active([a,a]);p.at(.01,20);p.sensor_packet();p.at(.02,20);returned=p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertIs(returned,a)
        self.assertTrue(m['returned_packet_object_held']);self.assertFalse(m['new_source_observation'])
        self.assertEqual(m['source_frame_epoch_s'],.01);self.assertAlmostEqual(m['channels']['gyro_B']['timestamp_s'],.00475,15)
        self.assertFalse(m['usable_for_alignment'])
    def test_bad_window_counters_do_not_fabricate_mean(self):
        p=active([packet(.01,.01)]);p.at(.01,20,total=0);p.sensor_packet();m=p.last_sensor_time_metadata
        self.assertIsNone(m['channels']['gyro_B']['timestamp_s']);self.assertFalse(m['usable_for_alignment'])
    def test_invalid_returned_packet_clock_is_not_rewritten(self):
        a=packet(-.01,0.);p=active([a]);self.assertIs(p.sensor_packet(),a)
        self.assertEqual(a.time_s,-.01);self.assertFalse(p.last_sensor_time_metadata['usable_for_alignment'])
    def test_explicit_enable_is_exact_bool(self):
        p=Optional([])
        with self.assertRaises(ValueError):p.configure_sensor_time_metadata(1)
        self.assertEqual(p.calls,0)
    def test_super_exception_remains_original_and_called_once(self):
        error=RuntimeError('producer failed')
        class Broken(Source):
            def sensor_packet(self):
                global CALLS
                CALLS+=1;self.calls+=1;raise error
        class Wrapped(SensorTimeMetadataMixin,Broken):pass
        p=Wrapped([]);p.configure_sensor_time_metadata(True)
        with self.assertRaises(RuntimeError)as e:p.sensor_packet()
        self.assertIs(e.exception,error);self.assertEqual(p.calls,1)
# Count explicit test assertion calls, not unittest's internal tuple comparisons.
def counted_assert(name):
    original=getattr(unittest.TestCase,name)
    def invoke(self,*a,**kw):
        global ASSERTIONS
        ASSERTIONS+=1;return original(self,*a,**kw)
    return invoke
for _name in ('assertIs','assertNotIn','assertEqual','assertIsNone','assertAlmostEqual','assertIn','assertFalse','assertTrue','assertRaises'):
    setattr(Tests,_name,counted_assert(_name))
if __name__=='__main__':
    D=Path(__file__).resolve().parent
    with (D/'STUB_RUN_STARTED.json').open('x',encoding='utf-8')as f:json.dump(dict(kind='NEW_SMALL_STUB_ONLY_NO_PHYSICS',tests_planned=14),f)
    buf=io.StringIO();r=unittest.TextTestRunner(stream=buf,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    result=dict(status='PASS_NEW_CLOCK_PRODUCER_STUBS_ONLY'if r.wasSuccessful()else'FAILED_NEW_STUBS_NO_RETRY',tests=r.testsRun,
        passed=r.wasSuccessful(),failures=len(r.failures),errors=len(r.errors),assertion_calls=ASSERTIONS,
        predetermined_source_calls=CALLS,output=buf.getvalue(),
        new_model_FK_forward_physics_DR_oldQA_Git_agents_hardware_calls=0,old_runtime_or_publisher_modified=False,
        stub_is_not_real_pipeline_or_hardware_clock_validation=True)
    with (D/'STUB_RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in result.items()if k!='output'},ensure_ascii=True))
    if not r.wasSuccessful():print(buf.getvalue());raise SystemExit(1)
