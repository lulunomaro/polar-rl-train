"""Correct only the admission reader to the actual *_COMPLETE receipt schema."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sf:sf.put(str(R/'FIRST_STAGING_READER_ERROR.txt'),ROOT+'/reports/FIRST_STAGING_READER_ERROR.txt')
 code=r'''
from pathlib import Path
import sys,json,hashlib,time,subprocess
D=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008');T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');OLD=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');E=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007/reports')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());write=lambda n,v:(D/'reports'/n).write_text(json.dumps(v,indent=2))
assert not (D/'reports/SAME_1MS_RANGE_EVIDENCE_REUSED.json').exists()
f=read(D/'reports/SOURCE_FREEZE.json')['sha256'];one=read(T/'reports/SOURCE_FREEZE.json')['sha256'];source=read(D/'reports/VALIDATED_SOURCE.json');audit=read(D/'reports/FAILURE_AND_FALLBACK_BOUNDARY.json')
before=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes()
pref=[];canon=json.loads(before);scope=read(E/'SENSOR_COMPLETE_PPO_PREFLIGHT_PASSED.json');assert scope['weights_discarded'] and scope['not_training_sources']
for name in ('sensor_discard_128_COMPLETE.json','sensor_discard_20000_COMPLETE.json'):
 p=E/name;r=read(p);h=r['health'];assert r['discarded_preflight'] and h['physics_dt_s']==.001 and h['actual_task_reset_events']==0
 assert h['actual_physics_callbacks']==h['expected_physics_callbacks'] and h['max_closure_error_m']<=.002 and r['checkpoint']['finite_tensors']==74
 pid=r['own_PID_bound_receipt']['pid'];segments=[x for x in canon['completed_segments'] if x['pid']==pid];assert segments==r['unique_completed_segment'] and len(segments)==1
 run=Path(r['run']);assert read(run/'latest_complete.json')==r['own_PID_bound_receipt'];assert sha(Path(r['checkpoint']['path']))==r['checkpoint']['sha256'];manifest=read(run/'run_manifest.json')
 assert manifest['env']['RM_PHYSICS_DT_S']=='0.001' and manifest['env']['RM_SOLVER_POS']=='16'
 for n,x in manifest['src_sha256'].items():assert sha(run/'src_snapshot'/n)==x,n
 pref.append(dict(receipt_path=str(p),receipt_sha256=sha(p),actual_updates=h['control_steps']//24,actual_environment_steps=r['actual_environment_steps'],checkpoint=r['checkpoint'],completed_segment=segments,manifest_sha256=sha(run/'run_manifest.json')))
assert sorted(x['actual_environment_steps'] for x in pref)==[6144,1920000]
diff={n:(h,f[n]) for n,h in one.items() if n in f and f[n]!=h};assert set(diff)=={'isaac/mod4/clock_training_health.py'}
write('SAME_1MS_RANGE_EVIDENCE_REUSED.json',dict(epoch=time.time(),complete_original_PPO_reused=True,preflight=pref,preflight_weights_discarded=True,no_repeat_128_or20k_preflight=True,reference206_root=str(T),reference206_source_freeze_sha256=sha(T/'reports/SOURCE_FREEZE.json'),sole_runtime_difference_from_original1ms=diff,health_v2_reviewed218_sha256=f['isaac/mod4/clock_training_health.py'],original1ms_fullresume_and15s_oldskills_source=source['checkpoint'],no_new_DR_task_or_plant_range=True))
py='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
for args,name,cwd in (([str(D/'test_health_1ms_cpu.py')],'HEALTH_1MS_CPU_PASSED.json',D),([str(D/'isaac/mod4/test_sensor_resume_actual_cpu.py'),source['checkpoint']['path']],'SOURCE24827_RESUME_CPU_PASSED.json',D/'isaac/mod4')):
 p=subprocess.run([py]+args,cwd=cwd,capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stdout+p.stderr;v=json.loads(p.stdout);assert v['passed'];write(name,v)
sys.path.insert(0,str(D));import supervise_validated_1ms_recovery as w;w.verify();assert not w.s.trainers() and w.s.q.base.budget_state()['active_segment'] is None
assert before==w.s.q.ctl.CANONICAL.read_bytes()
write('FALLBACK_CPU_SOURCE_PASSED.json',dict(epoch=time.time(),passed=True,source_count=len(f),only_env_reverted_from218=True,only_health_v2_changed_from206=True,all_old_evidence_preserved=True,no_GPU_no_PPO_no_budget_mutation=True,first_reader_error_corrected_only_from_actual_COMPLETE_schema=True))
print(json.dumps(dict(passed=True,source_count=len(f),health_contracts=read(D/'reports/HEALTH_1MS_CPU_PASSED.json')['count'],resume_contracts=read(D/'reports/SOURCE24827_RESUME_CPU_PASSED.json')['count'],reused_preflight_steps=[x['actual_environment_steps'] for x in pref])))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'FALLBACK_CPU_SOURCE_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(raw.decode())
finally:c.close()
