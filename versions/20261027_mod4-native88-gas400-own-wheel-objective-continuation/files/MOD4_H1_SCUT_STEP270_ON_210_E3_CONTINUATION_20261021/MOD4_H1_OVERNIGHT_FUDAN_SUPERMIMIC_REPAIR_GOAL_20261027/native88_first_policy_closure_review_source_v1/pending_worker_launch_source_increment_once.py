"""New worker-launch-gap metadata increment; no old fixture reexecution."""
from pathlib import Path
import sys,json,ast,hashlib,types,traceback
from unittest.mock import patch
D=Path(__file__).resolve().parent
def main():
 # Reuse only saved synthetic JSON bytes, never invoke the consumed fixture.
 old=D/'fixtures/SYNTHETIC_OBSERVER_PUBLICATION';F=D/'fixtures/SYNTHETIC_PENDING_WORKER_LAUNCH';F.mkdir(parents=True)
 for p in old.rglob('*'):
  if p.is_file() and p.name not in ('NODE_CURRENT.json','NODE_IDENTITY.json','native88_closed_source_CPU_v1.py','THREE_SLOT_COMPLETE_MANIFEST_V1.json'):
   target=F/p.relative_to(old);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 # Module/source args refer to the NEW fixture root and remain fake.
 spec=dict(key='h1',python='/SYNTHETIC/python',production_script='SYNTHETIC_worker.py',seed=27,source_SHA='ae5ff91877bcfdda72b864a181fdbbbd0c78401cb34591ca507adda44a6632e9',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',reference_artifact_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3',candidate_pins={})
 first=json.loads((F/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').read_bytes());producer=first['producer']
 for field in ('gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):spec[field]=producer[field]
 spec['objective_contract_SHA']=producer['runtime_objective_contract_SHA']
 dispatch=b'def expected_exec_identity(spec,args,B):\n return dict(argv=args,exe="/SYNTHETIC/python",root=str(B))\n';(F/'native88_closed_source_CPU_v1.py').write_bytes(dispatch)
 rows=[]
 for rel in ('native88_closed_source_CPU_v1.py','source/native_own_fudan88_gas400_training_v2.py','source/native_finalization_own88_gas400.py','source/native88_gas400_migration_v1.py'):
  h=hashlib.sha256((F/rel).read_bytes()).hexdigest();rows.append(dict(relative=rel,SHA=h));spec['candidate_pins'][rel]=h
 raw=json.dumps(dict(files=rows)).encode();(F/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_bytes(raw);spec['manifest_SHA']=hashlib.sha256(raw).hexdigest()
 ng=json.loads((F/'job0/GO_PRODUCTION.json').read_bytes());ng['manifest_SHA']=spec['manifest_SHA'];(F/'job0/GO_PRODUCTION.json').write_text(json.dumps(ng),encoding='utf8')
 ln=[spec['python'],'-u','-B',str(F/'three_slot_finite_node_v1.py')];lw=[spec['python'],'-u','-B',str(F/spec['production_script']),'--slot','h1','--phase','production','--num-envs','4096','--seed','27','--source-scope','native_models_only_fresh400N_environment']
 ids={41:dict(pid=41,creation=1.,exe='/SYNTHETIC/python',argv=ln,root=str(F)),42:dict(pid=42,creation=1.,exe='/SYNTHETIC/python',argv=lw,root=str(F))}
 (F/'NODE_IDENTITY.json').write_text(json.dumps(ids[41]),encoding='utf8');(F/'NODE_CURRENT.json').write_text(json.dumps(dict(row=dict(phase='ready'))),encoding='utf8')
 class NoSuch(Exception):pass
 class Proc:
  def __init__(self,pid):self.pid=pid
  def create_time(self):return ids[self.pid]['creation']
  def exe(self):return ids[self.pid]['exe']
  def cmdline(self):return ids[self.pid]['argv']
  def cwd(self):return ids[self.pid]['root']
 clock=[1000.];sleeps=[]
 def sleep(dt):
  sleeps.append(dt);clock[0]+=dt;(F/'NODE_CURRENT.json').write_text(json.dumps(dict(row=dict(worker=ids[42],phase='production'))),encoding='utf8')
 ns={};exec(compile((D/'native88_closing_protocol_v1.py').read_bytes(),'protocol','exec'),ns);exec(compile((D/'native88_observer_readonly_remote_v1.py').read_bytes(),'observer','exec'),ns)
 with patch.dict(sys.modules,{'psutil':types.SimpleNamespace(Process=Proc,NoSuchProcess=NoSuch)}),patch('time.time',lambda:clock[0]),patch('time.sleep',sleep),patch('subprocess.check_output',lambda *a,**k:'42, '+spec['GPU_UUID']+'\n'):
  result=ns['observe_target_readonly'](dict(root=str(F),spec=spec,detached_node=dict(detached_pid=41),go=ng,deadline_epoch=1010.))
 assert result['passed'] and result['first_metadata_read_count']==1 and len(sleeps)==1,result
 # Recycled PID branch must not inspect another process exe/argv.
 touched=[]
 class Recycled:
  def __init__(self,pid):self.pid=pid
  def create_time(self):return 2.
  def exe(self):touched.append('exe');raise AssertionError('foreign exe')
  def cmdline(self):touched.append('argv');raise AssertionError('foreign argv')
 with patch.dict(sys.modules,{'psutil':types.SimpleNamespace(Process=Recycled,NoSuchProcess=NoSuch)}):v=ns['_exact_recorded_identity'](ids[41])
 assert v['actual_out'] and not touched
 for path in D.glob('*.py'):ast.parse(path.read_bytes())
 with (D/'PENDING_WORKER_LAUNCH_INCREMENT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=2,pending_worker_launch_waited_naturally=True,first_metadata_reads=1,recycled_PID_no_foreign_identity_query=True,synthetic_metadata_only=True,
  final_observer_source_SHA=hashlib.sha256((D/'native88_observer_readonly_remote_v1.py').read_bytes()).hexdigest(),no_network_model_or_GPU=True),f,indent=2)
 print(json.dumps(dict(passed=True,count=2)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (D/'PENDING_WORKER_LAUNCH_INCREMENT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),synthetic_only=True),f,indent=2)
  raise
