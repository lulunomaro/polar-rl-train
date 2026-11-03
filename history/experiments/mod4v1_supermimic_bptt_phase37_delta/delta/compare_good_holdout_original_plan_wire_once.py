"""NEW functional source-input identity diagnosis after strict preflight failed.
Read one original project GROUP_PLAN wire once, compare the known cached published
metadata once. No model, trajectory, SDK, canonical, resource or parent operation.
"""
from pathlib import Path
import hashlib,json,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json';dest=R/'discovery/good_holdout_original_plan_wire_v1';assert not out.exists()and not dest.exists();H=lambda b:hashlib.sha256(b).hexdigest()
f=json.loads((R/'reports/GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIX_ACTUAL_PREFLIGHT_V1.json').read_bytes());assert f['returncode']==1 and 'fixed published original GROUP_PLAN bytes differ'in f['stderr'];remote='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700/GROUP_PLAN.json';cached=R.parent/'mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json';cb=cached.read_bytes();ch=H(cb);assert(len(cb),ch)==(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0');cval=json.loads(cb)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(remote,'rb')as stream:raw=stream.read(262145)
finally:s.close();c.close()
assert 0<len(raw)<=262144;sha=H(raw);value=json.loads(raw);assert type(value)is dict;dest.mkdir()
with(dest/'ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json').open('xb')as stream:stream.write(raw)
diffs=[]
def walk(a,b,path='$'):
 if type(a)is not type(b):
  if len(diffs)<30:diffs.append(dict(path=path,actual_type=type(a).__name__,cached_type=type(b).__name__))
 elif type(a)is dict:
  for k in sorted(a.keys()|b.keys()):
   if k not in a or k not in b:
    if len(diffs)<30:diffs.append(dict(path=path+'.'+k,actual_present=k in a,cached_present=k in b))
   else:walk(a[k],b[k],path+'.'+k)
 elif type(a)is list:
  if len(a)!=len(b)and len(diffs)<30:diffs.append(dict(path=path,actual_length=len(a),cached_length=len(b)))
  for i,(x,y)in enumerate(zip(a,b)):walk(x,y,path+'['+str(i)+']')
 elif a!=b and len(diffs)<30:diffs.append(dict(path=path,actual=a,cached=b))
walk(value,cval);canonical=lambda x:H(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode());v=dict(kind='GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_PUBLISHED_IDENTITY_FUNCTIONAL_DIAGNOSIS_V1',epoch=time.time(),actual_original_path=remote,actual_wire_local_path=str(dest/'ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json'),actual_wire_bytes=len(raw),actual_wire_SHA256=sha,cached_published_path=str(cached),cached_published_bytes=len(cb),cached_published_SHA256=ch,actual_canonical_SHA256=canonical(value),cached_canonical_SHA256=canonical(cval),whole_decoded_values_equal=value==cval,differences_first30=diffs,physical_original_wire_reads=1,original_wire_byte_hashes=1,original_wire_decodes=1,cached_metadata_reads=1,cached_metadata_decodes=1,actual_model_raw_trajectory_SDK_GPU_C_lock_signal_or_parent_operations=0,old_preflight_failure_unchanged=True,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf8')as stream:json.dump(v,stream,indent=2)
print(json.dumps(v,indent=2))
