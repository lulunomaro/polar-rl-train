"""CPU-only S0E result adjudication. Never launches GPU work or writes the canonical ledger."""
from pathlib import Path
import fcntl,hashlib,json,time,os,importlib.util,traceback
ROOT=Path(__file__).resolve().parent;R=ROOT/'reports';Q=ROOT/'eval_queue';RESULTS=ROOT/'eval_results'
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
C=Path('/home/egde/rl_candidates/MOD4_CONTINUOUS_MIX_BASELINE_20261006')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
 t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(d,indent=2));t.replace(p)
def finalized(folder,name,checkpoint):
 p=folder/name;proof=json.loads((folder/(name+'.receipt.json')).read_text())
 assert sha(p)==proof['sha256'] and p.stat().st_size==proof['bytes'] and proof['source_checkpoint_sha256']==checkpoint
 return json.loads(p.read_text())
def shape_compare(a,b):
 # Report exact data and magnitude; never invent a broad calibration acceptance tolerance.
 if len(a)!=len(b) or any(len(x)!=len(y) for x,y in zip(a,b)):return {'shape_equal':False,'exact':False}
 delta=[abs(float(x)-float(y)) for ax,bx in zip(a,b) for x,y in zip(ax,bx)]
 return {'shape_equal':True,'exact':a==b,'max_abs':max(delta,default=0.)}
def main():
 lock=(ROOT/'s0e_result_review.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 approval=json.loads((R/'PLAN_APPROVAL.json').read_text());assert approval['approved'] and 'S0E' in approval['allowed_stages']
 assert sha(R/'MOD4_MOE_MASTER_PLAN.md')==approval['approved_plan_sha256']
 scope=json.loads((R/'S0E_SDK_REVIEW_AND_FUNCTIONAL_QUEUE.json').read_text());jobs=scope['jobs']
 spec=importlib.util.spec_from_file_location('v4',C/'isaac/mod4/scut_curriculum_gate_v4.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
 refs={}
 for iteration,p in [(23509,Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/reports/auto_0304_physical_dr_three_profile_paired_cap12.5664_white_v3.json')),
  (23621,Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/reports/auto_0366_rough_intro_old_flat_skill_paired_cap12.5664_white_v3.json'))]:
  paired=json.loads(p.read_text());assert paired['checkpoint']['iteration_stored']==iteration
  refs[iteration]={x['kind']:Path(x['report_path']) for x in paired['rows'] if x['seed']==20261002 and x['profile']=='white_v3'}
 atomic(R/'S0E_RESULT_REVIEW_STARTED.json',{'epoch':time.time(),'pid':os.getpid(),'stage':'S0E','new_learning':False,'canonical_write_authority':False,'automatic_result_adjudication':True})
 while True:
  rows=[];attention=[]
  for job in jobs:
   folder=RESULTS/job;manifest=json.loads((Q/(job+'.json')).read_text());checkpoint=manifest['artifacts']['checkpoint']['sha256']
   if not (folder/'result.json.receipt.json').exists() or not (folder/'probe.json.receipt.json').exists():continue
   result=finalized(folder,'result.json',checkpoint);raw=finalized(folder,'probe.json',checkpoint)
   verdict=gate.evidence(raw,'flat' if manifest['kind']=='flat' else 'spin',minimum_seconds=15)
   old=json.loads(refs[manifest['source_CPU_verified']['iteration_stored']][manifest['kind']].read_text())
   initial={key:shape_compare(old[key],raw[key]) for key in ['reset_root_before_physics','reset_joint_pos_before_physics']}
   if result['phase']!='complete' or not verdict['pass_']:attention.append({'job':job,'result':result['phase'],'verdict':verdict})
   if not all(x['shape_equal'] for x in initial.values()):attention.append({'job':job,'initial_shape_mismatch':True})
   rows.append({'job_id':job,'manifest_sha256':sha(Q/(job+'.json')),'result_sha256':sha(folder/'result.json'),'probe_sha256':sha(folder/'probe.json'),
    'checkpoint_sha256':checkpoint,'kind':manifest['kind'],'iteration':manifest['source_CPU_verified']['iteration_stored'],'host':'10.24.4.249',
    'verdict':verdict,'old4090_reference_path':str(refs[manifest['source_CPU_verified']['iteration_stored']][manifest['kind']]),
    'old4090_reference_sha256':sha(refs[manifest['source_CPU_verified']['iteration_stored']][manifest['kind']]),'actual_initial_root_q_comparison':initial,
    'physics_process_wall_seconds':result['physics_process_wall_seconds'],'transfer_seconds':result['transfer_seconds'],
    'functional_groups':raw.get('groups'),'original_boolean_diagnostics_retained':True})
  atomic(R/'S0E_CALIBRATION_PROGRESS.json',{'epoch':time.time(),'pid':os.getpid(),'complete_jobs':len(rows),'expected_jobs':len(jobs),'rows':rows,'attention':attention,'new_learning':False})
  if attention:
   atomic(R/'S0E_CALIBRATION_ATTENTION.json',{'epoch':time.time(),'attention':attention,'all_raw_retained':True,'production_started':False});return 2
  if len(rows)==len(jobs):
   exact=all(z['exact'] for x in rows for z in x['actual_initial_root_q_comparison'].values())
   atomic(R/'S0E_CALIBRATION_REVIEW_READY.json',{'epoch':time.time(),'rows':rows,'all_six_task_model_data_admission_passed':True,'all_initial_root_q_bit_exact_to4090':exact,
    'stage':'S0E','phase':'functional_calibration_saved_review','requires_functional_direction_and_cross_host_bias_review_before_formal_use':True,
    'formal_cross_host_equivalence_confirmed':False,'new_learning':False,'canonical_sha256':sha(B),
    'full_GPU_replay_runtime_cost_seconds':sum(x['physics_process_wall_seconds'] for x in rows),'canonical_write_operations':0})
   state=json.loads((R/'EXECUTION_STATE.json').read_text());state.update(phase='functional_calibration_saved_review',epoch=time.time(),next_required_evidence='Read six actual groups/root/q/parameters and residuals, select usable asynchronous protocol, then implement approved S1/S1A')
   atomic(R/'EXECUTION_STATE.json',state);return 0
  time.sleep(30)
if __name__=='__main__':
 try:code=main()
 except Exception:
  atomic(R/'S0E_RESULT_READER_ATTENTION.json',{'epoch':time.time(),'error':traceback.format_exc(),'canonical_writes':0,'new_learning':False});raise
 raise SystemExit(code)
