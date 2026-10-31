"""Freeze the user-authorized10800s caller and check owner/worker time join."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
S=T/'E0_JUMP32066_GROUND_RETENTION_CONTINUATION_V209_20261031'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def load(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
owner=load('owner210_contract',N/'control/owner210_protocol.py');worker=load('worker210_contract',N/'package/mixed210_task_protocol.py')
schedule=read(N/'SCHEDULE_PUBLIC.json');task=read(N/'package/TASK210.json');assert owner.validate_schedule(schedule)
spec=schedule['experts']['e0_72'];ready=read(N/'ADMISSION210_READY.json')
row=dict(key='e0_72',phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=dict(value=ready,SHA=hashlib.sha256(json.dumps(ready,indent=2).encode()).hexdigest()),original_error=False)
assert owner.valid_ready(row,spec)
go=owner.flat_go_fields(spec);go.update(run_id='JOIN210_THREE_HOUR',learning_started_epoch=100.,save_deadline=10900.,nominal_end_epoch=11200.,max_parent_seconds=11100,exit_headroom_seconds=300)
assert worker.validate_go(go,'JOIN210_THREE_HOUR',task,101.)
negatives=0
for k,v in [('max_parent_seconds',3900),('save_deadline',3700.),('nominal_end_epoch',4000.),('max_parent_seconds',7500),('source_iteration',31984),('source_model_SHA','0'*64),('ground_envs',0),('input_Adam',641200)]:
 bad=copy.deepcopy(go);bad[k]=v
 try:worker.validate_go(bad,'JOIN210_THREE_HOUR',task,101.)
 except AssertionError:negatives+=1
 else:raise AssertionError(k)
source=(S/'launch209_original_single_writer_mixed_FIRST_once.py').read_text('utf8')
for a,b in [('ROOT209','ROOT210'),('PACKAGE209','PACKAGE210'),('CONTROL209','CONTROL210'),('ADMISSION209','ADMISSION210'),
 ('control209','control210'),('mixed209_finite_owner_authority72','mixed210_finite_owner_authority72'),('mixed209_fullstate_slot_node','mixed210_fullstate_slot_node'),
 ('launch209_original_single_writer_mixed_FIRST_once','launch210_original_single_writer_mixed_FIRST_once'),
 ('ACTUAL209','ACTUAL210'),('ACTUAL_SOURCE209','ACTUAL_SOURCE210'),('ONE209_E0_GROUND10_JUMP90','ONE210_E0_GROUND10_JUMP90_THREE_HOUR'),
 ('mixed209_transport','mixed210_transport'),('mixed209_memory_auth','mixed210_memory_auth'),('owned209_launch','owned210_launch')]:source=source.replace(a,b)
source=source.replace("assert read(R/'ROOT210_OWNER_WORKER_ACTUAL_ADMISSION_JOIN_CPU_ACTUAL.json')['passed']","assert read(R/'ROOT210_THREE_HOUR_OWNER_WORKER_JOIN_CPU_ACTUAL.json')['passed']")
source=source.replace("assert read(R/'ACTUAL210_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json')['global_serial_control_client_lease']=='FREE'","assert read(Path("+repr(str(S/'reports/ACTUAL209_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json'))+"))['global_serial_control_client_lease']=='FREE'")
source=source.replace('+3900','+11100').replace('reserve_required=3900','reserve_required=11100')
source=source.replace('finite_learning_seconds=3600,max_parent_seconds=3900','finite_learning_seconds=10800,max_parent_seconds=11100')
source=source.replace('J.resolve().is_relative_to(owned/\'tasks\') and J.is_dir()',"J.resolve().is_relative_to(owned/'tasks') and not J.exists()")
source=source.replace("O.mkdir(parents=True);(J/'control210').mkdir()","O.mkdir(parents=True);J.mkdir(parents=True);(J/'control210').mkdir()")
source=source.replace('shutil.disk_usage(J).free>25*1024**3',"shutil.disk_usage(owned/'tasks').free>25*1024**3")
needle="  sf=client.open_sftp();sf.get_channel().settimeout(90)"
insert='''  # NEW210 task namespace. One source/asset postcopy integrity pass for this
  # newly typed temporal task; reuse actual209 physics evidence, no0PT replay.
  package=read(N/'PACKAGE210_MANIFEST.json')
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   made=set()
   for row in package['files']:
    cur=J
    for bit in row['relative'].split('/')[:-1]:
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(str(N/row['local_relative']),J+'/'+row['relative'])
   sf.put(str(N/'PACKAGE210_MANIFEST.json'),J+'/PACKAGE210_MANIFEST.json')
  finally:sf.close()
  check="""from pathlib import Path
import hashlib,json
B=Path(v['job'])
for row in v['files']:
 p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==row['bytes']
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==row['SHA'],str(p)
task=json.loads((B/'TASK210.json').read_bytes());assert task['source_iteration']==32066 and task['source_Adam_step']==642840 and task['learning_seconds']==10800
assert Path(task['formal_source_model']).stat().st_size==17519967
print(json.dumps(dict(passed=True,new_source_postcopy_pass=1,actual209SDK_reward_command_evidence_reused=True,no0PT_or_model_read=True)))"""
  put('ROOT210_NEW_PACKAGE_POSTCOPY_AND_TASK_ACTUAL.json',d.code(client,d.PY72,check,dict(job=J,files=package['files']),timeout=90))
'''
assert needle in source;source=source.replace(needle,insert+needle)
ast.parse(source);write(N/'launch210_original_single_writer_mixed_FIRST_once.py',source)
write(R/'ROOT210_THREE_HOUR_OWNER_WORKER_JOIN_CPU_ACTUAL.json',json.dumps(dict(epoch=time.time(),passed=True,user_requested_learning_seconds=10800,max_parent=11100,
 wrong_time_or_source_TaskGO_rejections=negatives,actual2090PT_reuse_source_equivalence=True,
 unchanged_sdk_SHA=H(N/'package/mixed209_sdk.py'),no_new_model_raw_SDK_GPU_remote_read=True,
 original_charge_HMAC_twofcntl_unchanged=True,old209_one_hour_launch_not_run=True),indent=2))
write(R/'FROZEN210_THREE_HOUR_LAUNCH_CALLER_INDEX.json',json.dumps(dict(epoch=time.time(),source_only=True,
 entry='launch210_original_single_writer_mixed_FIRST_once.py',SHA=H(N/'launch210_original_single_writer_mixed_FIRST_once.py'),
 required_actual_new_model_GPU_loads=1,old_CPU_model_reads=0,no_automatic_extra_window=True),indent=2))
print(json.dumps(dict(passed=True,three_hour_CPU_negatives=negatives,launch_source_ready=True)))
