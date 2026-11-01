"""New human-authorized10mm termination source;old2mm bytes never overwritten."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
B=T/'W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V2_20261101'
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def main():
 assert json.loads((R/'DERIVE_CLOSURE10MM_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 assert ref(B/'INDEX_W35_LATEST32481_AUTH240_FROZEN.json')['SHA']=='8236c3b520b2a79cc1f1f751ffc1982d70ce584ec96fbfc4de1ccfb21f33f704'
 put(R/'DERIVE_CLOSURE10MM_ONCE_CONSUMED.json',dict(epoch=time.time(),source_only=True))
 same=['target_latest32_parent_ROOT_ONLY.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py']
 for name in same:
  with (N/name).open('xb') as f:f.write((B/name).read_bytes())
 s=(B/'contract_latest32.py').read_text(encoding='utf8')
 s=once(s,"KIND='W35_LATEST32481_32S_SAMEUID_RM70_MIMIC01_EVAL_ONLY_V1'", "KIND='W35_LATEST32481_32S_SAMEUID_RM70_CLOSURE10MM_MIMIC01_EVAL_ONLY_V1'")
 s=once(s,'closure_m=.002,explicit_guard_tightening=True', 'closure_m=.01,previous_closure_m=.002,user_authorized_closure10mm=True,explicit_mimic_guard_tightening=True')
 s=once(s,"startswith('ROOT_W35_LATEST32481_FULL32S_')", "startswith('ROOT_W35_LATEST32481_FULL32S_CLOSURE10MM_')")
 write(N/'contract_latest32.py',s)
 s=(B/'make_latest32_Task_SOURCE_ONLY.py').read_text(encoding='utf8')
 s=once(s,'closure_m=.002,explicit_guard_tightening=True','closure_m=.01,previous_closure_m=.002,user_authorized_closure10mm=True,explicit_mimic_guard_tightening=True')
 write(N/'make_latest32_Task_SOURCE_ONLY.py',s)
 s=(B/'guard_latest32.py').read_text(encoding='utf8')
 s=once(s,'"""Explicit planned mimic .05->.01 tightening before Mod4Env construction."""','"""Explicit user closure2mm->10mm and mimic.01 before Mod4Env construction."""')
 s=once(s,"assert cfg.terminations.closure.params['threshold']==.002,'Original closure must remain 2mm'", "assert cfg.terminations.closure.params['threshold']==.002,'Expected original frozen2mm before new user10mm override'")
 s=once(s,"'Expected original E2 authored .05 before explicit tightening'", "'Expected original W35 authored mimic.05 before planned.01'")
 s=once(s," cfg.terminations.mimic.params['threshold']=.01", " cfg.terminations.closure.params['threshold']=.01\n cfg.terminations.mimic.params['threshold']=.01")
 s=once(s,"expected['mimic']['params']['threshold']=.01", "expected['mimic']['params']['threshold']=.01;expected['closure']['params']['threshold']=.01")
 s=once(s,"'Only planned mimic threshold may differ'", "'Only user closure10mm and planned mimic01 may differ'")
 s=once(s,"kind='W35_LATEST32481_PLANNED_MIMIC01_BEFORE_ENV_CONSTRUCTOR'", "kind='W35_LATEST32481_USER_CLOSURE10MM_MIMIC01_BEFORE_ENV_CONSTRUCTOR'")
 s=once(s,'planned_effective_mimic_radians=.01,closure_m=.002,','planned_effective_mimic_radians=.01,previous_closure_m=.002,closure_m=.01,user_authorized_closure10mm=True,')
 s=once(s,'explicit_guard_tightening_not_all_physics_unchanged=True','explicit_termination_threshold_change_entity_constraints_and_solver_unchanged=True')
 s=once(s,"sole_assignment='cfg.terminations.mimic.params.threshold=.01'", "assignments=['cfg.terminations.closure.params.threshold=.01','cfg.terminations.mimic.params.threshold=.01']")
 write(N/'guard_latest32.py',s)
 s=(B/'evaluate_latest32481_full32s_ROOT_ONLY_once.py').read_text(encoding='utf8')
 s=once(s,"real.cfg.terminations.closure.params['threshold']==.002", "real.cfg.terminations.closure.params['threshold']==.01")
 s=s.replace('BEFORE_CONSTRUCTOR_MIMIC01_ACTUAL.json','BEFORE_CONSTRUCTOR_CLOSURE10MM_MIMIC01_ACTUAL.json')
 s=once(s,"guard['planned_effective_mimic_radians']==.01 and", "guard['planned_effective_mimic_radians']==.01 and guard['closure_m']==.01 and guard['previous_closure_m']==.002 and guard['user_authorized_closure10mm'] and")
 assert s.count('actual_closure_m=.002')==3;s=s.replace('actual_closure_m=.002','actual_closure_m=.01')
 s=once(s,"'400N50D0-D7/CAD70 peak-valley/2mm/original sampler and reward'", "'400N50D0-D7/CAD70 peak-valley/user closure10mm/mimic.01/original sampler and reward'")
 s=once(s,'explicit_mimic_guard_tightening_from_legacy05=True,','explicit_mimic_guard_tightening_from_legacy05=True,user_authorized_closure10mm=True,previous_closure_m=.002,')
 write(N/'evaluate_latest32481_full32s_ROOT_ONLY_once.py',s)
 s=(B/'run_ROOT_latest32481_full32s_once.py').read_text(encoding='utf8')
 s=once(s,"INDEX='INDEX_W35_LATEST32481_AUTH240_FROZEN.json'", "INDEX='INDEX_W35_LATEST32481_CLOSURE10MM_FROZEN.json'")
 s=once(s,"R/'CPU_AUTH240_NEW_JSON_INTERFACE_ACTUAL.json'", "R/'CPU_CLOSURE10MM_NEW_TASK_INTERFACE_ACTUAL.json'")
 write(N/'run_ROOT_latest32481_full32s_once.py',s)
 put(R/'CLOSURE10MM_EXPLICIT_SCOPE_AND_BYTE_BINDINGS.json',dict(epoch=time.time(),previous2mm_INDEX=ref(B/'INDEX_W35_LATEST32481_AUTH240_FROZEN.json'),
  user_override='Future MOD4 per-env closure termination10mm supersedes old2mm plan;old evidence remains2mm',previous_closure_m=.002,current_closure_m=.01,mimic_rad=.01,
  entity_closedloop_constraints_geometry_solver_400N50DR_reward_commands_unchanged=True,
  exact_same240_closed_freshCNone_contract_retained=True,unchanged_byte_files=[ref(N/x) for x in same],
  old2mm_source_overwrites=0,old_fixture_replays=0,model_raw_assets_Torch_SDK_remote_Git_GO=0,actual10mm_W35_case_pending=True))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_CLOSURE10MM_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
