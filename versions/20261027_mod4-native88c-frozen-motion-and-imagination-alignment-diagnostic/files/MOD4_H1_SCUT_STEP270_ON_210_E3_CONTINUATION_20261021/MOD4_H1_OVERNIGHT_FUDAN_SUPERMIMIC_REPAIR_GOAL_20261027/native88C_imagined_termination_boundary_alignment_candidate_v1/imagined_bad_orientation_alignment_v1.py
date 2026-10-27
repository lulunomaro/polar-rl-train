"""Typed source-bound imagined tilt boundary. No physics setter, torch or RNG.

Requires fresh target source verification and actual config-value verification by
the root's new admission/precontrol entry. This module is not such admission.
"""
from pathlib import Path
import ast,hashlib,math
SCHEMA='mod4.native88C.imagined_tilt_boundary_alignment.source.v1'
HARD_ORIENTATION_SOURCE_RELATIVE='job0/runtime/isaac/mod4/mod4_task.py'
HARD_ORIENTATION_SOURCE_SHA='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5'
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
