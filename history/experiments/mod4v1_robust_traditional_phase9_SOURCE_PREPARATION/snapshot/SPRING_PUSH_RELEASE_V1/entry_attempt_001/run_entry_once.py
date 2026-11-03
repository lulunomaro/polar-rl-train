"""Actual new main/help/constructor, explicitly FAKE plant/DR/assets, stopped preloop.
No full-model admission; expected ERROR+empty StreamedRows prefixes are retained.
"""
from pathlib import Path
import sys,json,ast,types,copy,traceback,hashlib,shutil,importlib.util,importlib.abc,io,contextlib
from types import SimpleNamespace
O=Path(__file__).resolve().parent;ROOT=O.parent;sys.path.insert(0,str(ROOT))
import numpy as np
from sensor_core import LinkageGeometry
from streamed_trace_rows_v1 import StreamedRows,scalar_default
from MINIHOP_AUDIT_V2.provenance_v2 import error_receipt
from SPRING_PUSH_RELEASE_V1 import binding
A=O/'entry_attempt_001';A.mkdir()
for n in('controller.py','binding.py','run_manual_spring_push_v1.py','run_entry_once.py','PREEXEC_UNIT_PLAN.json'):shutil.copyfile(O/n,A/n)
checks=0;typed=0;observed=[];count=dict(help=0,fake_plant=0,fake_DR=0,actual_new_ctor=0,initial_fake_grade=0,loop_body=0,sensor_packet=0,actuator=0,Geometry_wheel_kinematics=0,MuJoCo=0,NominalModel_FK=0,data_records=0)
def check(ok,msg):
 global checks
 checks+=1
 if not bool(ok):raise AssertionError(msg)
class BlockSDK(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname=='mujoco'or fullname.startswith('mujoco.')or fullname.endswith('nominal_model'):count['MuJoCo']+=1;raise RuntimeError('FORBIDDEN SDK/NominalModel import')
blocker=BlockSDK();sys.meta_path.insert(0,blocker)
pub=json.loads((ROOT/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json').read_bytes())
class Geometry(LinkageGeometry):
 def wheel_kinematics(self,*a,**kw):count['Geometry_wheel_kinematics']+=1;raise RuntimeError('No geometry query allowed in preloop admission')
class FakePlant:
 def __init__(self,*a):count['fake_plant']+=1;self.d=SimpleNamespace(time=0.);self.imu_offset=np.array([.03,0.,.04]);self.tick_phys=0;self.instrumentation_error=None
 def attach_dr(self,dr):return {'FAKE_NO_DR_SAMPLE':True}
 def reset(self,*a):pass
 def grade(self):count['initial_fake_grade']+=1;return {'FAKE_INITIAL_ONLY':True}
 def sensor_packet(self):count['sensor_packet']+=1;raise RuntimeError('loop/packet forbidden')
 def apply_torque_request(self,*a):count['actuator']+=1;raise RuntimeError('actuator forbidden')
class FakeDR:
 def __init__(self,*a,**kw):count['fake_DR']+=1
class Bounds(StreamedRows):
 def bind(self,p):self.plant=p;self.first_bar=self.next_bar=None

def load_gain(path):
 g=json.loads(Path(path).read_bytes())['gain'];return{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}
bridge=types.ModuleType('physics_bridge');bridge.ROOT=ROOT;bridge.MODEL_SHA=pub['source_xml_sha256'];bridge.FullDR=FakeDR;bridge.geometry=lambda:Geometry(pub['pins_xz_m'],radius=.0625);bridge.load_gain=load_gain
sys.modules['physics_bridge']=bridge
# Exact inspected old pure loader/dump function AST, not its simulator imports.
oldpath=ROOT/'run_minihop_landing_v4.py';oldtree=ast.parse(oldpath.read_text(encoding='utf-8'));names={'arrays','load_landing_gain','dump'};defs=[n for n in oldtree.body if isinstance(n,ast.FunctionDef)and n.name in names]
loader=types.ModuleType('run_minihop_landing_v4');loader.__dict__.update(Path=Path,ROOT=ROOT,np=np,json=json,load_gain=load_gain,scalar_default=scalar_default)
exec(compile(ast.Module(body=defs,type_ignores=[]),str(oldpath),'exec'),loader.__dict__)
loader.source_manifest=lambda scene,cfg:dict(files=[],base_large_asset_manifest_STUBBED=True,full_model_admission=False,scene=scene)
sys.modules['run_minihop_landing_v4']=loader
for name in('MINIHOP_AUDIT_V2.physics_bridge_minihop_flat_v2','MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2'):
 fake=types.ModuleType(name);fake.MiniHopAuditPlant=FakePlant;sys.modules[name]=fake
fakebounds=types.ModuleType('MANUAL_FIRST_BAR_V1.grade_rows_v2');fakebounds.BoundsRows=Bounds;sys.modules[fakebounds.__name__]=fakebounds
path=O/'run_manual_spring_push_v1.py';tree=ast.parse(path.read_text(encoding='utf-8'));mainnode=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');fornode=next(n for n in ast.walk(mainnode)if isinstance(n,ast.For));forline=fornode.lineno
spec=importlib.util.spec_from_file_location('actual_release_entry_admission',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
actualclass=m.MiniHop;latest={}
def ctor(*a,**kw):
 count['actual_new_ctor']+=1;h=actualclass(*a,**kw);latest['hop']=h;return h
m.MiniHop=ctor
record_original=binding.record

def track_record(p):
 if Path(p).resolve()==binding.DATA_PATH.resolve():count['data_records']+=1
 return record_original(p)
binding.record=track_record
class PreloopStop(BaseException):pass

def tracer(frame,event,arg):
 if event=='line'and frame.f_code is m.main.__code__and frame.f_lineno==forline:raise PreloopStop('EXPECTED_PRELOOP_STOP_NOT_TRIAL')
 return tracer

cfg=dict(scene='flat',forward_m_s=.1,brake_at_s=4.,duration_s=5.,end_gain_file='TALL_ROUGH_BANK_V1/gain_delta20.json',landing_gain={'file':'TALL_ROUGH_BANK_V1/gain_delta0.json'},seed=0,nominal=True,start_x_m=0.,hop=json.loads((O/'PREEXEC_UNIT_PLAN.json').read_bytes())['config'])
status='FAIL_FIRST_ENTRY_ATTEMPT';err=None
try:
 with contextlib.redirect_stdout(io.StringIO())as helptext:
  sys.argv=[str(path),'--help']
  try:m.main()
  except SystemExit as e:check(e.code==0,'actual argparse help')
 count['help']+=1;(A/'help.txt').write_text(helptext.getvalue(),encoding='utf-8');check(count['fake_plant']==0 and count['data_records']==0,'help no plant/data')
 for name,flag in(('default_off',False),('enabled',True)):
  c=copy.deepcopy(cfg)
  if flag:c['hop']['release_spring_compensation_during_push']=True
  p=A/(name+'_config.json');p.write_text(json.dumps(c),encoding='utf-8');out=A/name;data_before=count['data_records']
  sys.argv=[str(path),'--config',str(p),'--out',str(out)];sys.settrace(tracer)
  try:m.main()
  except PreloopStop:pass
  else:check(False,'must stop before first loop')
  finally:sys.settrace(None)
  h=latest['hop'];v=json.loads((out/'SOURCE_MANIFEST.json').read_bytes());e=json.loads((out/'ERROR.json').read_bytes())
  check(h.spring_release_active is flag,'actual ctor enabled not cfg-only');check(v['kind']=='NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN'and v['config']==c,'manifest kind/full actual cfg')
  check(v['spring_release_requested']is flag,'requested flag metadata')
  check(v['relative_V3_push_flight_capture_equations_unchanged']is False and v['only_push_nominal_spring_ff_changed']is True and v['flight_and_capture_equations_unchanged']is True,'honest equations metadata')
  check(v['nominal_gas_endpoint_data_SHA']==(binding.EXPECTED_DATA_SHA if flag else None),'actual data SHA/None off')
  check(count['data_records']-data_before==(1 if flag else 0),'default off no compensation read')
  check(e['controls']==0 and e['physics_steps']==0 and e['trace_prefix']['actual_prefix_matches_producer']and e['physics_prefix']['actual_prefix_matches_producer'],'expected empty raw prefixes')
  check((out/'trace.jsonl').stat().st_size==(out/'physics.jsonl').stat().st_size==0,'empty files preserved')
  observed.append(dict(name=name,actual_ctor_active=h.spring_release_active,manifest=v,expected_error=e))
 # Five typed/binding cases total: one exercises actual main and its prefix path.
 bad=copy.deepcopy(cfg);bad['hop']['release_spring_compensation_during_push']=True;bad['end_gain_file']='TALL_ROUGH_BANK_V1/gain_delta0.json';p=A/'badsource_config.json';p.write_text(json.dumps(bad),encoding='utf-8');out=A/'badsource';n=count['fake_plant'];sys.argv=[str(path),'--config',str(p),'--out',str(out)]
 typed+=1
 try:m.main()
 except ValueError:check(count['fake_plant']==n and(out/'ERROR.json').exists()and(out/'trace.jsonl').stat().st_size==0,'bad source fails before plant, prefix kept')
 else:check(False,'bad source must fail')
 for name,field,value in(('bad_flag','release_spring_compensation_during_push',1),('AIR_excluded','air_pitch_reference_enable',True)):
  c=copy.deepcopy(cfg);c['hop']['release_spring_compensation_during_push']=True;c['hop'][field]=value;typed+=1
  try:binding.prepare(c)
  except ValueError:check(True,name)
  else:check(False,name)
 c=copy.deepcopy(cfg);c['hop']['release_spring_compensation_during_push']=True;original_path=binding.DATA_PATH;tmp=A/'bad_data.json';tmp.write_text('{}',encoding='utf-8');binding.DATA_PATH=tmp;typed+=1
 try:
  try:binding.prepare(c)
  except ValueError:check(True,'bad data SHA')
  else:check(False,'bad data accepted')
 finally:binding.DATA_PATH=original_path
 b=binding.prepare(c);start=loader.arrays(json.loads((ROOT/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch']);start['q']=start['q'].copy();start['q'][3]+=.001;end=load_gain(ROOT/c['end_gain_file']);land=loader.load_landing_gain(c['landing_gain']);typed+=1
 try:binding.ctor_kwargs(b,start,end,land)
 except ValueError:check(True,'actual loaded endpoint pose binding')
 else:check(False,'bad loaded q accepted')
 # Static result schema: there is intentionally NO fabricated result.json trial.
 resultnode=next(n for n in ast.walk(mainnode)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets));keys={k.arg:k.value for k in resultnode.value.keywords}
 check(ast.unparse(keys['spring_release_enabled'])=='bool(hop.spring_release_active)'and 'nominal_gas_endpoint_data_SHA'in keys,'result actual-hop schema')
 check(count['fake_plant']==2 and count['actual_new_ctor']==2 and count['fake_DR']==2,'only two fake bootstrap/actual ctor contexts')
 check(typed==5 and count['Geometry_wheel_kinematics']==count['MuJoCo']==count['actuator']==count['sensor_packet']==count['loop_body']==0,'entry all forbidden counts zero')
 status='PASS_ACTUAL_ENTRY_HELP_AND_FAKE_PRELOOP_ONLY_NOT_MODEL_ADMISSION'
except BaseException:err=traceback.format_exc()
finally:binding.record=record_original;sys.settrace(None);sys.meta_path.remove(blocker)
result=dict(status=status,error=err,checks=checks,typed_binding_cases=typed,counts=count,real_model_boots=0,real_DR_samples=0,real_geometry_calls=0,expected_partial_errors_not_trials=True,large_asset_manifest_stubbed=True,result_schema_static_only=True,entry_SHA=hashlib.sha256(path.read_bytes()).hexdigest(),harness_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),contexts=observed)
with(O/'ENTRY_RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps({k:v for k,v in result.items()if k!='contexts'},indent=2))
if err:raise SystemExit(1)
