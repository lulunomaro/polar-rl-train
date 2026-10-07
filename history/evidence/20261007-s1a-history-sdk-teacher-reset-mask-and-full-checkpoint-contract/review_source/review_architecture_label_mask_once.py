"""CPU-test the explicit reset teacher mask before any new architecture worker."""
from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'ARCHITECTURE_LABEL_REVIEW.json').exists()
s=(D/'history_actor_ppo.py').read_text(encoding='utf8')
anchor='class HistoryActor(MLPModel):'
helper="""def masked_velocity_loss(history,encoder,label,valid):
    if valid.shape!=(history.shape[0],1) or not bool(((valid==0)|(valid==1)).all()):
        raise ValueError('Explicit per-sample reset validity required')
    selected=valid[:,0].bool()
    if not bool(selected.any()):return None
    return supervised_velocity_loss(history[selected],encoder,label[selected])

"""+anchor
assert anchor in s;s=s.replace(anchor,helper,1)
old="loss=supervised_velocity_loss(batch['feedback_history'],self.actor.encoder,batch['body_velocity_label'])"
new="loss=masked_velocity_loss(batch['feedback_history'],self.actor.encoder,batch['body_velocity_label'],batch['body_velocity_valid'])\n                if loss is None:continue"
assert old in s;s=s.replace(old,new,1)
s=s.replace("original_optimizer_restored=False,A2_auxiliary_supervision=False)","original_optimizer_restored=False,A2_auxiliary_supervision=False,reset_teacher_mask_required=True)",1)
(D/'history_actor_label_ppo.py').write_text(s,encoding='utf8')
t=(D/'test_history_actor_rng_review.py').read_text(encoding='utf8')
t=t.replace('from history_actor_ppo import HistoryActor,HistoryPPO','from history_actor_label_ppo import HistoryActor,HistoryPPO,masked_velocity_loss',1)
t=t.replace("body_velocity_label=torch.randn(128,3)","body_velocity_label=torch.randn(128,3),body_velocity_valid=torch.ones(128,1)",1)
anchor=" actor.zero_grad();actor(obs).sum().backward()"
extra=""" valid=torch.ones(128,1);valid[::3]=0
 labels=obs['body_velocity_label'].clone();altered=labels.clone();altered[::3]=1000
 loss1=masked_velocity_loss(obs['feedback_history'],actor.encoder,labels,valid)
 loss2=masked_velocity_loss(obs['feedback_history'],actor.encoder,altered,valid)
 assert torch.equal(loss1,loss2) and masked_velocity_loss(obs['feedback_history'],actor.encoder,labels,valid*0) is None
 tests.append(variant+'_reset_teacher_values_excluded_exactly')
"""+anchor
assert anchor in t;t=t.replace(anchor,extra,1)
(D/'test_history_teacher_mask.py').write_text(t,encoding='utf8')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sftp:
  for n in ('history_actor_label_ppo.py','test_history_teacher_mask.py'):sftp.put(str(D/n),'/home/egde/rl_candidates/MOD4_S1A_HISTORY_ARCHITECTURE_20261007/'+n)
 code=r'''
from pathlib import Path
import sys,json,subprocess,time
D=Path('/home/egde/rl_candidates/MOD4_S1A_HISTORY_ARCHITECTURE_20261007');R=D/'reports'
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007');sys.path.insert(0,str(N))
import continue_clock1000_worker_manifest_review_once as q;q.verify()
assert not (R/'ARCHITECTURE_LABEL_REVIEW.json').exists()
old=q.w.read(R/'ARCHITECTURE_RNG_REVIEW.json');assert old['passed']
for n,h in old['sha256'].items():assert q.base.sha(D/n)==h,n
before=q.ctl.CANONICAL.read_bytes()
test=subprocess.run([q.base.PY,str(D/'test_history_teacher_mask.py'),str(q.SOURCE)],cwd=D,capture_output=True,text=True)
(R/'ARCHITECTURE_LABEL_REVIEW_LOG.txt').write_text(test.stdout+test.stderr)
assert q.ctl.CANONICAL.read_bytes()==before
v=dict(epoch=time.time(),root=str(D),returncode=test.returncode,canonical_bytes_exact=True,GPU_probe_count=0,actual_task_PPO_updates=0,
 synthetic_CPU_optimizer_fixture_only=True,original_five_sources_unchanged=True,source_count=7,
 sha256={n:q.base.sha(D/n) for n in set(old['sha256'])|{'history_actor_label_ppo.py','test_history_teacher_mask.py'}})
if test.returncode==0:v['result']=json.loads(test.stdout.strip().splitlines()[-1]);v['passed']=True
else:v['passed']=False;v['error_tail']=test.stderr[-3000:]
q.base.atomic_json(R/'ARCHITECTURE_LABEL_REVIEW.json',v);print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'ARCHITECTURE_LABEL_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
 with c.open_sftp() as s:s.get('/home/egde/rl_candidates/MOD4_S1A_HISTORY_ARCHITECTURE_20261007/reports/ARCHITECTURE_LABEL_REVIEW_LOG.txt',str(R/'ARCHITECTURE_LABEL_REVIEW_LOG.txt'))
finally:c.close()
