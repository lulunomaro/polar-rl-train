"""LOCAL source-only reuse of proven authority and isolated launcher."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent
C=T/'E0_ALL_RANDOMIZATION_OFF_DR0_SOURCE_CONTRACT_V1_20261101'
L=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101'
def main():
 purpose=json.loads((N/'reports/DERIVE_DR064_PURPOSE_FROZEN.json').read_bytes());assert purpose['executions']==1
 with (N/'reports/DERIVE_DR064_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),source_only=True),f)
 for name in ('dr0_contract.py','dr0_actual_readback.py'):
  with (N/name).open('xb') as f:f.write((C/name).read_bytes())
 source=(L/'contract_latest32.py').read_text(encoding='utf8');tree=ast.parse(source)
 keep=[x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CANONICAL','GENERATION','KNOWN235_RUN') for t in x.targets) or isinstance(x,ast.FunctionDef) and x.name=='validate_authority']
 with (N/'authority235_dr064.py').open('x',encoding='utf8') as f:f.write(ast.unparse(ast.Module(body=keep,type_ignores=[]))+'\n')
 parent=(L/'target_latest32_parent_ROOT_ONLY.py').read_text(encoding='utf8');fn=next(x for x in ast.parse(parent).body if isinstance(x,ast.FunctionDef) and x.name=='audit_current')
 head='from pathlib import Path\nimport hashlib,json,psutil,time\nfrom authority235_dr064 import CANONICAL,validate_authority\ndef read(p):return json.loads(Path(p).read_bytes())\n'
 with (N/'audit235_dr064.py').open('x',encoding='utf8') as f:f.write(head+ast.get_source_segment(parent,fn)+'\n')
 p=T/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101/source/launcher213.py'
 with (N/'launcher213.py').open('xb') as f:f.write(p.read_bytes())
 rows=[]
 for name in ('dr0_contract.py','dr0_actual_readback.py','authority235_dr064.py','audit235_dr064.py','launcher213.py','probe_dr0_64_worker_ROOT_ONLY.py'):
  p=N/name;b=p.read_bytes();ast.parse(b);rows.append(dict(relative=name,path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
 with (N/'reports/DR064_SOURCE_COMPONENTS.json').open('x',encoding='utf8') as f:json.dump(dict(kind='DR064_MODEL_FREE_SOURCE_COMPONENTS',files=rows,core_INDEX_SHA='71d34a674382769f04f36a1ee6fc2018ba7e5215d14fbc7553471b11cf94f029',actual_SDK_pending=True),f,indent=2)
if __name__=='__main__':main()
