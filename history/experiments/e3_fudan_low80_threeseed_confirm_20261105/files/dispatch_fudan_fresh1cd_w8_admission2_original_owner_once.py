"""Launch one original resource/accounting owner with an outer actual-wait controller."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;marker=D/'FDN_N20000_W8_FRESH1CD_ADMISSION2_ORIGINAL_OWNER_DISPATCH_ONCE.json';assert not marker.exists();stage=json.loads((D/'FDN_N20000_W8_FRESH1CD_ADMISSION2_STAGE_RESULT.json').read_bytes());assert stage['returncode']==stage['owner_source_preflight_rc']==0;root=stage['root'];sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code='''from pathlib import Path
import os,sys,json,time,subprocess,traceback
R=Path(sys.argv[1]);assert not(R/'OWNER_CONTROLLER_STARTED.json').exists();put=lambda p,v:p.write_text(json.dumps(v,indent=2),encoding='utf8');put(R/'OWNER_CONTROLLER_STARTED.json',dict(pid=os.getpid(),epoch=time.time()));log=(R/'OWNER_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(R/'fudan_original_owner_v1.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);log.close();put(R/'OWNER_PARENT_IDENTITY.json',dict(pid=p.pid,epoch=time.time()));rc=p.wait();put(R/'OUTER_OWNER_WAIT_ACTUAL.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid,actual_wait_returncode=rc,original_owner_reaped=True))
'''
launch='''import sys,subprocess,json
from pathlib import Path
R=Path(sys.argv[1]);p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(R/'owner_outer_wait_controller_v1.py'),str(R)],cwd=R,stdin=subprocess.DEVNULL,stdout=(R/'OUTER_CONTROLLER_STDOUT_STDERR.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps(dict(controller_pid=p.pid,root=str(R),original_owner_resource_wait_max_seconds=1800,actual_PPO_updates_not_yet_observed=True)))
'''
marker.write_text(json.dumps(dict(epoch=time.time(),root=root,dispatch_intent=True),indent=2),encoding='utf8');c=connect72();s=c.open_sftp()
try:
 with s.open(root+'/owner_outer_wait_controller_v1.py','wx')as f:f.write(code)
 cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(launch)+' '+shlex.quote(root);i,o,e=c.exec_command(cmd,timeout=60);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();v=dict(epoch=time.time(),root=root,returncode=rc,stdout=a,stderr=b);(D/'FDN_N20000_W8_FRESH1CD_ADMISSION2_ORIGINAL_OWNER_DISPATCH_RESULT.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert rc==0,b
finally:s.close();c.close()
