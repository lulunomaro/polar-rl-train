"""Read a complete own active save and verify real PPO against original full source on CPU."""
import json,os,time,shlex
from pathlib import Path
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_original_linux20k_formal_once import S as BASE,PY,D
S=BASE.replace('_v1','_runtime_assets_complete_v3')
def main():
    c=connect_linux_only()
    try:
        src=r'''
from pathlib import Path
import json,hashlib,sys,torch,time
R=Path(S);sys.path.insert(0,str(R));sys.path.insert(0,str(R/'isaac/mod4'))
from wave50_lifetime_fullsave_cpu import fullsave
m=json.loads((R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes());paths=list((R/'formal/learning_logs').glob('*/latest_complete.json'))
if not paths:print(json.dumps(dict(epoch=time.time(),saved_PPO_pending=True,no_save_claimed=True)));sys.exit(0)
assert len(paths)==1;latest=json.loads(paths[0].read_bytes());p=Path(latest['checkpoint']);h=hashlib.sha256(p.read_bytes()).hexdigest();info=fullsave(p,count=20000)
own=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(m['source']['path'],map_location='cpu',weights_only=False)
a=own['actor_state_dict'];b=source['actor_state_dict'];assert set(a)==set(b);changed=[k for k in a if isinstance(a[k],torch.Tensor) and not torch.equal(a[k],b[k])]
def steps(c):return [float(x['step']) for x in c['optimizer_state_dict']['state'].values() if 'step' in x]
x,y=steps(own),steps(source);assert len(x)==len(y) and x;delta=[u-v for u,v in zip(x,y)];assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0
assert len(changed)==9
markers=[]
for q in p.parent.glob('*STARTUP*VERIFIED.json'):
 raw=q.read_bytes();v=json.loads(raw);assert v['pid']==latest['pid'] and v['source_sha256']==m['source']['sha256']
 if 'passed' in v:assert v['passed']
 # Original older D0-D7 proofs express explicit booleans, not a universal 'passed'.
 for k,z in v.items():
  if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert z is True,(q.name,k)
 markers.append(dict(name=q.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
assert len(markers)==12
updates=int(delta[0]/20);controls=updates*24
proof=dict(epoch=time.time(),passed=True,own_path=str(p),own_SHA=h,bytes=p.stat().st_size,source=m['source'],num_envs=20000,finite_floating_tensors=info['finite_tensors'],full_original_state_CPU_contract=info,actor_changed=changed,optimizer_step_delta=delta[0],actual_saved_updates=updates,controls=controls,envsteps=controls*20000,callbacks=controls*4,actual_own_saved_startup=markers,ownPID=latest['pid'],active_save_not_formal_final=True,qualified50=False)
q=R/'formal'/('OWN_SAVED_PPO_CPU_ACTUAL_'+str(time.time_ns())+'.json');q.write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(PY)+' -',timeout=60);si.write('S='+repr(S)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=D/'reports'/('ORIGINAL_LINUX20K_OWN_SAVED_PPO_CPU_ACTUAL_'+str(time.time_ns())+'.json');p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);v=json.loads(out)
        if v.get('passed'):
            dest=D/'ORIGINAL_LINUX20K_OWN_ACTIVE_SAVE';dest.mkdir(exist_ok=True);q=dest/Path(v['own_path']).name
            sf=c.open_sftp();sf.get(v['own_path'],str(q));sf.close();assert q.stat().st_size==v['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==v['own_SHA']
        print(json.dumps(dict(receipt=str(p),passed=v.get('passed'),own_SHA=v.get('own_SHA'),updates=v.get('actual_saved_updates'),envsteps=v.get('envsteps'),optimizer_step_delta=v.get('optimizer_step_delta'),pending=v.get('saved_PPO_pending'))))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    import hashlib
    main()
