import unittest,tempfile,json,hashlib,base64,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('bridge',Path(__file__).with_name('artifact_service.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);b.ROOT=self.root;b.Q=self.root/'eval_queue';b.RESULTS=self.root/'results';b.Q.mkdir()
  self.job='calibration-flat-anchor';p=self.root/'snapshot.bin';p.write_bytes(b'abc')
  self.d={'job_id':self.job,'stage':'S0E','immutable':True,'plan_sha256':'approved','artifacts':{'checkpoint':{'path':str(p),'bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}}}
  self.save()
 def tearDown(self):self.tmp.cleanup()
 def save(self):(b.Q/(self.job+'.json')).write_text(json.dumps(self.d))
 def req(self,op,**kw):return b.handle({'op':op,'job_id':self.job,**kw})
 def part(self,offset=0,data=b'abc'):
  return self.req('result_part',name='result.json',offset=offset,data=base64.b64encode(data).decode(),part_sha256=hashlib.sha256(data).hexdigest())
 def test_immutable_stages(self):
  self.d['stage']='S2';self.save()
  with self.assertRaises(ValueError):self.req('manifest')
 def test_identifier_and_filename_escape(self):
  for job in ['../bad','x; touch file','/etc/shadow']:
   with self.assertRaises(ValueError):b.handle({'op':'manifest','job_id':job})
  for name in ['../a.json','.secret','folder/a.json','x.exe']:
   with self.assertRaises(ValueError):self.req('result_part',name=name,offset=0,data='',part_sha256=hashlib.sha256(b'').hexdigest())
 def test_external_source_refused(self):
  self.d['artifacts']['checkpoint']['path']='/etc/passwd';self.save()
  with self.assertRaises(ValueError):self.req('artifact_part',artifact='checkpoint')
 def test_part_verification(self):
  r=self.req('artifact_part',artifact='checkpoint',offset=1,count=2);self.assertEqual(base64.b64decode(r['data']),b'bc')
  with self.assertRaises(ValueError):self.req('artifact_part',artifact='checkpoint',count=262145)
 def test_resume_exact_without_duplicate_append(self):
  self.part();self.part();self.assertEqual(self.req('result_status',name='result.json')['bytes'],3)
  with self.assertRaises(ValueError):self.part(data=b'xyz')
  with self.assertRaises(ValueError):self.part(offset=5)
 def test_final_receipt_hash_bound(self):
  self.part()
  with self.assertRaises(ValueError):self.req('finalize_result',name='result.json',bytes=3,sha256='incorrect')
  r=self.req('finalize_result',name='result.json',bytes=3,sha256=hashlib.sha256(b'abc').hexdigest())
  self.assertEqual(r['source_checkpoint_sha256'],self.d['artifacts']['checkpoint']['sha256'])
  self.assertTrue(self.req('result_status',name='result.json')['finalized'])
 def test_no_production_operations(self):
  for op in ['exec','launch','budget_write','stop_trainer']:
   with self.assertRaises(ValueError):self.req(op)
if __name__=='__main__':unittest.main()
