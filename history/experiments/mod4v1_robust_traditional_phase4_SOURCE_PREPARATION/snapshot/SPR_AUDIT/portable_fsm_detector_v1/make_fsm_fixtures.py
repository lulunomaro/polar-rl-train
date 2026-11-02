"""NEW C-port fixed references from63 existing scenario methods; no old score rerun."""
from pathlib import Path
import importlib.util,sys,json,math,dataclasses,hashlib,unittest,shutil
HERE=Path(__file__).resolve().parent;SRC=HERE.parent.parent/'FSM_DETECTOR_V1'
REG=json.loads((HERE/'REASON_REGISTRY.json').read_text())['ids'];SCALARS=json.loads((HERE/'CONFIG_LAYOUT.json').read_text())['scalar_fields'];instances=[];frames=[];scenario='';scenario_rows={}
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def num(x):
 if isinstance(x,bool):return str(int(x))
 if isinstance(x,int):return str(x)
 if x is None:return '0.0'
 if not math.isfinite(x):return 'NAN' if math.isnan(x) else '-INFINITY' if x<0 else 'INFINITY'
 return repr(x)
def arr(v,n):return '{'+','.join(num(v[i]) if isinstance(v,(tuple,list)) and i<len(v) else '0.0' for i in range(n))+'}'
def obj(items):return '{'+','.join('.'+k+'='+str(v) for k,v in items.items())+'}'
def rlist(v):
 ids=[REG[x] for x in v];bits=[sum(1<<(i%64) for i in ids if i//64==w) for w in range(2)];return obj({'bits':'{'+','.join('UINT64_C('+str(b)+')' for b in bits)+'}','count':len(ids),'ids':arr(ids,len(ids)) if ids else '{0}'})
def cfg_c(c):
 d={r['name']:num(getattr(c,r['name'])) for r in SCALARS};d['execution_context']={'unbound_prototype':0,'simulation':1,'synthetic_fixture':2}.get(c.execution_context,3)
 for label,n in [('current','current_warn_A6'),('temperature','temperature_warn_C'),('power','power_warn_W')]:d[label+'_limits_bound']=int(getattr(c,n)is not None)
 for n in ['current_warn_A6','current_fault_A6']:d[n]=arr(getattr(c,n),6)
 for n in ['temperature_warn_C','temperature_fault_C','power_warn_W','power_fault_W','eligible_step_min_m','eligible_step_max_m']:d[n]=num(getattr(c,n))
 d['eligible_step_range_bound']=int(c.eligible_step_min_m is not None and c.eligible_step_max_m is not None)
 for name in ['jump','recovery']:
  b=getattr(c,name)
  if b is None:d[name]='{0}'
  else:
   names=['target_q4','joint_min_q4','joint_max_q4'] if name=='recovery' else ['preload_q4','push_off_q4','flight_q4','landing_q4','joint_min_q4','joint_max_q4'];d[name]=obj({'bound':1,'binding_id':1,**{n:arr(getattr(b,n),4) for n in names}})
 return obj(d)
def frame_c(f):
 if not isinstance(f,defs.SensorFrame):return obj({'frame_type_valid':0})
 bits=int(f.valid_bits) if isinstance(f.valid_bits,(int,defs.Valid)) else 0;d={'schema_version':f.schema_version if isinstance(f.valid_bits,(int,defs.Valid)) else 0,'valid_bits':bits,'frame_type_valid':1,'command_present':int(isinstance(f.command,defs.Command)),'timestamp_s':num(f.timestamp_s),'proper_reference':int(f.proper_reference),'lever_com_confidence':num(f.lever_com_confidence),'com_force_model_confidence':num(f.com_force_model_confidence)}
 sb=0
 for bit,n,sz in [(1,'rpy_rad3',3),(2,'omega_rad_s3',3),(4,'proper_acc_m_s2',3),(8,'encoder_q4',4),(16,'encoder_qd4',4)]:
  v=getattr(f,n);d[n]=arr(v,sz)
  # Shape validity is separate from element finite checks in native core.
  if isinstance(v,(tuple,list)) and len(v)==sz:sb|=bit
 d['core_shape_bits']=sb
 if isinstance(f.command,defs.Command):d['command']=obj({n:num(getattr(f.command,n)) for n in f.command.__dataclass_fields__})
 p=f.force_proxy
 if isinstance(p,defs.ForceProxy):
  shape=isinstance(p.normal_N2,(tuple,list))and len(p.normal_N2)==2 and isinstance(p.confidence2,(tuple,list))and len(p.confidence2)==2
  d['force']=obj({'present':1,'shape_valid':int(shape),'timestamp_s':num(p.timestamp_s),'normal_N2':arr(p.normal_N2,2),'confidence2':arr(p.confidence2,2),'provenance_id':int(isinstance(p.provenance,str)and bool(p.provenance)),'value_present':arr([int(x is not None) for x in p.normal_N2] if shape else None,2)})
 p=f.motor
 if isinstance(p,defs.MotorFeedback):d['motor']=obj({'present':1,'timestamp_s':num(p.timestamp_s),'current_A6':arr(p.current_A6,6),'temperature_C6':arr(p.temperature_C6,6),'power_W':num(p.power_W),'power_kind':int(p.power_kind),'current_present':int(isinstance(p.current_A6,(tuple,list))and len(p.current_A6)==6),'temperature_present':int(isinstance(p.temperature_C6,(tuple,list))and len(p.temperature_C6)==6),'power_present':int(p.power_W is not None)})
 p=f.front
 if isinstance(p,defs.FrontObservation):
  names=['range_m','step_height_m','range_sigma_m','height_sigma_m'];d['front']=obj({'present':1,'timestamp_s':num(p.timestamp_s),'observation_id':p.observation_id,'kind':int(p.kind),'values_present':sum(1<<i for i,n in enumerate(names)if getattr(p,n)is not None),**{n:num(getattr(p,n))for n in names}})
 return obj(d)
def output_c(o):
 d={n:num(getattr(o,n)) for n in ['mode','profile','phase','phase_fraction','hard_inhibit','state_entered_s','jump_accepted','recovery_accepted']};d.update(schema_version=1,threshold_role=1,q4_reference_valid=int(o.expected_q4 is not None),expected_q4=arr(o.expected_q4,4),wheel_no_slip_allowed2=arr(o.wheel_no_slip_allowed2,2),reasons=rlist(o.reasons),latched_faults=rlist(o.latched_faults))
 p=o.contact;d['contact']=obj({'support':int(p.support),'wheel_state2':arr(p.wheel_state2,2),'confidence':num(p.confidence),'source':{'unobserved':0,'external_motor_force_proxy':1,'declared_COM_freefall_model_only':2}[p.source],'com_freefall_known':int(p.com_freefall_like is not None),'com_freefall_like':int(bool(p.com_freefall_like)),'reasons':rlist(p.reasons)})
 return obj(d)
def safe_json(x):
 if dataclasses.is_dataclass(x):return {k:safe_json(v)for k,v in dataclasses.asdict(x).items()}
 if isinstance(x,dict):return {str(k):safe_json(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [safe_json(v)for v in x]
 if isinstance(x,float)and not math.isfinite(x):return {'nonfinite':str(x)}
 return x
def main():
 global defs,scenario
 freeze=json.loads((HERE/'SOURCE_FREEZE.json').read_text())
 for r in freeze['sources']:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
 rev=HERE/'revisions/reference_attempt_01';rev.mkdir(parents=True,exist_ok=False);shutil.copy2(__file__,rev/Path(__file__).name)
 defs=load('fsm_detector',SRC/'fsm_detector.py');Orig=defs.DetectorFSM
 class Recorded(Orig):
  def __init__(self,c=None):
   super().__init__(c or defs.Config());self.cid=len(instances);instances.append({'id':self.cid,'scenario':scenario,'config':self.c})
  def step(self,f,now):
   o=super().step(f,now);frames.append({'context':self.cid,'scenario':scenario,'now_s':now,'input':f,'expected':o});return o
 defs.DetectorFSM=Recorded;tests=load('fd1_source_scenarios',SRC/'test_fsm_detector.py');methods=[]
 for name in sorted(vars(tests)):
  cls=getattr(tests,name)
  if isinstance(cls,type)and issubclass(cls,unittest.TestCase)and cls.__module__==tests.__name__:
   for method in sorted(n for n in vars(cls)if n.startswith('test_')):
    scenario=name+'.'+method;before=len(frames);getattr(cls(method),method)();scenario_rows[scenario]=len(frames)-before;methods.append(scenario)
 assert len(methods)==63
 h=['/* Generated fixed C-PORT fixtures. No test-source score update. */','#ifndef FD1_REFERENCE_FIXTURES_H','#define FD1_REFERENCE_FIXTURES_H','#include "fd1_detector.h"','#include <math.h>','typedef struct {uint32_t context;double now_s;fd1_input input;fd1_output expected;} fd1_fixture;',f'#define FD1_FIXTURE_CONTEXTS {len(instances)}u',f'#define FD1_FIXTURE_ROWS {len(frames)}u','static const fd1_config fd1_configs[FD1_FIXTURE_CONTEXTS]={']
 h += [cfg_c(r['config'])+','for r in instances];h+=['};','static const fd1_fixture fd1_fixtures[FD1_FIXTURE_ROWS]={'];h += ['{'+str(r['context'])+','+num(r['now_s'])+','+frame_c(r['input'])+','+output_c(r['expected'])+'},' for r in frames];h+=['};','#endif'];(HERE/'fd1_reference_fixtures.h').write_text('\n'.join(h)+'\n',encoding='utf-8')
 with (HERE/'REFERENCE_FRAMES.jsonl').open('w',encoding='utf-8')as fp:
  for r in frames:fp.write(json.dumps(safe_json(r),allow_nan=False)+'\n')
 (HERE/'REFERENCE_CONTEXTS.json').write_text(json.dumps(safe_json(instances),indent=2,allow_nan=False)+'\n',encoding='utf-8')
 report={'purpose':'NEW_NATIVE_INTERFACE_REFERENCE_GENERATION_NOT_OLD_TEST_SCORE','source_scenarios_visited':len(methods),'contexts':len(instances),'new_reference_frames':len(frames),'scenario_rows':scenario_rows,'cases_with_no_step_require_native_typed_config_tests':[n for n,c in scenario_rows.items()if not c],'old_artifacts_written':0,'physics_imported':any(n.startswith(('mujoco','physics_bridge'))for n in sys.modules),'modes_expected':sorted({int(r['expected'].mode)for r in frames}),'finite1e308_overflow_preserved':any('NONFINITE_TRAJECTORY_REFERENCE'in r['expected'].latched_faults for r in frames)}
 assert not report['physics_imported'];(HERE/'REFERENCE_GENERATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
