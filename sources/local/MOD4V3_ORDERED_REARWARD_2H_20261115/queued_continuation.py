"""Continue the existing valid student after its complete save; total user budget7200s."""
from pathlib import Path
import json,time,hashlib,shutil,subprocess,sys,traceback,os
T=Path(__file__).resolve().parent

def put(name,data):
 p=T/name;tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+chr(10));os.replace(tmp,p)
def status(state,**extra):put('EXTENSION_STATUS.json',dict(epoch=time.time(),state=state,supervisor_pid=os.getpid(),**extra))
def allowed(command,plan):
 g=plan['GPU_sharing'];return ('/mnt/mod4_windows_data/hjq/'in command and '--livestream'in command and any(n in command for n in g['allowed_owner_commands_contain']))or(g['allowed_existing_cpu_tuner']['script']in command and all(n in command for n in g['allowed_existing_cpu_tuner']['required_arguments']))
try:
 p=json.loads((T/'PLAN.json').read_text());previous=Path(p['previous_remote_job']);status('waiting_current_valid_segment',previous_job=str(previous),total_budget_seconds=7200)
 while not(previous/'SAFE_CLOSED.json').exists():
  if(previous/'ERROR.json').exists():raise RuntimeError('Previous PPO has an error; preserve its complete checkpoint and do not auto-restart')
  time.sleep(10)
 if(previous/'ERROR.json').exists():raise RuntimeError('Previous segment ended with ERROR.json')
 prior=json.loads((previous/'FINAL.json').read_text());before=p['total_round_budget']['invalid_first_phase_actual_PPO_seconds']+prior['elapsed_seconds'];remaining=int(7200-before)
 if remaining<=0:raise RuntimeError('No authorized PPO budget remains')
 source=previous/'model_final.pt';digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==prior['checkpoint']['SHA'];assert prior['checkpoint']['optimizer_entries']==17
 shutil.copy2(source,T/'continuation_parent.pt');assert hashlib.sha256((T/'continuation_parent.pt').read_bytes()).hexdigest()==digest
 p['parent_sha256']=digest;p['cumulative_training_seconds_before']=before;p['training_round']['seconds']=remaining;p['teacher_retention']['student_initial_sha256']=digest;p['teacher_retention']['student_initial_iteration']=prior['checkpoint']['iteration'];p['total_round_budget'].update(previous_corrected_phase_seconds=prior['elapsed_seconds'],remaining_new_phase_seconds=remaining);p['continuation'].update(state='ready_to_launch_current_valid_student',previous_final_sha256=digest,previous_final_iteration=prior['checkpoint']['iteration']);put('PLAN.json',p);put('CONTINUATION_INPUT.json',dict(previous_job=str(previous),previous_final=prior,parent_sha256=digest,cumulative_seconds_before=before,remaining_seconds=remaining,total_budget_seconds=7200))
 while True:
  ids=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).split();owners=[]
  for i in ids:
   try:cmd=Path('/proc/'+i+'/cmdline').read_bytes().replace(bytes([0]),b' ').decode()
   except FileNotFoundError:continue
   if not allowed(cmd,p):owners.append(dict(pid=int(i),command=cmd))
  free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip().splitlines()[0])
  if not owners and free>=p['GPU_sharing']['minimum_free_MiB']:break
  status('waiting_previous_GPU_release_or_other_owner',unexpected_owners=owners,free_MiB=free);time.sleep(10)
 result=subprocess.run([p['python'],'-B',str(T/'launch.py'),p['training_job'],'--kind','train','--num-envs','2048'],cwd=T,text=True,capture_output=True)
 if result.returncode:raise RuntimeError('Continuation launcher rejected: '+result.stdout+' '+result.stderr)
 launch=json.loads(result.stdout.strip().splitlines()[-1]);put('CONTINUATION_LAUNCH.json',launch);status('continuation_process_started',launch=launch,cumulative_seconds_before=before,remaining_seconds=remaining,total_budget_seconds=7200)
except BaseException:
 put('EXTENSION_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
