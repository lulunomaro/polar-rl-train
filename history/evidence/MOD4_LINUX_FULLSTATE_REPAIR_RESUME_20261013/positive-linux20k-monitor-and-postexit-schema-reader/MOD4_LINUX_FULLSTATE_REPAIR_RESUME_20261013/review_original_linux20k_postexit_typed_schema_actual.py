"""Prepared independent postexit review. Does not relabel parent errors or change training/budget."""
import json,os,shlex,time
from pathlib import Path
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_original_linux20k_formal_once import S as BASE,PY,D
S=BASE.replace('_v1','_runtime_assets_complete_v3')
def main():
    c=connect_linux_only()
    try:
        src=r'''
from pathlib import Path
import os,sys,json,time,hashlib,fcntl,torch
R=Path(S);e=R/'formal/EXIT_RECEIPT.json'
if not e.exists():print(json.dumps(dict(postexit_pending=True,no_final_claimed=True)));sys.exit(0)
exit=json.loads(e.read_bytes());assert exit['returncode']==0 and exit['child_actually_absent'] and not exit['physics_capacity_error']
assert not Path('/proc').joinpath(str(exit['child']['pid'])).exists()
parent=json.loads((R/'PARENT_IDENTITY.json').read_bytes());assert not Path('/proc').joinpath(str(parent['pid'])).exists()
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(B.read_bytes());assert b['active_segment'] is None
segments=[x for x in b['completed_segments'] if x.get('kind')==exit['canonical_unique_segment']];assert len(segments)==1
segment=segments[0];assert segment['owner_parent_pid']==parent['pid'] and segment['source_SHA']=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
for p in [B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
paths=list((R/'formal/learning_logs').glob('*/latest_complete.json'));assert len(paths)==1
latest=json.loads(paths[0].read_bytes());p=Path(latest['checkpoint']);sys.path.insert(0,str(R));sys.path.insert(0,str(R/'isaac/mod4'))
from wave50_lifetime_fullsave_cpu import fullsave
info=fullsave(p,count=20000);ck=torch.load(p,map_location='cpu',weights_only=False)
m=json.loads((R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes());source=torch.load(m['source']['path'],map_location='cpu',weights_only=False)
changed=[k for k,v in ck['actor_state_dict'].items() if isinstance(v,torch.Tensor) and not torch.equal(v,source['actor_state_dict'][k])];assert len(changed)==9
steps=lambda c:[float(x['step']) for x in c['optimizer_state_dict']['state'].values() if 'step' in x]
x,y=steps(ck),steps(source);delta=[u-v for u,v in zip(x,y)];assert delta and len(set(delta))==1 and delta[0]>0 and delta[0]%20==0
proofs=[]
for q in p.parent.glob('*STARTUP*VERIFIED.json'):
 raw=q.read_bytes();v=json.loads(raw);assert v['pid']==latest['pid'] and v['source_sha256']==m['source']['sha256']
 if 'passed' in v:assert v['passed']
 for k,z in v.items():
  if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert z is True
 proofs.append(dict(path=str(q),sha256=hashlib.sha256(raw).hexdigest()))
assert len(proofs)==12
error=R/'ORIGINAL_PARENT_ERROR.json'
proof=dict(epoch=time.time(),independent_postexit_pass=True,original_parent_error=json.loads(error.read_bytes()) if error.exists() else None,original_parent_error_not_relabelled=True,ownfullsave=info,ownsourcefreeze_manifest_SHA=hashlib.sha256((R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes()).hexdigest(),startup_typed_schema=proofs,actor9_changed=True,actual_saved_updates=int(delta[0]/20),optimizer_step_delta=delta[0],actual_exit=exit,canonical_unique_original_segment=segment,canonical_active_null=True,two_actual_fcntl_free=True,no_GPU_PPO_signal_or_budget_action=True,complete_training_trace_and_3060_frozen_behavior_review_still_required=True,qualified50=False)
q=R/'INDEPENDENT_POSTEXIT_TYPED_SCHEMA_ACTUAL.json';q.write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(PY)+' -',timeout=60);si.write('S='+repr(S)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=D/'reports'/('ORIGINAL_LINUX20K_POSTEXIT_TYPED_SCHEMA_ACTUAL_'+str(time.time_ns())+'.json');p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p)
        v=json.loads(out);print(json.dumps(dict(receipt=str(p),passed=v.get('independent_postexit_pass'),pending=v.get('postexit_pending'),actual_updates=v.get('actual_saved_updates'))))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
