"""One isolated, frozen S0P native benchmark; no training or ledger writes."""
from pathlib import Path
import json,os,subprocess,time,traceback
import supervise_world_spin as w
D=Path(__file__).resolve().parent;R=D/'reports'
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports')
P=w.P;B=w.ctl.CANONICAL;PY=w.base.PY
SOURCE=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt')
SOURCE_SHA='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
def write(n,v):w.base.atomic_json(R/n,v)
def verify():
 a=w.read(E/'PLAN_APPROVAL.json');assert a['approved'] and a['version']=='1.4' and 'S0P' in a['allowed_stages']
 assert w.base.sha(E/'MOD4_MOE_MASTER_PLAN.md')==a['approved_plan_sha256']
 b=w.base.budget_state();assert b['authorized_training_seconds']==828000 and b['owner_root']==str(P)
 assert not b['active_segment'] and not w.read(w.ctl.STATE_PATH).get('active_training')
 assert w.base.sha(SOURCE)==SOURCE_SHA
 for n,h in w.read(R/'SOURCE_FREEZE.json')['sha256'].items():assert w.base.sha(D/n)==h,n
 for pid in [670475,671176,671219]:
  row=w.helpers.identity(pid);assert not row or row['state']=='Z','Previous A0 owner/child still live'
 assert w.read(Path('/home/egde/rl_candidates/MOD4_MOE_A0_E0_PARALLEL_20261007/reports/A0_SAVED_REVIEW_READY.json'))['checkpoint']['sha256']=='b9973a402c1ef48f3aa68ed3573d371b62059c08f3faf131086ec1866b71755b'
def main():
 assert not (R/'BENCHMARK_STARTED.json').exists(),'Unique benchmark already executed'
 w.helpers.acquire(P/'autonomy_controller.lock');w.helpers.acquire(B.parent/'native_floor_supervisor.lock');verify()
 before=B.read_bytes();owner=w.helpers.identity(os.getpid());results=w.read(R/'BASELINE_REUSED.json')
 write('BENCHMARK_STARTED.json',dict(epoch=time.time(),owner=owner,source=str(SOURCE),source_sha256=SOURCE_SHA,scope='S0P frozen native timestep throughput',PPO_updates=0))
 for dt in [.001,.0025,.005]:
  verify();name='dt_'+str(int(dt*1000000))+'us';out=R/(name+'.json');log=D/(name+'.log')
  cmd=[PY,str(D/'physics_speed_probe.py'),'--headless','--dt',str(dt),'--checkpoint',str(SOURCE),'--output',str(out),'--num_envs','20000','--warmup','24','--steps','120','--profile_steps','8']
  with log.open('x') as f:
   child=subprocess.Popen(cmd,cwd=P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   write('BENCHMARK_STATE.json',dict(phase='frozen_native_timestep_probe',epoch=time.time(),owner=owner,child=w.helpers.identity(child.pid),dt=dt,output=str(out),log=str(log)))
   rc=child.wait(timeout=900)
  assert B.read_bytes()==before,'Frozen probe must not change canonical budget'
  if out.with_suffix(out.suffix+'.error').exists() or not out.exists():raise RuntimeError('Native probe failed: '+str(out)+', rc='+str(rc))
  row=w.read(out);assert rc==0 and row['phase']=='complete' and row['frozen_policy_only'] and row['PPO_update_count']==0
  assert abs(row['actual_step_dt']-.01)<1e-12 and row['physical_callback_count']==row['expected_callback_count']
  assert row['checkpoint_sha256']==SOURCE_SHA
  item={k:row[k] for k in ['actual_physics_dt','actual_step_dt','decimation','environment_policy_steps_per_second','steady_wall_seconds','actual_task_failed_environments','nonfinite','max_closure_error_m','max_mimic_error_rad','host_submission_seconds','cuda_event_seconds']}
  item.update(output=str(out),output_sha256=w.base.sha(out),physics_health_eligible=not row['nonfinite'] and row['actual_task_failed_environments']==0 and row['max_closure_error_m']<=.002 and row['max_mimic_error_rad']<=.01)
  results.append(item);write('BENCHMARK_RESULTS_PARTIAL.json',results)
 write('BENCHMARK_REVIEW_READY.json',dict(epoch=time.time(),results=results,canonical_bytes_exact=True,production_timestep_changed=False,behavior_and_PPO_validation_required=True))
 write('BENCHMARK_STATE.json',dict(phase='physics_speed_review_ready',epoch=time.time(),results=results,child=None,canonical_bytes_exact=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('BENCHMARK_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_budget_mutation=True));raise
