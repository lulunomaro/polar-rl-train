from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_DEPTH270_BOUND_SOURCE_V266_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
K=T/'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source'
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def ids(s):return re.sub(r'(?<![0-9])266(?![0-9])','267',s)
for p in (B/'source').glob('*.py'):
 if p.name.startswith('evaluate'):continue
 s=ids(p.read_text('utf8'))if p.name!='depth_stair263.py'else p.read_text('utf8')
 if p.name=='contract266.py':
  s=s.replace('NEW267_D435I_IDEAL_FORWARD_RAY_DEPTH_12CONTROLS_ZERO_PT','NEW267_OWN_FULLSTATE_DEPTH_64CONTROLS_FROZEN2135_ACTOR')
  s=s.replace("t['controls_per_case_max']==12 and t['controls_max']==12","t['controls_per_case_max']==64 and t['controls_max']==64")
  s=s.replace("t['model_byte_reads']==t['model_decodes']==0","t['model_byte_reads']==t['model_decodes']==1")
 if p.name.startswith('target'):
  s=s.replace('model_byte_reads_by_worker_max=0,model_decodes_max=0','model_byte_reads_by_worker_max=1,model_decodes_max=1')
  s=s.replace('controls_max=12,physics_max=96','controls_max=64,physics_max=512')
 (S/p.name.replace('266','267')).write_text(s,encoding='utf8')
c=ids((B/'run_ROOT266_NEW240_mean_regression_once.py').read_text('utf8'))
c=replace(c,"pattern='run_ROOT267_|","pattern='run_ROOT267_|run_ROOT266_|")
c=c.replace('num_envs=1,controls_per_case_max=12,controls_max=12,physics_callbacks_max=96,feedback_samples_max=24','num_envs=1,controls_per_case_max=64,controls_max=64,physics_callbacks_max=512,feedback_samples_max=128')
c=c.replace('model_byte_reads=0,model_decodes=0,model_copies=0','model_byte_reads=1,model_decodes=1,model_copies=0')
c=replace(c,'task=dict(kind=contract.KIND,','task=dict(run_id="OWN267_FROZEN2135_FULLSTATE_DEPTH",generation="NEW267_20261101",kind=contract.KIND,')
c=c.replace('GPU_model_byte_read_decode_max=0','GPU_model_byte_read_decode_max=1').replace('controls_max=12,physics_max=96,feedback_max=24','controls_max=64,physics_max=512,feedback_max=128')
c=c.replace('Sensor-only1env/12controls96physics24feedback, no PT/actor/optimizer.','N1/64controls512physics128feedback actual own fullstate+depth collector; one frozen2135 actor source read, no optimizer.')
(N/'run_ROOT267_NEW240_mean_regression_once.py').write_text(c,encoding='utf8')
getter=(K/'actual_DR_memory_getter_v1.py').read_text('utf8');assert getter.count('q.control_us==10000')==2 and getter.count('issue_tick%4==0')==1
getter=getter.replace('q.control_us==10000','q.control_us==20000').replace('issue_tick%4==0','issue_tick%8==0')
(S/'actual_DR_memory_getter267.py').write_text(getter,encoding='utf8')
(S/'compact_episode_static31_v1.py').write_bytes((K/'compact_episode_static31_v1.py').read_bytes())
w=ids((B/'source/evaluate266_front_depth_zero_PT_UNUSED_once.py').read_text('utf8'))
w=w.replace('import argparse,hashlib,json,os,runpy,sys,time,traceback','import argparse,hashlib,io,json,os,runpy,sys,time,traceback')
w=replace(w,'model_PT_ONNX_NN_or_optimizer=0','model_free_sensor_only=False,source_model_byte_read_admission=1,optimizer_steps=0')
begin=w.index(' actions=torch.zeros((1,6)');end=w.index('\nexcept BaseException:',begin)
tail=(N/'worker267_collector_tail_source.txt').read_text('utf8')
w=w[:begin]+tail+w[end:]
(S/'evaluate267_front_depth_zero_PT_UNUSED_once.py').write_text(w,encoding='utf8')
(S/'measured224_schema267.py').write_bytes((N/'measured224_schema267.py').read_bytes())
files=sorted(S.glob('*.py'))+[N/'run_ROOT267_NEW240_mean_regression_once.py',Path(__file__).resolve(),N/'worker267_collector_tail_source.txt',N/'measured224_schema267.py',N/'test267_new_measured_schema_CPU_once.py']
for p in files:
 if p.suffix=='.py':
  tree=ast.parse(p.read_text('utf8'),filename=str(p))
  for x in ast.walk(tree):
   if isinstance(x,ast.Attribute)and isinstance(x.value,ast.Name)and x.value.id=='hashlib':assert hasattr(hashlib,x.attr)
report=R/'ROOT267_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=sum(p.suffix=='.py'for p in files),original266_unchanged=True,source_interface='own state224=physical73+dynamic54+ownL0theta4+BODYcontacts93/400; raw full-component snapshots retained separately. Not a claim all sensor Markov memory is contained in224.',original_getter_change='Only20ms queue boundary/multiple8; no setter, random draw or backend parameter getter.',new_actual_models_read_max=1,model_decodes_max=1,controls=64,physics=512,feedback=128,actual_case_pending=True,learning=False))
put(N/'SOURCE267_FILES_BEFORE_NEW_CPU.json',dict(files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]]))
print(json.dumps(dict(passed=True,source_files=len(files))))
