from pathlib import Path
import sys,os,json,hashlib,time,shlex
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_linux_runtime_cpu_once import S
D=Path(__file__).resolve().parent
P=D/'payload_v2'

def main():
    assert not (D/'reports/LINUX_V2_TARGET_CPU_ACTUAL.json').exists()
    (P/'temporary_state_binding.py').write_bytes((D/'port_cpu/temporary_state_binding.py').read_bytes())
    c=connect_linux_only()
    try:
        sf=c.open_sftp();sf.mkdir(S+'/payload_v2')
        for p in P.iterdir():sf.put(str(p),S+'/payload_v2/'+p.name)
        sf.put(str(D/'port_cpu/actual_CPU_17b_20000_v2/LINUX20000_PORT_CPU_ACTUAL_REVIEW.json'),S+'/LOCAL_PARENT_SOURCE_AND_EXPANSION_CPU_PROOF.json')
        sf.close()
        python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
        cmd=shlex.quote(python)+' '+shlex.quote(S+'/payload_v2/prepare_code_binding_plan_CPU_schema_reviewed.py')
        si,so,se=c.exec_command(cmd,timeout=45);out=so.read();err=se.read();code=so.channel.recv_exit_status()
        q=D/'reports/LINUX_CODE_BINDING_PLAN_TARGET_CPU_ACTUAL.json';q.write_bytes(json.dumps(dict(code=code,stdout=out.decode(),stderr=err.decode(),no_GPU_or_budget=True),indent=2).encode());assert code==0,str(q)
        text=r'''
from pathlib import Path
import sys,json,torch,hashlib,os,time,shutil,subprocess
P=Path(S);D=P/'payload_v2';sys.path.insert(0,str(D));import temporary_state_binding as b
source=P/'source/WINDOWS512_LAST_COMPLETE_28UPDATES.pt';rng=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False)
b.validate_source512(ck,b.H(source));candidate,proof=b.expand_learned_source(ck,b.H(source));b.validate(candidate,b.H(source));assert b.floating_count(candidate)==107
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
plan=json.loads((D/'LINUX_CODE_BINDING_PLAN.json').read_bytes());assert plan['source_checkpoint_SHA']==b.SOURCE_SHA and plan['target_num_envs']==20000
for f in D.glob('*.py'):compile(f.read_text(),str(f),'exec')
cpu=dict(epoch=time.time(),passed=True,source_SHA=b.H(source),num_envs=20000,actorcriticAdam_globalprivate_exact=True,all99paths_and_13counts_exact=True,exact_family_quotas=[6000,4000,4000,3000,3000],no_RNG_or_CUDA=True,fullstate_first_runtime_binding_pending=True,local22_negative_and_disk_proof='LOCAL_PARENT_SOURCE_AND_EXPANSION_CPU_PROOF.json')
(P/'TARGET_FULLSTATE_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2))
files=[]
for folder in (P/'runtime',D):
 for f in sorted(folder.rglob('*')):
  if f.is_file() and '__pycache__' not in str(f):
   h=hashlib.sha256()
   with f.open('rb') as fd:
    for block in iter(lambda:fd.read(1048576),b''):h.update(block)
   files.append(dict(path=str(f),bytes=f.stat().st_size,sha256=h.hexdigest()))
print(json.dumps(dict(cpu=cpu,sourcefreeze=files,available_RAM_B=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024,durable_free_B=shutil.disk_usage(P).free,GPU_free=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout),ensure_ascii=False))
'''
        # The explicit interpreter imports torch only; no AppLauncher / Isaac import.
        si,so,se=c.exec_command(shlex.quote(python)+' -',timeout=75);si.write('S='+repr(S)+'\n'+text);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();code=so.channel.recv_exit_status()
        q=D/'reports/LINUX_V2_TARGET_CPU_ACTUAL.json';q.write_bytes(json.dumps(dict(code=code,stdout=out.decode(),stderr=err.decode(),no_GPU_or_budget=True),indent=2).encode());assert code==0,str(q)
        r=json.loads(out);(D/'TARGET_SOURCEFREEZE_CPU_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf8')
        print(json.dumps(dict(report=str(q),passed=r['cpu']['passed'],RAM_available_B=r['available_RAM_B'],durable_free_B=r['durable_free_B'],source_files=len(r['sourcefreeze']))))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
