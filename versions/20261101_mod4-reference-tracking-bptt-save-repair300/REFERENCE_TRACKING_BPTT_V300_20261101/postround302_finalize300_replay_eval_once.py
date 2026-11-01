"""Dedicated local timer for full original close, new tracking eval and replay."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=N/'postround302'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe';CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
def call(exe,args):
    p=subprocess.run([exe,'-B','-X','utf8',*map(str,args)],cwd=N,capture_output=True,text=True,encoding='utf8')
    if p.returncode:raise RuntimeError(dict(args=list(map(str,args)),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
    return dict(returncode=0,stdout=p.stdout,stderr=p.stderr)
def main():
    put('POSTROUND302_ONCE_CONSUMED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,scope='local wait, then one original close/fullCPU/evaluation/replay; no nextGO'))
    binding=json.loads((R/'ROOT300_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json').read_bytes());go=binding['current']['go']['jump_72']
    while time.time()<go['nominal_end_epoch']-898:time.sleep(min(10,go['nominal_end_epoch']-898-time.time()))
    normal=N/'normal300';index=normal/'INDEX300_NORMAL_SOURCE_FROZEN.json'
    put('POSTROUND300_NORMAL_COMMAND_RETURNED.json',call(CONTROL,[normal/'collect300_tracking_formal_cost_normal900_UNUSED_once.py','--root-lease-label','ROOT300_EXCLUSIVE_NORMAL900_POSTROUND_'+str(time.time_ns()),'--auth-provider',T.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py','--additional-control-pattern','run302_eval|launch300_|collect300_','--caller-index-SHA',H(index)]))
    put('POSTROUND300_CPU_COMMAND_RETURNED.json',call(CPU,[N/'review300_NEW_final_whole_CPU_UNUSED_once.py']))
    full=json.loads((R/'ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());complete=json.loads((R/'ROOT300_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert full['passed']
    E=T/'REFERENCE_TRACKING300_POSTROUND_EVAL_V302_20261101';E.mkdir(exist_ok=False);(E/'reports').mkdir()
    shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
    for p in(P/'eval302_source').glob('*.py'):shutil.copyfile(p,E/'source'/p.name)
    shutil.copyfile(P/'eval302_source/contract302.py',E/'contract302.py');shutil.copyfile(P/'run302_eval_once_template.py',E/'run302_eval_once.py')
    shutil.copyfile(T/'TEACHER286_REPLAY_EVAL_V288_20261101/source/wheel_geometry220.py',E/'source/wheel_geometry220.py')
    shutil.copyfile(N/'reference300.npz',E/'reference300.npz')
    task=json.loads((T/'TEACHER286_REPLAY_EVAL_V288_20261101/TASK288_FROZEN.json').read_bytes());original=json.loads((N/'TASK300_FROZEN.json').read_bytes())
    task.update(kind='FROZEN300_REFERENCE_TRACKING_EVAL302',model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['Pi'],source_run=original['run_id'],worker_SHA=H(E/'source/evaluate302.py'),reference=original['reference'],source_full_CPU_receipt_SHA=H(R/'ROOT300_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'))
    (E/'TASK302_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    put('POSTROUND300_EVAL_COMMAND_RETURNED.json',call(CONTROL,[E/'run302_eval_once.py']))
    result=json.loads((E/'reports/ROOT302_EVALUATION_FULL_RETURNED.json').read_bytes())['result']
    viewer=(P/'view302_actual_final300_replay_template.py').read_text('utf8').replace('policy_updates=2336','policy_updates='+str(full['Pi'])).replace('Pi2336 Critic2336','Pi'+str(full['Pi'])+' Critic'+str(full['critic']))
    viewer=viewer.replace('FAILED: bad_orientation; held-out stairs0/72; ground completed0/8',f"REFERENCE TRACKER: stable{result['strict_successes']}/80 / bothcross{result['crossed_cases']}/80; planned goals")
    vp=E/'view302_actual_final300_replay.py';vp.write_bytes(viewer.encode())
    with(E/'reports/VIEW302_CONSOLE.log').open('xb')as f:p=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe','-B','-X','utf8',str(vp)],cwd=E,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    with(E/'reports/VIEW302_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=p.pid,actual_recorded_replay=True),f,indent=2)
    decision='Review reference tracking errors and real replay; continue same tracking task only if actual task progress supports it, else target observed defect. Autonomous depth-only skill is separate.'
    put('POSTROUND300_REPLAY_EVAL_DECISION.json',dict(epoch=time.time(),status='COMPLETE_SAVE_REPLAY_EVAL_DECISION',model_SHA=full['SHA'],eval_root=str(E),strict_successes=result['strict_successes'],crossed_cases=result['crossed_cases'],terminations=result['terminations'],planned_reference_tracker=True,autonomous_depth_student=False,decision=decision,new_GO=0,Git='Pending ordinary supplement by heartbeat; do not rerun consumed stages.'))
    print(json.dumps(dict(passed=True,strict=result['strict_successes'],crossed=result['crossed_cases'])),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:put('POSTROUND302_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
