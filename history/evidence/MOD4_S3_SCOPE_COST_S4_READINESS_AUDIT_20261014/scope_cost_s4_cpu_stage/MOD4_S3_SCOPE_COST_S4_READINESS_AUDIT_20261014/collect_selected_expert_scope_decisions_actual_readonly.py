"""Follow declared expert scope references, bounded registry-name discovery."""
from pathlib import Path
import sys,json,time,hashlib,os,traceback
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports'
sys.path.insert(0,str(W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'))
from read_linux_resume_boundary_actual import connect_linux_only
CODE='''from pathlib import Path
import json,time,hashlib,os
root=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');reports=root/'reports'
patterns=['D9_RETENTION18_ACTUAL_REVIEW.json','E1_WAVE35_SECOND*COMPLETE*DECISION*.json','E1_WAVE35_SECOND*COMPLETE*REVIEW*.json','E1_CURB20_DIRECTION_EXPOSURE_MATCHED*COMPLETE*DECISION*.json','E1_CURB20_DIRECTION_EXPOSURE_MATCHED*COMPLETE*REVIEW*.json','E1_SLOPE*COMPLETE_SCOPE_DECISION.json','EXPERT*.json','*REGISTRY*.json']
files=set();matched={}
for pattern in patterns:
 found=sorted(reports.glob(pattern));matched[pattern]=[str(p) for p in found];files.update(found)
registry=[];visited=0
for base,dirs,names in os.walk(root):
 rel=Path(base).relative_to(root);visited+=1
 if len(rel.parts)>=4:dirs[:]=[]
 dirs[:]=[n for n in dirs if n not in ('__pycache__','.git','assets','logs','learning_logs')]
 assert visited<10000
 for name in names:
  if 'registry' in name.lower() and Path(name).suffix.lower() in ('.json','.yaml','.yml'):
   p=Path(base)/name;registry.append(str(p));files.add(p)
canonical=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
sha=hashlib.sha256(canonical.read_bytes()).hexdigest();rows=[]
for p in sorted(files):
 assert p.resolve().is_relative_to(root.resolve()) and p.stat().st_size<25000000
 b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
assert hashlib.sha256(canonical.read_bytes()).hexdigest()==sha
print(json.dumps(dict(epoch=time.time(),patterns=matched,files=rows,bounded_registry_candidates=registry,registry_search_root=str(root),registry_search_max_depth=4,registry_search_not_global_host_absence_claim=True,canonical_SHA=sha,canonical_bytes_unchanged_during_read=True,no_GPU_PPO_signal_budgetwrite=True)))
'''

def main():
 c=sf=None;stamp=str(time.time_ns())
 try:
  c=connect_linux_only();si,so,se=c.exec_command('python3 -',timeout=60);si.write(CODE);si.flush();si.channel.shutdown_write()
  raw=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace');j=json.loads(raw)
  sf=c.open_sftp();sf.get_channel().settimeout(60);folder=A/'actual_scope_decisions'/stamp;folder.mkdir(parents=True);copied=[]
  for i,row in enumerate(j['files']):
   p=folder/(str(i)+'_'+Path(row['path']).name);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
   assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];copied.append(dict(**row,local_path=str(p.resolve()),twohost_bytes_SHA_exact=True))
  j['local_collected_files']=copied;p=R/('EXPERT_SCOPE_DECISIONS_ACTUAL_COLLECTION_'+stamp+'.json');p.write_bytes(json.dumps(j,ensure_ascii=False,indent=2).encode())
  print(json.dumps(dict(report=str(p.resolve()),scoped_evidence_files=[Path(r['path']).name for r in copied],registry_candidates=j['bounded_registry_candidates'],registry_lookup_is_bounded=True,no_GPU_or_PPO=True)),flush=True)
 except BaseException:
  p=R/('EXPERT_SCOPE_READONLY_ORIGINAL_ERROR_'+stamp+'.json');p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True,no_auto_retry=True),indent=2).encode());raise
 finally:
  if sf:sf.close()
  if c:c.close()
  os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':main()
