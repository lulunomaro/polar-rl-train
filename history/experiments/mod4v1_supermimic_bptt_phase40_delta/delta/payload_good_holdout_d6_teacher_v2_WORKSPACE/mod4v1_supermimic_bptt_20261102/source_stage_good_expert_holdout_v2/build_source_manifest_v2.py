"""Build/verify the NEW nine-member SOURCE seal; never prepare, stage or launch.
Only pinned project text/JSON is read. Complete runtime/bank/asset/vendor inputs
remain an independent future preflight obligation, not this SOURCE mirror.
"""
from pathlib import Path, PurePosixPath
import argparse
import ast
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R=HERE.parent
WORKSPACE=R.parent
T=WORKSPACE/'mod4v1_experts_fulldr_rm70_20261101'
OLD=R/'source_stage_good_expert_holdout_v1'
UPSTREAM=R/'source_good_expert_holdout_subset_v1'
PLAN=T/'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
SUPERVISOR=T/'NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py'
REVIEW=R/'source_good_holdout_parent_readiness_review_v1/SOURCE_REPORT.md'
FILES=('README.md','SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','TEST_REPORT.json','WHITELIST_DIFF.json',
       'build_source_manifest_v2.py','derive_stage_good_holdout_v2.py','stage_good_expert_holdout_v2.py','test_good_holdout_v2_source.py')
ENTRY_PIN=(47717,'f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d')
PLAN_PIN=(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
EXTRA_PIN=(9247,'7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27')
INDEX_PIN=(21075,'6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
OLD_ROOT='94330bb54b9dda0a7081d139f1cd0bd156f5e62c387273871f5b7cfebdea2e79'
UPSTREAM_ROOT='032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534'
CHANGED={'prepare','preflight_summary','stage'}
ADDED={'preservation_digest','original_dependency_map','retain_originals','validate_preservation','preservation_summary'}


def need(value,message):
    if not value:raise ValueError(message)


def H(raw):return hashlib.sha256(raw).hexdigest()

def identity(raw):return dict(bytes=len(raw),SHA256=H(raw))

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def root_of(rows):
    return H(''.join(f"{r['name']}\t{r['bytes']}\t{r['SHA256']}\n" for r in sorted(rows,key=lambda r:r['name'])).encode())


def relative(path):
    value=path.relative_to(WORKSPACE).as_posix()
    pure=PurePosixPath(value)
    need(not pure.is_absolute() and '..' not in pure.parts and pure.parts[0] in (R.name,T.name),'outside SOURCE workspace')
    return value


def original_path(value):
    """Exact original Windows provenance prefix to the actual project mirror."""
    text=str(value).replace('\\','/')
    prefix='F:/RMPOLAR-RL/'
    need(text.startswith(prefix),'unexpected source provenance root')
    suffix=text[len(prefix):]
    pure=PurePosixPath(suffix)
    need(not pure.is_absolute() and all(part not in ('','.','..') for part in suffix.split('/')),'invalid SOURCE relative path')
    need(pure.parts[0] in (R.name,T.name),'SOURCE reference outside the two project trees')
    return WORKSPACE.joinpath(*pure.parts)


def read_text(path,pin=None):
    path=Path(path)
    relative(path)
    need(path.suffix.lower() in ('.py','.json','.md','.txt','.yml','.yaml'),'not SOURCE text: '+path.name)
    need(not path.is_symlink(),'SOURCE symlink forbidden')
    raw=path.read_bytes()
    if pin is not None:need((len(raw),H(raw))==pin,'SOURCE pin differs: '+relative(path))
    raw.decode('utf-8')
    if path.suffix=='.py':ast.parse(raw)
    return raw


def verify_old_seal(folder,filename,root,count,inputs):
    path=folder/filename
    seal=json.loads(read_text(path));inputs.add(path)
    need(seal['root_SHA256']==root and len(seal['files'])==count and root_of(seal['files'])==root,'old immutable SOURCE seal differs')
    for row in seal['files']:
        name=row['name'];need(PurePosixPath(name).name==name,'old sealed filename must be flat')
        member=folder/name
        read_text(member,(row['bytes'],row['SHA256']));inputs.add(member)
    return dict(workspace_relative=relative(path),root_SHA256=root,files=count)


def function_map(raw):
    return {node.name:node for node in ast.parse(raw).body if isinstance(node,ast.FunctionDef)}


def function_source(raw,node):
    return '\n'.join(raw.decode().splitlines()[node.lineno-1:node.end_lineno])+'\n'


def metadata_products():
    inputs=set()
    upstream_seal=verify_old_seal(UPSTREAM,'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json',UPSTREAM_ROOT,14,inputs)
    old_seal=verify_old_seal(OLD,'SOURCE_STAGE_GOOD_EXPERT_SEAL_V1.json',OLD_ROOT,8,inputs)
    index_path=UPSTREAM/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
    index=json.loads(read_text(index_path,INDEX_PIN));inputs.add(index_path)
    old_raw=read_text(OLD/'stage_good_expert_holdout_v1.py',(38828,'fc9dd74437258d408e0223359b45814909b5a9a2f80df450dfdea1f546290a2f'))
    entry=read_text(HERE/'stage_good_expert_holdout_v2.py',ENTRY_PIN)
    spec=importlib.util.spec_from_file_location('_good_holdout_v2_manifest_source',HERE/'stage_good_expert_holdout_v2.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # Import is the complete stdlib-only CLI, not its main/prepare/stage functions.
    plan_raw=read_text(PLAN,PLAN_PIN);plan=json.loads(plan_raw);inputs.add(PLAN)
    read_text(SUPERVISOR,EXTRA_PIN);inputs.add(SUPERVISOR)
    producer_worker=R/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py'
    producer_worker_raw=read_text(producer_worker,(17704,'7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7'));inputs.add(producer_worker)
    expected=module.original_dependency_map(plan['worker_files'],index)
    need(len(expected)==27,'fixed original27 required')
    dependency_sources={row['relative']:original_path(row['path']) for row in index['inherited_original_worker_source_entries']}
    dependency_sources['single_gpu_group_supervisor.py']=SUPERVISOR
    need(len(dependency_sources)==25,'all25 actual original text source paths required')
    original_rows=[]
    for rel,(n,sha) in sorted(expected.items()):
        row=dict(relative=rel,bytes=n,SHA256=sha)
        if rel in dependency_sources:
            path=dependency_sources[rel];read_text(path,(n,sha));inputs.add(path)
            row.update(source_workspace_relative=relative(path),source_class='ACTUAL_ORIGINAL_TEXT_BYTES_VERIFIED')
        else:
            need(rel.startswith('pinned_assets/'),'unexpected original non-text dependency')
            row['source_class']='ORIGINAL_ASSET_METADATA_ONLY_NOT_OPENED_HERE'
        original_rows.append(row)
    flat=[]
    for row in index['overlay_entries']:
        path=original_path(row['path']);read_text(path,(row['bytes'],row['SHA256']));inputs.add(path)
        flat.append(dict(relative=row['relative'],flat_name=path.name,source_workspace_relative=relative(path),bytes=row['bytes'],SHA256=row['SHA256']))
    need(len(flat)==20 and len({r['relative'] for r in flat})==20 and len({r['flat_name'] for r in flat})==20,'complete unmodified flat20 overlay required')
    for row in index['provenance']:
        path=original_path(row['path']);read_text(path,(row['bytes'],row['SHA256']));inputs.add(path)
    read_text(REVIEW,(24021,'6145d41a8184daba7014b37ef5f06eac1dd2fb8795eee53720a48f2c03a930e8'));inputs.add(REVIEW)
    old_functions=function_map(old_raw);new_functions=function_map(entry)
    changed={n for n in old_functions if ast.dump(old_functions[n],include_attributes=False)!=ast.dump(new_functions[n],include_attributes=False)}
    need(changed==CHANGED and set(new_functions)-set(old_functions)==ADDED,'narrow whole-function whitelist differs')
    proofs=[]
    for name in sorted(old_functions):
        a=function_source(old_raw,old_functions[name]).encode();b=function_source(entry,new_functions[name]).encode()
        proofs.append(dict(function=name,changed=name in changed,old_source_SHA256=H(a),new_source_SHA256=H(b),whole_AST_unchanged=name not in changed))
    need(sum(not row['changed'] for row in proofs)==22,'all22 other original functions must remain complete')
    for name in ('metadata_validate','native_boundary','producer_final','verify_close_dependency_imports','main'):
        need(name not in changed,'protected complete function changed: '+name)
    report=json.loads(read_text(HERE/'TEST_REPORT.json'))
    need(report['passed'] is True and report['tests_run']==18 and report['errors']==report['failures']==0,'NEW18 source tests required')
    need(all(type(v) is int and v==0 for v in report['audit'].values()),'SOURCE I/O audit must be zero')
    need(report['actual_prepare_preflight_stage_dispatch_executed'] is False and report['actual_parent_worker_executed'] is False,'SOURCE report must not be native execution')
    need(report['pure_source_metadata_validate_exercised_with_synthetic_producers'] is True and report['old18_tests_replayed'] is False,'actual unmodified metadata schema must be tested without replaying old tests')
    rows=[]
    for path in sorted(inputs,key=relative):rows.append(dict(workspace_relative=relative(path),**identity(read_text(path))))
    mirror=dict(kind='COMPLETE_GOOD_HOLDOUT_V2_PINNED_TEXT_MIRROR_INPUTS',source_only=True,
        root_layout='F:/RMPOLAR-RL is provenance only; mirror contains the two named sibling project trees under any actual workspace root',
        files=rows,files_count=len(rows),raw_assets_static_banks_models_included=False,
        complete_runtime_materialization_proved=False,requires_new_source_package_members_and_seal_separately=True)
    mirror_raw=encoded(mirror)
    diff=dict(kind='GOOD_HOLDOUT_V2_EXACT_THREE_FUNCTION_SOURCE_DIFF',source_only=True,changed_functions=sorted(changed),
        new_source_helpers=sorted(ADDED),unchanged_original_functions=22,whole_function_source_proofs=proofs,
        old_cli=dict(workspace_relative=relative(OLD/'stage_good_expert_holdout_v1.py'),**identity(old_raw)),
        new_cli=dict(name='stage_good_expert_holdout_v2.py',**identity(entry)),
        semantics=dict(original_dependency_set='exact fixed27, not arbitrary extras',
            retained_original_namespace=module.RETAIN_PREFIX,independent_input_paths_bytes_and_hashes=True,
            stage_binds_actual_stream_hash_observations=True,sidecar=module.ORIGINAL_PRESERVATION_NAME,
            plan_metadata_bound_unchanged=262144,sidecar_bound_bytes=8*1024*1024,
            overlay20_and_all_runtime_protocols_unchanged=True,new_manual_approval_gate=False))
    source_index=dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V2',source_derivation_version=2,
        status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',enabled=False,source_native_enabled=False,staged=False,dispatched=False,
        actual_native_binding='UNKNOWN',actual_frozen_evaluation=None,quality_improvement_claim=None,
        entry=dict(name='stage_good_expert_holdout_v2.py',**identity(entry)),upstream_source_seal=upstream_seal,old_materializer_seal=old_seal,
        original_group_plan=dict(workspace_relative=relative(PLAN),**identity(plan_raw)),original_worker_files=original_rows,
        producer_guard_source_test_input=dict(workspace_relative=relative(producer_worker),**identity(producer_worker_raw),executed=False),
        original_dependency_count=27,actual_original_text_sources_verified=25,asset_rows_metadata_only=2,
        source_index=dict(workspace_relative=relative(index_path),bytes=INDEX_PIN[0],SHA256=INDEX_PIN[1]),
        flat_source_dir_complete20_mapping=flat,
        source_mirror=dict(name='SOURCE_MIRROR_INPUTS.json',**identity(mirror_raw),files_count=len(rows)),
        wire=dict(COMPLETE_NAME=module.COMPLETE_NAME,plan_overlay_protocol='V1 unchanged',
            parent='single_gpu_good_expert_holdout_parent_v1.py',requested_roles=list(module.REQUESTED),
            deferred_roles=[role for role in module.ROLES if role not in module.REQUESTED],H1_constructed=False,
            seeds=list(module.ALLOWED_SEEDS),num_envs=80,controls_each_role=750,teacher='original embedded public teacher mean, not residual'),
        future_required_inputs=['actual closed V8 group and fixed27 worker_files plus complete permitted worker_sources/pinned_assets',
            'both complete selected-role E1 runtime/source/static-bank/dependency trees',
            'actual closed Admission2 metadata plus TASK/INSTALL_MANIFEST/full all-state producer guard source proof',
            'full original vendor7 with fixed tree hash, not overlay3 imports',
            'independent external parent dispatcher/controller/wait/evidence collector, not supplied by this source package'],
        preserved_original_resource_logic='privateGPU_EX + global_finite_EX/Creadonly/empty23500/RAM96/disk25/wait1800/ready900/deadline2400',
        native_unknowns=['actual E1/SDK robot writer MRO/source binding and physical reset readback',
            'actual original inputs completeness/asset/vendor7 bytes on target','actual cache/open/hash/decode/freeze and App close/native waits',
            'independent per-seed quality outcomes'],source_test_report=report)
    return {'SOURCE_MIRROR_INPUTS.json':mirror,'WHITELIST_DIFF.json':diff,'SOURCE_INDEX.json':source_index}


def create_or_verify(name,value,verify):
    path=HERE/name;raw=encoded(value)
    if path.exists():need(path.read_bytes()==raw,'frozen/new generated SOURCE metadata differs: '+name)
    else:
        need(not verify,'missing sealed SOURCE metadata: '+name)
        with path.open('xb')as stream:stream.write(raw)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    products=metadata_products()
    for name,value in products.items():create_or_verify(name,value,args.verify)
    rows=[dict(name=name,**identity(read_text(HERE/name))) for name in sorted(FILES)]
    seal=dict(kind='SOURCE_ONLY_GOOD_EXPERT_HOLDOUT_MATERIALIZER_IMMUTABLE_SEAL_V2',status='SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE',
        enabled=False,source_native_enabled=False,staged=False,dispatched=False,actual_native_binding='UNKNOWN',
        root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root_of(rows),files=rows)
    create_or_verify('SOURCE_SEAL.json',seal,args.verify)
    print(json.dumps(dict(kind='SOURCE_GOOD_HOLDOUT_V2_SEAL_VERIFIED_NO_WRITES'if args.verify else'SOURCE_GOOD_HOLDOUT_V2_SEALED',
        files=len(rows),root_SHA256=seal['root_SHA256'],mirror_files=products['SOURCE_MIRROR_INPUTS.json']['files_count'],
        original_dependency_count=27,new_tests=18,actual_prepare_preflight_stage_dispatch_executed=False),indent=2))


if __name__=='__main__':main()
