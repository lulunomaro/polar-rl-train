from route_second_io import *

def main():
    dest=D/'restore_diagnosis_sources';assert not dest.exists();dest.mkdir()
    n,w=io.connect_both()
    try:
      indices=[]
      with n.open_sftp() as f:
        for name in ('mild_dr.py','sensor_resume_contract.py','feedback_delay_checkpoint.py','spring_pressure_audit_runtime.py'):
          p=OLD+'/isaac/mod4/'+name;raw=f.open(p,'rb').read();(dest/name).write_bytes(raw);indices.append(dict(path=p,bytes=len(raw),sha256=H(raw),actual_source_bytes_saved_locally=True))
        names=f.listdir(ROOT)
        for name in names:
          if name.endswith('.error.txt') or name.startswith('e1_WAVE50_route_second_bounded_observation_') and name.endswith('.log'):
            raw=f.open(ROOT+'/'+name,'rb').read();(dest/name).write_bytes(raw);indices.append(dict(path=ROOT+'/'+name,bytes=len(raw),sha256=H(raw),own_failed_startup_original=True))
      v=run(n,r'''from pathlib import Path
import json,torch,time,hashlib
p=Path(SOURCE_TOKEN);torch.set_num_threads(1);ck=torch.load(p,map_location='cpu',weights_only=False);s=ck['sensor_DR_state']
def describe(x):
 if torch.is_tensor(x):return dict(shape=list(x.shape),dtype=str(x.dtype),min=float(x.min()) if x.numel() else None,max=float(x.max()) if x.numel() else None,unique_values=[float(v) for v in torch.unique(x).tolist()] if x.numel() and len(torch.unique(x))<40 else None)
 if isinstance(x,dict):return {k:describe(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return dict(type=str(type(x)),length=len(x))
 return x if isinstance(x,(str,int,float,bool)) or x is None else str(type(x))
print(json.dumps(dict(epoch=time.time(),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),sensor_DR_state=describe(s),CPU_only_no_RNG_GPU_or_budget_write=True)))
'''.replace('SOURCE_TOKEN',repr(SOURCE)))
      save('FAILED_SECOND_STARTUP_RESTORE_SOURCE_ACTUAL.json',dict(epoch=time.time(),indices=indices,source_CPU_schema=v,no_hotpatch_GPU_or_once_replay=True));print(json.dumps(v))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('RESTORE_SOURCE_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_replay=True));raise
