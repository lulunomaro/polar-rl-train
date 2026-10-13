"""Independent replacement for the pre-Kit EULA bootstrap failure. Original failure is retained."""
from pathlib import Path
import json,os,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_original_linux20k_formal_once import S as OLD,PY,D
S=OLD.replace('_v1','_EULA_environment_v2')
parent=(D/'original_linux_formal_parent.py').read_text().replace("env=os.environ.copy()", "env=os.environ.copy();env['OMNI_KIT_ACCEPT_EULA']='YES'")
p=D/'original_linux_formal_parent_EULA_environment_v2.py';p.write_bytes(parent.encode());compile(parent,str(p),'exec')
c=connect_linux_only()
try:
    src=r'''
from pathlib import Path
import json,hashlib,shutil,fcntl,subprocess
O=Path(OLD);R=Path(S);assert not R.exists()
e=json.loads((O/'formal/EXIT_RECEIPT.json').read_bytes());assert e['child_actually_absent']
assert b'EOF when reading a line' in (O/'formal/worker_stdout.log').read_bytes()
assert not list((O/'formal/learning_logs').glob('*'))
assert json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes())['active_segment'] is None
assert not subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
R.mkdir();m=json.loads((O/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes());rows=[]
for x in m['sourcefreeze']:
 p=Path(x['path']);q=R/p.relative_to(O);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);x=dict(x,path=str(q));rows.append(x)
m['scope']=S;m['sourcefreeze']=rows;m['EULA_bootstrap_environment_only']=True;m['prior_bootstrap_failure_preserved']=str(O/'formal/EXIT_RECEIPT.json')
(R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').write_text(json.dumps(m,indent=2));shutil.copy2(O/'TARGET_ORIGINAL_FULLSTATE_CPU_ACTUAL.json',R/'TARGET_ORIGINAL_FULLSTATE_CPU_ACTUAL.json');print(json.dumps(dict(scope=S,original_runtime_byteexact=True,no_GPU_or_PPO_replay=True)))
'''
    def run(src,label):
        si,so,se=c.exec_command('python3 -',timeout=45);si.write('S='+repr(S)+'\nOLD='+repr(OLD)+'\nPY='+repr(PY)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status();p=D/'reports'/(label+'.json');p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);print(out.decode())
    run(src,'ORIGINAL_LINUX_EULA_ONLY_FRESH_SCOPE_MATERIALIZED_ACTUAL')
    sf=c.open_sftp();sf.put(str(p),S+'/original_linux_formal_parent.py');sf.close()
    src=r'''
from pathlib import Path
import json,hashlib,subprocess,time
R=Path(S);m=json.loads((R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes())
for x in m['sourcefreeze']:
 if x['path']==str(R/'original_linux_formal_parent.py'):x['sha256']=hashlib.sha256(Path(x['path']).read_bytes()).hexdigest();x['bytes']=Path(x['path']).stat().st_size
 assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
(R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').write_text(json.dumps(m,indent=2))
assert not (R/'FORMAL_ONCE_CONSUMED.json').exists();argv=[PY,'-u',str(R/'original_linux_formal_parent.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(epoch=time.time(),pid=p.pid,start_ticks=int((Path('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split()[19]),argv=argv,cwd=S,EULA_only_new_environment=True,PPO_claimed=False)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
    run(src,'ORIGINAL_LINUX_EULA_REVIEWED_FORMAL_DISPATCH_ACTUAL')
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
