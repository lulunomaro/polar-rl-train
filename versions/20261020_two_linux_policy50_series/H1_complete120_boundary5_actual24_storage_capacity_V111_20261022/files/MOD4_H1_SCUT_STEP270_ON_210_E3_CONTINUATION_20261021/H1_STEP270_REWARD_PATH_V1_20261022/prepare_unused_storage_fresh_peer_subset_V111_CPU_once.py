"""Prepare existing unused closure-only storage supports; never contact a host here."""
from pathlib import Path
import ast,hashlib,itertools,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports'
FUNCTION='''def select_capacity_subset(rows,source_free,target_free):
    from itertools import combinations
    reserve=25*1024**3
    feasible=[]
    for n in range(1,len(rows)+1):
        for group in combinations(rows,n):
            total=sum(x['bytes'] for x in group)
            if source_free+total>reserve and target_free-total>reserve:
                feasible.append((n,total,tuple(x['path'] for x in group),list(group)))
        if feasible:break
    return min(feasible,key=lambda x:x[:3])[-1] if feasible else None
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 reserve=25*1024**3;ns={};exec(FUNCTION,ns);f=ns['select_capacity_subset'];rows=[dict(path='a',bytes=200),dict(path='b',bytes=300),dict(path='c',bytes=400)]
 cases=[('one_small_suffices',reserve-100,reserve+1000,['a']),('two_fit_when_no_one_suffices',reserve-450,reserve+600,['a','b']),('capacity_insufficient_no_target',reserve-450,reserve+450,None),('strict_target_25GiB_boundary',reserve-100,reserve+200,None),('strict_source_25GiB_boundary',reserve-200,reserve+1000,['b'])]
 checks=[]
 for name,source,target,expected in cases:
  got=f(rows,source,target);actual=None if got is None else [x['path'] for x in got];assert actual==expected,(name,actual,expected);checks.append(dict(name=name,passed=True))
 files=[]
 for stage,name in [('H1_STEP270_REWARD_BOUNDARY_REPAIR_RESOURCE_V23_20261022','relocate_selected_H1_closed_forensics_unused_once.py'),('H1_STEP270_REWARD_BOUNDARY_RESOURCE_V24_20261022','relocate_selected_H1_closed_forensics_unused_once.py'),('H1_STEP270_REWARD_BOUNDARY_RESOURCE_V24_20261022','relocate_selected_pair_closed_forensics_unused_once.py')]:
  n=T/stage;p=n/name;s=p.read_text('utf8');assert 'select_capacity_subset' not in s
  old=p.with_name(p.stem.replace('_once','')+'_UNEXECUTED_PRE_CAPACITY_DRAFT.py');assert not old.exists();old.write_bytes(p.read_bytes())
  marker="def main():";assert s.count(marker)==1;s=s.replace(marker,FUNCTION+'\n'+marker)
  needle="manifest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()\n        c=d.connect72(secret);d.code(c,d.PY72,ops.INSTALL,dict(root=ROOT72,parent='/home/lc01/Zonglin Li/zonglin2/forensic_originals'),timeout=30)"
  assert s.count(needle)==1,p
  new="""c=d.connect72(secret)
        capacity=d.code(c,d.PY72,"from pathlib import Path;import json,shutil,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage(Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals')).free,no_target_or_process_created=True)))",{},timeout=30)
        selected=select_capacity_subset(rows,inv['source_free'],capacity['free'])
        put('PEER_FORENSICS_FRESH_PEER_CAPACITY_SELECTION_ACTUAL.json',dict(epoch=time.time(),source_free_snapshot=inv['source_free'],peer_capacity_snapshot=capacity,selected=selected,original_source_and_target_reserve_bytes=25*1024**3,no_transfer_process_created_yet=True))
        if selected is None:
            put('PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json',dict(epoch=time.time(),source_above_original_disk25=False,no_target_or_process_created=True,source_free=inv['source_free'],target_free=capacity['free'],not_permission_to_lower_guard_or_delete_unique_files=True));return
        rows=selected
        manifest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        d.code(c,d.PY72,ops.INSTALL,dict(root=ROOT72,parent='/home/lc01/Zonglin Li/zonglin2/forensic_originals'),timeout=30)"""
  s=s.replace(needle,new);ast.parse(s);p.write_text(s,encoding='utf8');files.append(dict(path=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),prior_unused_source=str(old),prior_SHA=hashlib.sha256(old.read_bytes()).hexdigest()))
 put('V111_UNUSED_CLOSED_STORAGE_FRESH_PEER_CAPACITY_SUBSET_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_and_AST=True,checks=checks,files=files,scope='Only unused finite storage orchestration after actual closure/wholeCPU/health/cost; first fresh peer capacity and smallest sufficient subset before any target or process',source_target_reserve_25GiB_unchanged=True,receiver_final_capacity_and_full_SHA_ack_guards_unchanged=True,passed_TLS_HMAC_core_not_edited_or_reexecuted=True,no_training_source_or_runtime_hotpatch_no_host_contact=True))
 print(json.dumps(dict(prepared_unused_support=True,CPU_cases=len(checks),source_files=len(files),no_host_contact=True)))
except BaseException:put('V111_UNUSED_STORAGE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
