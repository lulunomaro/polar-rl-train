"""SOURCE-only V3 dependency derivation; no candidate edits, staging or execution."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
V2=ROOT/'source_phase1_capture_worker_v2'
B2=ROOT/'source_phase1_passive_sensor_capture_v2'
DIAG=ROOT/'source_phase1_sensor_reset_identity_diagnosis_v1'
V2_SEAL='caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5'
V2_ROOT='83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
B2_SEAL='be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'
B2_MANIFEST='2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca'
INHERITED=('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py',
           'worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def identity(path):
    path=Path(path)
    if path.suffix.lower() not in ('.py','.json','.md','.txt'):raise ValueError('SOURCE suffix required')
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw,filename=str(path))
    return dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def check_row(row,path=None):
    path=Path(path if path is not None else row['path'])
    actual=identity(path)
    if actual!={'bytes':row['bytes'],'SHA256':row.get('SHA256',row.get('sha256'))}:
        raise ValueError('full SOURCE pin mismatch: '+str(path))
    return dict(path=str(path),**actual)


def sealed_members(folder,expected,count):
    seal_path=folder/'SOURCE_SEAL.json';info=identity(seal_path)
    if info['SHA256']!=expected:raise ValueError('dependency seal mismatch: '+str(folder))
    value=json.loads(seal_path.read_text(encoding='utf-8'));files=value['files']
    if type(files) is dict:files=[dict(relative=key,**row) for key,row in files.items()]
    if len(files)!=count:raise ValueError('complete member count mismatch')
    members=[]
    for row in files:
        relative=Path(row['relative'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('member path escape')
        checked=check_row(row,folder/relative)
        members.append(dict(relative=row['relative'],bytes=checked['bytes'],SHA256=checked['SHA256']))
    root=value.get('content_root_sha256')
    if folder.name in ('source_phase1_actuation_capture_v1','source_phase1_state_context_partition_v1'):
        # Exact original seal_source.py root format: sorted name + NUL + SHA + LF.
        payload=''.join(name+'\0'+value['files'][name]['sha256']+'\n' for name in sorted(value['files'])).encode()
    else:payload=canonical(value['files'])
    if root is not None and hashlib.sha256(payload).hexdigest()!=root:
        raise ValueError('seal content root mismatch: '+str(folder))
    return dict(path=str(seal_path),**info,members=members,content_root_sha256=root)


def verify_frozen_v2():
    sealed=sealed_members(V2,V2_SEAL,13)
    if sealed['content_root_sha256']!=V2_ROOT:raise ValueError('V2 lineage root mismatch')
    if identity(V2/'CAPTURE_SOURCE_INDEX.json')!=dict(bytes=65961,SHA256='cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7'):
        raise ValueError('V2 source index mismatch')
    index=json.loads((V2/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))
    for row in index['original17']+index['new_sources']+index['dependency_sources']+index['bootstrap_original_sources']:
        check_row(row)
    for value in index['dependency_seals'].values():
        folder=Path(value['path']).parent
        observed=sealed_members(folder,value['SHA256'],len(value['members']))
        if observed!=value:raise ValueError('frozen dependency record changed')
    for relative,row in index['all_actuation_original_sources'].items():check_row(row,ROOT/relative)
    for name in INHERITED:
        if (HERE/name).read_bytes()!=(V2/name).read_bytes():raise ValueError('V3 candidate differs from V2: '+name)
    return sealed,index


def source_pin_closure(value):
    """Full files behind all sealed manifest source pins; never import plant files."""
    found={};references=0
    def walk(item):
        nonlocal references
        if type(item) is dict:
            if 'source_path' in item or 'source_sha256' in item:
                if not {'source_path','source_sha256'}<=item.keys():raise ValueError('incomplete manifest source pin')
                path=str(Path(item['source_path']).resolve());digest=item['source_sha256'];references+=1
                if path in found and found[path]!=digest:raise ValueError('manifest pins disagree')
                found[path]=digest
            for child in item.values():walk(child)
        elif type(item) is list:
            for child in item:walk(child)
    walk(value)
    rows=[]
    for path,digest in sorted(found.items()):
        if Path(path).suffix!='.py' or not Path(path).is_relative_to(ROOT):raise ValueError('manifest source closure escaped')
        actual=identity(path)
        if actual['SHA256']!=digest:raise ValueError('manifest original SOURCE mismatch: '+path)
        rows.append(dict(path=path,**actual))
    if not rows:raise ValueError('empty manifest original source closure')
    return dict(pin_references=references,unique_full_source_files=len(rows),sources=rows,
                full_bytes_SHA_AST_verified=True,plant_source_modules_executed=False)


def full_source_import(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    try:spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name,None);raise
    return module


def verify_B2():
    sealed=sealed_members(B2,B2_SEAL,13)
    manifest_path=B2/'SOURCE_API_MANIFEST.json'
    if identity(manifest_path)!=dict(bytes=336133,SHA256=B2_MANIFEST):raise ValueError('final B2 manifest mismatch')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    closure=source_pin_closure(manifest)
    api=full_source_import(B2/'source_api.py','_phase1_capture_v3_B2_source_api_metadata')
    if api.build_manifest()!=manifest:raise ValueError('complete B2 manifest regeneration differs')
    if len(manifest['roles'])!=8 or any(row['reset_chain']['status']!='SOURCE_CONFIRMED_LIVE_UNKNOWN' for row in manifest['roles'].values()):
        raise ValueError('eight role source/live status mismatch')
    receipt=json.loads((B2/'STDLIB_FAKE_TEST_RECEIPT_v3.json').read_text(encoding='utf-8'))
    return sealed,dict(path=str(manifest_path),**identity(manifest_path),original_source_closure=closure,
                       full_manifest_regenerated_equal=True,role_count=8,role_status='SOURCE_CONFIRMED_LIVE_UNKNOWN',
                       upstream_stdlib_receipt=receipt,upstream_tests_not_reexecuted_here=True,
                       B2_actual_Torch_CPU_or_SDK_executed_here=False)


def verify_diagnostics():
    path=DIAG/'FINAL_SOURCE_HANDOFF_RECEIPT.json';value=json.loads(path.read_text(encoding='utf-8'))
    if value['status']!='PASS' or value['B2_source_seal']['sha256']!=B2_SEAL:raise ValueError('final diagnostic handoff mismatch')
    check_row(value['B2_source_seal'])
    for row in value['B2_members']:check_row(row,B2/row['relative'])
    rows=[check_row(row) for row in value['source_diagnosis_files']]
    return dict(final_handoff=dict(path=str(path),**identity(path)),source_references=rows,
                read_only_references_not_runtime_modules=True,actual_native_binding='NOT_EXECUTED')


def build_index():
    if (HERE/'SOURCE_SEAL.json').exists():raise RuntimeError('frozen V3; new lineage required')
    v2,index=verify_frozen_v2();sensor,manifest=verify_B2();diagnostics=verify_diagnostics()
    old=copy.deepcopy(index)
    index['source_version']=3
    for row in index['new_sources']:
        row['path']=str(HERE/row['install_relative']);check_row(row)
    for row in index['dependency_sources']:
        if row['install_relative'].startswith('phase1_deps/sensor/'):
            row.update(path=str(B2/Path(row['path']).name),**identity(B2/Path(row['path']).name))
    index['dependency_seals']['sensor']=sensor
    inherited_derivation=old['source_derivation']
    index['source_derivation']=dict(kind='PHASE1_CAPTURE_WORKER_V3_B2_DEPENDENCY_ONLY_DERIVATION',source_version=3,
        v2_frozen_seal=v2,v1_frozen_seal=inherited_derivation['v1_frozen_seal'],
        actual_bootstrap_source_evidence=inherited_derivation['actual_bootstrap_source_evidence'],
        inherited_v2_source_derivation=inherited_derivation,
        unchanged_V2_candidate_files=list(INHERITED),candidate_logic_diff_count=0,worker_main_diff_count=0,
        dependency_only_change='final sealed B2 source_api/passive_capture/manifest + complete 13-member sensor seal',
        preserved_V1_typed_protocol=True,parent_source_unchanged=True,
        strict_original_B2_verifier_reimplemented_here=False,actual_outer_reset_callable='UNKNOWN_UNTIL_NEW_NATIVE_RECEIPT',
        upstream_sensor_source_revision=2,actual_V3_native_or_resource_run=False)
    index['sensor_source_manifest']=manifest
    index['sensor_reset_diagnostic_source_references']=diagnostics
    index['full_B2_package_verified']=True
    # Explicitly verify the minimal wire-compatible projection back to V2.
    projection=copy.deepcopy(index)
    projection['source_version']=2;projection['source_derivation']=inherited_derivation
    projection['new_sources']=old['new_sources'];projection['dependency_sources']=old['dependency_sources']
    projection['dependency_seals']['sensor']=old['dependency_seals']['sensor']
    for key in ('sensor_source_manifest','sensor_reset_diagnostic_source_references','full_B2_package_verified'):projection.pop(key)
    if projection!=old:raise ValueError('V3 index diff exceeds B2 dependency metadata')
    path=HERE/'CAPTURE_SOURCE_INDEX.json';text=json.dumps(index,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:path.write_text(text,encoding='utf-8',newline='\n')
    else:
        with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)
    return dict(index=identity(path),source_version=3,original17=len(index['original17']),new_sources=len(index['new_sources']),
                dependencies=len(index['dependency_sources']),dependency_sealed_members={name:len(row['members']) for name,row in index['dependency_seals'].items()},
                B2_original_source_files=manifest['original_source_closure']['unique_full_source_files'],
                B2_original_pin_references=manifest['original_source_closure']['pin_references'],diagnostic_source_references=len(diagnostics['source_references']),
                candidate_logic_diff_count=0,native_or_resource_executed=False)


if __name__=='__main__':print(json.dumps(build_index(),indent=2))
