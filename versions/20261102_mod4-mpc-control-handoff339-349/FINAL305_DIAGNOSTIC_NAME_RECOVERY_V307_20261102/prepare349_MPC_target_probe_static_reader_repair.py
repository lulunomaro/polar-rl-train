"""Independent pre-deploy fix: remove copied actor assertion from the no-NN probe."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,sys,time
P=Path(__file__).resolve().parent;T=P.parent
S=T/'MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V348_20261102'
D=T/'MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V349_20261102'
R=P/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
assert not list((S/'reports').glob('*CONSUMED*'))
old=(S/'source/evaluate348.py').read_text('utf8')
assert 'assert all(torch.equal(value,actor.state_dict()[key])for key,value in weights.items())'in old
put(R/'LOCAL348_UNUSED_ACTOR_ASSERT_STATIC_DEFECT.json',dict(epoch=time.time(),source=str(S/'source/evaluate348.py'),SHA=H(S/'source/evaluate348.py'),executed=False,network=0,SDK=0,model_reads=0,physics=0,defect='Copied final actor immutability assertion refers to removed actor/weights in no-NN probe; caught before deployment.',repair='Independent349 removes stale assertion and captures actual requested/applied targets and current motor states. Original348 frozen package preserved.'))
D.mkdir(exist_ok=False);(D/'reports').mkdir()
def rename(s):return re.sub(r'(?<=[A-Za-z_])348(?!\d)','349',s)
for path in sorted(S.rglob('*')):
    if not path.is_file()or'__pycache__'in path.parts or path.name.startswith('INDEX348')or'reports'in path.relative_to(S).parts:continue
    dest=D/rename(str(path.relative_to(S)));dest.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix in('.py','.json'):dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
    else:shutil.copyfile(path,dest)
worker=(D/'source/evaluate349.py').read_text('utf8')
worker=worker.replace(' assert all(torch.equal(value,actor.state_dict()[key])for key,value in weights.items())'," assert TASK['model_byte_reads']==TASK['model_decodes']==0")
worker=worker.replace(" real.reset();obs=vec.get_observations();active=", " real.reset();put('ACTUAL349_INITIAL_PHYSX_STATE.json',dict(root13=tensor(robot.data.root_state_w).cpu().tolist(),q=tensor(robot.data.joint_pos).cpu().tolist(),dq=tensor(robot.data.joint_vel).cpu().tolist(),joint_names=list(robot.joint_names),all80_same_planned_initial=True,DR_same_distribution_not_matched=True));obs=vec.get_observations();active=")
worker=worker.replace("   force=captured['wheel_forces'][selected].cpu().numpy(),action=action[selected].cpu().numpy(),depth=d[selected].cpu().numpy()))", "   force=captured['wheel_forces'][selected].cpu().numpy(),action=action[selected].cpu().numpy(),depth=d[selected].cpu().numpy(),motor_q=captured['motor_q'][selected].cpu().numpy(),motor_dq=captured['motor_dq'][selected].cpu().numpy(),motor_pos_target=captured['motor_pos_target'][selected].cpu().numpy(),motor_vel_target=captured['motor_vel_target'][selected].cpu().numpy()))")
worker=worker.replace("  for i in torch.where(done&active)[0].cpu().tolist():", "  mids=[robot.joint_names.index(n)for n in('left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin')]\n  captured.update(motor_q=tensor(robot.data.joint_pos)[:,mids].detach().clone(),motor_dq=tensor(robot.data.joint_vel)[:,mids].detach().clone(),motor_pos_target=tensor(robot.data.joint_pos_target)[:,mids].detach().clone(),motor_vel_target=tensor(robot.data.joint_vel_target)[:,mids].detach().clone())\n  for i in torch.where(done&active)[0].cpu().tolist():")
worker=worker.replace("   action6=np.stack([f['action'][j]for f in frames[:count]]),depth9=np.stack([f['depth'][j]for f in frames[:count]]))", "   action6=np.stack([f['action'][j]for f in frames[:count]]),depth9=np.stack([f['depth'][j]for f in frames[:count]]),motor_q=np.stack([f['motor_q'][j]for f in frames[:count]]),motor_dq=np.stack([f['motor_dq'][j]for f in frames[:count]]),motor_pos_target=np.stack([f['motor_pos_target'][j]for f in frames[:count]]),motor_vel_target=np.stack([f['motor_vel_target'][j]for f in frames[:count]]))")
assert 'actor.state_dict'not in worker and 'torch.load('not in worker and 'actor('not in worker
assert 'ACTUAL349_INITIAL_PHYSX_STATE.json'in worker and 'motor_q=np.stack'in worker
(D/'source/evaluate349.py').write_text(worker,encoding='utf8')
task=read(D/'TASK349_FROZEN.json');task['worker_SHA']=H(D/'source/evaluate349.py');task['planned_motor_control']['SHA']=H(D/'planned_mpc_motor349.json');task['planned_motor_control']['bytes']=(D/'planned_mpc_motor349.json').stat().st_size
(D/'TASK349_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for path in D.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
ns={};exec(compile((D/'contract349.py').read_text('utf8'),str(D/'contract349.py'),'exec'),ns);assert ns['validate_task'](task)
probe="from pathlib import Path\np=Path("+repr(str(D/'source/evaluate349.py'))+")\ns=p.read_text('utf8');exec(compile(s[:s.index('p=argparse.ArgumentParser()')],str(p),'exec'),dict(__file__=str(p)))\nprint('PASS')"
checked=subprocess.run([sys.executable,'-B','-X','utf8','-c',probe],cwd=D/'source',capture_output=True,text=True,encoding='utf8',check=True)
assert checked.stdout.strip()=='PASS'
files=[path for path in sorted(D.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
index=D/'INDEX349_SOURCE_TASK_CALLERS_FROZEN.json';put(index,dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in files]))
put(R/'STATIC349_MPC_MOTOR_TARGET_COMPARISON.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(index),SDK=0,NN=0,network=0,GO=0,initialstate_all80_matched=True,source100to50_diagnostic_limit=True,original_physics_queue_PD_preserved=True))
print(json.dumps(dict(passed=True,root=str(D),INDEX_SHA=H(index),SDK=0,NN=0,GO=0)))
