"""Prepare a minimal new source overlay; never install or execute learner/MDP."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,math,importlib.util,difflib
D=Path(__file__).resolve().parent;T=D.parent.parent
B=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1'
CFG=B/'job0/runtime/isaac/mod4/mod4_task.py'
MDP=B/'source/converted_MOD4_jump_mdp_v4.py'
def H(x):return hashlib.sha256(x).hexdigest()
def put(name,value):
 with (D/name).open('x',encoding='utf-8',newline='\n') as f:
  if isinstance(value,str):f.write(value)
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
cfg=CFG.read_bytes();old=MDP.read_bytes();cfg_sha=H(cfg)
assert b'params={"limit_angle": 0.75}' in cfg
helper='''"""Typed source-bound imagined tilt boundary. No physics setter, torch or RNG.

Requires fresh target source verification and actual config-value verification by
the root's new admission/precontrol entry. This module is not such admission.
"""
from pathlib import Path
import ast,hashlib,math
SCHEMA='mod4.native88C.imagined_tilt_boundary_alignment.source.v1'
HARD_ORIENTATION_SOURCE_RELATIVE='job0/runtime/isaac/mod4/mod4_task.py'
HARD_ORIENTATION_SOURCE_SHA='__CFG_SHA__'
HARD_TILT_LIMIT_RAD=.75
TILT_RZZ_BOUNDARY=math.cos(HARD_TILT_LIMIT_RAD)
SOFT_TILT_RZZ_WIDTH=.04

def _limit_from_source(raw):
 tree=ast.parse(raw.decode('utf-8-sig'))
 cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TerminationsCfg'),None)
 if cls is None:raise ValueError('TerminationsCfg missing')
 matches=[]
 for n in cls.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bad_orientation' for t in n.targets):matches.append(n.value)
 if len(matches)!=1:raise ValueError('bad_orientation assignment must be unique')
 call=matches[0]
 if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name) or call.func.id!='DoneTerm':raise ValueError('bad_orientation DoneTerm changed')
 kwargs={k.arg:k.value for k in call.keywords}
 if ast.unparse(kwargs['func'])!='mdp_term.bad_orientation':raise ValueError('hard orientation function changed')
 params=ast.literal_eval(kwargs['params'])
 if set(params)!={'limit_angle'}:raise ValueError('hard orientation params changed')
 return params['limit_angle']

def verify_hard_orientation_source_bytes(raw,*,actual_hard_limit_angle_rad):
 if not isinstance(raw,bytes):raise TypeError('exact source bytes required')
 SHA=hashlib.sha256(raw).hexdigest()
 if SHA!=HARD_ORIENTATION_SOURCE_SHA:raise ValueError('hard orientation source SHA changed')
 angle=_limit_from_source(raw)
 if type(angle) not in (float,int) or float(angle)!=HARD_TILT_LIMIT_RAD:raise ValueError('source hard angle differs')
 if type(actual_hard_limit_angle_rad) not in (float,int) or not math.isfinite(actual_hard_limit_angle_rad) or float(actual_hard_limit_angle_rad)!=float(angle):raise ValueError('actual configured hard angle differs')
 return dict(schema=SCHEMA,source_SHA=SHA,hard_limit_angle_rad=float(angle),
  imagined_tilt_Rzz_boundary=TILT_RZZ_BOUNDARY,imagined_soft_width_Rzz=SOFT_TILT_RZZ_WIDTH,
  physical_hard_termination_changed=False,signed_contact_reward_or_phase_changed=False,
  models_optimizers_normalizers_global_counters_changed=False,
  source_and_caller_config_value_checked=True,actual_SDK_readback_proven_by_this_function=False,
  soft_surrogate_not_hard_predicate=True)

def verify_actual_hard_orientation_source(cfg_source_path,*,actual_hard_limit_angle_rad):
 return verify_hard_orientation_source_bytes(Path(cfg_source_path).read_bytes(),actual_hard_limit_angle_rad=actual_hard_limit_angle_rad)

def scalar_diagnostic(tilt_rad,height_m):
 if not all(type(v) in (int,float) and math.isfinite(v) for v in (tilt_rad,height_m)):raise ValueError('finite diagnostic scalars required')
 sig=lambda x:1/(1+math.exp(-x))
 p=sig((TILT_RZZ_BOUNDARY-math.cos(tilt_rad))/SOFT_TILT_RZZ_WIDTH)
 low=sig((.12-height_m)/.02)
 return dict(tilt_failure=p,low_height_failure=low,combined_failure=1-(1-p)*(1-low))
'''.replace('__CFG_SHA__',cfg_sha)
put('imagined_bad_orientation_alignment_v1.py',helper)
nl=b'\r\n' if b'\r\n' in old else b'\n'
anchor=b'from dataclasses import dataclass'
assert old.count(anchor)==1
new=old.replace(anchor,b'from imagined_bad_orientation_alignment_v1 import (TILT_RZZ_BOUNDARY, HARD_TILT_LIMIT_RAD, HARD_ORIENTATION_SOURCE_SHA)'+nl+anchor)
a=b'tilt_failure=torch.sigmoid((.3-state[1][...,2,2])/.04)'
b=b'tilt_failure=torch.sigmoid((TILT_RZZ_BOUNDARY-state[1][...,2,2])/.04)'
assert new.count(a)==1;new=new.replace(a,b)
a=b'# Original absolute physical low-height/tilt thresholds, using source-style'+nl+b'        # .02/.04 temperatures; actual hard callback truth remains independent.'
b=b'# Source-pinned real hard angle mapped to Rzz; this remains a soft surrogate.'+nl+b'        # Height/widths unchanged; actual hard callback truth remains independent.'
assert new.count(a)==1;new=new.replace(a,b)
a=b'soft_survival=dict(height_threshold=.12,tilt_Rzz_threshold=.3,height_temperature=.02,tilt_temperature=.04),'
b=b'soft_survival=dict(height_threshold=.12,tilt_Rzz_threshold=TILT_RZZ_BOUNDARY,hard_angle_source_bound_rad=HARD_TILT_LIMIT_RAD,hard_angle_source_SHA=HARD_ORIENTATION_SOURCE_SHA,height_temperature=.02,tilt_temperature=.04,soft_surrogate_not_hard_predicate=True),'
assert new.count(a)==1;new=new.replace(a,b)
a=b"termination='original hard callbacks unchanged; calibrated analytic native soft approximation'"
b=b"termination='original hard callbacks unchanged; source-bound angle with smooth surrogate, not equivalent hard predicate'"
assert new.count(a)==1;new=new.replace(a,b)
with (D/'converted_MOD4_jump_mdp_v4.py').open('xb') as f:f.write(new)
def methods(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(raw.decode('utf-8-sig'))) if isinstance(n,ast.FunctionDef)}
aa,bb=methods(old),methods(new)
changed=[n for n in aa if aa[n]!=bb[n]]
assert changed==['soft_termination','contract_manifest'],changed
assert all(aa[n]==bb[n] for n in aa if n not in changed)
contract=dict(schema='mod4.native88C.imagined_tilt_boundary_alignment.source.v1',
 selected_source_only_candidate=True,actual_installed_or_training_passed=False,
 hard_cfg_relative='job0/runtime/isaac/mod4/mod4_task.py',hard_cfg_SHA=cfg_sha,
 original_mdp_relative='source/converted_MOD4_jump_mdp_v4.py',original_mdp_SHA=H(old),candidate_mdp_SHA=H(new),
 helper_relative='source/imagined_bad_orientation_alignment_v1.py',helper_SHA=H(helper.encode()),
 hard_limit_angle_rad=.75,old_imagined_Rzz_boundary=.3,new_imagined_Rzz_boundary=math.cos(.75),
 imagined_Rzz_width_unchanged=.04,height_threshold_unchanged=.12,height_width_unchanged=.02,
 physical_hard_action_reward_command_success_inputs_optimizer_RNG_unchanged=True,
 signedZ_contact_style_weights_phase_gating_unchanged=True,
 required_continuation='Preserve qualifiedC WM/Pi/Critic/3optimizers/allnorms/globalcounts; explicitly record new imagined surrogate contract, not exact old native objective semantics.',
 required_fresh_admission=['newsource/auth/manifest/pins','target exact hardcfg source+actual configured angle verification','fresh installed SDK/source+resources+account and root-owned precontrol','new publisher/reviewer nativecontract'],
 no_deployment_or_authorization_created=True)
put('IMAGINED_TERMINATION_ALIGNMENT_SOURCE_CONTRACT_ACTUAL.json',contract)
spec=importlib.util.spec_from_file_location('imagined_bad_orientation_alignment_v1',D/'imagined_bad_orientation_alignment_v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
proof=m.verify_actual_hard_orientation_source(CFG,actual_hard_limit_angle_rad=.75)
cases={str(v):m.scalar_diagnostic(v,.2997927963733673) for v in (0.,.7,.75,.7507237792015076,1.)}
assert cases['0.75']['tilt_failure']==.5
assert cases['0.7']['tilt_failure']<.5<cases['0.7507237792015076']['tilt_failure']
neg=[]
for name,raw,angle in [('actual_angle_mismatch',cfg,.76),('source_byte_mismatch',cfg+b'\n# negative fixture',.75)]:
 try:m.verify_hard_orientation_source_bytes(raw,actual_hard_limit_angle_rad=angle)
 except ValueError as e:neg.append(dict(case=name,rejected=True,error=str(e)))
 else:raise AssertionError(name)
put('SOURCE_AST_AND_SCALAR_CPU_ACTUAL.json',dict(passed=True,scope='stdlib AST + source bytes +5scalarcases +2negativecases; no torch/MDP/model/SDK execution',
 source_verification_fixture=proof,changed_methods=changed,other_method_AST_exact=True,
 original_mdp_SHA=H(old),new_mdp_SHA=H(new),boundary_cases=cases,negative_cases=neg,
 actualSDK_or_training_benefit_proven=False))
put('EXACT_SOURCE_DIFF_ACTUAL.patch','\n'.join(difflib.unified_diff(old.decode().splitlines(),new.decode().splitlines(),fromfile=str(MDP),tofile='candidate/source/converted_MOD4_jump_mdp_v4.py',n=3))+'\n')
put('HANDOFF.md',f'''# FROZEN: source-bound imagined bad-orientation boundary candidate

Runtime overlay, **not installed**:
- replacement `source/converted_MOD4_jump_mdp_v4.py` SHA `{H(new)}`
- addition `source/imagined_bad_orientation_alignment_v1.py` SHA `{H(helper.encode())}`
- pin new `IMAGINED_TERMINATION_ALIGNMENT_SOURCE_CONTRACT_ACTUAL.json` in new auth/manifest/publisher/reviewer contract.

Only the imagined tilt50% boundary changes from Rzz.3 (acos(.3)=72.5424°) to cos(actual pinned hard angle.75)={math.cos(.75):.12f} (42.9718°). Rzz soft width.04 stays; root-height .12/.02 union stays. This is a smooth surrogate, never the same predicate or actual physical evidence. Original hard config/clock/action/reward/command/success/input dimensions/signedZ/style/phase/RNG/optimizers/norms/weights remain untouched. Metadata reflects the changed imaginary boundary. All original MDP method ASTs except `soft_termination` and metadata `contract_manifest` are exact; class construction/to() is unchanged, so no binding is lost on device copies.

Typed helper has no torch, physics setter, model load or RNG. The known.75 is tied to full original `mod4_task.py` SHA `{cfg_sha}` and exact TerminationsCfg.bad_orientation AST, not a fallback/unknown hardcode. Mandatory future caller API:
`verify_actual_hard_orientation_source(cfg_source_path, actual_hard_limit_angle_rad=<actual resolved env config value>)`.
Root must fresh-verify Task/contract/source pins and actual resolved config before firstcontrol/Pi. The helper checks the passed value and source; it explicitly **does not claim** to read SDK by itself. The sourceCPU case used a literal fixture value.75, not SDK readback. No entry/controller/admission has been generated here. New source/auth/fresh installedCPU/precontrol are required; no hotpatch.

Five scalar boundaries and two fail-closed source/config mismatches passed, no learner/WM/actor/SDK imported. At real single-case tilt.7507237792, aligned tilt failure={cases['0.7507237792015076']['tilt_failure']:.10f} vs original≈.0000208136. At exactly.75, aligned tilt failure.5. This demonstrates boundary semantics only, not training benefit, physical fidelity or skill. No runtime error occurred in this new preparation. Preserve qualifiedC WM/Pi/Critic/3opts/norms/globalcounts under an explicit changed-imagined-surrogate continuation contract; do not reset them automatically.

Do not also modify contactZ->norm, posture reward weights, phase gating or real thresholds. Those are independent unresolved candidates. Source/scalar report and exact diff are frozen; ordinaryGit supplementation/admission/execution are root-owned. No model/raw/PT/NPZ read/stat/hash, actor/WM forward, SDK/physics/GPU, network/SSH or Git occurred. All old directories remain unchanged.
''')
put('FREEZE_STATUS_ACTUAL.json',dict(frozen_UTC=datetime.now(timezone.utc).isoformat(),complete=True,source_only=True,
 actual_installed_or_training_passed=False,Git_supplementation='PENDING_ROOT',errors=[]))
rows=[]
for p in sorted(D.iterdir()):
 if p.is_file() and p.name!='INDEX.json':
  raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
put('INDEX.json',dict(files=rows,self_excluded='INDEX.json'))
print(json.dumps(dict(frozen=True,directory=str(D),INDEX_SHA=H((D/'INDEX.json').read_bytes()),mdp_SHA=H(new),helper_SHA=H(helper.encode()),actual_case_aligned=cases['0.7507237792015076'])))
