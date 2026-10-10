"""CPU-read actual365 active or final ownsave; pending future receipts are not failures."""
from pathlib import Path
import json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def main():
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import json,sys,torch,time,hashlib
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_e1_wave_isolated_revision004_once as m
j=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=j(D/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==366 and all(H(D/n)==h for n,h in f.items())
saved=[];pending=[]
for run in (D/'learning_logs').glob('*'):
 if not run.is_dir():continue
 if not (run/'latest_complete.json').exists():pending.append(dict(run=str(run),phase='own_save_not_yet_generated'));continue
 rec=j(run/'latest_complete.json');manifest=j(run/'run_manifest.json');assert rec['pid']>0 and manifest['source_map']==f and manifest['init_checkpoint_sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
 freeze=run/'rolling_source_freeze.json'
 if not freeze.exists():pending.append(dict(run=str(run),phase='parent_ownfreeze_not_yet_completed'));continue
 assert j(freeze)['sha256']==f and all(H(run/'e1_source_snapshot'/n)==h for n,h in f.items())
 assert all(H(run/'src_snapshot'/n)==h for n,h in manifest['src_sha256'].items())
 info=m.fullsave(Path(rec['checkpoint']));assert info['finite_tensors']==102 and info['sha256']==H(Path(rec['checkpoint']));info['bytes']=Path(rec['checkpoint']).stat().st_size
 names=('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json')
 startup={n:j(run/n) for n in names}
 for v in startup.values():assert v['source_sha256']==manifest['init_checkpoint_sha256'] and not v['PhysX_exact_resume_claimed']
 terrain=startup[names[0]];assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G2_to_G3_geometry_transition'] and not terrain['explicitly_new_E1_terrain'] and terrain['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and terrain['complete_D1_D7_optimizer_global_named_streams_verified'] and terrain['E1_episode_incremented_once']
 command=startup[names[1]];assert command['predecessor_command_state_restored_exact'] and not command['explicitly_new_command_scope'] and command['saved_source_episode_plus_one_verified'] and command['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and command['old_full_D1_D7_optimizer_global_named_streams_verified']
 passed=D/'reports/e1_wave_G3_isolated_observation_PASSED.json';final=None
 if passed.exists():
  final=j(passed);assert final['checkpoint']['sha256']==info['sha256'] and final['own_PID_bound_receipt']==rec and len(final['unique_completed_segment'])==1
 saved.append(dict(run=str(run),own_PID_bound_receipt=rec,checkpoint=info,actual_snapshot_count=len(manifest['src_sha256']),own366freeze_verified=True,startup_same_G3_same_command_verified=startup,final_PASS_and_unique_segment=final,active_save_is_not_final_or_behavior_graduation=final is None))
if not saved and not pending:pending.append(dict(phase='run_or_ownsave_not_yet_generated'))
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),read_only_CPU_no_CUDA_initialized=True,saved=saved,pending=pending,no_GPU_PPO_canonical_or_signal=True)))
'''.replace('Path(ROOT)','Path('+repr(ROOT)+')')
  _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
  p=R/('WAVE_OWN_CPU_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(dict(report=str(p),saved=[dict(checkpoint=x['checkpoint'],snapshot_count=x['actual_snapshot_count'],final=x['final_PASS_and_unique_segment'] is not None) for x in v['saved']],pending=v['pending'])))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/('WAVE_OWN_CPU_READER_ERROR_'+str(int(time.time()))+'.json');assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),reader_only_no_production_mutation=True),indent=2).encode());raise
