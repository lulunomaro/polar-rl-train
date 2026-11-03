"""NEW scientific-purpose original whole-JSON cache, not a lifecycle collector/retry.
Only an already qualified, closed own capture root and exactly two ORIGINAL
FINAL documents may be read. No model/raw trajectory/SDK/resource operations.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest()
PINS={'capture_evidence_verifier_v1.py':(41739,'2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979'),'actual_capture_application_v1.py':(9896,'2fdac2ffe491fee7f20ef96b128c0b00f6a8dd9d94f8fe604c021e9bf36dd5ba')}

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);a=p.parse_args();inp=Path(a.input);assert inp.resolve().parent==HERE and inp.name=='INPUT_METADATA.json';v=json.loads(inp.read_bytes());assert v['kind']=='NEW_OWN_CAPTURE_SCIENTIFIC_WHOLE_CACHE_APPLICATION_V1'and v['qualified_closed_execution']is True
 root=Path(v['root']);base=Path('/home/lc01/Zonglin Li/zonglin2/tasks');assert root.parent==base and root.name==v['group_id']and root.name.startswith('MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_')and not root.is_symlink()
 for name,pin in PINS.items():
  b=(HERE/name).read_bytes();assert(len(b),H(b))==pin
 sys.path.insert(0,str(HERE));import capture_evidence_verifier_v1 as pure;import actual_capture_application_v1 as app
 assert not any(n.split('.')[0]in{'torch','isaacsim','isaaclab','omni','warp','pxr','paramiko','fcntl'}for n in sys.modules)
 aliases={'worker_final':'cases/E3/FINAL.json','group_final':'FINAL.json'};cache={};proof={};opens={}
 def cached(alias):
  if alias in cache:return cache[alias]
  rel=aliases[alias];path=root/rel;assert path.resolve().is_relative_to(root.resolve())and not path.is_symlink();pin=v['expected_whole_files'][alias];assert type(pin['bytes'])is int and 0<pin['bytes']<=64*1024*1024 and len(pin['SHA256'])==64
  opens[alias]=opens.get(alias,0)+1
  with path.open('rb')as f:raw=f.read(64*1024*1024+1)
  assert len(raw)==pin['bytes']and H(raw)==pin['SHA256'];value=json.loads(raw);assert type(value)is dict;cache[alias]=value;proof[alias]=dict(original_bytes=len(raw),original_SHA256=H(raw),decoded_canonical_SHA256=pure.digest(value));return value
 worker=cached('worker_final');group=cached('group_final');assert worker['group_id']==group['group_id']==root.name and worker['passed_execution']is True and worker['controls']in(64,128)and worker['model_PT_reads']==worker['training_updates']==worker['optimizer_updates']==0
 life=v['lifecycle'];life['group_final']=group;task=v['task'];assert task['group_id']==root.name and task['train']is False and task['quality_evaluation']is False
 provenance=dict(v['original_byte_provenance']);provenance.update(proof)
 for alias,document in dict(life,task=task,worker_final=worker).items():
  if document is not None:assert provenance[alias]['decoded_canonical_SHA256']==pure.digest(document)
 before={k:pure.digest(x)for k,x in cache.items()};analysis=app.apply_capture(worker,task,life,provenance,v['reported_producer_pins']);assert all(pure.digest(cache[k])==value for k,value in before.items());assert cached('worker_final')is worker and cached('group_final')is group and opens=={'worker_final':1,'group_final':1}
 result=dict(kind='ACTUAL_NEW_OWN_CAPTURE_SCIENTIFIC_CACHE_APPLICATION_V1',epoch=time.time(),root=str(root),source_scope='FULL_ORIGINALS_READ_ONCE_EACH_FOR_RETAINED_SENSOR_QUEUE_SCIENCE_NOT_STATUS_OR_GIT',whole_files=proof,physical_JSON_opens=opens,JSON_decodes=dict(opens),cache_reuse_identity=True,whole_input_canonical_digests_unchanged=True,raw_trace_payload_exported=False,actual_original_controls=worker['controls'],actual_original_physics_callbacks=worker['physics_callbacks'],actual_feedback_samples=worker['feedback_samples'],actual_PT_model_raw_trajectory_SDK_GPU_canonical_lock_or_signal_operations=0,application=analysis,gate1='UNKNOWN',exact=False,stage2_GO=False)
 print(json.dumps(result,allow_nan=False))

if __name__=='__main__':main()
