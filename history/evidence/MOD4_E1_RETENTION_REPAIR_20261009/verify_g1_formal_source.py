"""Verify actual formal PPO startup and run-frozen source; no production mutation."""
from pathlib import Path
import os,sys,json,shlex,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009'
def main():
 assert not (R/'FORMAL_START_ACTUAL_VERIFIED.json').exists()
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code="""from pathlib import Path
import json,hashlib,os,time,re
D=Path(ROOT);j=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=j(D/'reports/E1_STATE.json');assert s['phase']=='bounded_E1_G1_retention_repair_learning';assert not (D/'reports/E1_ATTENTION.json').exists()
child=s['child'];p=Path('/proc')/str(child['pid']);st=(p/'stat').read_text().split(') ',1)[1].split();argv=(p/'cmdline').read_bytes().decode().split('\\0');assert int(st[19])==child['start_ticks'] and str(D/'isaac/mod4/train_e1_g1_repair_resume_ppo.py') in argv
name=argv[argv.index('--run_name')+1];runs=list((D/'learning_logs').glob('*_'+name));assert len(runs)==1;run=runs[0]
m=j(run/'run_manifest.json');f=j(D/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==321 and m['source_map']==f
for n,h in f.items():assert sha(D/n)==h,n
assert len(m['src_sha256'])==62
for n,h in m['src_sha256'].items():assert sha(run/'src_snapshot'/n)==h,n
source='655a36b78926bc17d4230996fe152b62d0f997f3037105d5247582697440481f';assert m['init_checkpoint_sha256']==source
startup=j(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');assert startup['pid']==child['pid'] and startup['source_sha256']==source and startup['explicit_G0_to_G1_geometry_transition'] and not startup['terrain_state_restored_exact'] and startup['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and startup['complete_D1_D7_optimizer_global_named_streams_verified'] and startup['E1_episode_incremented_once'] and not startup['PhysX_exact_resume_claimed']
cp=j(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');assert cp['source_sha256']==source and cp['actual_CUDA_chassis_PD_disk_roundtrip_exact'] and cp['complete_D1_D6_optimizer_global_named_streams_verified']
pre=j(D/'reports/E1_COMPLETE_PPO_PREFLIGHT_PASSED.json');assert pre['weights_discarded'] and pre['small']['actual_environment_steps']==6144 and pre['big']['actual_environment_steps']==1920000
assert pre['small']['checkpoint']['finite_tensors']==pre['big']['checkpoint']['finite_tensors']==96
log=Path(s['active_log']);text=log.read_text(errors='replace');updates=len(re.findall('Learning iteration',text));assert updates>0 and 'Traceback (most recent call last)' not in text
b=j(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'));assert b['authorized_training_seconds']==828000 and b['active_segment']['pid']==child['pid']
proof=dict(epoch=time.time(),trial_id='E1-G1-FORMAL-ACTUAL-01',root=str(D),phase=s['phase'],run=str(run),child=dict(pid=child['pid'],start_ticks=int(st[19]),cwd=os.readlink(p/'cwd'),argv=argv),source_sha256=source,actual_PPO_logs=updates,source_count321_exact=True,snapshot_count62_exact=True,complete_D1_D7_optimizer_globalnamed_CUDA_startup_passed=True,explicit_G0_to_G1_geometry_transition_not_old_mesh_exact=True,terrain_startup=startup,preflights=dict(small=pre['small'],big=pre['big']),own_formal_latest_complete=j(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None,early_missing_ownsave_is_pending=True,deadline=s['deadline_epoch'],formal_final_behavior_pending=True,canonical_active_child_exact=True,new_budget_seconds=0,read_only=True)
print(json.dumps(proof))
""".replace('ROOT',repr(ROOT))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace')
  v=json.loads(b);(R/'FORMAL_START_ACTUAL_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
  # One new central report only, not a rewrite of the previous phase snapshot.
  path='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/E1_G1_FORMAL_START_ACTUAL_VERIFIED.json';raw=(R/'FORMAL_START_ACTUAL_VERIFIED.json').read_bytes()
  with c.open_sftp() as sf:
   with sf.open(path,'wbx') as out:out.write(raw)
   assert sf.open(path).read()==raw
  (R/'FORMAL_REPORT_SYNCED.json').write_text(json.dumps(dict(epoch=time.time(),source=str(R/'FORMAL_START_ACTUAL_VERIFIED.json'),central=path,bytes_exact=True,no_runtime_or_budget_write=True)),encoding='utf8')
  print(json.dumps({k:v for k,v in v.items() if k not in ('preflights','terrain_startup')}))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
