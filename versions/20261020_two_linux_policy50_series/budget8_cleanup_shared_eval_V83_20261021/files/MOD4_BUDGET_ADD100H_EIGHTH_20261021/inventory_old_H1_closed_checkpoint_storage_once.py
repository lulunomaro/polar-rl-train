from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import collections,json,os,re,subprocess,time
owned=Path('/mnt/mod4_linux_durable_20261013');names=['T3_1710v1','T3_1710v2','T3_1710v10hr','MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016','MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016'];out=[]
for name in names:
 root=owned/name;assert root.resolve().is_relative_to(owned.resolve()) and not root.is_symlink();groups=collections.defaultdict(lambda:dict(bytes=0,count=0,samples=[]));flags=[]
 for path,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[d for d in dirs if not (Path(path)/d).is_symlink()]
  for n in files:
   p=Path(path)/n
   if p.is_symlink():continue
   if p.suffix=='.pt':
    st=p.stat();k=str(p.parent);g=groups[k];g['bytes']+=st.st_size;g['count']+=1
    if len(g['samples'])<3:g['samples'].append(dict(path=str(p),bytes=st.st_size))
   if n in ('NODE_EXIT_ACTUAL.json','NODE_TERMINAL_ACTUAL.json','FINAL.json','latest_complete.json'):flags.append(str(p))
 out.append(dict(root=str(root),checkpoint_groups=dict(groups),boundary_receipt_paths=flags))
print(json.dumps(dict(epoch=time.time(),groups=out,only_old_project_metadata_and_file_sizes_read=True,no_hash_or_delete_or_GPU_or_account_write=True)))
'''
try:
 with (R/'OLD_TRAINING_STORAGE_INVENTORY_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,READ,timeout=90)
 finally:c.close()
 with (R/'OLD_H1_AND_TRAINING_CHECKPOINT_STORAGE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v,ensure_ascii=False))
except BaseException:
 with (R/'OLD_TRAINING_STORAGE_INVENTORY_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
