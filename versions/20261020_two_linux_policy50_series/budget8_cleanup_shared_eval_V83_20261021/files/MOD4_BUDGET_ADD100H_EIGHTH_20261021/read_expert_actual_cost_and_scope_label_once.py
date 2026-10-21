from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
REMOTE=r'''
from pathlib import Path
import collections,fcntl,hashlib,json,os,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest();locks=[]
try:
 for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['budget_extensions'][-1]['extension_id']=='USER_ADD100H_20261021_8TH'
 # Correct only a descriptive inherited label; the exact eight applied records and all accounting stay unchanged.
 oldlabel=c['budget_scope'];c['budget_scope']='Original10h + four20h + fifth40h + sixth100h + seventh100h + eighth100h; actual charged learning time; no automatic addition'
 new=json.dumps(c,ensure_ascii=False,indent=2).encode();before=json.loads(raw);assert all(c[k]==val for k,val in before.items() if k!='budget_scope')
 if new!=raw:
  temp=C.with_name(C.name+'.eighth-label-'+str(time.time_ns()))
  with temp.open('xb') as f:f.write(new);f.flush();os.fsync(f.fileno())
  assert C.read_bytes()==raw;os.replace(temp,C);fd=os.open(C.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 fields=collections.Counter();schemas=collections.Counter();direct=collections.defaultdict(lambda:dict(seconds=0.,segments=0));separate=[];multi=[]
 for i,row in enumerate(c['completed_segments']):
  schemas[','.join(sorted(row))]+=1
  for k in row:fields[k]+=1
  if isinstance(row.get('experts'),dict):
   for k,x in row['experts'].items():
    direct[k]['seconds']+=x.get('charged_seconds',0.);direct[k]['segments']+=1
   multi.append(dict(index=i,kind=row.get('kind'),run_id=row.get('run_id'),experts={k:x.get('charged_seconds') for k,x in row['experts'].items()}))
  else:
   separate.append(dict(index=i,fields={k:val for k,val in row.items() if isinstance(val,(str,int,float,bool)) and k not in ('authorization',)}))
 print(json.dumps(dict(epoch=time.time(),canonical_path=str(C),authorized=1548000,extensions=8,charged=c['charged_training_seconds'],remaining=c['remaining_training_seconds'],active=None,completed_count=len(c['completed_segments']),explicit_expert_intervals=dict(direct),single_segment_metadata=separate,explicit_expert_segments=multi,field_counts=fields,schema_counts=schemas,scope_label_correction=dict(old=oldlabel,new=c['budget_scope'],only_description_changed=True,before_SHA=H(raw),after_SHA=H(C.read_bytes()),accounting_and_all_eight_records_exact=True),no_full_canonical_copy=True)))
finally:
 for f in reversed(locks):f.close()
'''
try:
 with (R/'EXPERT_COST_READ_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,REMOTE,timeout=90)
 finally:c.close()
 with (R/'EXPERT_COST_AND_SCOPE_LABEL_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(experts=v['explicit_expert_intervals'],single_count=len(v['single_segment_metadata']),schema_counts=v['schema_counts'],budget=dict(total=v['authorized'],charged=v['charged'],remaining=v['remaining']),scope_label_corrected=True)))
except BaseException:
 with (R/'EXPERT_COST_READ_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
