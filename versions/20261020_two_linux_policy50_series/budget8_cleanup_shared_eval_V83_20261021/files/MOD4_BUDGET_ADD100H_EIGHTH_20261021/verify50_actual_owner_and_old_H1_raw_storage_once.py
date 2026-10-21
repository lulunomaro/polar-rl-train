from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021'
s=importlib.util.spec_from_file_location('strict210',N/'strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import collections,hashlib,json,os,psutil,subprocess,time
root=Path(v['owner_root']);owner=v['identity'];actual=psutil.Process(owner['pid']);assert actual.create_time()==owner['creation'] and actual.cmdline()==owner['argv'];hashes={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in v['expected']};assert hashes==v['expected'];raw=(root/'three_slot_finite_owner_v1.py').read_text();assert 'sum(b.CAPS[k] for k in specs)' in raw and "==1548000" in raw and "budget_extensions'])==8" in raw
groups=[]
for name in ('T3_1710v1','T3_1710v2','T3_1710v10hr'):
 old=Path('/mnt/mod4_linux_durable_20261013')/name;ext=collections.defaultdict(lambda:dict(bytes=0,count=0));largest=[]
 for path,dirs,files in os.walk(old,followlinks=False):
  dirs[:]=[d for d in dirs if not (Path(path)/d).is_symlink()]
  for n in files:
   p=Path(path)/n
   if p.is_symlink():continue
   st=p.stat();e=ext[p.suffix.lower() or '<none>'];e['bytes']+=st.st_size;e['count']+=1;largest.append((st.st_size,str(p)))
 groups.append(dict(root=str(old),extensions=dict(ext),largest_files=sorted(largest,reverse=True)[:12]))
print(json.dumps(dict(epoch=time.time(),passed=True,actual_owner_create_argv=True,owner_remote_fullSHA=hashes,approved_scheduled_caps_and_new_total_count_actual=True,old_storage_groups=groups,no_canonical_write_or_training_hotpatch_or_model_hash=True)))
'''
try:
 proof=json.loads((N/'reports/TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes());assert proof['passed'];q=json.loads((N/'reports/TWO50_ORIGINAL_ACCOUNT_COHORT_DETACHED_ACTUAL.json').read_bytes());bound=json.loads((R/'EIGHTH_NEW_CONTROLLERS_AND_UNUSED_WORKFLOW_CPU_ACTUAL.json').read_bytes());c=t.connect()
 try:v=t.code(c,READ,dict(owner_root=q['owner_root'],identity=proof['source210']['owner_identity'],expected=bound['bound_source_SHA']),timeout=90)
 finally:c.close()
 with (R/'COHORT50_ACTUAL_OWNER_BYTES_AND_OLD_RAW_STORAGE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v))
except BaseException:
 with (R/'OWNER_STORAGE_VERIFY_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
