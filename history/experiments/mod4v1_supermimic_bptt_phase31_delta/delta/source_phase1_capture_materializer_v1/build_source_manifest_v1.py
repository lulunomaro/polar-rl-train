"""Build/verify this NEW SOURCE manifest and seal; never invoke prepare/stage/main."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
import stage_phase1_capture_v1 as m

HERE=Path(__file__).resolve().parent
R=HERE.parent
FILES=('README.md','derive_static_helpers_v1.py','static_source_helpers_v1.py','stage_phase1_capture_v1.py',
       'test_materializer_stdlib_v1.py','TEST_REPORT.json','build_source_manifest_v1.py','SOURCE_INDEX.json',
       'SOURCE_MIRROR_INPUTS.json','WHITELIST_DIFF.json')
ORIGINAL='source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'
ORIGINAL_PIN=(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40')


def H(raw):return hashlib.sha256(raw).hexdigest()


def raw_json(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def put_new_or_equal(name,raw):
    path=HERE/name
    if path.exists():
        old=path.read_bytes();m.need(old==raw,'existing NEW source artifact differs; do not overwrite: '+name)
    else:
        with path.open('xb') as stream:stream.write(raw)


def record(path):
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw)
    return dict(relative=path.relative_to(HERE).as_posix(),bytes=len(raw),SHA256=H(raw))


def metadata_products():
    bundle=m.load_sources(R)  # source PIN verification, not original/native static input preflight
    original_raw=(R/ORIGINAL).read_bytes();m.need((len(original_raw),H(original_raw))==ORIGINAL_PIN,'original stager source changed')
    old={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(original_raw).body if isinstance(n,ast.FunctionDef)}
    helper_raw=(HERE/'static_source_helpers_v1.py').read_bytes()
    helper={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(helper_raw).body if isinstance(n,ast.FunctionDef)}
    m.need(len(helper)==17 and all(old[k]==v for k,v in helper.items()),'complete17 helper AST proof differs')
    report=json.loads((HERE/'TEST_REPORT.json').read_bytes())
    m.need(report['passed'] is True and report['tests_run']==23 and report['errors']==report['failures']==0
           and all(v==0 for v in report['audit'].values()),'23 SOURCE tests/audit0 required')
    m.need(all(report[k]==0 for k in ('actual_prepare_calls','actual_preflight_calls','stage_calls','native_worker_or_parent_calls')),'actual execution is not SOURCE')
    files={}
    def add(path):
        path=Path(path);m.need(path.is_relative_to(R),'source mirror path outside pinned R')
        info=m.identity(path);rel=path.relative_to(R).as_posix()
        row=dict(relative=rel,bytes=info['bytes'],SHA256=info['SHA'])
        m.need(rel not in files or files[rel]==row,'conflicting source-mirror reference');files[rel]=row
    for path,_ in bundle['sources'].values():add(path)
    add(m.reference_path(R,bundle['index']['original_index']['path']));add(R/ORIGINAL)
    for relative in bundle['index']['all_actuation_original_sources']:add(m.reference_path(R,relative))
    mirror=dict(kind='COMPLETE_PINNED_TEXT_SOURCE_MIRROR_INPUTS_PHASE1_V1',purpose=m.PURPOSE,
        root_semantics='R_source_only_mirror_preserve_relative_paths_not_flat27',files=[files[r] for r in sorted(files)],
        file_count=len(files),all_actual_source_bytes_verified=True,original_C_source_pin_count=182,
        excludes_actual_original_runtime_banks_assets_native_root_and_all_models=True,
        actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,native_executed=False)
    helper_nodes={n.name:n for n in ast.parse(helper_raw).body if isinstance(n,ast.FunctionDef)}
    def portable(value):
        if isinstance(value,list):return [portable(v) for v in value]
        if isinstance(value,dict):return {k:(Path(v).relative_to(R).as_posix() if k=='path' and isinstance(v,str) and Path(v).is_relative_to(R) else portable(v)) for k,v in value.items()}
        return value
    diff=dict(kind='PHASE1_CAPTURE_MINIMAL_SOURCE_WHITELIST_DIFF_V1',original_relative=ORIGINAL,
        original_bytes=ORIGINAL_PIN[0],original_SHA256=ORIGINAL_PIN[1],unchanged_complete_helper_AST_names=sorted(helper),
        complete_AST_equality_verified=True,
        helper_complete_function_source_SHA256={k:H(ast.get_source_segment(helper_raw.decode('utf-8'),helper_nodes[k]).encode()) for k in sorted(helper)},
        intentional_omissions=['producer_final: synthetic PT0 has no PPO/A1 producer descriptor route'],
        NEW_functions=['canonical','reference_path','verify_package','load_sources','native_boundary','retain_originals','validate_preservation',
                       'prepare','metadata_validate','preflight_summary','stage','main'],
        native_boundary_delta='keep actual closed root/GO/semantic metadata, no producer FINAL/checkpoint descriptors',
        prepare_delta='full original8/staticbanks/assets/deps/vendor7 with independent preoverlay bytes and conflict-only retained namespace; E3-only capture_controls64/128',
        metadata_delta='whole fixed source closure safe imports; actual canonical7a092/AppV6->dc4Base; PT/C/lock I/O and native import guard; no actor/FD admission',
        stage_delta='exclusive streaming copy/observed installed hashes; fixed purpose/materialized/parent_launches receipt; no launch',
        parent_resource_blocks_changed=False,worker13_changed=False,old_seals_changed=False)
    mirror_raw=raw_json(mirror)
    index=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_INDEX_V1',purpose=m.PURPOSE,entry=record(HERE/'stage_phase1_capture_v1.py'),
        requested_roles=['E3'],complete_role_catalog=list(m.ROLES),deferred_roles=list(m.ROLES[1:]),H1_constructed=False,
        controls=[64,128],num_envs=80,seed=20260928,policy='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',PT_reads=0,training=False,quality_evaluation=False,
        CLI_required=['--original-group-root','--source-root','--native-root','--new-root','--group-id','--gpu-uuid'],
        CLI_modes_exactone=['--preflight-only','--stage'],root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,
        controller_receipt_interface=dict(purpose=m.PURPOSE,materialized=True,parent_launches=0,receipt_bytes_SHA256_pinned_by_external_controller=True),
        source_closure=portable(bundle['receipt']),source_mirror=dict(relative='SOURCE_MIRROR_INPUTS.json',bytes=len(mirror_raw),SHA256=H(mirror_raw),files=len(files)),
        unchanged_helpers=dict(count=17,relative='static_source_helpers_v1.py',bytes=len(helper_raw),SHA256=H(helper_raw),proof='WHITELIST_DIFF.json'),
        inventory_proof='independent complete actual input byte inventory+original planSHA/logical treeSHA/input_path/readbytes; conflicts retained; stage uses observed stream hashes',
        source_only=True,source_native_enabled=False,materialized=False,staged=False,dispatched=False,actual_SDK_executed=False,
        tests_run=23,actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,
        real_static_inputs_or_vendor7_integrity_tested=False,gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    return {'SOURCE_MIRROR_INPUTS.json':mirror_raw,'WHITELIST_DIFF.json':raw_json(diff),'SOURCE_INDEX.json':raw_json(index)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    products=metadata_products()
    if args.verify:
        for name,raw in products.items():m.need((HERE/name).read_bytes()==raw,'generated source metadata differs: '+name)
        seal=json.loads((HERE/'SOURCE_SEAL.json').read_bytes())
        rows=[record(HERE/name) for name in FILES]
        m.need(rows==seal['files'] and m.canonical(rows)==seal['content_root_sha256'],'NEW materializer SOURCE seal differs')
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_SEAL_VERIFIED_NO_WRITES',files=len(rows),content_root_sha256=seal['content_root_sha256'])))
    else:
        for name,raw in products.items():put_new_or_equal(name,raw)
        rows=[record(HERE/name) for name in FILES]
        seal=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_SEAL_V1',files=rows,content_root_sha256=m.canonical(rows),
            frozen=True,source_only=True,purpose=m.PURPOSE,source_native_enabled=False,materialized=False,staged=False,dispatched=False,
            actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,actual_SDK_executed=False,
            gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
        put_new_or_equal('SOURCE_SEAL.json',raw_json(seal))
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_SEALED_NOT_PREPARED',files=len(rows),source_mirror_files=json.loads(products['SOURCE_MIRROR_INPUTS.json'])['file_count'],content_root_sha256=seal['content_root_sha256'])))


if __name__=='__main__':main()
