"""Explicit frozen-only reader correction with exact reuse of all completed anchor/SDK evidence."""
from pathlib import Path
import sys,json,time,os,subprocess,traceback
D=Path(__file__).resolve().parent;R=D/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_S1A_FROZEN_EVAL_CONTROLLER_20261007')
sys.path.insert(0,str(D));import supervise_frozen_matched_replay_once as prior
q=prior.q;LIVE=None
def write(n,v):q.q.base.atomic_json(R/n,v)
def verify():
 prior.verify()
 assert not q.q.helpers.identity(q.q.w.read(OLD/'reports/FROZEN_MATCHED_REPLAY_LAUNCHED.json')['owner']['pid'])
 s=q.q.w.read(OLD/'reports/FROZEN_MATCHED_REPLAY_STATE.json');assert not q.q.helpers.identity(s['child']['pid'])
def admission(raw,kind):
 sys.path.insert(0,str(D/'isaac/mod4'));import scut_curriculum_gate_v4 as g
 # World probe intentionally uses the established spin/contact data schema.
 v=g.evidence(raw,'spin' if kind=='world' else kind,minimum_seconds=15);assert v['pass_'],v
 if kind=='world':
  from world_progress_contract import target
  v=dict(v,world_target=target(raw,.5))
 return v
def run(variant,kind,source,count):
 global LIVE
 verify();job='behavior_'+variant+'_'+kind;output=R/(job+'.json');log=D/(job+'.log');assert not output.exists() and not log.exists()
 env=q.q.w.runtime();env['PYTHONPATH']=str(D)+os.pathsep+str(D/'isaac/mod4')
 args=[q.q.base.PY,str(D/'isaac/mod4'/('frozen_history_'+kind+'.py')),'--headless','--checkpoint',str(source),'--output',str(output),
  '--steps','1500','--num_envs',str(count),'--seed','20261002','--dr-profile','white_v3']
 args+=['--speed_limit','1.5','--ramp_suite'] if kind=='flat' else ['--max-rate','12.566370614359172','--contact-readback']
 start=time.time()
 with log.open('x') as f:child=subprocess.Popen(args,cwd=q.q.P,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;write('FROZEN_PROTOCOL_REVIEW_STATE.json',dict(epoch=time.time(),phase='frozen_matched_behavior_after_protocol_review',owner=q.q.helpers.identity(os.getpid()),child=q.q.helpers.identity(child.pid),variant=variant,kind=kind,output=str(output),active_log=str(log),new_learning=False))
 child.wait(timeout=1800);LIVE=None;text=log.read_text(errors='replace');assert child.returncode==0 and output.exists() and 'Traceback (most recent call last)' not in text
 raw=q.q.w.read(output);audit=raw['frozen_architecture_audit'];assert audit['variant']==variant and audit['history_advances']==1500 and audit['actual_command_error']<=1e-6 and not audit['actor_receives_teacher']
 v=admission(raw,kind);row=dict(epoch=time.time(),variant=variant,kind=kind,source=q.q.base.checkpoint(source),output=str(output),output_sha256=q.q.base.sha(output),actual_pid=child.pid,exit_code=child.returncode,process_wall_seconds=time.time()-start,admission=v,new_learning=False)
 write(job+'_COMPLETE.json',row);return row
def main():
 assert not (R/'FROZEN_PROTOCOL_REVIEW_STARTED.json').exists();verify()
 q.q.helpers.acquire(q.q.P/'autonomy_controller.lock');q.q.helpers.acquire(q.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 before=q.q.ctl.CANONICAL.read_bytes();ready=q.q.w.read(prior.B/'reports/S1A_MATCHED_HISTORY_REVIEW_READY.json')
 sdk=q.q.w.read(OLD/'reports/FROZEN_HISTORY_NATIVE_SDK_PASSED.json');assert len(sdk['receipts'])==2 and sdk['canonical_bytes_exact']
 rows=[]
 for kind in ('flat','spin','world'):
  p=OLD/'reports'/('behavior_anchor_'+kind+'.json');r=q.q.w.read(p);assert r['checkpoint']==str(q.q.SOURCE) and r['seed']==20261002 and r.get('profile',(r.get('mild_initial_parameters') or {}).get('profile'))=='white_v3' and r['steps']==1500
  v=admission(r,kind);rows.append(dict(role='anchor',kind=kind,output=str(p),output_sha256=q.q.base.sha(p),admission=v,reused_exact_completed_raw=True))
 write('FROZEN_WORLD_PROTOCOL_REVIEW.json',dict(epoch=time.time(),original_reader_attention=q.q.w.read(OLD/'reports/FROZEN_MATCHED_REPLAY_ATTENTION.json'),actual_world_spin_schema=True,original_model_and_data_gate_unchanged=True,reused_sdk=sdk,reused_anchor=rows,extra_anchor_probes=0,old219_files_exact=True,new_budget_seconds=0))
 write('FROZEN_PROTOCOL_REVIEW_STARTED.json',dict(epoch=time.time(),owner=q.q.helpers.identity(os.getpid()),new_learning=False))
 for variant in ('A0','A1','A2'):
  source=Path(ready[variant]['checkpoint']['path']);assert q.q.base.checkpoint(source)==ready[variant]['checkpoint']
  for kind,count in (('flat',80),('spin',88),('world',88)):rows.append(run(variant,kind,source,count))
 assert before==q.q.ctl.CANONICAL.read_bytes()
 write('FROZEN_MATCHED_REPLAY_READY.json',dict(epoch=time.time(),receipts=rows,canonical_bytes_exact=True,firstseed_white3_only=True,actual_policy_behavior_winner_not_selected=True))
 write('FROZEN_PROTOCOL_REVIEW_STATE.json',dict(epoch=time.time(),phase='frozen_first_matched_replay_review_ready',child=None,new_learning=False))
if __name__=='__main__':
 try:main()
 except Exception:
  write('FROZEN_PROTOCOL_REVIEW_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(LIVE and LIVE.poll() is None),no_budget_mutation=True));raise
