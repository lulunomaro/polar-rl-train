"""Crash/retry safety without starting Isaac, loading Torch or running learning."""
from pathlib import Path
import unittest,tempfile,json,hashlib,base64
from unittest.mock import patch
import eval_worker as w
def digest(b):return hashlib.sha256(b).hexdigest()
class TransferTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_download_resumes_existing_prefix(self):
  data=b'a'*(w.CHUNK+13);p=self.root/'checkpoint.bin';p.with_suffix('.bin.partial').write_bytes(data[:8]);offsets=[]
  def rpc(req):
   offsets.append(req['offset']);chunk=data[req['offset']:req['offset']+req['count']]
   return {'offset':req['offset'],'data':base64.b64encode(chunk).decode(),'part_sha256':digest(chunk)}
  with patch.object(w,'rpc',rpc):w.fetch('job','checkpoint',{'bytes':len(data),'sha256':digest(data)},p)
  self.assertEqual(offsets[0],8);self.assertEqual(p.read_bytes(),data)
 def test_corrupt_transfer_never_promoted(self):
  p=self.root/'checkpoint.bin'
  with patch.object(w,'rpc',lambda _: {'offset':0,'data':base64.b64encode(b'bad').decode(),'part_sha256':digest(b'bad')}):
   with self.assertRaises(AssertionError):w.fetch('job','checkpoint',{'bytes':3,'sha256':digest(b'new')},p)
  self.assertFalse(p.exists());self.assertTrue(p.with_suffix('.bin.partial').exists())
 def test_finished_artifact_does_not_redownload(self):
  p=self.root/'checkpoint.bin';p.write_bytes(b'good')
  with patch.object(w,'rpc',side_effect=AssertionError('Unnecessary transfer')):w.fetch('job','checkpoint',{'bytes':4,'sha256':digest(b'good')},p)
 def test_upload_retry_starts_at_remote_prefix(self):
  p=self.root/'probe.json';p.write_bytes(b'abcdef');calls=[]
  def rpc(req):
   calls.append(req)
   return {'bytes':2,'finalized':False} if req['op']=='result_status' else {'ok':True}
  with patch.object(w,'rpc',rpc):w.upload('job',p)
  self.assertEqual(calls[1]['offset'],2);self.assertEqual(base64.b64decode(calls[1]['data']),b'cdef')
  self.assertEqual(calls[-1]['sha256'],digest(b'abcdef'))
 def test_physics_completion_resumes_only_result_upload(self):
  folder=self.root/'jobs/calibration-job';folder.mkdir(parents=True)
  result={'phase':'complete'};(folder/'PHYSICS_COMPLETE.json').write_text(json.dumps(result));(folder/'result.json').write_text(json.dumps(result))
  with patch.object(w,'ROOT',self.root),patch.object(w,'rpc',return_value={}),patch.object(w,'upload',return_value={}) as upload,patch.object(w.subprocess,'Popen',side_effect=AssertionError('Physics replayed')):
   w.execute('calibration-job')
  self.assertTrue((folder/'complete.json').exists());self.assertEqual(upload.call_count,2)
 def test_new_learning_job_rejected_before_subprocess(self):
  d={'immutable':True,'stage':'S0E','kind':'expert_ppo'}
  with patch.object(w,'ROOT',self.root),patch.object(w,'rpc',return_value=d),patch.object(w.subprocess,'Popen',side_effect=AssertionError('Unauthorized learning')):
   with self.assertRaises(AssertionError):w.execute('calibration-job')
if __name__=='__main__':unittest.main()
