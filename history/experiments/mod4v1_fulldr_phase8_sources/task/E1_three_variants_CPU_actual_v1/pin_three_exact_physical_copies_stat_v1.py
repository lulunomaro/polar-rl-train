"""Savedreceipt-derived exactphysical copies only, stat no sourcecontent."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf')
p=W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/reports/FINAL878_THREE_MODELS_METADATA_ACTUAL_EXIT_LOCKS_COST_INPUTS.json';pr=p.read_bytes();m=json.loads(pr);downloads=[r for n in m['nodes'] for r in n['final_downloads']];r=next(r for r in downloads if r['rank']==0);assert r['SHA']=='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1'
f=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/reports/FIRST_CURB_SLOPE_FINAL_MODELS_AND_EXACT_DISTINCT_INTERVAL_COST_CPU_ACTUAL.json';fr=f.read_bytes();fm=json.loads(fr);rows=[dict(variant='CURB_PROTECTED878',role='E1_CURB',path=r['local_path'],expected_SHA=r['SHA'],expected_bytes=r['bytes'],source_metadata_path=str(p),source_metadata_SHA=hashlib.sha256(pr).hexdigest(),rank0_only_historical_world3=True)]
for job,name,role in [(0,'CURB_INDEPENDENT113','E1_CURB'),(1,'SLOPE_INDEPENDENT50','E1_SLOPE')]:
 x=next(x for x in fm['closed_models'] if x['job']==job);rows.append(dict(variant=name,role=role,path=x['local_path'],expected_SHA=x['SHA'],expected_bytes=x['bytes'],source_metadata_path=str(f),source_metadata_SHA=hashlib.sha256(fr).hexdigest()))
for x in rows:
 try:s=Path(x['path']).stat();x.update(exists=True,actual_bytes=s.st_size,mtime_ns=s.st_mtime_ns);assert s.st_size==x['expected_bytes']
 except FileNotFoundError:x.update(exists=False,status='STOP_THIS_ASSET_EXACT_COPY_MISSING_NO_SUBSTITUTE')
out=B/'THREE_EXACT_SOURCE_PHYSICAL_STAT_V1.json'
with out.open('x',encoding='utf-8') as file:json.dump(dict(kind='SOURCE_RECEIPT_BOUND_PHYSICAL_COPIES_STAT_ONLY',sources=rows,sourcebytes_hash_decode=0,original210_network_not_retried=True),file,ensure_ascii=False,indent=2)
print(json.dumps(dict(report=str(out),sources=rows,sourcebyte_reads_hashes_decodes=0),ensure_ascii=False,indent=2))
