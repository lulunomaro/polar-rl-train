"""Prepare a new exact source branch and CPU-only dispatcher waiting for true exit."""
from pathlib import Path
import sys,json,shlex,ast,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;N=B/'MOD4_S3_E1_SCENE_QUERY_RESOURCE_REVIEW_20261009';NR=N/'reports'
assert not N.exists();NR.mkdir(parents=True)
P=B/'MOD4_S3_E1_FULL_DR_TERRAIN_PREPARE_20261009';read=lambda p:json.loads(p.read_text(encoding='utf8'))
proof=read(P/'reports/E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json');assert proof['actual_resource_setting_SDK_scope_accepted']
files={}
files['isaac/mod4/e1_scene_query_resource.py']=(P/'e1_scene_query_resource.py').read_bytes()
for old,new in (('train_e1_terrain_resume_ppo.py','train_e1_resource_resume_ppo.py'),('train_e1_terrain_fresh_preflight_ppo.py','train_e1_resource_fresh_preflight_ppo.py')):
 text=(D/'isaac/mod4'/old).read_text(encoding='utf8');needle='from e1_terrain_training_env import E1TerrainLearningEnv as Mod4Env,configure_intro'
 assert text.count(needle)==1
 files['isaac/mod4/'+new]=text.replace(needle,'from e1_terrain_training_env import E1TerrainLearningEnv as Mod4Env\nfrom e1_scene_query_resource import configure_intro').encode()
native=(D/'native_e1_terrain_probe.py').read_text(encoding='utf8');needle='from e1_terrain_training_env import E1TerrainLearningEnv as Mod4Env,configure_intro';assert native.count(needle)==1
files['native_e1_resource_probe.py']=native.replace(needle,'from e1_terrain_training_env import E1TerrainLearningEnv as Mod4Env\nfrom e1_scene_query_resource import configure_intro').encode()
ctl=(D/'supervise_e1_gentle_full_contract.py').read_text(encoding='utf8')
ctl=ctl.replace('train_e1_terrain_resume_ppo.py','train_e1_resource_resume_ppo.py').replace('train_e1_terrain_fresh_preflight_ppo.py','train_e1_resource_fresh_preflight_ppo.py').replace('native_e1_terrain_probe.py','native_e1_resource_probe.py')
first=ctl.index('def wait_existing():');last=ctl.index('\ndef freeze_run(',first)
wait='''def wait_existing():
    previous=Path('/home/egde/rl_candidates/MOD4_S3_E1_FULL_CONTRACT_20261009');pr=previous/'reports'
    att=read(pr/'E1_ATTENTION.json');assert 'TimeoutExpired' in att['error'] and att['active_segment'] is None
    assert (pr/'E1_NATIVE20K.json.error').exists() and not (previous/'discard_logs').exists() and not (previous/'learning_logs').exists()
    assert read(R/'E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json')['actual_resource_setting_SDK_scope_accepted']
    while True:
        st=read(OLD/'reports/D7_STATE.json');assert st['phase']=='E0_D7_saved_review_ready' and (OLD/'reports/D7_REVIEW_READY.json').exists()
        assert not (OLD/'reports/D7_ATTENTION.json').exists()
        ps=read(pr/'E1_STATE.json')
        locators=(st['owner'],read(OLD/'reports/D7_GUARDIAN_STARTED.json'),ps['owner'],ps['child'])
        exited=all(not (x:=identity(p['pid'])) or x['state']=='Z' or x['start_ticks']!=p['start_ticks'] for p in locators)
        if exited and not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training'):
            write('E1_PREVIOUS_FAILED_NATIVE_EXIT_AUDITED.json',dict(epoch=time.time(),previous_attention_retained=True,previous_parent_and_frozen_native_actual_exit_verified=True,PPO_previously_never_started=True,active_and_Sactive_empty=True,new_budget_seconds=0));return
        phase('waiting_actual_failed_frozen_native_exit_before_new_E1_authority',child=None,no_GPU_authority_yet=True,no_signal_to_old_process=True)
        time.sleep(15)

'''
ctl=ctl[:first]+wait+ctl[last:]
ctl=ctl.replace("assert read(R/'E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json')['actual_interface_scope_accepted']","assert read(R/'E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json')['actual_interface_scope_accepted']\n    assert read(R/'E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json')['actual_resource_setting_SDK_scope_accepted']")
files['supervise_e1_scene_query_resource_review.py']=ctl.encode()
for n,b in files.items():
 ast.parse(b.decode());p=N/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_S3_E1_SCENE_QUERY_RESOURCE_REVIEW_20261009';old='/home/egde/rl_candidates/MOD4_S3_E1_FULL_CONTRACT_20261009'
try:
 code=r'''
from pathlib import Path
import hashlib,json,shutil
D=Path(ROOT);OLD=Path(OLDROOT);assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==296
for n,h in f.items():
 assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==h
 out=D/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,out)
for n in ('SELECTED_E0_FOR_E1_BEHAVIOR_SOURCE.json','E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json','E1_FULL_TARGET_CPU_PASSED.json','NEXT_S3_E1_FULL_LEARNING_WORK_ORDER.json','D9_RETENTION18_ACTUAL_REVIEW.json'):shutil.copy2(OLD/'reports'/n,D/'reports'/n)
print(json.dumps(dict(copied296_exact=True)))
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n,b in files.items():sf.put(str(N/n),root+'/'+n);assert sf.open(root+'/'+n).read()==b
  sf.put(str(P/'reports/E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json'),root+'/reports/E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json')
 code=r'''
from pathlib import Path
import sys,json,hashlib,ast,time,torch,subprocess
D=Path(ROOT);OLD=Path(OLDROOT);R=D/'reports';torch.set_num_threads(1)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());f['candidate_root']=str(D);f['epoch']=time.time()
for n,h in f['sha256'].items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h
for n in NEW:
 ast.parse((D/n).read_text());f['sha256'][n]=hashlib.sha256((D/n).read_bytes()).hexdigest()
f['source_count']=len(f['sha256']);assert f['source_count']==301;f['all296_original_staged_bytes_exact']=True
(R/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2))
sys.path.insert(0,str(D));import supervise_e1_scene_query_resource_review as w
w.verify();src=w.source();assert not torch.cuda.is_initialized() and not w.trainers()
assert not (R/'E1_LAUNCHED.json').exists();before=w.s.q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as out:
 p=subprocess.Popen([w.s.q.base.PY,str(D/'supervise_e1_scene_query_resource_review.py')],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
ident=w.identity(p.pid);assert ident and str(D/'supervise_e1_scene_query_resource_review.py') in ident['argv']
row=dict(epoch=time.time(),parent=ident,source=w.fullsave(src,require_e1=False),source_count=301,all296_original_staged_bytes_exact=True,new_files=NEW,actual_scene_query_setting_SDK_accepted=True,no_GPU_authority_until_previous_actual_exit=True,PPO_and_budget_transactions=0,new_budget_seconds=0,native20k_then_complete_new_scope_PPO_required=True,first_genuinely_new_E1_task_seconds=2700,repeated45min_clock_trial=False,budget_bytes_exact=before==w.s.q.ctl.CANONICAL.read_bytes())
w.write('E1_RESOURCE_REVIEW_DISPATCH_LAUNCHED.json',row);print(json.dumps(dict(parent=ident,source_count=301,waiting_previous_frozen_exit=True,no_GPU_or_PPO_yet=True)))
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root)).replace('NEW',repr(list(files)))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('SOURCE_FREEZE.json','E1_RESOURCE_REVIEW_DISPATCH_LAUNCHED.json'):sf.get(root+'/reports/'+n,str(NR/n))
 (R/'E1_RESOURCE_RECOVERY_PREPARED.json').write_text(json.dumps(dict(epoch=read(NR/'E1_RESOURCE_REVIEW_DISPATCH_LAUNCHED.json')['epoch'],new_root=root,source_count=301,new_entry='supervise_e1_scene_query_resource_review.py',no_GPU_authority_until_previous_native_exit=True,all296_original_staged_bytes_exact=True),indent=2),encoding='utf8')
 print(raw.decode())
finally:c.close()
