"""Actual independent Linux target/sourcefreeze/CPU admission only. GPU approval remains false."""
from pathlib import Path
import json,os,shlex,time,hashlib
from deploy_original_linux20k_formal_once import S as BASE,PY,D
from read_linux_resume_boundary_actual import connect_linux_only
OLD=BASE.replace('_v1','_runtime_assets_complete_v3');NEW=BASE.replace('original_Linux20k_d05_continuation_v1','left_exploration20k_target_CPU_v1')
local=json.loads((D/'left_exploration20k_CPU_only_v1/CPU_COMPONENT_ACTUAL.json').read_bytes());assert local['CPU_component_passed'] and local['no_production_deployment']
c=connect_linux_only()
try:
 src=r'''
from pathlib import Path
import shutil,json,hashlib
O=Path(OLD);R=Path(NEW);assert not R.exists()
assert json.loads((O/'INDEPENDENT_POSTEXIT_TYPED_SCHEMA_ACTUAL.json').read_bytes())['independent_postexit_pass']
R.mkdir();m=json.loads((O/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes());rows=[]
for x in m['sourcefreeze']:
 p=Path(x['path']);q=R/p.relative_to(O);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'];rows.append(dict(x,path=str(q),source_origin=str(p)))
(R/'source').mkdir();(R/'LEFT_EXPLORATION_SOURCE_FREEZE_PREPARED.json').write_text(json.dumps(dict(actual_source_files=rows,original_Linux_geometry_clockDRhardware_code_bytes_exact=True,no_GPU_task_started=True,approved_GPU=False),indent=2))
print(json.dumps(dict(root=NEW,sourcefiles=len(rows),GPU_approval=False)))
'''
 def run(cmd,src,label):
  si,so,se=c.exec_command(cmd,timeout=70);si.write('OLD='+repr(OLD)+'\nNEW='+repr(NEW)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();p=D/'reports'/(label+'.json');p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);return json.loads(out)
 material=run('python3 -',src,'LEFT_EXPLORATION20K_TARGET_MATERIALIZED_ACTUAL')
 sf=c.open_sftp();q=Path(local['candidate']['path']);sf.put(str(q),NEW+'/source/own20k_left_joint_margin014_std1_CPU_prepared.pt');sf.close()
 src=r'''
from pathlib import Path
import json,sys,hashlib,torch
R=Path(NEW);sys.path.insert(0,str(R));sys.path.insert(0,str(R/'isaac/mod4'))
from wave50_lifetime_fullsave_cpu import fullsave
p=R/'source/own20k_left_joint_margin014_std1_CPU_prepared.pt';assert hashlib.sha256(p.read_bytes()).hexdigest()=='8ff1a32789364351e70ab23a7d96accf6cfdcdc670d1d352a6bea998d4b50d42'
info=fullsave(p,count=20000);ck=torch.load(p,map_location='cpu',weights_only=False);mark=ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'];assert mark['source_envs']==20000 and mark['initial_left_scalar_std']==1
assert mark['source_SHA']=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
assert mark['offset_reference_requires_actual_all20k_native_API_before_use'] and not torch.cuda.is_initialized()
f=R/'source/CPU_DISK_ROUNDTRIP_FIXTURE.pt';torch.save(ck,f);loaded=torch.load(f,map_location='cpu',weights_only=False)
def same(a,b):
 if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 if hasattr(a,'shape'):
  import numpy as np
  return type(a)is type(b) and np.array_equal(a,b)
 return type(a)is type(b) and a==b
assert same(ck,loaded)
proof=dict(passed_target_CPU_only=True,full_original_contract=info,all_full20k_private_and_DR_CPU_disk_roundtrip_exact=True,native_API_offset_defaultq_CUDA_roundtrip_and_episode_plus_one_NOT_passed=True,approved_GPU=False,PPO_NOT_started=True,source_SHA=mark['source_SHA'],candidate_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),no_budget_or_oldonce_action=True)
(R/'TARGET_FULLSTATE107_CPU_PASSED.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
 proof=run('CUDA_VISIBLE_DEVICES= '+shlex.quote(PY)+' -',src,'LEFT_EXPLORATION20K_ACTUAL_TARGET_FULLSTATE_CPU')
 print(json.dumps(dict(root=NEW,passed_target_CPU=proof['passed_target_CPU_only'],candidate_SHA=proof['candidate_SHA'],GPU_PPO_STARTED=False)))
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
