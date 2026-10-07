"""Isolated exact 1ms fallback plus already-reviewed health v2; no GPU launch here."""
from pathlib import Path
import sys,json,ast,shlex
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
controller=D/'supervise_validated_1ms_recovery.py';ast.parse(controller.read_text())
cpu=(D.parent/'MOD4_EPISODE_SUPERVISION_REPAIR_20261007/test_episode_health_cpu.py').read_text()
assert cpu.count('self.physics_dt=.0025')==1 and cpu.count('tick+=4')==1
cpu=cpu.replace('self.physics_dt=.0025','self.physics_dt=.001').replace('tick+=4','tick+=10')
(D/'test_health_1ms_cpu.py').write_text(cpu,encoding='utf8');ast.parse(cpu)
c=connect()
try:
 code=r'''
from pathlib import Path
import json,shutil,hashlib,time
OLD=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');D=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008')
assert not D.exists();D.mkdir();(D/'reports').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];one=read(T/'reports/SOURCE_FREEZE.json')['sha256']
for n,h in f.items():
 assert sha(OLD/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
for n,h in one.items():assert sha(T/n)==h,n
shutil.copy2(T/'isaac/mod4/env.json',D/'isaac/mod4/env.json')
print(json.dumps(dict(staged_original218=True,original1ms_env_exact=True,no_GPU_or_PPO=True)))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 with c.open_sftp() as sf:
  for n in ('supervise_validated_1ms_recovery.py','test_health_1ms_cpu.py'):sf.put(str(D/n),ROOT+'/'+n)
  sf.put(str(R/'FAILURE_AND_FALLBACK_BOUNDARY.json'),ROOT+'/reports/FAILURE_AND_FALLBACK_BOUNDARY.json')
 code=r'''
from pathlib import Path
import sys,json,hashlib,subprocess,time,ast
D=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008');OLD=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda n,v:(D/'reports'/n).write_text(json.dumps(v,indent=2))
src=(OLD/'supervision_sdk_probe.py').read_text()
replacements={'args.dt==.0025':'args.dt==.001','os.environ["RM_SOLVER_POS"]=="32"':'os.environ["RM_SOLVER_POS"]=="16"','x==(32,4)':'x==(16,4)','<=32<=':'<=16<=','all_position32_velocity4=True':'all_position16_velocity4=True','solver32_training_test_physical_admission=True':'validated1ms_health_boundary_admission=True'}
for a,b in replacements.items():assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b)
compile(src,'health_1ms_sdk_probe.py','exec');(D/'health_1ms_sdk_probe.py').write_text(src)
f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];f['isaac/mod4/env.json']=sha(D/'isaac/mod4/env.json')
for n in ('supervise_validated_1ms_recovery.py','test_health_1ms_cpu.py','health_1ms_sdk_probe.py'):f[n]=sha(D/n)
one=read(T/'reports/SOURCE_FREEZE.json')['sha256'];differences={n:(h,f[n]) for n,h in one.items() if n in f and f[n]!=h};assert set(differences)=={'isaac/mod4/clock_training_health.py'},differences
write('SOURCE_FREEZE.json',dict(sha256=f,source_count=len(f),original1ms_runtime_except_health_v2_exact=True,original218_except_env_exact=True,old_copied_controllers_forbidden_entry=True))
audit=read(D/'reports/FAILURE_AND_FALLBACK_BOUNDARY.json');source=audit['fallback']['validated24827'];assert source['cpu']['sha256']=='5abd2a912f5c717849c25de09448581c226e6c9e79581f4a44e0e4a8f27261c1'
write('VALIDATED_SOURCE.json',dict(epoch=time.time(),checkpoint=source['cpu'],own_receipt=source['receipt'],own_health=source['health'],own_manifest=source['manifest'],own_freeze=source['freeze'],selection='Actual full1ms healthy2h and matched retention; no failed/highest/preflight source selected'))
E=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007/reports');pref=[]
for p in E.glob('*PASSED.json'):
 r=read(p)
 if r.get('discarded_preflight') and r.get('health',{}).get('physics_dt_s')==.001:
  assert r['health']['actual_task_reset_events']==0 and r['health']['actual_physics_callbacks']==r['health']['expected_physics_callbacks']
  assert r['health']['max_closure_error_m']<=.002 and r['checkpoint']['finite_tensors']==74
  pref.append(dict(receipt_path=str(p),receipt_sha256=sha(p),actual_updates=r['actual_updates'],actual_environment_steps=r['actual_environment_steps'],checkpoint=r['checkpoint'],completed_segment=r['unique_completed_segment']))
assert sorted(x['actual_environment_steps'] for x in pref)==[6144,1920000],pref
write('SAME_1MS_RANGE_EVIDENCE_REUSED.json',dict(epoch=time.time(),complete_original_PPO_reused=True,preflight=pref,preflight_weights_discarded=True,no_repeat_128_or20k_preflight=True,reference206_root=str(T),reference206_source_freeze_sha256=sha(T/'reports/SOURCE_FREEZE.json'),sole_runtime_difference_from_original1ms=diff if False else differences,health_v2_reviewed218_sha256=f['isaac/mod4/clock_training_health.py'],original1ms_fullresume_and15s_oldskills_source=source['cpu'],no_new_DR_task_or_plant_range=True))
py='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
for args,name,cwd in (([str(D/'test_health_1ms_cpu.py')],'HEALTH_1MS_CPU_PASSED.json',D),([str(D/'isaac/mod4/test_sensor_resume_actual_cpu.py'),source['cpu']['path']],'SOURCE24827_RESUME_CPU_PASSED.json',D/'isaac/mod4')):
 p=subprocess.run([py]+args,cwd=cwd,capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stdout+p.stderr;v=json.loads(p.stdout);assert v['passed'];write(name,v)
sys.path.insert(0,str(D));import supervise_validated_1ms_recovery as w;w.verify();assert not w.s.trainers() and w.s.q.base.budget_state()['active_segment'] is None
write('FALLBACK_CPU_SOURCE_PASSED.json',dict(epoch=time.time(),passed=True,source_count=len(f),only_env_reverted_from218=True,only_health_v2_changed_from206=True,all_old_evidence_preserved=True,no_GPU_no_PPO_no_budget_mutation=True))
print(json.dumps(dict(passed=True,source_count=len(f),reused_preflight_steps=[x['actual_environment_steps'] for x in pref],source=source['cpu'],controller_CPU_guard_passed=True)))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read()
 if o.channel.recv_exit_status()!=0:
  (R/'FIRST_STAGING_READER_ERROR.txt').write_bytes(raw+err);raise RuntimeError((raw+err).decode())
 v=json.loads(raw);(R/'STAGING_CPU_SOURCE_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(raw.decode())
finally:c.close()
