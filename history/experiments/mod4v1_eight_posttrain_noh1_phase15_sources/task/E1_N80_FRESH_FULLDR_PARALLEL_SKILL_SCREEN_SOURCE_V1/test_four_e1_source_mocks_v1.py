"""SOURCE_ONLY syntheticstdlib MOCK, not PT/Torch/SDK/API execution."""
from pathlib import Path
import ast,copy,hashlib,json
from e1_group_scope import KIND,validate_group_task,wait_group_start
from e1_identity_cache import WholeCheckpointIdentityCache
from e1_endpoint_predicate import EndpointPredicate,support_from_8
B=Path(__file__).resolve().parent;contracts=json.loads((B/'ROLE_CONTRACTS.json').read_bytes());checks=[]
def C(name,x):assert x,name;checks.append(name)
def raises(fn):
 try:fn()
 except (AssertionError,ValueError,TimeoutError,RuntimeError):return True
 return False
class Tensor:
 def __init__(self,v,shape=()):self.v=copy.deepcopy(v);self.shape=shape;self.dtype='float32'
 def detach(self):return self
 def clone(self):return Tensor(self.v,self.shape)
 def item(self):return self.v
 def tolist(self):return copy.deepcopy(self.v)
 def __getitem__(self,k):raise AssertionError('No saved20k tensorindex/slice allowed in syntheticidentityMOCK')
class Torch:
 def __init__(self,root):self.root=root;self.loads=0
 def load(self,buf,**kw):self.loads+=1;assert buf.read()==b'SYNTHETIC_JSON_FIXTURE_NOT_MODEL';return self.root
 def is_tensor(self,x):return isinstance(x,Tensor)
 def equal(self,a,b):return a.v==b.v and a.shape==b.shape

def root_for(meta):
 a={f'mlp.{layer}.{name}':Tensor(1,((256,35) if layer==0 and name=='weight' else (1,))) for layer in (0,2,4,6) for name in ('weight','bias')};a['distribution.std_param']=Tensor(meta['original_STD6'],(6,))
 c={f'mlp.{layer}.{name}':Tensor(1,((256,38) if layer==0 and name=='weight' else (1,))) for layer in (0,2,4,6) for name in ('weight','bias')}
 return dict(actor_state_dict=a,critic_state_dict=c,optimizer_state_dict=dict(state={i:dict(step=Tensor(meta['original_17Adam_step']),exp_avg=Tensor(0)) for i in range(17)},param_groups=[dict(lr=meta['original_LR'],params=list(range(17)))]),iter=meta['original_iteration'],saved20k_unknown=dict(n=20000,unsliced=Tensor('20k_history',(20000,4))),unknown_root={'unknown_nested':['kept']})
for role,c in contracts.items():
 meta=c['core'];root=root_for(meta);fake=Torch(root);payload=b'SYNTHETIC_JSON_FIXTURE_NOT_MODEL';reads=[]
 cache=WholeCheckpointIdentityCache('SYNTHETIC.fixture.json',fake,expected_metadata=meta,expected_SHA=hashlib.sha256(payload).hexdigest(),expected_bytes=len(payload),read_bytes=lambda p:(reads.append(p) or payload))
 C(role+' oncewholemockcache',len(reads)==1 and fake.loads==1 and cache.SHA_calls==1)
 C(role+' rawroot allunknown preserved',cache.assert_entire_root_unchanged() and 'unknown_root' in cache.metadata['rootkeys'])
 C(role+' physicalhistory notexposed',raises(lambda:cache.core('saved20k_unknown')))
 C(role+' criticAdamLRiter cached notlive',cache.metadata['iteration']==meta['original_iteration'] and set(cache.metadata['Adam17'])=={meta['original_17Adam_step']})
 root['unknown_root']['unknown_nested'].append('bad');C(role+' unknownnestedmutation caught',raises(cache.assert_entire_root_unchanged));root['unknown_root']['unknown_nested'].pop()
 root['critic_state_dict']['mlp.0.weight'].v=2;C(role+' criticmutation caught',raises(cache.assert_entire_root_unchanged));root['critic_state_dict']['mlp.0.weight'].v=1
 C(role+' complete rootrestoredidentity',cache.assert_entire_root_unchanged())
 task=dict(kind=KIND,purpose=KIND,role=role,group_id='TEST_GROUP',GPU_UUID='GPU-TEST',num_envs=80,seed=20260928,optimizer_updates=0,fresh_fullDR_cohort=True,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,gas_N=400,stiffness_N_m=2000,source_SHA=c['source']['SHA'],source_bytes=c['source']['bytes'],controls=c['controls'],physics_callbacks=c['controls']*8,feedback_samples=c['controls']*2,absolute_worker_deadline_epoch=9999999999,actual_group_admission=dict(group_id='TEST_GROUP',GPU_UUID='GPU-TEST',source_SDK_admitted=True,private_GPU_EX_held=True,global_finite_EX_held=True,inherited_lock_fds=[7,8]))
 C(role+' parentgroupfdcontract',validate_group_task(task,role,B,B/'MOCK_CASE',contracts,environment={'CUDA_VISIBLE_DEVICES':'GPU-TEST'},fd_check=lambda n:None))
 bad=copy.deepcopy(task);bad['saved20k_DR_physically_applied']=True;C(role+' nofake20krestore',raises(lambda:validate_group_task(bad,role,B,B/'MOCK_CASE',contracts,environment={'CUDA_VISIBLE_DEVICES':'GPU-TEST'},fd_check=lambda n:None)))
 C(role+' wrongGPUcaught',raises(lambda:validate_group_task(task,role,B,B/'MOCK_CASE',contracts,environment={'CUDA_VISIBLE_DEVICES':'GPU-WRONG'},fd_check=lambda n:None)))
 marker=dict(group_id='TEST_GROUP',GPU_UUID='GPU-TEST',members=list(contracts),all_members_ready=True)
 reply=wait_group_start(task,B,now=lambda:0.,pause=lambda x:(_ for _ in ()).throw(AssertionError('No waitneeded')),read_json=lambda p:None if p.name=='GROUP_STARTUP_ABORT.json' else marker)
 C(role+' readybarrierzerophysicsactorRNG',reply['no_actor_or_physics_or_RNG_calls'])
 C(role+' abortnoretry',raises(lambda:wait_group_start(task,B,now=lambda:0.,pause=lambda x:None,read_json=lambda p:{'abort':True} if p.name=='GROUP_STARTUP_ABORT.json' else None)))
 clock=iter([0.,901.]);C(role+' barrier900timeout',raises(lambda:wait_group_start(task,B,now=lambda:next(clock),pause=lambda x:None,read_json=lambda p:None)))
for edge,label in [(.275,'curb'),(1.2,'slope')]:
 p=EndpointPredicate(edge);ep=[0]*80;before=[[-edge-.1,-edge-.1] if i%3!=1 else [edge+.1,edge+.1] for i in range(80)];after=[[-x for x in row] for row in before];support=[[True,True]]*80
 p.observe(0,ep,before,support,[False]*80);p.observe(1,ep,after,support,[False]*80);out=p.finish()
 C(label+' exact27up27down26stand',out['groups']['ascending']['contact_confirmed_envs']==27 and out['groups']['descending']['contact_confirmed_envs']==27 and out['groups']['stand']['environments']==26 and out['groups']['stand']['contact_confirmed_envs']==0)
 p=EndpointPredicate(edge);p.observe(0,[0]*80,before,support,[False]*80);p.observe(1,[1]*80,after,support,[False]*80);C(label+' resetnotstitched',sum(x['contact_confirmed'] for x in p.finish()['rows'])==0)
 p=EndpointPredicate(edge);p.observe(0,ep,before,support,[False]*80);p.observe(1,ep,after,support,[True]*80);C(label+' firstfailureprefixcuts',sum(x['contact_confirmed'] for x in p.finish()['rows'])==0)
C('eightcallbacks>1Noriginalsupport',support_from_8([2.]*8) and not support_from_8([1.]*8))
# No moduleimportingSDK/Torch atsource-test time andchilddoesnotflock/nvidia/GO.
s=(B/'e1_parallel_worker_safe.py').read_text(encoding='utf-8');C('no childGPUacquirequery',all(x not in s for x in ('nvidia-smi','fcntl.flock','GO_PRODUCTION')))
for p in B.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
with (B/'FOUR_E1_SOURCE_ONLY_MOCK_PROOF_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SYNTHETIC_STDLIB_ONLY_NOT_PT_OR_TORCH_OR_SDK',passed=True,check_count=len(checks),checks=checks,PT_model_stat_read_hash_decode=0,SDK_GPU_SSH_GO_canonical_PPO=0,old29MOCK_reexecutions=0),f,indent=2)
print(json.dumps(dict(MOCK_ONLY=True,passed=True,checks=len(checks),model_SDK_operations=0),indent=2))
