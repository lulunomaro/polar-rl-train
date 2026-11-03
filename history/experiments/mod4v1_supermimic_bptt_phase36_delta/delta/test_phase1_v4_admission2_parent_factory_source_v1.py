"""Parent source-factory tests in isolated synthetic temporary roots only.
No generated dispatcher or collector is executed; no SSH, SDK, Torch, models,
canonical files, native parent or resource calls are made.
"""
from pathlib import Path
import ast,contextlib,copy,hashlib,io,json,runpy,sys,tempfile,time,unittest
R=Path(__file__).resolve().parent
NAMES=('prepare_phase1_v4_admission2_parent_after_release_once.py','dispatch_phase1_e3_capture_device_binding_v4_original_parent_once.py','collect_phase1_capture_device_binding_v4_closed_metadata_once.py')
SOURCES={n:(R/n).read_bytes()for n in NAMES}
OUT='reports/PHASE1_V4_ADMISSION2_PARENT_AND_COLLECTION_SOURCE_V1.json';DISP='dispatch_phase1_e3_capture_v4_admission2_original_parent_once.py';COLL='collect_phase1_capture_v4_admission2_closed_metadata_once.py'
class FactoryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='phase1_a2_source_fixture_');self.root=Path(self.tmp.name).resolve();(self.root/'reports').mkdir()
  for n,b in SOURCES.items():(self.root/n).write_bytes(b)
  self.old=dict(root='/synthetic/tasks/CLOSED_ROOT',parent_exit_scope=dict(epoch=10),closed_result=dict(SHA256='a'*64))
  self.stage=dict(returncode=0,group_root='/synthetic/tasks/NEW_A2_ROOT',receipt=dict(materialized=True,parent_launches=0,metadata_validation=dict(passed=True)))
  self.w=dict(old_root=self.old['root'],old_closed_epoch=10,old_closed_metadata_SHA='a'*64,actual=dict(epoch=20,original_relevant_leases_clear=True,original_frozen_resources_observed_clear=True,canonical_summary=dict(authority_generation='MOD4_SINGLE_WRITER72_20261026',active_segment=None,remaining_training_seconds=100,finite_minimum_remaining_seconds=100),required_project_lock_rows=[dict(path='synthetic_'+str(i),records=[])for i in range(4)]))
  self.path=self.root/'reports/SYNTHETIC_RELEASE_ONLY.json'
 def tearDown(self):self.tmp.cleanup()
 def write_inputs(self):
  for n,v in [('reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json',self.old),('reports/PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_STAGE.json',self.stage)]:
   (self.root/n).write_text(json.dumps(v),encoding='utf-8')
  self.path.write_text(json.dumps(self.w),encoding='utf-8')
 def execute_factory(self):
  self.write_inputs();saved=sys.argv
  try:
   sys.argv=[str(self.root/NAMES[0]),'--release-witness',str(self.path)]
   with contextlib.redirect_stdout(io.StringIO()):runpy.run_path(str(self.root/NAMES[0]),run_name='__main__')
  finally:sys.argv=saved
 def must_block(self):
  with self.assertRaises(AssertionError):self.execute_factory()
  self.assertFalse(any((self.root/n).exists()for n in(OUT,DISP,COLL)))
 def test_positive_only_creates_source(self):
  self.execute_factory();v=json.loads((self.root/OUT).read_bytes());self.assertEqual(v['actual_parent_or_SDK_or_C_or_lock_or_model_operations'],0);self.assertTrue(v['original_future_fresh_gates_still_required'])
  t=ast.parse((self.root/DISP).read_bytes());old=ast.parse(SOURCES[NAMES[1]])
  literals=lambda tr:[n.value for n in ast.walk(tr)if isinstance(n,ast.Constant)and type(n.value)is str and 'subprocess.Popen'in n.value]
  self.assertEqual(literals(t),literals(old));self.assertEqual(len(literals(t)),1);ast.parse((self.root/COLL).read_bytes())
  self.assertEqual(len(v['source_files']),2);self.assertFalse((self.root/'PAPER_ALIGNED_REBUILD_20261103').exists())
  self.assertIn('PHASE1_BOUNDARY_DEVICE_ACTUAL_CPU_V1.json',(self.root/DISP).read_text());self.assertIn("q['negative_cases']==11",(self.root/DISP).read_text())
 def test_ready_false(self):self.w['actual']['original_frozen_resources_observed_clear']=False;self.must_block()
 def test_leases_false(self):self.w['actual']['original_relevant_leases_clear']=False;self.must_block()
 def test_active_owner(self):self.w['actual']['canonical_summary']['active_segment']={'owner_run_id':'synthetic_busy'};self.must_block()
 def test_wrong_generation(self):self.w['actual']['canonical_summary']['authority_generation']='wrong';self.must_block()
 def test_missing_lock_row(self):self.w['actual']['required_project_lock_rows'].pop();self.must_block()
 def test_nonempty_lock(self):self.w['actual']['required_project_lock_rows'][0]['records']=['synthetic_WRITE'];self.must_block()
 def test_missing_lock_file(self):self.w['actual']['required_project_lock_rows'][0]['missing']=True;self.must_block()
 def test_old_observation(self):self.w['actual']['epoch']=9;self.must_block()
 def test_wrong_closed_hash(self):self.w['old_closed_metadata_SHA']='b'*64;self.must_block()
 def test_wrong_old_root(self):self.w['old_root']='/synthetic/tasks/DIFFERENT';self.must_block()
 def test_unmaterialized(self):self.stage['receipt']['materialized']=False;self.must_block()
 def test_failed_metadata(self):self.stage['receipt']['metadata_validation']['passed']=False;self.must_block()
 def test_below_reserve(self):self.w['actual']['canonical_summary']['remaining_training_seconds']=99;self.must_block()
 def test_collector_derivation_failure_does_not_write_dispatcher(self):
  p=self.root/NAMES[2];p.write_text(p.read_text().replace('PHASE1_CAPTURE_DEVICE_BINDING_V4_CLOSED_METADATA_COLLECTION_STARTED_ONCE.json','SYNTHETIC_WRONG_LITERAL.json'),encoding='utf-8');self.must_block()
 def test_witness_outside_reports(self):self.path=self.root/'SYNTHETIC_RELEASE_ONLY.json';self.must_block()
if __name__=='__main__':
 runner=unittest.TextTestRunner(verbosity=2);result=runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(FactoryTests));v=dict(kind='ISOLATED_SOURCE_FACTORY_SYNTHETIC_TESTS_NOT_NATIVE_OR_RELEASE_PROOF_V1',epoch=time.time(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),source_files=[dict(name=n,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest())for n,b in SOURCES.items()],generated_dispatcher_and_collector_executions=0,SSH_SDK_Torch_model_canonical_resource_or_parent_calls=0,synthetic_evidence_not_actual_release=True)
 out=R/'reports/PHASE1_V4_ADMISSION2_PARENT_FACTORY_SOURCE_TESTS_V1.json';assert not out.exists()
 with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
 print(json.dumps(v,indent=2));raise SystemExit(0 if result.wasSuccessful()else 1)
