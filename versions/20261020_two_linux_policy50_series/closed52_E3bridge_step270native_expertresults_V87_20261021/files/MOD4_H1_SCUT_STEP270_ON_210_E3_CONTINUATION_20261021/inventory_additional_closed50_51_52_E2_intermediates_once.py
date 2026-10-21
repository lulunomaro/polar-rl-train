from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,re,shutil,time
owned=Path('/mnt/mod4_linux_durable_20261013');C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None;roots=[owned/('T2policy50_2010v'+str(i)+'/e2') for i in (50,51,52)];rows=[];preserved=[]
for root in roots:
 assert root.resolve().is_relative_to(owned.resolve()) and not root.is_symlink();ne=json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes());tr=json.loads((root/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert ne['actual_all_own_children_waited'] and tr['terminal_all_own_children_waited'] and tr['returncode']==0 and not tr['errors'] and tr['final']['passed'];final=tr['final']['final'];assert final['SHA']==v['final_SHA'][str(root)];out=root/'job0/production';files=sorted([p for p in out.glob('model_update*.pt') if re.fullmatch(r'model_update[0-9]+\.pt',p.name)],key=lambda p:int(re.search(r'[0-9]+',p.stem)[0]));keep={files[0],*files[-2:],Path(final['path'])};assert len(files)>3
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(root)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 preserved.append(dict(root=str(root),final=final,retained_checkpoints=[str(p) for p in sorted(keep)],terminal_SHA=hashlib.sha256((root/'NODE_TERMINAL_ACTUAL.json').read_bytes()).hexdigest(),exit_SHA=hashlib.sha256((root/'NODE_EXIT_ACTUAL.json').read_bytes()).hexdigest()))
 for p in files:
  assert not p.is_symlink() and p.resolve().is_relative_to(out.resolve()) and p.is_file()
  if p in keep:continue
  st=p.stat();rows.append(dict(path=str(p),root=str(root),bytes=st.st_size,mtime_ns=st.st_mtime_ns,inode=st.st_ino,producer_SHA=None,SHA_status='not read/rehashed for cleanup; exact stat and closed producer scope'))
print(json.dumps(dict(epoch=time.time(),passed=True,canonical_SHA=hashlib.sha256(C.read_bytes()).hexdigest(),canonical_charged=c['charged_training_seconds'],canonical_remaining=c['remaining_training_seconds'],owned=str(owned),roots=[str(p) for p in roots],candidates=rows,preserved=preserved,total_candidate_bytes=sum(x['bytes'] for x in rows),free_before=shutil.disk_usage(owned).free,only_closed_E2_intermediate_pt=True,no_deletion_yet=True)))
'''
try:
 final_SHA={}
 for i in (50,51,52):
  p=next(W.glob('MOD4_TWO_LINUX_POLICY50_COHORT_'+str(i)+'_*/reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'));x=json.loads(p.read_bytes())['models']['e2']['final'];final_SHA[x['path'].split('/job0/production/')[0]]=x['SHA']
 with (R/'E2_INTERMEDIATE_CLEANUP_INVENTORY_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),explicit_human_message='210 4090可以删除一些老旧不用的训练数据来释放空间'),f,ensure_ascii=False)
 c=t.connect()
 try:v=t.code(c,READ,dict(final_SHA=final_SHA),timeout=90)
 finally:c.close()
 with (R/'CLOSED_E2_INTERMEDIATE_CLEANUP_INVENTORY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(passed=v['passed'],closed_roots=len(v['roots']),candidates=len(v['candidates']),reclaim_bytes=v['total_candidate_bytes'],free_before=v['free_before'])))
except BaseException:
 with (R/'E2_CLEANUP_INVENTORY_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
