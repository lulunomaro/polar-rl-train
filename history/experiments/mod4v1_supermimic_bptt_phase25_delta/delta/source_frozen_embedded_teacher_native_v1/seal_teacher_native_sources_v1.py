"""One-shot small-source seal only: no tests, actors, models, resources or stage."""
from pathlib import Path
import ast, copy, hashlib, json, zipfile
HERE=Path(__file__).resolve().parent; PROJECT=HERE.parent
OLD=PROJECT/'source_frozen_eval_microbatch_parent_v1'
CORE=PROJECT/'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py'
OLD_STAGE=PROJECT/'source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py'


def H(raw): return hashlib.sha256(raw).hexdigest()
def info(path):
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA256=H(raw))
def put(name,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
    with (HERE/name).open('xb') as stream:stream.write(raw)
    return raw

def read(path):return path.read_text(encoding='utf-8').replace('\r\n','\n')
def fn(text,name):return next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def dump(node):return ast.dump(node,include_attributes=False)
def normalized(node):
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1':n.value='ONEGPU_REQUESTED_E3_W35_A1_FROZEN80_MICROBATCH_V1'
            return n
        def visit_Call(self,n):
            self.generic_visit(n)
            if isinstance(n.func,ast.Name) and n.func.id=='dict':n.keywords=[k for k in n.keywords if k.arg not in ('policy_variant','evaluation_purpose','actor_semantics')]
            return n
    return Normalize().visit(copy.deepcopy(node))
def pair(a,b,name,normalize=False):
    x,y=fn(a,name),fn(b,name)
    if normalize:x,y=normalized(x),normalized(y)
    assert dump(x)==dump(y),name
    return dict(equal=True,AST_SHA256=H(dump(x).encode()),normalization_applied=normalize)


def main():
    outputs=('TEACHER_NATIVE_PROTECTED_SOURCE_PROOF_V1.json','TEACHER_NATIVE_SMALL_SOURCE_BUNDLE_V1.zip',
             'TEACHER_NATIVE_SOURCE_DELIVERY_V1.json','SHA256_TEACHER_NATIVE_DELIVERY_V1.txt')
    assert not any((HERE/name).exists() for name in outputs),'one-shot seal output exists'
    # Exact read-only originals and complete new Python source syntax.
    pins={OLD/'single_gpu_e3_w35_a1_frozen_parent_v1.py':(8991,'9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b'),
          OLD/'worker_formal_a1_microbatch_v1.py':(15016,'a370656816f134c13219f5e013cedfddc8f16ca41d85ef1f7cb9b751152cce56'),
          CORE:(37927,'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e'),
          OLD_STAGE:(32953,'9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952')}
    for path,pin in pins.items():
        observed=info(path);assert (observed['bytes'],observed['SHA256'])==pin
    for path in HERE.glob('*.py'):compile(path.read_bytes(),str(path),'exec')
    index_path=HERE/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json';index=json.loads(index_path.read_bytes())
    assert len(index['entries'])==16
    original=json.loads((PROJECT/'source_stage_a1_microbatch_eval_v2/MICROBATCH_STAGE_INDEX_V2.json').read_bytes())
    old_by={r['relative']:r for r in original['entries']};new_by={r['relative']:r for r in index['entries']}
    changed={'single_gpu_e3_w35_a1_frozen_parent_v1.py','frozen_eval_microbatch_runtime_v1.py','worker_sources/parent/worker_five_original_n80.py'}
    assert all(old_by[k]==new_by[k] for k in set(old_by)-changed)
    parent=read(HERE/'single_gpu_e3_w35_embedded_teacher_parent_v1.py')
    worker=read(HERE/'worker_formal_embedded_teacher_v1.py');runtime=read(HERE/'frozen_embedded_teacher_native_runtime_v1.py');base=read(CORE)
    proof=dict(kind='SOURCE_AST_PROTECTION_NOT_NATIVE_PROOF_V1',original_pins=[info(p) for p in pins],
        parent_complete_main=pair(read(OLD/'single_gpu_e3_w35_a1_frozen_parent_v1.py'),parent,'main',True),
        worker_complete_main=pair(read(OLD/'worker_formal_a1_microbatch_v1.py'),worker,'main',True),
        exact_common_functions={n:pair(base,runtime,n) for n in ('record_primary_error','close_original_eval_resources')},
        allowed_normalization=dict(parent_constant='reference label only',worker_dict_keywords=['policy_variant','evaluation_purpose','actor_semantics']),
        additional_parent_entry='original main returns first, then closed metadata grade; failure exits 1; no external wait proof',
        unchanged_original_index_rows=11,new_maps=16,actual_native_or_math_operations=0)
    a=next(n for n in fn(base,'evaluate_waited_eval_case').body if isinstance(n,ast.Try)).body
    b=next(n for n in fn(runtime,'evaluate_waited_eval_case').body if isinstance(n,ast.Try)).body
    def i(nodes,text):return next(j for j,n in enumerate(nodes) if text in ast.unparse(n))
    pieces={'common_cache_prefix':(a[:i(a,"mean = source.get('frozen_mean')")],b[:i(b,"final.get('policy_variant')")]),
            'common_close_suffix':(a[i(a,'PRE_CLOSE.json'):],b[i(b,'PRE_CLOSE.json'):])}
    proof['semantic_policy_only_replacement']={}
    for name,(x,y) in pieces.items():
        dx=dump(ast.Module(body=x,type_ignores=[]));dy=dump(ast.Module(body=y,type_ignores=[]));assert dx==dy
        proof['semantic_policy_only_replacement'][name]=dict(equal=True,AST_SHA256=H(dx.encode()))
    before={n.name:dump(n) for n in ast.parse(read(OLD_STAGE)).body if isinstance(n,ast.FunctionDef)}
    after={n.name:dump(n) for n in ast.parse(read(HERE/'stage_embedded_teacher_native_v1.py')).body if isinstance(n,ast.FunctionDef)}
    actual_changed=sorted(k for k in before if before[k]!=after.get(k))
    assert set(actual_changed)<=set(('source_mappings','prepare','metadata_validate','preflight_summary','stage')),actual_changed
    proof['stager_changed_old_functions_only']=actual_changed
    proof['stager_unchanged_old_function_AST_SHA256']={k:H(before[k].encode()) for k in before if before[k]==after.get(k)}
    test=json.loads((HERE/'TEST_RESULTS_TEACHER_NATIVE_STDLIB_V1.json').read_bytes())
    assert test['passed'] is True and test['tests']==18 and test['failures']==test['errors']==0 and test['Torch_imported'] is False
    put('TEACHER_NATIVE_PROTECTED_SOURCE_PROOF_V1.json',proof)
    flat={}
    for row in index['entries']:
        path=Path(row['path']);raw=path.read_bytes();assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
        name=row['path'].replace('\\','/').rsplit('/',1)[-1];assert name not in flat;flat[name]=raw
    selected=['EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json','stage_embedded_teacher_native_v1.py',
              'TEACHER_NATIVE_FIELDS_CONTRACT_V1.json','TEACHER_NATIVE_STAGE_QUICKSTART_V1.md',
              'TEST_RESULTS_TEACHER_NATIVE_STDLIB_V1.json','TEACHER_NATIVE_PROTECTED_SOURCE_PROOF_V1.json']
    members={'flat/'+n:raw for n,raw in flat.items()}
    members.update({name:(HERE/name).read_bytes() for name in selected})
    manifest=dict(kind='TEACHER_NATIVE_PORTABLE_SMALL_SOURCE_CONTENTS_V1',source_only=True,files=[dict(relative=k,bytes=len(v),SHA256=H(v)) for k,v in sorted(members.items())],
        actual_runtime_assets_or_models_in_bundle=False,actual_staging_or_dispatch=False)
    members['TEACHER_NATIVE_BUNDLE_CONTENTS_V1.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    zip_path=HERE/'TEACHER_NATIVE_SMALL_SOURCE_BUNDLE_V1.zip'
    with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,raw in sorted(members.items()):z.writestr(name,raw)
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None and set(z.namelist())==set(members)
        for name,raw in members.items():assert z.read(name)==raw
    delivery=dict(kind='TEACHER_NATIVE_SOURCE_DELIVERY_NOT_NATIVE_V1',source_only=True,
        stable_code=[info(HERE/name) for name in ('stage_embedded_teacher_native_v1.py','EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json',
            'frozen_embedded_teacher_native_runtime_v1.py','single_gpu_e3_w35_embedded_teacher_parent_v1.py','worker_formal_embedded_teacher_v1.py','producer_teacher_guard_v1.py')],
        bundle=info(zip_path),bundle_members=len(members),tests=test,protected_proof=info(HERE/'TEACHER_NATIVE_PROTECTED_SOURCE_PROOF_V1.json'),
        actual_stage_dispatch_Torch_SDK_GPU_PT_raw_C_locks_SSH_Git_operations=0,actual_qualified_reference=None,relative_improvement=None)
    put('TEACHER_NATIVE_SOURCE_DELIVERY_V1.json',delivery)
    final_names=selected+['frozen_embedded_teacher_native_runtime_v1.py','single_gpu_e3_w35_embedded_teacher_parent_v1.py',
        'worker_formal_embedded_teacher_v1.py','producer_teacher_guard_v1.py','build_embedded_teacher_native_v1.py',
        'test_embedded_teacher_native_stdlib_v1.py','seal_teacher_native_sources_v1.py',zip_path.name,'TEACHER_NATIVE_SOURCE_DELIVERY_V1.json']
    rows=[info(HERE/name) for name in dict.fromkeys(final_names)]
    with (HERE/'SHA256_TEACHER_NATIVE_DELIVERY_V1.txt').open('x',encoding='utf-8',newline='\n') as stream:
        for row in rows:stream.write(row['SHA256']+'  '+str(row['bytes'])+'  '+row['path']+'\n')
    print(json.dumps(delivery,indent=2))


if __name__=='__main__':main()
