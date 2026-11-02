"""Source-only append proof after dispatch; never edit stagedsource or model."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;old=T/'E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/worker_n20k_typed_noupdate.py'
def loop(p):
 tree=ast.parse(p.read_bytes());v=[n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and any(isinstance(a,ast.Constant) and a.value==24 for a in n.iter.args)];assert len(v)==1;return ast.dump(v[0],include_attributes=False)
base=loop(old);rows=[]
for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
 sf=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');actual=B/(name+'_ACTUAL_TYPED_SOURCE_V1');meta=json.loads((actual/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());rel='runtime/isaac/mod4/'+meta['entry'];assert loop(actual/'worker_n20k_typed_noupdate.py')==base
 functions=[]
 for fn in ['build_env','runner_config','describe','dry_run']:
  a=[ast.parse((x/rel).read_bytes()) for x in [sf,actual]];f=[next(n for n in z.body if isinstance(n,ast.FunctionDef) and n.name==fn) for z in a];assert ast.dump(f[0],include_attributes=False)==ast.dump(f[1],include_attributes=False);functions.append(fn)
 rows.append(dict(variant=name,ownfactory_runnerconfig_describe_dryrun_AST_exact=functions,native_for24_AST_exact=True,native_for24_AST_SHA=hashlib.sha256(base.encode()).hexdigest(),original_sourcefinal_SHA=hashlib.sha256((sf/'FINAL_SOURCE_INDEX.json').read_bytes()).hexdigest(),append_only_no_staged_case_hotpatch=True))
p=B/'ACTUAL_NEW_SOURCE_INVARIANCE_APPEND_PROOF_V1.json'
with p.open('x',encoding='utf-8') as f:json.dump(dict(kind='APPEND_SOURCE_AST_ONLY_NOT_NEW_SDK_OR_MODEL_PASS',rows=rows,PT_SDK_operations=0),f,indent=2)
print(json.dumps(dict(proof=str(p),variants=3,no_staged_edits=True,source_model_reads=0),indent=2))
