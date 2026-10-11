from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,inspect,hashlib,torch
D=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010');sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_e1_wave_isolated_revision004_once as old
m=old.m
out=dict(controllers={name:dict(path=inspect.getsourcefile(fn),source=inspect.getsource(fn)) for name,fn in {'train':m.train,'verify_original_records':m.verify_original_records,'publish':m.publish,'left':m.s.left,'worker_verify':m.s.q.verify}.items()},globals={name:str(getattr(m,name)) for name in ('D','R')},s_globals={name:str(getattr(m.s,name)) for name in ('D','R') if hasattr(m.s,name)},q_globals={name:str(getattr(m.s.q,name)) for name in ('D','R','ER','P') if hasattr(m.s.q,name)},freeze=json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes()),reports=sorted(p.name for p in (D/'reports').glob('*.json')),no_CUDA_initialized=not torch.cuda.is_initialized())
assert out['no_CUDA_initialized'];print(json.dumps(out))
''')
  p=save('WAVE_OLD_SOURCE_CONTRACT_READONLY_'+str(time.time_ns())+'.json',v)
  with n.open_sftp() as f:
   for name,h in v['freeze']['sha256'].items():
    raw=f.open(OLD+'/'+name,'rb').read();assert H(raw)==h;dest=D/'inherited_source'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==raw
    else:dest.write_bytes(raw)
  print(json.dumps(dict(report=str(p),sources=len(v['freeze']['sha256']),CPU_only=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':main()
