"""Explicit reset-frame label validity, without changing the old actor/critic/plant."""
from pathlib import Path
import sys,shlex,json,ast
D=Path(__file__).resolve().parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_S1A_HISTORY_LABEL_LIFECYCLE_20261007'
OLD='/home/egde/rl_candidates/MOD4_S1A_HISTORY_SDK_FRAME_REVIEW_20261007'
assert not (R/'HISTORY_LABEL_REVIEW_LAUNCHED.json').exists()
s=(D/'history_sdk_frame_probe.py').read_text(encoding='utf8')
s=s.replace('from history_observation_adapter import HistoryObservationAdapter,tensor','from history_label_adapter import LabelHistoryAdapter\nfrom history_observation_adapter import tensor',1)
s=s.replace('vec=HistoryObservationAdapter(inner)','vec=LabelHistoryAdapter(inner)',1)
old="""        stats['body_velocity_frame_error']=max(stats['body_velocity_frame_error'],float((label-independent).abs().max()))
        stats['critic_velocity_scale_error']=max(stats['critic_velocity_scale_error'],float((current['critic'][:,7:10]-.5*label).abs().max()))"""
new="""        valid=current['body_velocity_valid'][:,0].bool()
        if valid.any():
            stats['body_velocity_frame_error']=max(stats['body_velocity_frame_error'],float((label[valid]-independent[valid]).abs().max()))
            stats['critic_velocity_scale_error']=max(stats['critic_velocity_scale_error'],float((current['critic'][valid,7:10]-.5*label[valid]).abs().max()))
        assert torch.equal(valid,torch.tensor([True]*env.num_envs,device=env.device)) or bool((label[~valid]==0).all())"""
assert old in s;s=s.replace(old,new,1)
s=s.replace("samples.append(dict(tick=int(env.common_step_counter),label=obs['body_velocity_label'].cpu().tolist(),","samples.append(dict(tick=int(env.common_step_counter),teacher_valid=obs['body_velocity_valid'].cpu().tolist(),label=obs['body_velocity_label'].cpu().tolist(),",1)
s=s.replace("initial_parameters=initial_params,final_parameters=parameter_audit(env)","reset_frames_teacher_invalid=True,first_next_physics_frame_teacher_valid=True,old_critic38_unchanged=True,\n      initial_parameters=initial_params,final_parameters=parameter_audit(env)",1)
# Explicitly exercise every reset validity bit, not a percentage condition.
anchor="            stats['reset_other_rows_error']=max"
s=s.replace(anchor,"            assert not obs['body_velocity_valid'][ids].any() and obs['body_velocity_valid'][keep].all()\n"+anchor,1)
anchor="        check(obs)\n        if i in (75,150,225):"
s=s.replace(anchor,"        assert obs['body_velocity_valid'].all(), 'Normal following physical frame must be valid'\n"+anchor,1)
(D/'history_teacher_lifecycle_probe.py').write_text(s,encoding='utf8');ast.parse(s)
ctl=(D/'supervise_history_sdk_once.py').read_text(encoding='utf8')
ctl=ctl.replace("D/'history_sdk_probe.py'","D/'history_teacher_lifecycle_probe.py'")
ctl=ctl.replace("('history_sdk_probe.py','history_observation_adapter.py'","('history_teacher_lifecycle_probe.py','history_label_adapter.py','history_observation_adapter.py'")
anchor="    before=q.ctl.CANONICAL.read_bytes()"
new=anchor+"""
    old=Path('/home/egde/rl_candidates/MOD4_S1A_HISTORY_SDK_FRAME_REVIEW_20261007')
    attention=q.w.read(old/'reports/HISTORY_SDK_ATTENTION.json');assert attention['active_segment'] is None
    prior=q.w.read(old/'reports/history_sdk.json')
    assert prior['actual_task_failed_environments']==0 and prior['statistics']['initial_actor_action_error']==0
    assert not q.helpers.identity(q.w.read(old/'reports/HISTORY_SDK_LAUNCHED.json')['owner']['pid'])
    assert not q.helpers.identity(q.w.read(old/'reports/HISTORY_SDK_CURRENT.json')['child']['pid'])
    write('TEACHER_RESET_LIFECYCLE_REVIEW.json',dict(epoch=time.time(),previous_error=attention,
      original_frozen_report=prior,explicit_reset_frame_label_mask=True,teacher_loss_must_honor_mask=True,
      original_manager_policy35_critic38_plant_and_reset_unchanged=True,canonical_bytes_exact=True))
"""
assert anchor in ctl;ctl=ctl.replace(anchor,new,1)
(D/'supervise_teacher_lifecycle_review_once.py').write_text(ctl,encoding='utf8');ast.parse(ctl)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sf:
  try:sf.stat(ROOT);raise AssertionError('Named label lifecycle review already exists')
  except FileNotFoundError:pass
  sf.mkdir(ROOT);sf.mkdir(ROOT+'/reports');sf.mkdir(ROOT+'/new_changes')
  for n in ('history_label_adapter.py','history_teacher_lifecycle_probe.py','supervise_teacher_lifecycle_review_once.py'):sf.put(str(D/n),ROOT+'/new_changes/'+n)
 code=r'''
from pathlib import Path
import sys,shutil,json,subprocess,time
D=Path('ROOT');OLD=Path('OLD');R=D/'reports'
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007');sys.path.insert(0,str(N))
import continue_clock1000_worker_manifest_review_once as q;q.verify()
assert not q.base.trainers() and q.base.budget_state()['active_segment'] is None
f=q.w.read(OLD/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==199
for n,h in f['sha256'].items():
 assert q.base.sha(OLD/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
for n in ('HISTORY_SDK_ATTENTION.json','history_sdk.json','history_sdk.json.error','HISTORY_NATIVE_FRAME_REVIEW.json'):
 shutil.copy2(OLD/'reports'/n,R/('PREVIOUS_'+n))
changes=['history_label_adapter.py','history_teacher_lifecycle_probe.py','supervise_teacher_lifecycle_review_once.py']
for n in changes:shutil.copy2(D/'new_changes'/n,D/n)
sources={n:q.base.sha(D/n) for n in set(f['sha256'])|set(changes)};assert len(sources)==202
q.base.atomic_json(R/'SOURCE_FREEZE.json',dict(sha256=sources,original199_byte_exact=True,changes=changes,
 scope='New training-only validity mask for reset-frame derived velocity cache; old manager/plant bytes unchanged'))
before=q.ctl.CANONICAL.read_bytes()
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/'supervise_teacher_lifecycle_review_once.py')],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=q.helpers.identity(p.pid),root=str(D),source_count=202,original199_byte_exact=True,no_new_PPO=True)
q.base.atomic_json(R/'HISTORY_SDK_LAUNCHED.json',v);assert q.ctl.CANONICAL.read_bytes()==before
print(json.dumps(v))
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")").replace("Path('OLD')","Path("+repr(OLD)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'HISTORY_LABEL_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
