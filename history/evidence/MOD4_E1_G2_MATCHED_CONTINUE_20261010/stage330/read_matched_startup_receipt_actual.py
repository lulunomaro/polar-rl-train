"""Read actual same-G2 startup, own source snapshot and canonical PID without mutation."""
from pathlib import Path
import sys,os,time,json,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def main():
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        code="""from pathlib import Path
import json,hashlib,os,time,re
D=Path(ROOT);read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(D/'reports/E1_STATE.json');assert state['phase']=='bounded_E1_G2_retention_repair_learning';child=state['child'];p=Path('/proc')/str(child['pid']);s=(p/'stat').read_text().split(') ',1)[1].split()
assert int(s[19])==child['start_ticks'] and str(D/'isaac/mod4/train_e1_g2_reviewed_resume_ppo.py') in (p/'cmdline').read_bytes().decode().split('\\0')
runs=[p for p in (D/'learning_logs').glob('*') if (p/'run_manifest.json').exists()];assert len(runs)==1;run=runs[0];m=read(run/'run_manifest.json');f=read(D/'reports/SOURCE_FREEZE.json')['sha256']
assert len(f)==330 and m['source_map']==f and m['init_checkpoint_sha256']=='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b'
for n,h in f.items():assert H(D/n)==h,n
for n,h in m['src_sha256'].items():assert H(run/'src_snapshot'/n)==h,n
starts={n:read(run/n) for n in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json')}
assert all(x['source_sha256']==m['init_checkpoint_sha256'] for x in starts.values())
t=starts['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert t['terrain_state_restored_exact'] and not t['explicitly_new_E1_terrain'] and not t['explicit_G0_to_G2_geometry_transition'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['complete_D1_D7_optimizer_global_named_streams_verified'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
assert starts['CHASSIS_PD_RESUME_STARTUP_VERIFIED.json']['actual_CUDA_chassis_PD_disk_roundtrip_exact'] and starts['CHASSIS_PD_RESUME_STARTUP_VERIFIED.json']['complete_D1_D6_optimizer_global_named_streams_verified']
assert starts['GAS_DAMPING_RESUME_STARTUP_VERIFIED.json']['actual_CUDA_gas_state_disk_roundtrip_exact'] and starts['SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json']['actual_CUDA_spring_state_disk_roundtrip_exact'] and starts['ACTION_DELAY_RESUME_STARTUP_VERIFIED.json']['complete_D3_sensor_feedback_optimizer_global_named_streams_verified']
own=read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None;checkpoint=None
if own:
 assert own['pid']==child['pid'];path=Path(own['checkpoint']);checkpoint=dict(path=str(path),sha256=H(path),bytes=path.stat().st_size)
health=read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None
if health:assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4 and health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact'] and not health['nonfinite_observed'] and health['stop_reason'] is None
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=read(B);assert b['active_segment']['pid']==child['pid'] and b['authorized_training_seconds']==828000
log=Path(state['active_log']).read_text(errors='replace');count=len(re.findall(r'Learning iteration',log));assert count>0
print(json.dumps(dict(epoch=time.time(),run=str(run),child=child,phase=state['phase'],deadline=state['deadline_epoch'],source_count=len(f),actual_snapshot_count=len(m['src_sha256']),all_source_and_snapshot_SHA_exact=True,starts=starts,actual_PPO_log_entries=count,own_checkpoint=checkpoint,own_receipt=own,health=health,ownsave_and_health_may_be_pending=True,active_canonical_PID_match=True,canonical_readonly=True,remaining_accounted=b['authorized_training_seconds']-b['charged_training_seconds'],all_courses_finished=False,no_GPU_PPO_or_budget_mutation_by_reader=True)))
""".replace('ROOT',repr(ROOT))
        compile(code,'<actual-read-only>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');v=json.loads(b)
        path=R/('STARTUP_ACTUAL_'+str(int(v['epoch']))+'.json');assert not path.exists();path.write_text(json.dumps(v,indent=2),encoding='utf8')
        print(json.dumps(dict(report=str(path),PPO_log_entries=v['actual_PPO_log_entries'],source_count=v['source_count'],snapshot_count=v['actual_snapshot_count'],own_checkpoint=v['own_checkpoint'],health_pending=v['health'] is None,same_G2_terrain_CUDA_restore_exact=True,canonical_PID_match=True)))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        (R/('STARTUP_READER_ERROR_'+str(int(time.time()))+'.json')).write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-STARTUP-READER-01',error=traceback.format_exc(),no_production_mutation=True),indent=2),encoding='utf8');raise
