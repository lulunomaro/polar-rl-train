"""Fresh synthetic CPU only. No checkpoint, saved raw, SDK, remote or CUDA access."""
from pathlib import Path
import ast,hashlib,importlib.metadata as md,importlib.util,json,math,sys,traceback
import torch
from tensordict import TensorDict
from e2_original_profile_catalog_candidate_v1 import classify,transition_phase
from e2_profile_domain_telemetry_v1 import E2Book
from lossless_snapshot_pinned75d683 import LosslessSnapshot
B=Path(__file__).resolve().parent;L=B.parent;checks=[]
def ok(name,value):assert bool(value),name;checks.append(name)
def rejected(name,f):
 try:f()
 except (AssertionError,TypeError):checks.append(name);return
 raise AssertionError('Negative case accepted: '+name)
def function(path,name,scope):
 tree=ast.parse(path.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope);return scope[name]
def context(n,key=9,uid=0,episode=0,phase=1,heading=0.,xy=None,reference=.5,written_phase=0.,written_valid=True):
 return dict(key=torch.full((n,),key,dtype=torch.long),phase=phase,episode=torch.full((n,),episode,dtype=torch.long),command_uid=torch.full((n,),uid,dtype=torch.long),before_xy=torch.zeros(n,2) if xy is None else xy,reference_projection=torch.full((n,),reference),direction=torch.zeros(n),signed_yaw=torch.full((n,),4. if key in (5,7,9) else -4.),written_phase=torch.full((n,),written_phase),written_phase_valid=torch.full((n,),written_valid,dtype=torch.bool))
def after(n,delta,xy):return dict(errors=[torch.zeros(n) for _ in range(3)],heading_delta=torch.full((n,),delta),xy=xy)
def main():
 assert not torch.cuda.is_initialized();torch.set_num_threads(2)
 standing=torch.zeros(10,dtype=torch.bool);standing[0]=True;pure=torch.zeros_like(standing);pure[4:8]=True;moving=torch.zeros_like(standing);moving[8:]=True;transition=torch.zeros_like(standing);transition[6:8]=True
 command=torch.zeros(10,3);command[1,0]=-1;command[3,0]=1;signed=torch.tensor([0,0,0,0,-1,1,-1,1,-4,4.])
 key=classify(torch,standing,pure,moving,transition,command,signed);ok('all ten E2 original mode labels exact',torch.equal(key,torch.arange(10)))
 wrong=standing.clone();wrong[8]=True;rejected('overlapping standing/moving rejected',lambda:classify(torch,wrong,pure,moving,transition,command,signed))
 wrong=transition.clone();wrong[9]=True;rejected('transition outside pure rejected',lambda:classify(torch,standing,pure,moving,wrong,command,signed))
 ok('phase exact boundary right bucket',torch.equal(transition_phase(torch,torch.tensor([0.,.99,1.,4.,5.,6.,7.,10.,11.,12.,15.])),torch.tensor([0,0,1,2,3,4,5,6,7,8,8])))
 src=L/'E2_PPO50_gas400_source_preparation_20261028/runtime_candidate_v1/isaac/mod4'
 scope={'torch':torch};body=function(src/'spin_translation_math.py','body_command',scope);transition_yaw=function(src/'e2_directional_spin_runtime_v1.py','transition_yaw',{'torch':torch})
 angles=torch.arange(10000,dtype=torch.float64)*(2*math.pi/10000);vx,vy=body(.5,torch.zeros_like(angles),angles)
 reference=vx*torch.cos(angles)-vy*torch.sin(angles)
 ok('original body command is cosine, world projection cosine squared',torch.allclose(reference,torch.cos(angles)**2))
 ok('complete ideal cycle average .5',abs(float(reference.mean())-.5)<1e-12)
 ok('instant absolute error from .5 nonzero even ideal body tracking',float((reference-.5).abs().mean())>.31)
 ok('original transition reversal exact',torch.equal(transition_yaw(torch.tensor([0.,1.,4.,5.,6.,7.,10.,11.,12.]),torch.ones(9)),torch.tensor([0.,1.,1.,0.,0.,-1.,-1.,0.,0.])))
 n=2;book=E2Book(torch,n,'cpu',['timeout']);no=torch.zeros(n,dtype=torch.bool);xy=torch.zeros(n,2)
 for i in range(80):
  c=context(n,xy=xy.clone());xy[:,0]+=.01;book.observe(c,after(n,.08,xy),no,no,[no])
 row=next(x for x in book.summary() if x['phase']=='steady' and x['profile']==9)
 ok('same command cycle has two unique env, two windows',row['unique_env_with_sampled_window']==2 and row['complete_sampled_window_events']==2)
 ok('actual displacement/time cycle progress .5',abs(row['actual_cycle_projected_progress_m_s']-.5)<2e-6)
 ok('reference comparison separate from body error',row['body_forward_MAE']==0 and row['nominal_half_m_s_cycle_abs_error_time_weighted']<2e-6)
 for name,boundary in [('command UID',dict(uid=1)),('episode UID',dict(episode=1)),('profile sign',dict(key=8)),('warm/steady',dict(phase=0))]:
  b=E2Book(torch,1,'cpu',[]);xy=torch.zeros(1,2)
  for i in range(60):
   c=context(1,xy=xy.clone(),**(boundary if i>=30 else {}));xy[:,0]+=.01;b.observe(c,after(1,.11,xy),torch.zeros(1,dtype=torch.bool),torch.zeros(1,dtype=torch.bool),[])
  ok(name+' boundary prevents mixed cycle credit',int(b.windows.sum())==0)
 b=E2Book(torch,1,'cpu',[]);xy=torch.zeros(1,2)
 for i in range(60):
  c=context(1,xy=xy.clone());xy[:,0]+=.01;b.observe(c,after(1,.11,xy),torch.tensor([i==29]),torch.tensor([False]),[])
 ok('terminated boundary prevents mixed cycle',int(b.windows.sum())==0)
 b=E2Book(torch,1,'cpu',[]);c=context(1,key=7,written_valid=False);b.observe(c,after(1,0.,torch.zeros(1,2)),torch.tensor([False]),torch.tensor([False]),[]);ok('initial unknown written phase not fabricated',int(b.phase_count.sum())==0)
 c=context(1,key=7,written_phase=6.);b.observe(c,after(1,0.,torch.zeros(1,2)),torch.tensor([False]),torch.tensor([False]),[]);ok('cached actual phase records reverse ramp bucket',int(b.phase_count[1,4,1,0])==1)
 snap=LosslessSnapshot(torch,3,torch.tensor([0,2]));fresh=TensorDict({'policy':torch.arange(6).reshape(3,2),'nested':TensorDict({'x':torch.ones(3,1)},batch_size=[3])},batch_size=[3]);v=snap._snapshot(fresh)
 ok('real local TensorDict recursive selected batch',v['snapshot_batch_size']==[2] and v['entries']['policy']['value']==[[0,1],[4,5]] and v['entries']['nested']['entries']['x']['shape']==[2,1])
 v=snap._snapshot({1:torch.ones(3),'1':torch.zeros(3),(1,'x'):True});ok('typed keys preserve int string tuple without collision',[x['key']['kind'] for x in v['entries']]==['int','str','tuple'])
 rng=torch.arange(16,dtype=torch.uint8);ok('private RNG bytevector not selected',snap._snapshot({'rng':rng})['rng']['shape']==[16]);rejected('unknown domain type explicit error',lambda:snap._snapshot(object()))
 spec=importlib.util.spec_from_file_location('fresh_E2_worker_guard',B/'evaluate_E2_adapted93_new86_frozen900_once_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 task=dict(kind='MOD4_E2_ADAPTED93_NEW86_FROZEN_PROFILE_DOMAIN_V1',source_SHA=m.MODEL_SHA,num_envs=20000,controls=900,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,actual_target86_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=True,canonical72_known_owner_readonly_passed=True,domain_kind='E2_WORLD_MOVING_SIGNED4',original_Adam=859300,original_LR=.00022500000000000002);m.guard(task);checks.append('E2 declared Task positive')
 for key,value in [('original_LR',6.666666666666667e-5),('original_Adam',857460),('domain_kind','W35'),('no_optimizer_steps',False),('controls',1200),('source_SHA','0'*64)]:rejected('wrong Task '+key,lambda k=key,v=value:m.guard(dict(task,**{k:v})))
 parsed=[]
 for p in sorted(B.glob('*.py')):ast.parse(p.read_bytes());parsed.append(p.name)
 ok('source metadata CPU does not decode PT','torch.load(' not in (B/'E2_new86_target_source_SDK_metadata_admission_v1.py').read_text())
 ok('worker never learner/backward/optimizer step',not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('learn','backward','step') and not(x.func.attr=='step' and isinstance(x.func.value,ast.Name) and x.func.value.id=='vec') for x in ast.walk(ast.parse((B/'evaluate_E2_adapted93_new86_frozen900_once_v1.py').read_bytes()))))
 ok('CPU synthetic only CUDA remains uninitialized',not torch.cuda.is_initialized())
 value=dict(passed=True,checks=checks,count=len(checks),AST_files=parsed,local_torch=torch.__version__,local_tensordict=md.version('tensordict'),actual_target_tensordict_expected='0.14.1',local_version_differs_target=True,target_API_actual_pending=True,no_PT_raw_NPZ_savedmodel_SDK_remote_GPU_calls=True)
 with (B/'reports/E2_FRESH_SYNTHETIC_CPU_AND_SOURCE_AST_ACTUAL_V1.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(dict(passed=True,checks=len(checks),source_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/E2_FRESH_SYNTHETIC_CPU_ORIGINAL_ERROR_V1.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,traceback=traceback.format_exc(),no_model_or_remote=True),f,indent=2)
  raise
