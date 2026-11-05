"""Submit the one newly staged two-slot original-accounting owner. No model/SDK in dispatcher."""
from pathlib import Path
import json,sys,time,shlex
D=Path(__file__).resolve().parent;marker=D/'DISPATCH_E0_SCUT_HOUR_ONCE.json';result=D/'DISPATCH_E0_SCUT_HOUR_RESULT.json';assert not marker.exists()and not result.exists();stage=json.loads((D/'STAGE_E0_SCUT_HOUR_RESULT.json').read_bytes());assert stage['returncode']==0 and stage['owner_import_only_preflight_rc']==0 and stage['selected_PT_stat_hash_decode']==0 and stage['owner_dispatched']is False;plan=json.loads((D/'SOURCE_PLAN_E0_SCUT_HOUR_ACTUAL_V1.json').read_bytes());assert plan['native_asset_gate_role']=='E0' and len(plan['entries'])==1 and plan['entries'][0]['role']=='E0';root=stage['root'];marker.write_text(json.dumps(dict(epoch=time.time(),root=root,single_original_owner_submission=True,host86_excluded=True),indent=2),encoding='utf8')
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
controller='''from pathlib import Path
import subprocess,json,time,os
B=Path(__file__).resolve().parent
assert not(B/'OUTER_OWNER_WAIT_ACTUAL.json').exists()
def put(n,v):
 p=B/n;t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(v,indent=2));os.replace(t,p)
with (B/'OWNER_STDOUT_STDERR.log').open('xb')as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'migration_nine_original_owner_v1.py')],cwd=str(B),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 put('OUTER_OWNER_IDENTITY.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid))
 rc=p.wait();put('OUTER_OWNER_WAIT_ACTUAL.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid,actual_wait_returncode=rc,original_owner_reaped=True))
'''
launch='''from pathlib import Path
import subprocess,json,os
B=Path(ROOT)
assert not(B/'OWNER_STARTED.json').exists()and not(B/'OUTER_OWNER_IDENTITY.json').exists()
with (B/'OUTER_CONTROLLER_STDOUT_STDERR.log').open('xb')as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'OUTER_OWNER_WAIT_CONTROLLER.py')],cwd=str(B),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps(dict(controller_pid=p.pid,root=str(B),original_preGO_wait_seconds=1800,actual_native_and_PPO_not_yet_observed=True)))
'''.replace('ROOT',repr(root))
c=connect72();sftp=c.open_sftp()
try:
 p=root+'/OUTER_OWNER_WAIT_CONTROLLER.py'
 try:sftp.lstat(p)
 except FileNotFoundError:pass
 else:raise FileExistsError(p)
 with sftp.open(p,'wb')as f:f.write(controller)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(launch),timeout=30);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();r=dict(epoch=time.time(),root=root,returncode=rc,stdout=stdout,stderr=stderr);result.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2));assert rc==0
finally:sftp.close();c.close()
