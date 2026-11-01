"""One isolated, no-PPO SDK verification. Never rerun an existing attempt."""
import hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
D=Path(__file__).resolve().parent;P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CODE=D/'isaac/mod4';R=D/'reports';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
sys.path.insert(0,str(P/'isaac/mod4'))
import supervise_autonomy as ctl
base,helpers=ctl.base,ctl.helpers
sys.path.insert(0,str(CODE))
from scut_curriculum_gate_v4 import evidence
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phase(name,**kw):base.atomic_json(R/'SDK_VERIFICATION_STATE.json',dict(phase=name,updated_epoch=time.time(),**kw))
def runtime():
 e={k:v for k,v in os.environ.items() if not k.startswith('RM_')};e.update({k:str(v) for k,v in read(CODE/'env.json').items()})
 e.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1');return e
def main():
 assert not (R/'SDK_VERIFICATION_STATE.json').exists(),'Attempt already started: inspect, do not rerun'
 import torch;torch.set_num_threads(1)
 helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 ctl.idle();assert not ctl.S.get('active_training')
 hand=read(R/'PREPARED.json');final=read(P/'reports/AUTONOMY_FINISHED.json')
 assert final['target_2rev_s_confirmed'] and sha(P/'reports/AUTONOMY_FINISHED.json')==hand['spin_final_sha256']
 for old in hand['retired_processes']:assert helpers.identity(old['pid']) is None
 for n,h in read(R/'SOURCE_FREEZE.json')['sha256'].items():assert sha(D/n)==h,n
 ck=Path(final['checkpoint']['path']);assert base.checkpoint(ck)==final['checkpoint']
 assert base.budget_state()['authorized_training_seconds']==324000
 ledger=ctl.CANONICAL.read_bytes();assert not base.budget_state()['active_segment']
 base.STATE.update(read(P/'status.json'))
 phase('cpu_then_actual_sdk_readback',source=final['checkpoint'],no_PPO=True)
 for name in ['test_directional_runtime.py','test_world_cycle_metrics.py']:
  with (R/(name+'.log')).open('x') as log:
   rc=subprocess.call([PY,str(CODE/name)],cwd=CODE,env=runtime(),stdout=log,stderr=subprocess.STDOUT)
  assert rc==0,name
 reports=[]
 for suffix,extra in [('automatic',[]),('manual_reference',['--manual-reference'])]:
  out=R/('sdk_short_'+suffix+'.json');assert not out.exists()
  with out.with_suffix('.log').open('x') as log:
   child=subprocess.Popen([PY,str(CODE/'world_spin_probe.py'),'--headless','--contact-readback','--checkpoint',str(ck),'--steps','300','--num_envs','22','--max-rate','12.566370614359172','--dr-profile','white_v2','--seed','20261002','--output',str(out),*extra],cwd=P,env=runtime(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  phase('actual_sdk_'+suffix,source=final['checkpoint'],child=helpers.identity(child.pid),output=str(out),no_PPO=True)
  base.status(stage='world_spin_sdk_readback',supervisor_pid=os.getpid(),training_pid=None,evaluation_pid=child.pid,active_log=str(out.with_suffix('.log')),active_code_root=str(D),world_progress_goal_m_s=.15,spin_stage_finished=True)
  report=base.wait_probe(child,out);a=evidence(report,'spin',3)
  assert a['pass_'],a
  assert report['command_observation_error']<1e-6 and report['reward_readback_error']<1e-4
  reports.append(report)
 exact={k:reports[0][k]==reports[1][k] for k in ['reset_joint_pos_before_physics','reset_root_before_physics','initial_parameter_audit','final_parameter_audit','per_environment','alive','first_failure_step','group_ids','world_cycle_metrics']}
 assert all(exact.values()),exact
 assert ctl.CANONICAL.read_bytes()==ledger,'Frozen SDK checks must not charge PPO'
 receipt=dict(pass_=True,source=final['checkpoint'],initial_and_behaviour_exact=exact,actual_command_observation_and_reward_readback=True,steps=300,seconds=3,num_envs_each=22,automatic_and_reference_survivors=44,ledger_bytes_exact=True,production_training_started=False,complete_cycle_skill_accepted=False)
 base.atomic_json(R/'SDK_READBACK_PASSED.json',receipt)
 phase('sdk_readback_passed_pending_complete_cycle_and_retention',**receipt)
 base.status(stage='world_spin_candidate_ready',training_pid=None,evaluation_pid=None,validation_pid=None,latest_sdk_readback=receipt)
if __name__=='__main__':
 try:main()
 except BaseException:
  base.atomic_json(R/'SDK_VERIFICATION_ERROR.json',dict(error=traceback.format_exc(),at=time.time(),instructions='Preserve this attempt. Do not restart entry or clear canonical. No PPO authorized by a failed readback.'))
  phase('sdk_verification_attention_required',error=traceback.format_exc());raise
