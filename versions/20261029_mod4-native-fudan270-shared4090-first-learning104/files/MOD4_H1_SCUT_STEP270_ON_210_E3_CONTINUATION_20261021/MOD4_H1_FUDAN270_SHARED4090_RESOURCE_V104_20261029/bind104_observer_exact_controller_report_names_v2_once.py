from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;L=N.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';A=L/'TWO104_FUDAN270_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1';B=L/'TWO104_FUDAN270_FIRST_CLOSING_INITIAL_CPU_SOURCE_V2'
B.mkdir();(B/'reports').mkdir()
rows=[]
for p in A.iterdir():
 if p.is_file() and p.suffix in ('.py','.md'):
  s=p.read_text('utf8').replace(A.name,B.name).replace('TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json','TWO104_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').replace('TWO103_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json','TWO104_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json')
  if p.suffix=='.py':ast.parse(s)
  q=B/p.name
  with q.open('x',encoding='utf8') as f:f.write(s)
  rows.append(dict(path=str(q),bytes=q.stat().st_size,SHA=hashlib.sha256(q.read_bytes()).hexdigest()))
with (B/'FROZEN_UNUSED_TWO104_BOUND_FIRST_CLOSING_INITIAL_CPU_INDEX_V2.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),unused=True,source_only_report_filename_alignment=True,originalV1_retained=True,files=rows),f,indent=2)
print(json.dumps(dict(selected_first_close_review_source=str(B),no_remote_GPU_or_model=True)))
