"""Read-only reusable monitor; waiting is not training takeover."""
import sys,shlex
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();remote='/home/egde/rl_candidates/'+D.name
try:
    code='''import sys,time,json,re
from pathlib import Path
D=Path('/home/egde/rl_candidates/MOD4_SCUT_PERSISTENT_MIX_20261006');sys.path.insert(0,str(D))
import supervise_scut_persistent_mix as p;q=p.q;c=p.c;read=c.w.read;c.verify()
install=read(c.R/'CADENCE_INSTALL_BOUNDARY.json');launched=read(c.R/'CADENCE_LAUNCHED.json');s=read(c.w.STATE)
b=c.base.budget_state();active=b['active_segment']
def actual(saved):
 a=q.live(saved)
 if a:
  stat=(Path('/proc')/str(a['pid'])/'stat').read_text().rsplit(')',1)[1].split();a.update(ppid=int(stat[1]),session=int(stat[3]))
 return a
out=dict(epoch=time.time(),phase=s['phase'],dispatcher=actual(launched['dispatcher']),
 prior_parent=actual(install['old_parent']),prior_guardian=actual(install['old_guardian']),
 prior_trainer=actual(install['old_trainer']),guard=actual(read(c.R/'CADENCE_GUARDIAN_STARTED.json')) if (c.R/'CADENCE_GUARDIAN_STARTED.json').exists() else None,
 active=active,all_trainers=c.base.trainers(),total=b['authorized_training_seconds'],charged=b['charged_training_seconds'],
 remaining=b['authorized_training_seconds']-b['charged_training_seconds']-(max(0,time.time()-active['accounted_through_epoch']) if active else 0),
 new_training_authority_started=(c.R/'CADENCE_TRAINING_AUTHORITY_STARTED.json').exists(),source202_exact=True,
 dispatcher_log_tail=(D/'cadence_supervisor.log').read_text(errors='replace')[-1800:])
if active:
 identity=c.helpers.identity(active['pid']);assert identity and identity['cwd']==str(c.P)
 out['actual_trainer']=actual(identity);log=Path(active['log']);text=log.read_text(errors='replace');out['active_log']=str(log)
 out['active_log_tail']=text[-1800:];out['current_observed_faults']=[line for line in text.splitlines() if any(x in line for x in ('Traceback (most recent call last)','CUDA out of memory','nan tensor'))][-5:]
 paths=re.findall(r'\\[mod4-isaac\\] log_dir=(.+)',text)
 if paths:
  run=Path(paths[-1].strip());manifest=read(run/'run_manifest.json');out['run']=str(run)
  out['actual_deadline']=manifest['env'].get('RM_RESCUE_DEADLINE')
  for n,h in manifest['src_sha256'].items():assert c.base.sha(run/'src_snapshot'/n)==h
  if (run/'latest_complete.json').exists():
   latest=read(run/'latest_complete.json');assert latest['pid']==active['pid']
   out.update(own_latest_complete=latest,own_checkpoint=c.base.checkpoint(Path(latest['checkpoint'])))
  if str(c.CODE/'train_mod4_ppo.py') in identity['argv']:
   cfg=dict(manifest['env']);cfg.pop('RM_RESCUE_DEADLINE',None);assert cfg==read(c.CODE/'env.json')
   state=read(c.ctl.STATE_PATH);assert manifest['init_checkpoint_sha256']==state['active_training']['source']['sha256']
   out['own_manifest_and11_snapshots_exact']=True
   if (run/'rolling_source_freeze.json').exists():
    assert read(run/'rolling_source_freeze.json')['sha256']==read(c.w.F)['sha256'];out['own202_run_freeze_exact']=True
else:
 out['actual_eval']=actual(s.get('child'))
if (c.R/'CADENCE_REVIEW_READY.json').exists():out['review_ready']=read(c.R/'CADENCE_REVIEW_READY.json')
c.base.atomic_json(c.R/'CADENCE_CURRENT_ACTUAL.json',out);print(json.dumps(out))
'''
    _,out,err=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
    output=out.read().decode();error=err.read().decode();assert out.channel.recv_exit_status()==0,error;print(output)
    with c.open_sftp() as s:
        s.get(remote+'/reports/CADENCE_CURRENT_ACTUAL.json',str(D/'reports/CADENCE_CURRENT_ACTUAL.json'))
        for n in ('SCUT_CADENCE_STATE.json','CADENCE_HANDOVER_ACCEPTED.json','CADENCE_GUARDIAN_STARTED.json','CADENCE_TRAINING_AUTHORITY_STARTED.json','CADENCE_REVIEW_READY.json'):
            try:s.get(remote+'/reports/'+n,str(D/'reports'/n))
            except FileNotFoundError:pass
finally:c.close()
