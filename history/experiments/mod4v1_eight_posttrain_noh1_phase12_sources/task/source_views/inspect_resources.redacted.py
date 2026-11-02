"""Read-only discovery of existing E0/SuperMimic resources on host72."""
from pathlib import Path
import sys,json,re,stat,concurrent.futures
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'traditional_control_20261101'))
from ssh_task import connect
BASE='/home/lc01/Zonglin Li/zonglin2'

def main():
    c=connect();s=c.open_sftp()
    try:
        si,so,se=c.exec_command('nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits',timeout=30);si.close();print(json.dumps({'gpu':so.read().decode(),'gpu_err':se.read().decode(),'exit':so.channel.recv_exit_status()}),flush=True)
        for rel in ['','tasks','src','assets','config','state','runtime_exports']:
            path=BASE+('/'+rel if rel else '')
            try:
                allrows=s.listdir_attr(path)
                rows=allrows
                if rel=='tasks':rows=[r for r in rows if re.search(r'e0|expert|frozen|super.?mimic|mimic|branch|step270|freeze',r.filename,re.I)]
                rows=sorted(rows,key=lambda r:r.st_mtime,reverse=True)
                print(json.dumps({'path':path,'total':len(allrows),'matched':len(rows),'entries':[{'name':r.filename,'dir':stat.S_ISDIR(r.st_mode),'bytes':r.st_size,'mtime':r.st_mtime} for r in rows[:100]]}),flush=True)
            except Exception as e:print(json.dumps({'path':path,'error':repr(e)}),flush=True)
        for path in [BASE+'/AGENTS.md',BASE+'/src/fangzhen_linux/AGENTS.md',BASE+'/README.md',BASE+'/run-python.sh']:
            try:
                with s.open(path,'rb') as f:text=f.read(30000).decode('utf-8','replace')
                print(json.dumps({'document':path,'text':text},ensure_ascii=False),flush=True)
            except FileNotFoundError:pass
    finally:s.close();c.close()
if __name__=='__main__':main()
