"""Continue only unexecuted CPU proof and dispatch. Root path is added to CPU sys.path."""
import re,json,os,shlex
from pathlib import Path
from deploy_original_linux20k_formal_once import S,PY,D
from read_linux_resume_boundary_actual import connect_linux_only
assert not (D/'reports/ORIGINAL_LINUX20K_FORMAL_DISPATCH_ACTUAL.json').exists()
s=(D/'deploy_original_linux20k_formal_once.py').read_text()
cpu=re.search("        cpu=r'''(.*?)'''",s,re.S).group(1).replace("sys.path.insert(0,str(R/'isaac/mod4'))", "sys.path.insert(0,str(R));sys.path.insert(0,str(R/'isaac/mod4'))")
dispatch=re.search("        dispatch=r'''(.*?)'''",s,re.S).group(1)
c=connect_linux_only()
try:
    for label,command,source in [('ORIGINAL_LINUX20K_TARGET_CPU_ROOTPATH_REVIEWED_ACTUAL','CUDA_VISIBLE_DEVICES= '+shlex.quote(PY)+' -','S='+repr(S)+'\n'+cpu),('ORIGINAL_LINUX20K_FORMAL_DISPATCH_ACTUAL','python3 -','S='+repr(S)+'\nPY='+repr(PY)+'\n'+dispatch)]:
        si,so,se=c.exec_command(command,timeout=60);si.write(source);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=D/'reports'/(label+'.json');p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);print(out.decode())
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
