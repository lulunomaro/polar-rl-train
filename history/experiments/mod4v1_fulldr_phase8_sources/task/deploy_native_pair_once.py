"""Stage a NEW model-free MOD4v1 admission and dispatch its finite private-GPU parent."""
from pathlib import Path
import json,hashlib,datetime,time,shlex,ast
from project_connector import connect72
R=Path(__file__).resolve().parent;A=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets');BASE='/home/lc01/Zonglin Li/zonglin2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');job=BASE+'/tasks/MOD4V1_NATIVE0PT_PAIR_'+stamp+'_'+str(time.time_ns())
files=[('native_mod4v1_probe.py',R/'native_mod4v1_probe.py'),('native_probe_supervisor.py',R/'native_probe_supervisor.py'),('assets/robot.usd',A/'robot.usd'),('assets/import_contract.json',A/'import_contract.json')]
for rel,p in files:
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
plan={'kind':'MOD4V1_NEW_NATIVE_NO_PT_PAIR','new_remote_job':job,'gpus':[{'label':'gpu0','uuid':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'},{'label':'gpu1','uuid':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}],'asset_sha256':H(A/'robot.usd'),'contract_sha256':H(A/'import_contract.json'),'worker_sha256':H(R/'native_mod4v1_probe.py'),'files':[{'relative':rel,'bytes':p.stat().st_size,'sha256':H(p)} for rel,p in files],'model_opens':0,'optimizer_updates':0,'canonical_writes':0}
assert plan['asset_sha256']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
report={'plan':plan,'status':'STAGING','source_checkpoint_opens':0};c=connect72();s=c.open_sftp()
try:
 try:s.stat(job)
 except FileNotFoundError:pass
 else:raise RuntimeError('New admission job already exists; never replay')
 s.mkdir(job);s.mkdir(job+'/assets')
 for rel,p in files:s.put(str(p),job+'/'+rel)
 with s.open(job+'/PLAN.json','x')as f:f.write(json.dumps(plan,indent=2))
 code="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'native_probe_supervisor.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);q=psutil.Process(p.pid);print(json.dumps({'pid':p.pid,'creation':q.create_time(),'root':str(B),'launched':True,'native_or_training_success_not_yet_claimed':True}))"%(job,BASE+'/run-python.sh')
 i,o,e=c.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);report.update(status='PARENT_DISPATCHED',parent=json.loads(out),stderr=err)
finally:s.close();c.close()
p=R/'reports'/('native_pair_dispatch_'+stamp+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(report,ensure_ascii=False,indent=2))
