"""Exact saved424/404 textSHA joins only; NEVER PT/stat/USD/NPZ/binary reads."""
from pathlib import Path
import hashlib,json,collections,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');C=W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011';S=W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'
TEXT={'.py','.json','.md','.txt'};NEVER={'.pt','.pth','.ckpt','.onnx','.safetensors','.usd','.usda','.usdc','.npz','.npy','.pkl','.zip','.pyc'}

def main():
 sup=json.loads((T/'legacy_source_joins/CURB141_EXACT_RUNTIME_PACKAGE_SUPPLEMENT_v1.json').read_text(encoding='utf-8'))
 sf=Path(sup['source_freeze']['path']);sr=S/'reports/SNAPSHOT_OWN_FORMAL_CPU_1791686991841256500.json';sc=json.loads(sr.read_text(encoding='utf-8'))
 specs=[('CURB141',json.loads(sf.read_text(encoding='utf-8'))['sha256'],sf,424,[Path(sup['local_package_root']),C/'exposure_matched_payload',C/'startup_reviewed_payload',C/'payload',C/'inherited_source',W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload/job0/runtime']),('SLOPE135',sc['manifest']['source_map'],sr,404,[S/'snapshot_reviewed_payload',S/'inherited_source',S/'payload',W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload/job1/runtime'])]
 result=dict(kind='EXACT_CANONICAL_CURB141424_SLOPE135404_SOURCE_JOIN',permission='SOURCE_METADATA_ONLY',PT_stats_reads_hashes_decodes=0,SSH_SDK_GPU_budget_operations=0,packages={});cache={}
 for name,source_map,ref,count,roots in specs:
  assert len(source_map)==count;(B/(name+'_MOTHER_SOURCE_MAP_v2.json')).write_text(json.dumps(dict(actualsource_map_path=str(ref),actualsource_map_SHA=hashlib.sha256(ref.read_bytes()).hexdigest(),source_count=count,source_map=source_map),indent=2),encoding='utf-8')
  rows=[];missing=[];other=[]
  for rel,expected in source_map.items():
   suffix=Path(rel).suffix.lower()
   if suffix not in TEXT and ".py." not in Path(rel).name:
    other.append(dict(relative=rel,original_source_SHA=expected,status='SOURCE_MAP_BINARY_OR_NON_TEXT_REFERENCE_ONLY_NOT_STATTED_OR_READ'));continue
   paths=[]
   for root in roots:
    for p in (root/rel,root/Path(rel).name,root/'isaac/mod4'/Path(rel).name):
     if p not in paths:paths.append(p)
   matches=[];mismatches=[]
   for p in paths:
    assert p.suffix.lower() in TEXT or ".py." in p.name
    if not p.is_file():continue
    key=str(p)
    if key not in cache:
     raw=p.read_bytes();cache[key]=(len(raw),hashlib.sha256(raw).hexdigest())
    size,sha=cache[key]
    if sha==expected:matches.append(dict(path=key,bytes=size,SHA=sha))
    else:mismatches.append(dict(path=key,actual_SHA=sha))
   if matches:rows.append(dict(relative=rel,expected_SHA=expected,selected=matches[0],all_same_SHA_candidates=matches,nonmatching_candidates=mismatches))
   else:missing.append(dict(relative=rel,expected_SHA=expected,checked_text_paths=[str(p) for p in paths],nonmatching_candidates=mismatches))
  result['packages'][name]=dict(original_count=count,verified_text_count=len(rows),metadata_only_nontext_count=len(other),missing_text_count=len(missing),files=rows,nontext=other,missing=missing,explicit_source_roots=[str(p) for p in roots])
 out=B/'EXACT_424_404_TEXT_SOURCE_JOIN_v2.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(report=str(out),packages={k:dict(count=v['original_count'],verified=v['verified_text_count'],metadataonly=v['metadata_only_nontext_count'],missing=v['missing_text_count'],missing_relatives=[r['relative'] for r in v['missing']]) for k,v in result['packages'].items()}),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('E1_RESOLVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
