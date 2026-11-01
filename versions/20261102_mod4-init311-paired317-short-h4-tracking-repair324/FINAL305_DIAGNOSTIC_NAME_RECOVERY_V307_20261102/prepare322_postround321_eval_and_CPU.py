"""Prepare unused save/close/fullCPU/new322eval/recorded-render workflow for321."""
from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;D=T/'REFERENCE_H4_TRACKING_REPAIR_V321_20261102';E=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102';P=D/'postround322';assert not P.exists();P.mkdir();(P/'eval_source').mkdir()
def write(p,text):ast.parse(text);p.write_bytes(text.encode())
def rename(text,old,new):
    keep=[]
    def hide(m):keep.append(m.group());return'@SHA'+str(len(keep)-1)+'@'
    text=re.sub(r'\b[0-9a-f]{64}\b',hide,text);text=re.sub(r'(?<=[A-Za-z_])'+old+r'(?!\d)',new,text)
    for i,value in enumerate(keep):text=text.replace('@SHA'+str(i)+'@',value)
    return text
cpu=rename((T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/review305_NEW_final_whole_CPU_UNUSED_once.py').read_text('utf8'),'305','321')
cpu=cpu.replace('9712+ck','12468+ck').replace('wm-9712','wm-12468').replace("(('actor',45533),('critic',2593))","(('actor',48257),('critic',5317))").replace("s['actor_Adam_offset']==45533 and s['critic_Adam_offset']==2593","s['actor_Adam_offset']==48257 and s['critic_Adam_offset']==5317")
cpu=cpu.replace("assert not s['old_Fudan_return']", "assert s['policy_horizon']==4 and s['WM_supervision_horizon']==32 and s['actor_terminal_bootstrap']is False\n    assert not s['old_Fudan_return']")
write(D/'review321_NEW_final_whole_CPU_UNUSED_once.py',cpu)
worker=rename((E/'source/evaluate308.py').read_text('utf8'),'308','322');worker=rename(worker,'305','321')
write(P/'eval_source/evaluate322.py',worker)
write(P/'eval_source/contract322.py',rename(rename((E/'contract308.py').read_text('utf8'),'308','322'),'305','321'))
runner=rename((E/'run308_eval_once.py').read_text('utf8'),'308','322')
runner=runner.replace("patterns='","patterns='watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|collect321_|launch321_|",1)
write(P/'run322_eval_once_template.py',runner)
viewer=rename((E/'view308_actual_final305_replay.py').read_text('utf8'),'308','322');viewer=rename(viewer,'305','321')
viewer=viewer.replace('Pi2724 Critic2724','PiPLACEHOLDER CriticPLACEHOLDER').replace('policy_updates=2724','policy_updates=PLACEHOLDER')
viewer=viewer.replace('reference tracking BPTT / matching tracking critic','H4 tracking BPTT / actor terminal0 / WM H32')
write(P/'view322_actual_final321_replay_template.py',viewer.replace('policy_updates=PLACEHOLDER','policy_updates=0'))
renderer=rename((E/'render308_recorded_frames.py').read_text('utf8'),'308','322');renderer=rename(renderer,'305','321')
renderer=renderer.replace('RECOVERED321_TRACKING_REPLAY_EVAL_V322_20261102','REFERENCE_TRACKING321_POSTROUND_EVAL_V322_20261102')
write(P/'render322_recorded_frames_template.py',renderer)
script='''"""Unused localtimer: original321 close/fullCPU then one new322eval/render."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=N/'postround322'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe';CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def call(exe,args):
 r=subprocess.run([exe,'-B','-X','utf8',*map(str,args)],cwd=N,capture_output=True,text=True,encoding='utf8')
 if r.returncode:raise RuntimeError(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,args=list(map(str,args))))
 return dict(returncode=0,stdout=r.stdout,stderr=r.stderr)
def main():
 assert not(R/'POSTROUND322_ONCE_CONSUMED.json').exists()
 binding=json.loads((R/'ROOT321_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json').read_bytes());go=binding['current']['go']['jump_72']
 put('POSTROUND322_ONCE_CONSUMED.json',dict(epoch=time.time(),pid=__import__('os').getpid(),scope='original321fullsaveclose/newCPU/eval322/actualrecordedrender,noGO'))
 for row in json.loads((N/'INDEX322_POSTROUND_FOR321_FROZEN.json').read_bytes())['files']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']
 while time.time()<go['nominal_end_epoch']-898:time.sleep(max(.01,min(10,go['nominal_end_epoch']-898-time.time())))
 normal=N/'normal321'
 put('POSTROUND321_NORMAL_COMMAND_RETURNED.json',call(CONTROL,[normal/'collect321_tracking_formal_cost_normal900_UNUSED_once.py','--root-lease-label','ROOT321_EXCLUSIVE_NORMAL900_POSTROUND_'+str(time.time_ns()),'--auth-provider',T.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py','--additional-control-pattern','run322_eval|launch321_|collect321_|watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_adaptation|deploy_w35','--caller-index-SHA',H(normal/'INDEX321_NORMAL_SOURCE_FROZEN.json')]))
 put('POSTROUND321_CPU_COMMAND_RETURNED.json',call(CPU,[N/'review321_NEW_final_whole_CPU_UNUSED_once.py']))
 full=json.loads((R/'ROOT321_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());complete=json.loads((R/'ROOT321_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert full['passed']
 E=T/'REFERENCE_TRACKING321_POSTROUND_EVAL_V322_20261102';E.mkdir(exist_ok=False);(E/'reports').mkdir()
 shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
 for p in(P/'eval_source').glob('*.py'):shutil.copyfile(p,E/'source'/p.name)
 shutil.copyfile(P/'eval_source/contract322.py',E/'contract322.py');shutil.copyfile(P/'run322_eval_once_template.py',E/'run322_eval_once.py')
 shutil.copyfile(T/'TEACHER286_REPLAY_EVAL_V288_20261101/source/wheel_geometry220.py',E/'source/wheel_geometry220.py');shutil.copyfile(N/'reference305.npz',E/'reference305.npz')
 task=json.loads((T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/TASK308_FROZEN.json').read_bytes());original=json.loads((N/'TASK321_FROZEN.json').read_bytes())
 task.update(kind='FROZEN321_REFERENCE_TRACKING_EVAL322',model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['Pi'],source_run=original['run_id'],worker_SHA=H(E/'source/evaluate322.py'),reference=original['reference'],source_full_CPU_receipt_SHA=H(R/'ROOT321_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'))
 (E/'TASK322_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 put('POSTROUND321_EVAL_COMMAND_RETURNED.json',call(CONTROL,[E/'run322_eval_once.py']))
 result=json.loads((E/'reports/ROOT322_EVALUATION_FULL_RETURNED.json').read_bytes())['result']
 viewer=(P/'view322_actual_final321_replay_template.py').read_text('utf8').replace('PiPLACEHOLDER CriticPLACEHOLDER','Pi'+str(full['Pi'])+' Critic'+str(full['critic'])).replace('policy_updates=0','policy_updates='+str(full['Pi']))
 (E/'view322_actual_final321_replay.py').write_bytes(viewer.encode());renderer=(P/'render322_recorded_frames_template.py').read_text('utf8');(E/'render322_recorded_frames.py').write_bytes(renderer.encode())
 put('POSTROUND321_NATIVE_REPLAY_RENDER_RETURNED.json',call(CONTROL,[E/'render322_recorded_frames.py']))
 put('POSTROUND321_REPLAY_EVAL_DECISION.json',dict(epoch=time.time(),status='COMPLETE_SAVE_EVAL_RENDER_PENDING_NATIVE_VISUAL_REVIEW',model_SHA=full['SHA'],eval_root=str(E),strict_successes=result['strict_successes'],crossed_cases=result['crossed_cases'],terminations=result['terminations'],finished8s=sum(r['full_window']for r in result['results']),actorH4=True,terminalbootstrap=False,WMH32=True,new_GO=False,next='Currentmodelmustnativelyviewactualrenderanduseactualeval/trackingerrorsbeforecontinuation/repair;0/80notgraduation;writeallreportstoGit.'))
if __name__=='__main__':
 try:main()
 except BaseException:put('POSTROUND322_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
'''
write(D/'postround322_finalize321_replay_eval_once.py',script)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[D/'postround322_finalize321_replay_eval_once.py',D/'review321_NEW_final_whole_CPU_UNUSED_once.py',*sorted(P.rglob('*.py'))]
with(D/'INDEX322_POSTROUND_FOR321_FROZEN.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
with(D/'reports/SOURCE322_UNUSED_POSTROUND_READY.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed_static=True,launched=False,requires_actual321_first_binding=True,fullCPUoffsets=[48257,5317,12468],samefixed270newseed9137eval80firstepisodes400controls=True,native_recorded_pose_render=True,no_new_GO=True),f,indent=2)
print(json.dumps(dict(passed_static=True,postround=str(D/'postround322_finalize321_replay_eval_once.py'),launched=False)))
