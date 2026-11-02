"""AST source dependency/timing review; no projectmodule execution/actor/model I/O."""
from pathlib import Path
import ast,hashlib,json,re
B=Path(__file__).resolve().parent;T=B.parent.parent
for name in ['CURB141','SLOPE135']:
 root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');meta=json.loads((root/'E1_CANONICAL_SOURCE_METADATA.json').read_text(encoding='utf-8'));rt=root/'runtime/isaac/mod4';queue=[root/'prepared_e1_native24_noupdate_worker_v1.py',rt/meta['entry'],rt/(meta['restore_helper']+'.py')];seen=set();nodes=[];external=set();lines=[]
 while queue:
  p=queue.pop(0)
  if p in seen:continue
  seen.add(p);raw=p.read_bytes();s=raw.decode('utf-8-sig');tree=ast.parse(s);imports=[]
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):imports += [a.name for a in node.names]
   elif isinstance(node,ast.ImportFrom) and node.module:imports.append(node.module)
  internal=[]
  for mod in sorted(set(imports)):
   candidates=[rt/(mod+'.py'),root/'runtime'/(mod.replace('.','/')+'.py')]
   hits=[c for c in candidates if c.is_file()]
   if hits:internal.append(str(hits[0].relative_to(root)));queue.append(hits[0])
   else:external.add(mod)
  for i,line in enumerate(s.splitlines(),1):
   if re.search(r'(?i)(step_dt|control_us|control_period|POLICY_HZ|phase_elapsed|resampling_time|episode_length_s|validate_clock|\b10000\b|\b3500\b|\.01.*decimation|round\(\.01)',line):lines.append(dict(relative=str(p.relative_to(root)),line=i,text=line.strip()))
  nodes.append(dict(relative=str(p.relative_to(root)),SHA=hashlib.sha256(raw).hexdigest(),AST_SHA=hashlib.sha256(ast.dump(tree,include_attributes=False).encode()).hexdigest(),local_import_edges=internal))
 stale=[]
 for row in lines:
  text=row['text']
  if re.search(r'((step_dt|control_dt).*==\s*\.01|round\(\.01|nominal.*3500|control_us\s*==\s*10000)',text) and not text.startswith(('#','"','\'')):
   stale.append(row)
 out=dict(kind='E1_ACTIVE_SOURCE_DEPENDENCY_AND_CLOCK_REVIEW_CANDIDATES',canonical=name,nodes=nodes,external_imports=sorted(external),timing_review_lines=lines,possible_stale_active_clock_or_nominal=stale,project_modules_executed=False,PT_SDK_GPU_operations=0)
 with (root/'ACTIVE_SOURCE_DEPENDENCY_CLOCK_REVIEW_V1.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(canonical=name,active_nodes=len(nodes),review_lines=len(lines),possible_stale=stale),indent=2))
