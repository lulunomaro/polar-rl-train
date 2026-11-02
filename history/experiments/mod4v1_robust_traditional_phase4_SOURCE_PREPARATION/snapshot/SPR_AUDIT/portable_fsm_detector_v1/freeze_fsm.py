"""Source/hash/semantic freeze before new native FSM code. No old tests/run/physics."""
from pathlib import Path
import ast,hashlib,json,importlib.util,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent;SRC=ROOT/'FSM_DETECTOR_V1'
REASONS='''BAD_SCHEMA BAD_COMMAND NONFINITE_TIME CLOCK_ROLLBACK SAMPLE_TIME_ROLLBACK CONTROL_TICK_GAP FUTURE_TIMESTAMP DRIVER_FAULT CLIPPED_OR_OVERRUN MISSING_REQUIRED_VALID_BITS NONFINITE_OR_BAD_CORE_SHAPE PROPER_REFERENCE_UNDECLARED STALE_CORE_OR_COMMAND CORE_OR_COMMAND_LOST FALL_HARD TILT_WARN OMEGA_HARD OMEGA_WARN CURRENT_LIMITS_UNBOUND CURRENT_MONITOR_UNAVAILABLE TEMPERATURE_LIMITS_UNBOUND TEMPERATURE_MONITOR_UNAVAILABLE POWER_LIMITS_UNBOUND POWER_MONITOR_UNAVAILABLE REQUIRED_MOTOR_MONITOR_LOST BAD_CURRENT_FEEDBACK BAD_TEMPERATURE_FEEDBACK CURRENT_HARD TEMPERATURE_HARD BAD_POWER_FEEDBACK POWER_KIND_MISMATCH POWER_HARD CURRENT_WARN TEMPERATURE_WARN POWER_WARN FORCE_COM_CONFLICT CONTACT_UNCERTAIN COM_FORCE_UNOBSERVABLE_FROM_THIS_REFERENCE FAULT_LATCHED BAD_ARGUMENT ESTOP EXPLICIT_FAULT_RESET_TO_DISARMED EXPLICIT_DISARM REQUIRED_INPUT_LOSS_TIMEOUT ARM_REQUEST_NOT_READY ARMING_TIMEOUT_DISARM_REARM_REQUIRED JUMP_TOTAL_TIMEOUT FLIGHT_TIMEOUT CORE_REQUIRED_UNAVAILABLE RECOVERY_SUPPORT_UNCERTAIN_OR_PARTIAL RECOVERY_TIMEOUT STEP_SUPPORT_UNCERTAIN TYPED_OBSTACLE_LOST_OR_UNCERTAIN STEP_APPROACH_TIMEOUT PRELOAD_SUPPORT_UNCERTAIN_OR_LOST TAKEOFF_NOT_OBSERVED_TIMEOUT TAKEOFF_UNCERTAIN LANDING_SUPPORT_UNCERTAIN LANDING_TIMEOUT DISARM_REARM_REQUIRED PROXY_UNLOADED_NOT_GROUND_TRUTH CONTACT_UNCERTAIN_OR_PARTIAL RECOVERY_UNBOUND_OR_DISABLED JUMP_UNBOUND_DISABLED_OR_NOT_READY TRAJECTORY_UNBOUND NONFINITE_TRAJECTORY_REFERENCE BAD_CONFIG BAD_CONTEXT BAD_ALIAS'''.split()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,o):
 p=HERE/n;assert not p.exists(),n;p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def row(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
 idx=json.loads((SRC/'INDEX.json').read_text());old={}
 for key in ['core','C_interface_proposal','test_source']:
  r=idx[key];assert sha(Path(r['path']))==r['sha256']
 def add(p):old[str(p.resolve())]=row(p)
 # Reuse exact previous inventories; do not scan unrelated workspace files.
 io=ROOT/'SPR_AUDIT/HOST_ACTIVE_QP_IO_V1';fr=json.loads((io/'SOURCE_FREEZE.json').read_text())
 for r in fr['old_files']:add(Path(r['path']));assert old[r['path']]['sha256']==r['sha256']
 for r in json.loads((io/'INDEX.json').read_text())['files']:add(io/r['path'])
 for n in ['INDEX.json','VALIDATION.json','MANIFEST.json','SOURCE_CLOSURE.json','index_partial_run_01.log']:add(io/n)
 for r in idx['files'] if 'files' in idx else []:add(SRC/r.get('relative',r['path']))
 # Exact known sealed FSM package inventory (all attempts preserved).
 for n in ['fsm_detector.py','test_fsm_detector.py','fsm_detector_v1.h','header_smoke.c','run_host_checks.py','README.md','PROPOSED_THRESHOLDS.json','finalize_fsm.py','ERROR_REPORT.md','VALIDATION.json','INDEX.json']:add(SRC/n)
 for a in ['001','002','003']:
  for n in ['fsm_detector.py','test_fsm_detector.py','fsm_detector_v1.h','header_smoke.c','run_host_checks.py']:add(SRC/'attempts'/a/'sources'/n)
  for n in ['python_unittest.log','c_header_syntax.log','RESULT.json']:add(SRC/'attempts'/a/n)
 for n in ['finalize_fsm.py','STDERR.txt','ERROR.json']:add(SRC/'metadata_attempts/001'/n)
 # Import only the inspected, stdlib-only definition module; no old test runner.
 spec=importlib.util.spec_from_file_location('frozen_fd1_defs',SRC/'fsm_detector.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);c=m.Config()
 scalars=[]
 for name in c.__dataclass_fields__:
  v=getattr(c,name)
  if isinstance(v,bool):scalars.append({'name':name,'ctype':'uint8_t','default':int(v)})
  elif isinstance(v,(int,float)):scalars.append({'name':name,'ctype':'uint32_t' if name in ('required_motor_bits','power_limit_kind') else 'double','default':float(v) if isinstance(v,float) else int(v)})
 (HERE/'fd1_config_fields.inc').write_text('/* Generated frozen Config scalar fields. */\n'+''.join(f" {r['ctype']} {r['name']};\n" for r in scalars),encoding='utf-8')
 (HERE/'fd1_defaults.inc').write_text('/* Source defaults, no tuned threshold. */\n'+''.join(f" c->{r['name']}={repr(r['default'])};\n" for r in scalars),encoding='utf-8')
 (HERE/'fd1_reasons.inc').write_text('/* Frozen IDs: 66 Python reason strings +3 typed API extensions. */\n'+''.join(f' FD1_R_{name}={i},\n' for i,name in enumerate(REASONS)),encoding='utf-8')
 (HERE/'fd1_reason_names.inc').write_text(''.join(' "'+name+'",\n' for name in REASONS),encoding='utf-8')
 dump('REASON_REGISTRY.json',{'reason_word_count':2,'reason_count':len(REASONS),'ordered_output_lists_preserved':True,'ids':{n:i for i,n in enumerate(REASONS)},'typed_extensions':REASONS[66:]})
 dump('CONFIG_LAYOUT.json',{'scalar_fields':scalars,'additional_fields':['execution_context','current_limits_bound/current arrays','temperature_limits_bound/tiers','power_limits_bound/tiers/kind','eligible_step_range_bound/min/max','jump bound/id/envelope/targets','recovery bound/id/envelope/target']})
 dump('SOURCE_FREEZE.json',{'scope':'NEW_NATIVE_FSM_ONLY','sources':[row(SRC/n) for n in ['README.md','fsm_detector.py','test_fsm_detector.py','fsm_detector_v1.h','INDEX.json','VALIDATION.json','PROPOSED_THRESHOLDS.json']],'old_files':list(old.values()),'old_tests_not_rerun_for_score':True,'new_reference_generation_pending':True,'source_imports':sorted({n.names[0].name if isinstance(n,ast.Import) else n.module for n in ast.walk(ast.parse((SRC/'fsm_detector.py').read_text())) if isinstance(n,(ast.Import,ast.ImportFrom))})})
 dump('NUMERICAL_BUDGET.json',{'declared_before_native_code':True,'number_format':'IEEE binary64; no binary32 narrowing; relative seconds unchanged','rounding':'round-to-nearest; no fast-math; fp-contract=off','discrete_and_ordered_reasons_mismatches_allowed':0,'finite_numeric_absolute':1e-12,'finite_numeric_relative':1e-12,'clock_state_entered_absolute_s':0.0,'invalid_q4_all_zero_required':True,'reference_frames':'generated from original63 scenario methods, same native inputs, no dynamics','no_physical_threshold_is_changed':True,'ARM_object_not_runtime_or_WCET':True})
 print(json.dumps({'old_files':len(old),'source_sha':sha(SRC/'fsm_detector.py'),'reason_count':len(REASONS),'scalars':len(scalars),'status':'FROZEN_BEFORE_NATIVE_CODE'}))
if __name__=='__main__':main()
