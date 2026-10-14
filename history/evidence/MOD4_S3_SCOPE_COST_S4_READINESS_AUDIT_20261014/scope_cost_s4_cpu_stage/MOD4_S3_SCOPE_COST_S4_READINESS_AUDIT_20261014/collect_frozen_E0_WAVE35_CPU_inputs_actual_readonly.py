"""Read protected frozen expert sources for CPU interface/isolation checks only."""
from pathlib import Path
import json,sys,time,hashlib,os,traceback
A=Path(__file__).resolve().parent;R=A/'reports';W=A.parent
sys.path.insert(0,str(W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'))
from read_linux_resume_boundary_actual import connect_linux_only
SOURCES=[dict(expert='E0',path='/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009/learning_logs/2026-10-09_09-45-49_d7_stable_block1_1791510179560330441/model_31903.pt',sha256='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'),dict(expert='E1_WAVE35',path='/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_SECOND_BOUNDED_20261011/learning_logs/2026-10-11_23-27-01_e1_WAVE35_second_bounded_observation_1791732224672851875/model_32259.pt',sha256='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd')]
def main():
 c=sf=None;stamp=str(time.time_ns())
 try:
  c=connect_linux_only();code='''from pathlib import Path
import json,hashlib,time
rows=[]
for row in SOURCES:
 p=Path(row['path']);assert p.resolve().is_relative_to(Path('/home/egde/rl_candidates')) and p.is_file()
 h=hashlib.sha256()
 with p.open('rb') as f:
  while block:=f.read(8388608):h.update(block)
 assert h.hexdigest()==row['sha256']
 rows.append(dict(**row,bytes=p.stat().st_size))
print(json.dumps(dict(epoch=time.time(),sources=rows,read_only=True,no_GPU_or_PPO_or_budgetwrite=True)))
'''.replace('SOURCES',repr(SOURCES))
  si,so,se=c.exec_command('python3 -',timeout=60);si.write(code);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace');j=json.loads(raw)
  folder=A/'frozen_expert_CPU_inputs'/stamp;folder.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(60)
  for row in j['sources']:
   p=folder/(row['expert']+'_'+Path(row['path']).name);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
   assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];row.update(local_path=str(p.resolve()),twohost_byteSHA_exact=True,original_retained=True,CPU_preparation_only_not_gate_admission=True)
  out=R/('FROZEN_E0_WAVE35_CPU_INPUTS_ACTUAL_'+stamp+'.json');out.write_bytes(json.dumps(j,ensure_ascii=False,indent=2).encode())
  print(json.dumps(dict(report=str(out.resolve()),sources=j['sources'],no_GPU_or_gate_training=True)),flush=True)
 except BaseException:
  p=R/('FROZEN_EXPERT_CPU_INPUT_READ_ORIGINAL_ERROR_'+stamp+'.json');p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True,no_auto_retry=True),indent=2).encode());raise
 finally:
  if sf:sf.close()
  if c:c.close()
  os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':main()
