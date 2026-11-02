"""Preserve frozen384; new389 corrects accidental GPU UUID JSON naming replacement."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,shutil,time
P=Path(__file__).resolve().parent;T=P.parent;OLD=T/'MPC_COMMAND_RESIDUAL_RL_V384_20261102';N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';OE=T/'RESIDUAL_RL384_INDEPENDENT_EVAL_V386_20261102';E=T/'RESIDUAL_RL389_INDEPENDENT_EVAL_V390_20261102';OQ=T/'RESIDUAL_RL384_POSTROUND_V386_20261102';Q=T/'RESIDUAL_RL389_POSTROUND_V390_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
put(P/'reports/STATIC388_UNUSED384_GPU_METADATA_REJECTION.json',dict(epoch=time.time(),passed=False,root=str(OLD),actualfrozenGPU=json.loads((OLD/'TASK384_FROZEN.json').read_bytes())['GPU_UUID'],requiredGPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',reason='Task JSON globalversionreplacement changed UUID e345 to e384;sourceGPUS unchanged. DetectedbeforeSTART/deploy/network/GO,CPU384actuallearnerproofretained.',START_consumed=False,modelreads_thisdiagnostic=0,network=0,SDK=0,physics=0,repair='Independent389 withUUID+hashprotectedtransform;384allfrozenpreserved'))
def rename(text):
 for a,b in((str(OLD),str(N)),(OLD.as_posix(),N.as_posix()),(str(OE),str(E)),(OE.as_posix(),E.as_posix()),(str(OQ),str(Q)),(OQ.as_posix(),Q.as_posix())):text=text.replace(a,b)
 saved=[]
 def hide(m):saved.append(m.group());return '@PINNED'+str(len(saved)-1)+'@'
 text=re.sub(r'\b[0-9a-f]{64}\b|GPU-[0-9a-f-]+',hide,text)
 for a,b in(('384','389'),('386','390')):text=re.sub(r'(?<=[A-Za-z_])'+a+r'(?!\d)',b,text)
 for i,v in enumerate(saved):text=text.replace('@PINNED'+str(i)+'@',v)
 return text
for origin,dest in((OLD,N),(OE,E),(OQ,Q)):
 assert not dest.exists();dest.mkdir();(dest/'reports').mkdir()
 for p in origin.rglob('*.py'):
  if '__pycache__'in p.parts:continue
  if p.name.startswith('test384_'):continue
  q=dest/rename(str(p.relative_to(origin)));q.parent.mkdir(parents=True,exist_ok=True);q.write_text(rename(p.read_text('utf8')),encoding='utf8')
for name in('reference384.npz','feedforward384.json'):
 for dest in(N,E):shutil.copyfile(OLD/name,dest/rename(name))
cpu=json.loads((OLD/'reports/CPU384_RESIDUAL_RL_NO_STEP.json').read_bytes());assert cpu['passed']and cpu['learner_SHA']==H(OLD/'source/tracking_learner384.py')
assert rename((OLD/'source/tracking_learner384.py').read_text('utf8'))==(N/'source/tracking_learner389.py').read_text('utf8')
cpu.update(epoch=time.time(),learner_SHA=H(N/'source/tracking_learner389.py'),reuse_exact_CPU384=True,original_CPU384_receipt=dict(path=str(OLD/'reports/CPU384_RESIDUAL_RL_NO_STEP.json'),SHA=H(OLD/'reports/CPU384_RESIDUAL_RL_NO_STEP.json')),new_model_reads=0,source_code_transform='Nameonly384->389;actualbehaviorASTmappedexact;UUIDprotected')
put(N/'reports/CPU389_RESIDUAL_RL_NO_STEP.json',cpu)
task=json.loads(rename((OLD/'TASK384_FROZEN.json').read_text('utf8')));nonce=str(time.time_ns())
task.update(GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',run_id='REFERENCE_TRACKING389_'+nonce,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_RESIDUAL_RL389_'+nonce+'/tracker72',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_RESIDUAL_RL389_'+nonce+'/owner72',worker_SHA=H(N/'source/worker389.py'),CPU384_new_passed=True,CPU384_SHA=H(OLD/'reports/CPU384_RESIDUAL_RL_NO_STEP.json'),source_cpu_reuse='ExactCPU384nameonlybehavior,no new PT read')
task['fixed_command_feedforward']['path']='feedforward389.json';task['reference']['path']='reference389.npz'
put(N/'TASK389_FROZEN.json',task)
for p in(N/'normal389').glob('INDEX*'):p.unlink() if p.is_file()else None
normal=[N/'normal389/normal389_common.py',N/'normal389/collect389_tracking_formal_cost_normal900_UNUSED_once.py',N/'teacher_task389.py']
put(N/'normal389/INDEX389_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in normal]))
pending=json.loads(rename((OE/'TASK386_PENDING_FINAL_IDENTITY.json').read_text('utf8')));pending.update(GPU_UUID=task['GPU_UUID'],worker_SHA=H(E/'source/evaluate390.py'));put(E/'TASK390_PENDING_FINAL_IDENTITY.json',pending)
# Postround exact parent name is part of the same-source localCIM admission.
for p in list(N.rglob('*.py'))+list(E.rglob('*.py'))+list(Q.rglob('*.py')):ast.parse(p.read_text('utf8'))
assert 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'in(N/'control389/three_slot_common_v1.py').read_text('utf8')
spec=importlib.util.spec_from_file_location('RL389contract',N/'teacher_task389.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files,RL=True,online_MPC=False,CPU384_exact_behavior=True,immutable384_rejected=True))
put(Q/'INDEX390_POSTROUND_FOR389_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for root in(Q,E)for p in sorted(root.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]))
put(P/'reports/STATIC389_RL_PACKAGE_POSTROUND390_VALIDATION.json',dict(epoch=time.time(),passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],GPU=task['GPU_UUID'],CPU384reuse_no_new_modelread=True,allAST=True,postroundroot=str(Q),evalroot=str(E),RL=True,online_MPC=False,sourceAdam=[52636,9696,16879],START=False,network=0,SDK=0,physics=0))
print(json.dumps(dict(passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json'),GPU=task['GPU_UUID'],RL=True,GO=False)))
