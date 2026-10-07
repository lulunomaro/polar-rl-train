"""Approved frozen1ms SDK and matched behavioral evidence; no optimizer or budget writes."""
from pathlib import Path
import sys,json,time,os,subprocess,traceback,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
B=Path('/home/egde/rl_candidates/MOD4_S1A_HISTORY_LAUNCH_REVIEW_20261007')
sys.path.insert(0,str(B));import supervise_matched_history_launch_review_once as q
LIVE=None
def write(n,v):q.q.base.atomic_json(R/n,v)
def verify():
 q.verify()
 for n,h in q.q.w.read(R/'SOURCE_FREEZE.json')['sha256'].items():assert q.q.base.sha(D/n)==h,n
 assert not q.q.base.trainers() and q.q.base.budget_state()['active_segment'] is None
 assert not q.q.w.read(q.q.ctl.STATE_PATH).get('active_training')

def run(variant,kind,source,count,steps,sdk=False,role=None):
 global LIVE
 verify();job=('sdk' if sdk else 'behavior')+'_'+(role or variant)+'_'+kind
 output=R/(job+'.json');log=D/(job+'.log');assert not output.exists() and not log.exists()
 env=q.q.w.runtime();env['PYTHONPATH']=str(D)+os.pathsep+str(D/'isaac/mod4')
 args=[q.q.base.PY,str(D/'isaac/mod4'/('frozen_history_'+kind+'.py')),'--headless','--checkpoint',str(source),
  '--output',str(output),'--steps',str(steps),'--num_envs',str(count),'--seed','20261002','--dr-profile','white_v3']
 args+=['--speed_limit','1.5','--ramp_suite'] if kind=='flat' else ['--max-rate','12.566370614359172','--contact-readback']
 start=time.time()
 with log.open('x') as f:child=subprocess.Popen(args,cwd=q.q.P,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;write('FROZEN_MATCHED_REPLAY_STATE.json',dict(epoch=time.time(),phase='frozen_history_SDK' if sdk else 'frozen_matched_architecture_behavior',
  owner=q.q.helpers.identity(os.getpid()),child=q.q.helpers.identity(child.pid),variant=variant,kind=kind,source=q.q.base.checkpoint(source),
  output=str(output),active_log=str(log),new_learning=False))
 child.wait(timeout=1800);LIVE=None
 text=log.read_text(errors='replace');assert child.returncode==0 and output.exists() and 'Traceback (most recent call last)' not in text,('Frozen worker error',str(log))
 raw=q.q.w.read(output);assert not raw.get('nonfinite')
 audit=raw['frozen_architecture_audit'];assert audit['variant']==variant and audit['history_advances']==steps and audit['actual_command_error']<=1e-6 and not audit['actor_receives_teacher']
 if sdk:
  assert raw['resets']==0 and all(raw['per_environment']['alive']) and raw['max_closure_after_grace_m']<=.002 and raw['max_mimic_after_grace_rad']<=.01
  verdict=dict(pass_=True,only_inference_SDK_contract=True,not_formal_skill_graduation=True)
 else:
  sys.path.insert(0,str(D/'isaac/mod4'));import scut_curriculum_gate_v4 as gate
  verdict=gate.evidence(raw,kind,minimum_seconds=15);assert verdict['pass_'],verdict
 row=dict(epoch=time.time(),variant=variant,kind=kind,source=q.q.base.checkpoint(source),output=str(output),output_sha256=q.q.base.sha(output),
  actual_pid=child.pid,exit_code=child.returncode,process_wall_seconds=time.time()-start,admission=verdict,SDK_only=sdk,new_learning=False)
 write(job+'_COMPLETE.json',row);return row

def main():
 assert not (R/'FROZEN_MATCHED_REPLAY_STARTED.json').exists()
 verify();q.q.helpers.acquire(q.q.P/'autonomy_controller.lock');q.q.helpers.acquire(q.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 before=q.q.ctl.CANONICAL.read_bytes();ready=q.q.w.read(B/'reports/S1A_MATCHED_HISTORY_REVIEW_READY.json')
 assert not q.q.helpers.identity(q.q.w.read(B/'reports/S1A_HISTORY_LAUNCHED.json')['owner']['pid'])
 sources=dict(anchor=q.q.SOURCE,**{k:Path(ready[k]['checkpoint']['path']) for k in ('A0','A1','A2')})
 for k in ('A1','A2'):assert q.fullsave(sources[k])[0]==ready[k]['checkpoint']
 write('FROZEN_MATCHED_REPLAY_STARTED.json',dict(epoch=time.time(),owner=q.q.helpers.identity(os.getpid()),sources={k:q.q.base.checkpoint(v) for k,v in sources.items()},
  scope='Two3s new inference SDK then exact firstseed-white_v3 flat/spin/world anchor+A0+A1+A2',new_learning=False,source_count=219))
 sdk=[]
 for k in ('A1','A2'):sdk.append(run(k,'flat',sources[k],10,300,sdk=True))
 assert before==q.q.ctl.CANONICAL.read_bytes()
 write('FROZEN_HISTORY_NATIVE_SDK_PASSED.json',dict(epoch=time.time(),receipts=sdk,canonical_bytes_exact=True,original218_inference_sources_exact=True))
 rows=[]
 for k in ('anchor','A0','A1','A2'):
  for kind,count in (('flat',80),('spin',88),('world',88)):
   # Anchor uses the unchanged A0 architecture; role label stays independent in job identity.
   if k=='anchor':
    row=run('A0',kind,sources[k],count,1500,role='anchor');row['role']='anchor';rows.append(row)
   else:
    row=run(k,kind,sources[k],count,1500);row['role']=k;rows.append(row)
 assert before==q.q.ctl.CANONICAL.read_bytes()
 write('FROZEN_MATCHED_REPLAY_READY.json',dict(epoch=time.time(),receipts=rows,canonical_bytes_exact=True,
  actual_policy_behavior_winner_not_selected=True,firstseed_white3_only=True,original_flags_and_raw_preserved=True))
 write('FROZEN_MATCHED_REPLAY_STATE.json',dict(epoch=time.time(),phase='frozen_first_matched_replay_review_ready',child=None,new_learning=False))

if __name__=='__main__':
 try:main()
 except Exception:
  write('FROZEN_MATCHED_REPLAY_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(LIVE and LIVE.poll() is None),no_budget_mutation=True))
  raise
