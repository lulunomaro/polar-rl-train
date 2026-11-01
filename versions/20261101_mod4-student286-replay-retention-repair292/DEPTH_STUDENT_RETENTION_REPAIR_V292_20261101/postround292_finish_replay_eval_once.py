"""Wait locally for original close window, then collect/save/replay/evaluate once."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=N/'postround292'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
    with (R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
def call(exe,args):
    proc=subprocess.run([exe,'-B','-X','utf8',*map(str,args)],cwd=N,capture_output=True,text=True,encoding='utf8')
    if proc.returncode:raise RuntimeError(dict(args=[str(x)for x in args],returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
    return dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
def main():
    put('POSTROUND292_WAITER_ONCE_CONSUMED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,scope='local timer, then original collector/CPU/new evaluation/replay only',new_training_GO=0))
    w=json.loads((R/'CURRENT_ACTUAL292_REPLAY_EVAL_CONTINUE_WORK_ORDER.json').read_bytes());g=w['original_go'];q=w['next']
    due=g['nominal_end_epoch']-900+2
    while time.time()<due:time.sleep(min(10,due-time.time()))
    put('POSTROUND292_ORIGINAL_NORMAL_WINDOW_REACHED.json',dict(epoch=time.time(),due=due,original_go=g))
    normal=call(CONTROL,[q['normal_collector'],'--root-lease-label','ROOT292_EXCLUSIVE_NORMAL900_POSTROUND_'+str(time.time_ns()),'--auth-provider',q['auth_provider'],'--additional-control-pattern','run293_eval|launch292_|collect292_','--caller-index-SHA',q['normal_index_SHA']])
    put('POSTROUND292_NORMAL_COMMAND_RETURNED.json',normal)
    cpu=call(CPU,[q['CPU_reader'],'--caller-index-SHA',q['CPU_index_SHA']]);put('POSTROUND292_CPU_COMMAND_RETURNED.json',cpu)
    complete=json.loads((R/'ROOT292_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
    full=json.loads((R/'ROOT292_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());assert full['passed'] and complete['owner_closed']['canonical_None']
    E=T/'RETENTION292_POSTROUND_REPLAY_EVAL_V293_20261101';E.mkdir(exist_ok=False);(E/'reports').mkdir()
    shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
    for p in (P/'eval293_source').glob('*.py'):shutil.copyfile(p,E/'source'/p.name)
    shutil.copyfile(P/'eval293_source/contract293.py',E/'contract293.py')
    shutil.copyfile(P/'run293_eval_once_template.py',E/'run293_eval_once.py')
    task=json.loads((T/'TEACHER286_REPLAY_EVAL_V288_20261101/TASK288_FROZEN.json').read_bytes())
    task.update(kind='FROZEN292_RETENTION_FINAL_HELDOUT270_GROUND_EVAL293',model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['actual_new_Pi_updates'],source_run=complete['run_id'],worker_SHA=H(E/'source/evaluate293.py'),source_full_CPU_receipt_SHA=H(R/'ROOT292_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'))
    (E/'TASK293_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
    evaluation=call(CONTROL,[E/'run293_eval_once.py']);put('POSTROUND292_NEW_EVAL293_COMMAND_RETURNED.json',evaluation)
    result=json.loads((E/'reports/ROOT293_EVALUATION_FULL_RETURNED.json').read_bytes())['result']
    viewer=(P/'view293_actual_final292_replay_template.py').read_text('utf8')
    viewer=viewer.replace('policy_updates=2336','policy_updates='+str(full['actual_new_Pi_updates']))
    viewer=viewer.replace('Pi2336 Critic2336','Pi'+str(full['actual_new_Pi_updates'])+' Critic'+str(full['actual_new_critic_updates']))
    viewer=viewer.replace('FAILED: bad_orientation; held-out stairs0/72; ground completed0/8',f"Held-out stairs{result['strict_successes']}/72; crossed{result['crossed_cases']}/72; ground completed{result['ground_complete']}/8")
    vp=E/'view293_actual_final292_replay.py';vp.write_bytes(viewer.encode())
    log=E/'reports/VIEW293_ORIGINAL_CONSOLE.log'
    with log.open('xb')as f:child=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe','-B','-X','utf8',str(vp)],cwd=E,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    with (E/'reports/VIEW293_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=child.pid,actual_recorded_replay=True),f,indent=2)
    if result['strict_successes']>0:
        decision='Promising270 first-flight measurements; verify actual top contact manifold before skill claim, then evaluate robustness before further training.'
    elif result['ground_complete']>=3:
        decision='Ground retained at source baseline or better,270not learned. Continue existing teacher-assisted objective with this complete checkpoint after reviewing per-env replay and WM prediction quality; do not claim graduation.'
    else:
        decision='Retention repair still below source ground baseline. Preserve failed complete checkpoint; next action is targeted policy/WM repair, no unchanged continuation.'
    put('POSTROUND292_REPLAY_EVAL_DECISION.json',dict(epoch=time.time(),status='COMPLETE_SAVE_REPLAY_EVAL_DECISION',model_SHA=full['SHA'],eval_root=str(E),strict_successes=result['strict_successes'],crossed_cases=result['crossed_cases'],ground_complete=result['ground_complete'],terminations=result['terminations'],decision=decision,followup='Hourly chat must inspect/act on this result and archive all new reports, within existing canonical budget.',new_GO=0,archive_status='Pending next heartbeat ordinary supplement; source phase already archived separately.'))
    print(json.dumps(dict(passed=True,result=str(R/'POSTROUND292_REPLAY_EVAL_DECISION.json'),decision=decision)),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        put('POSTROUND292_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_consumed_once=True,followup='Read exact saved failure/own process and lock state; make independent fix.'))
        raise
