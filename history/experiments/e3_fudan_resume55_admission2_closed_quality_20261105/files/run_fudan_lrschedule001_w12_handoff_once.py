"""Controlled sequential authorized train->actual-wait->original-eval handoff; no retries.
The original owners alone retain resource locks/accounting/SDK lifecycles. This
controller reads metadata and runs explicitly named new-purpose CLI entrypoints.
"""
from pathlib import Path
import json,time,hashlib,subprocess,sys,traceback
D=Path(__file__).resolve().parent;PY=Path(sys.executable);MJ=Path(r'C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/python.exe')
marker=D/'FDN_LRSCHEDULE001_W12_CONTROLLED_HANDOFF_ONCE.json';status=D/'FDN_LRSCHEDULE001_W12_HANDOFF_STATUS.json';assert not marker.exists()and not status.exists()
NATIVE_PREFIX='FDN_N20000_W12_LRSCHEDULE001_';EVAL_PREFIX='FDNLR001_FROZEN_';stage=json.loads((D/(NATIVE_PREFIX+'STAGE_RESULT.json')).read_bytes());assert stage['returncode']==stage['owner_source_preflight_rc']==0 and stage['num_envs']==20000
names=('dispatch_fudan_lrschedule001_w12_original_owner_once.py','collect_fudan_lrschedule001_w12_window_once.py','stage_fudan_lrschedule001_frozen_original_once.py','dispatch_fudan_lrschedule001_frozen_original_once.py','export_fudan_lrschedule001_pi_for_mujoco_once.py','evaluate_fudan_lrschedule001_pi_mujoco31_lowrise_once.py','collect_fudan_lrschedule001_frozen_original_once.py','publish_fudan_lrschedule001_closed_quality_once.py')
assert MJ.is_file();pins={n:hashlib.sha256((D/n).read_bytes()).hexdigest()for n in names};context=dict(root=stage['root'],native_num_envs=20000,finite_update_cap=25,schedule_scale=.01,original_owner_resource_accounting_unchanged=True,policy_and_physics_not_modified_by_bridge=True,models_raw_or_canonical_access_by_this_controller=0,automatic_retry=False)
marker.write_text(json.dumps(dict(epoch=time.time(),entry_source_SHA=pins,**context),indent=2),encoding='utf8');phase='PREPARED';eval_dispatched=False

def put(state,**extra):
 record=dict(epoch=time.time(),phase=state,**context,**extra);tmp=status.with_suffix('.tmp');tmp.write_text(json.dumps(record,indent=2,allow_nan=False),encoding='utf8');tmp.replace(status);print('CONTROLLED_HANDOFF '+json.dumps(record),flush=True)

def run(label,name,*args,python=PY):
 global phase
 assert name in pins and hashlib.sha256((D/name).read_bytes()).hexdigest()==pins[name],('Prepared new CLI source changed',name)
 phase=label;put(label,entry=name);subprocess.run([str(python),'-B',str(D/name),*map(str,args)],cwd=str(D),check=True);put(label+'_RETURNED',entry=name)

try:
 run('NATIVE_ORIGINAL_DISPATCH',names[0]);run('NATIVE_OWN_METADATA_COLLECT',names[1])
 pointer=json.loads((D/(NATIVE_PREFIX+'LATEST_CLOSED_RESULT_PATH.json')).read_bytes());closed_path=Path(pointer['path']);closed=json.loads(closed_path.read_bytes());m=closed['metadata'];f=m['FDN_FINAL.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json']
 assert closed['closed']is True and closed['root']==stage['root']and f is not None and f['version']==7 and f['final']is f['complete_save']is True and f['error']is None and f['close_errors']==[]
 assert q['qualified']is True and all(q['checks'].values())and owner['errors']==[]and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
 assert f['window_counters']==f['counters']and 0<f['counters']['updates']<=25 and all(v==0 for v in f['base_counters'].values())and f['latest_complete_save']==m['FDN_LATEST_COMPLETE_SAVE.json']
 context.update(actual_native_closed_metadata=str(closed_path),actual_native_updates=f['counters']['updates'],source_full_save_metadata=f['latest_complete_save']);put('NATIVE_ACTUAL_WAIT_COST_RELEASE_QUALIFIED')
 # No model stat/read/hash here. The original N80 parent still rechecks every gate.
 run('STAGE_ORIGINAL_N80_AFTER_REAL_CLOSURE',names[2],'--closed',closed_path)
 run('DISPATCH_ORIGINAL_N80_NEW_PURPOSE',names[3]);eval_dispatched=True;cpu_error=None
 try:
  run('CPU_EXPORT_WHOLE_NEW_SOURCE_ONCE',names[4],'--closed',closed_path)
  export=json.loads((D/'FDNLR001_PI_ONLY_EXPORT_STARTED_ONCE.json').read_bytes());assert export['complete']is True and export['source']['sha256']==f['latest_complete_save']['sha256']
  context['local_pi_export']=export['local_pi_export'];run('NOMINAL_FIVE_LEGAL_POSES_ONCE',names[5],'--pi-export',export['local_pi_export'],python=MJ)
 except BaseException as exc:
  cpu_error=exc;context['CPU_export_or_nominal_error']=repr(exc);put('CPU_PATH_FAILED_EVAL_PARENT_STILL_MUST_BE_COLLECTED')
 finally:
  if eval_dispatched:run('ORIGINAL_N80_ACTUAL_WAIT_COLLECT',names[6])
 scope=json.loads((D/(EVAL_PREFIX+'ORIGINAL_SCOPE_RESULT.json')).read_bytes());assert scope['execution_qualified']is True and all(scope['execution_checks'].values())and scope['actual_parent_wait_qualification']['qualified']is True
 if cpu_error is not None:raise RuntimeError('CPU path failed; original evaluation collected without replay')from cpu_error
 run('PUBLISH_ACTUAL_QUALITY_ONLY',names[7]);put('COMPLETE_ACTUAL_WINDOW_AND_INDEPENDENT_EVALUATION',goal_complete=False,Registry_v12_and_selected_mother_unchanged=True)
except BaseException as exc:
 put('STOPPED_WITH_REAL_EVIDENCE_NO_AUTOMATIC_RETRY',failed_phase=phase,error=repr(exc),traceback=traceback.format_exc(),original_parents_unchanged=True,goal_complete=False);raise
