"""Finish386 local preparation; freeze384RL and its sole postround with new CPU384."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V384_20261102';Q=T/'RESIDUAL_RL384_POSTROUND_V386_20261102';E=T/'RESIDUAL_RL384_INDEPENDENT_EVAL_V386_20261102';OLD=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
put(P/'reports/LOCAL386_POSTROUND_PREPARER_FAILURE.json',dict(epoch=time.time(),passed=False,error='NameError:H not defined at pendingfinaltask construction',source=str(P/'prepare386_RL384_eval_postround.py'),exitcode=1,network=0,SDK=0,model_reads=0,GO=False,partial_sources_preserved=True,repair='387 finishes local pendingtask andpostround;allpreGOunfrozen'))
cpu=json.loads((N/'reports/CPU384_RESIDUAL_RL_NO_STEP.json').read_bytes());assert cpu['passed']and cpu['learner_SHA']==H(N/'source/tracking_learner384.py')and cpu['optimizer_steps']==0
# Ensure precise read scope, planned reset, actual contact eval independent of controller.
p=E/'source/evaluate386.py';s=p.read_text('utf8').replace('"""40 matched D0-D7 pairs: source vs bounded air-wheel request; zero NN."""','"""Frozen RL384 actor + fixed command baseline, actual270manifold evaluation."""').replace('source_model_byte_read_admission=0','source_model_byte_read_admission=1')
s=s.replace("'ACTUAL386_ZERO_MODEL_AND_CONTROL_SCOPE.json'","'ACTUAL386_RL_ACTOR_AND_CONTROL_SCOPE.json'")
p.write_text(s,encoding='utf8')
task=json.loads((OLD/'TASK377_FROZEN.json').read_bytes());task.update(kind='FROZEN384_RESIDUAL_RL_EVAL386',source_run='PENDING_RL384_FINAL',max_controls=400,model_byte_reads=1,model_decodes=1,worker_SHA=H(E/'source/evaluate386.py'),human_request='Independent learnedRL384 actoronly actual270manifold80episodes,noonlineMPC',RL_residual=True,online_MPC=False)
task['reference']=json.loads((N/'TASK384_PREPARE.json').read_bytes())['reference'];put(E/'TASK386_PENDING_FINAL_IDENTITY.json',task)
# Exact local postround parent may synchronously wait for this own finite child.
# It has no SSH and cannot dispatch a second controller while blocked in run().
p=E/'run386_eval_once.py';s=p.read_text('utf8');old="    assert len(rows)==1 and rows[0]['ProcessId']==os.getpid() and rows[0]['ExecutablePath'].lower()==sys.executable.lower()"
new="""    own=[row for row in rows if row['ProcessId']==os.getpid()]
    other=[row for row in rows if row['ProcessId']!=os.getpid()]
    assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower()
    allowed=os.environ.get('MOD4_386_OWN_POSTROUND_PARENT_PID')
    if other:
        assert allowed and len(other)==1 and other[0]['ProcessId']==int(allowed)
        import psutil
        actual=psutil.Process(int(allowed));assert actual.pid==os.getppid()
        assert actual.exe().lower()==sys.executable.lower()and actual.cmdline()[-1].replace('\\\\','/').endswith('/postround386_close_RL384_eval_once.py')
        assert str(actual.create_time())==os.environ['MOD4_386_OWN_POSTROUND_PARENT_CREATE']
"""
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8')
# FinalfullCPU additionally proves origin actor/protocol saved; it reads final once.
p=N/'review384_NEW_final_whole_CPU_UNUSED_once.py';s=p.read_text('utf8');needle="    assert ck['kind']=='REFERENCE_TRACKING_BPTT384_COMPLETE'"
s=s.replace(needle,needle+"\n    assert ck['residual_RL']and ck['student']['RL_residual']and not ck['student']['online_MPC']\n    assert ck['student']['residual_origin_actor_state_dict']['mlp.0.weight'].shape==(128,103)\n    assert ck['student']['residual_policy_protocol']['radius']==1.")
p.write_text(s,encoding='utf8')
# Task signed contract includes residual scope; source weights/threeAdam untouched.
task=json.loads((N/'TASK384_PREPARE.json').read_bytes());task['worker_SHA']=H(N/'source/worker384.py');task['CPU383_new_required']=False;task['CPU384_new_passed']=True;task['CPU384_SHA']=H(N/'reports/CPU384_RESIDUAL_RL_NO_STEP.json')
for p in(N/'teacher_task384.py',N/'tracking_task384.py',N/'source/teacher_task384.py',N/'source/tracking_task384.py',N/'control384/teacher_task384.py'):
 s=p.read_text('utf8').replace("reference_only=True,Fudan_objective_used=False", "residual_RL=True,residual_radius=1.,reference_only=True,Fudan_objective_used=False")
 s=s.replace("WM_ONLY=False,FROZEN_TEACHER=True", "WM_ONLY=False,FROZEN_TEACHER=True,residual_RL=True,residual_radius=1.,online_MPC=False")
 p.write_text(s,encoding='utf8')
put(N/'TASK384_FROZEN.json',task)
normal=[N/'normal384/normal384_common.py',N/'normal384/collect384_tracking_formal_cost_normal900_UNUSED_once.py',N/'teacher_task384.py']
put(N/'normal384/INDEX384_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in normal]))
spec=importlib.util.spec_from_file_location('RL384contract',N/'teacher_task384.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
for p in list(N.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(p.read_text('utf8'),filename=str(p))
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX384_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files,RL=True,online_MPC=False,source_actor_optimizer_fullrestore=True))
print(json.dumps(dict(passed=True,RL=True,root=str(N),index_SHA=H(N/'INDEX384_SOURCE_TASK_CALLERS_FROZEN.json'),CPU384=True,actor_gradient=cpu['synthetic_H8_direct_no_step']['actor_grad_norm'],GO=False)))
