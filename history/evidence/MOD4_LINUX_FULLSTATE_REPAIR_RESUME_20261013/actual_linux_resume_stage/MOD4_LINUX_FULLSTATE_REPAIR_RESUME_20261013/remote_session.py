from pathlib import Path
import json, os, time
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
def execute(source,label,timeout=40):
    c=connect_linux_only()
    try:
        si,so,se=c.exec_command('python3 -',timeout=timeout)
        si.write(source);si.flush();si.channel.shutdown_write()
        out=so.read();err=se.read();code=so.channel.recv_exit_status()
        receipt=dict(epoch=time.time(),code=code,stderr=err.decode(errors='replace'),stdout=out.decode(errors='replace'),single_linux_connection=True)
        p=D/'reports'/(label+'_'+str(time.time_ns())+'.json')
        p.write_bytes(json.dumps(receipt,ensure_ascii=False,indent=2).encode())
        assert code==0, str(p)
        return json.loads(out),p
    finally:
        c.close();os.environ.pop('RM_SSH_PASSWORD',None)
