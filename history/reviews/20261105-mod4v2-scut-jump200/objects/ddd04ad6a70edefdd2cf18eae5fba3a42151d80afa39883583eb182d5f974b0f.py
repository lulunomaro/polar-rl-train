from pathlib import Path
import hashlib,json
J=Path(__file__).resolve().parent
plan=json.loads((J/'PLAN.json').read_bytes())
P=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/env20000_1h/owner.py')
raw=P.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='d631e9e8a8dc7182ecc13bb33459a3aa77703b5d76d80969906e75cead4f6aee'
source=raw.decode('utf8')
assert source.count("if __name__=='__main__':main()")==1
source=source.replace("if __name__=='__main__':main()",'')
exec(compile(source,str(P),'exec'),globals())
def resource(uuid):
    import psutil,shutil,subprocess,time
    line=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    row=[s.strip()for s in line.split(',')]
    apps=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).strip()
    free,used,util=int(row[2]),int(row[3]),int(row[4])
    if not(row[0]==uuid and row[1]=='NVIDIA GeForce RTX 4090'and free>15669 and(not apps or(used<=4096 and util<=30))):
        raise BlockingIOError('Selected4090 has insufficient measured capacity')
    ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
    if ram<=64*1024**3 or disk<=50*1024**3:raise BlockingIOError('Original host headroom required')
    return dict(epoch=time.time(),line=line,compute_apps=apps,light_occupancy_allowed=True,ram=ram,disk=disk)
if __name__=='__main__':main()
