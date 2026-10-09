"""New isolated q-evidence restore continuation; reuse actual native/128 scope."""
from pathlib import Path
import sys,json,shlex,ast,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;N=B/'MOD4_S3_E1_RESET_EVIDENCE_REVIEW_20261009';NR=N/'reports'
assert not N.exists();NR.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
v=read(R/'E1_RESOURCE_PROGRESS_ACTUAL.json');assert v['actual_parent'] is None and v['actual_child'] is None and v['budget']['active_segment'] is None and v['Sactive'] is None
assert set(v['source_drift'])=={'isaac/mod4/train_crash.txt'} and '_rescue_reset_q' in v['train_crash_text']
files={}
for n in ('e1_reset_evidence.py','e1_reset_evidence_training_env.py','test_e1_reset_evidence_cpu.py'):files['isaac/mod4/'+n]=(D/n).read_bytes()
train=(R/'restoration_source_reads/train_e1_resource_resume_ppo.py').read_text(encoding='utf8')
needle='from e1_terrain_training_env import E1TerrainLearningEnv as Mod4Env';assert train.count(needle)==1
train=train.replace(needle,'from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv as Mod4Env')
needle='crash = REPO / "isaac" / "mod4" / "train_crash.txt"';assert train.count(needle)==1
train=train.replace(needle,'crash = Path(args.log_root).parent / (args.run_name + ".error.txt")')
files['isaac/mod4/train_e1_reset_evidence_resume_ppo.py']=train.encode()
ctl=(D/'supervise_e1_scene_query_resource_review.py').read_text(encoding='utf8').replace('train_e1_resource_resume_ppo.py','train_e1_reset_evidence_resume_ppo.py')
first=ctl.index('def wait_existing():');last=ctl.index('\ndef freeze_run(',first)
ctl=ctl[:first]+'''def wait_existing():
    previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_SCENE_QUERY_RESOURCE_REVIEW_20261009');pr=previous/'reports'
    ps=read(pr/'E1_STATE.json');att=read(pr/'E1_ATTENTION.json')
    assert att['own_child_still_alive']==False and att['active_segment'] is None
    locators=[ps['owner'],ps['child'],read(pr/'E1_GUARDIAN_STARTED.json')]
    assert all(not (x:=identity(p['pid'])) or x['state']=='Z' or x['start_ticks']!=p['start_ticks'] for p in locators)
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert read(R/'E1_RESET_EVIDENCE_CPU_PASSED.json')['passed']
    write('E1_RESET_SCHEMA_FAILURE_EXIT_AUDITED.json',dict(epoch=time.time(),previous_parent_guardian_child_actual_exit=True,old_error_and_completed_segments_retained=True,new_budget_seconds=0))

'''+ctl[last:]
first=ctl.index('def native20k(init):');last=ctl.index('\ndef train(',first)
ctl=ctl[:first]+'''def native20k(init):
    proof=read(R/'REUSED_E1_NATIVE20K_PASSED.json');compact=read(R/'REUSED_E1_NATIVE_COMPACT.json')
    assert proof['no_PPO'] and compact['checkpoint_sha256']==s.q.base.sha(init) and compact['physical_callback_count']==480 and compact['health']['actual_physics_callbacks']==576
    assert compact['E1_actual_ground_error_m']==0 and compact['E1_height_reward_formula_error']==0
    assert compact['E1_terrain_identity']['seed']==20260928 and compact['E1_terrain_identity']['partition_exact']
    write('E1_NATIVE20K_PASSED.json',dict(proof,reused_actual_native=True,no_GPU_replay=True,reuse_reason='Only independently requested reset-q audit metadata and failed-log destination change; actual ground/plant/configure/native source exact. Real new20k restore must still pass.'))

'''+ctl[last:]
needle="for count,updates in ((128,2),(20000,4)):\n        _,row=train(init,count,updates,900,'e1_discard_'+str(count),True);pre.append(row)"
assert needle in ctl
ctl=ctl.replace(needle,"row=read(R/'REUSED_E1_DISCARD128_PASSED.json');assert row['discarded_preflight'] and row['actual_environment_steps']==6144 and row['health']['actual_physics_callbacks']==192 and len(row['unique_completed_segment'])==1\n    write('e1_discard_128_PASSED.json',dict(row,reused_actual128=True,no_PPO_replay=True,original_root_301_scope=True));pre.append(row)\n    _,row=train(init,20000,4,900,'e1_discard_20000',True);pre.append(row)")
ctl=ctl.replace("assert read(R/'E1_FULL_TARGET_CPU_PASSED.json')['passed']","assert read(R/'E1_FULL_TARGET_CPU_PASSED.json')['passed']\n    assert read(R/'E1_RESET_EVIDENCE_CPU_PASSED.json')['passed']")
files['supervise_e1_reset_evidence_review.py']=ctl.encode()
for n,b in files.items():ast.parse(b.decode());p=N/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+N.name;old='/home/egde/rl_candidates/'+D.name;d7='/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009'
try:
 code=r'''
from pathlib import Path
import json,hashlib,shutil
D=Path(ROOT);OLD=Path(OLDROOT);D7=Path(D7ROOT);assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==301
for n,h in f.items():
 p=OLD/n
 if n=='isaac/mod4/train_crash.txt':
  shutil.copy2(p,D/'reports/PREDECESSOR_RESUME_FAILURE_TRAIN_CRASH_RETAINED.txt');p=D7/n
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
 out=D/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for n in ('SELECTED_E0_FOR_E1_BEHAVIOR_SOURCE.json','E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json','E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json','E1_FULL_TARGET_CPU_PASSED.json','NEXT_S3_E1_FULL_LEARNING_WORK_ORDER.json','D9_RETENTION18_ACTUAL_REVIEW.json'):shutil.copy2(OLD/'reports'/n,D/'reports'/n)
for a,b in (('E1_NATIVE20K_PASSED.json','REUSED_E1_NATIVE20K_PASSED.json'),('e1_discard_128_PASSED.json','REUSED_E1_DISCARD128_PASSED.json'),('E1_ATTENTION.json','PREDECESSOR_E1_ATTENTION_RETAINED.json')):shutil.copy2(OLD/'reports'/a,D/'reports'/b)
print('copied301 original expected bytes exact; previous writable diagnostic retained separately')
'''.replace('OLDROOT',repr(old)).replace('D7ROOT',repr(d7)).replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n,b in files.items():sf.put(str(N/n),root+'/'+n);assert sf.open(root+'/'+n).read()==b
  compact=NR/'REUSED_E1_NATIVE_COMPACT.json';compact.write_text(json.dumps(v['native_compact'],indent=2),encoding='utf8');sf.put(str(compact),root+'/reports/'+compact.name)
  sf.put(str(R/'E1_RESET_RESTORE_FAILED_SEGMENTS_AUDITED.json'),root+'/reports/E1_RESET_RESTORE_FAILED_SEGMENTS_AUDITED.json')
 code=r'''
from pathlib import Path
import sys,json,hashlib,ast,time,torch,subprocess
D=Path(ROOT);OLD=Path(OLDROOT);R=D/'reports';torch.set_num_threads(1)
out=subprocess.check_output([sys.executable,str(D/'isaac/mod4/test_e1_reset_evidence_cpu.py')],text=True)
assert 'CPU6' in out and not torch.cuda.is_initialized();(R/'E1_RESET_EVIDENCE_CPU_PASSED.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,tests=6,no_CUDA_initialized=True,output=out,bookkeeping_only_no_plant_setter=True),indent=2))
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());f['candidate_root']=str(D);f['epoch']=time.time()
for n,h in f['sha256'].items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h
for n in NEW:ast.parse((D/n).read_text());f['sha256'][n]=hashlib.sha256((D/n).read_bytes()).hexdigest()
f['source_count']=len(f['sha256']);assert f['source_count']==306;f['all_original_expected301_source_bytes_exact']=True;f['old_mutable_diagnostic_retained_separately']=True
(R/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2));sys.path.insert(0,str(D));import supervise_e1_reset_evidence_review as w
w.verify();w.wait_existing();src=w.source();assert not torch.cuda.is_initialized();assert not (R/'E1_LAUNCHED.json').exists();before=w.s.q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/'supervise_e1_reset_evidence_review.py')],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
ident=w.identity(p.pid);assert ident and ident['argv'][1]==str(D/'supervise_e1_reset_evidence_review.py')
row=dict(epoch=time.time(),parent=ident,source=w.fullsave(src,require_e1=False),source_count=306,new_files=NEW,old_schema_failure_exited_and_segments_retained=True,native_and128_actual_scope_reused=True,new20k_complete_restore_then_PPO_required=True,new_budget_seconds=0,first_new_terrain_task_seconds=2700,repeated_clock45min=False,budget_bytes_exact_at_dispatch=before==w.s.q.ctl.CANONICAL.read_bytes())
w.write('E1_RESET_EVIDENCE_DISPATCH_LAUNCHED.json',row);print(json.dumps(row))
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root)).replace('NEW',repr(list(files)))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('SOURCE_FREEZE.json','E1_RESET_EVIDENCE_CPU_PASSED.json','E1_RESET_EVIDENCE_DISPATCH_LAUNCHED.json','REUSED_E1_NATIVE20K_PASSED.json','REUSED_E1_DISCARD128_PASSED.json'):sf.get(root+'/reports/'+n,str(NR/n))
 print(raw.decode())
finally:c.close()
