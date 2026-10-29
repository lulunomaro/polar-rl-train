"""UNUSED <=300s serial72->close->210 metadata/source admission and detach.

Root must first grant global serial lease and obtain fresh exact LOCAL CIM.
No old once is run; old modules are imported for existing memory transports only.
No model CPU decode, budget/owner writer, policy forward, or GPU scene in caller.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import sys
import threading
import time
import traceback

B=Path(__file__).resolve().parent
R=B/'reports'
L=B.parent
T=L.parent
W=T.parent


def read(path):return json.loads(Path(path).read_bytes())
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    R.mkdir(exist_ok=True)
    with (R/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    loaded=importlib.util.module_from_spec(spec);sys.modules[name]=loaded
    spec.loader.exec_module(loaded)
    return loaded


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--known72-binding-json',type=Path,help='Current exact {owner,run_id,go}, required if actual72 C active; no historical default')
    args=parser.parse_args()
    # The marker is not reset after any failure. A second invocation refuses.
    put('PANEL210_INSTALL_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),local_pid=os.getpid(),unused_namespace=True,no_secondwriter_or_model_CPUdecode=True))
    deadline=time.monotonic()+300
    known=read(args.known72_binding_json) if args.known72_binding_json else None
    if known is not None:assert set(known)=={'owner','run_id','go'}
    config=read(B/'LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json')
    manifest_raw=(B/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json').read_bytes()
    assert H(manifest_raw)==config['input_manifest_SHA']
    manifest=json.loads(manifest_raw)
    assert manifest['new_root']==config['new'] and manifest['old_root']==config['old']
    assert config['no_actual_current_owner_or_CNone_known_in_this_source']
    assert manifest['source_model_CPU_decode_requested'] is False
    codes={}
    for field in ('authority_CODE','pre_CODE','run_CODE'):
        row=config[field];p=B/row['relative'];assert p.parent==B
        raw=p.read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA'];ast.parse(raw)
        codes[field]=raw.decode('utf-8')
    copy_raw=(B/'COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py').read_bytes()
    assert H(copy_raw)==config['copy_CODE_SHA'];ast.parse(copy_raw)
    overlay=[];unchanged=[]
    for row in manifest['files']:
        p=Path(row['local_path'])
        if p.parent in (B,L/'W35_PROFILE_ENV_DOMAIN_PANEL_UNUSED_SOURCE_20261029_V1'):
            raw=p.read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA'];overlay.append((row,raw))
        else:unchanged.append(row)  # Old model/NPZ/USD contents are not opened locally.
    assert len(overlay)==5 and len(unchanged)==464
    def cap(maximum):
        remaining=deadline-time.monotonic()
        assert remaining>5,'finite metadata startup deadline before next remote phase'
        return min(maximum,remaining)
    wrapper=module('panel210_same_authorized_compressed_memory_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    transport,previous=wrapper.install()
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'))
    import strict_user_forwarded_original210_transport_v1 as route
    secret_module=module('panel210_existing_memory_72_authority_readonly',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    secret=None;client=None;stop=threading.Event()
    def progress():
        while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_W35_PROFILE_PANEL210_SOURCE_METADATA',epoch=time.time(),model_CPU_decode_count=0)),flush=True)
    thread=threading.Thread(target=progress,daemon=True);thread.start()
    try:
        secret=secret_module.recover()
        client=d.connect72(secret);secret=None
        authority=d.code(client,d.PY72,codes['authority_CODE'],dict(known_binding=known),timeout=cap(30))
        assert authority['passed_readonly_original72_finite_authority']
        authority['passed']=True
        authority['metadata_extension']=config['source_extension']
        put('CURRENT72_PROFILE_PANEL_AUTHORITY_READONLY_ACTUAL.json',authority)
        client.close();client=None  # No two control SSH connections overlap.
        client=route.connect()
        pre=d.code(client,route.PY,codes['pre_CODE'],dict(job=config['new'],GPU=config['GPU']),timeout=cap(30))
        put('PANEL210_FRESH_UNUSED_MOUNT_LIGHT_RESOURCE_ACTUAL.json',pre)
        copyproof=d.code(client,route.PY,copy_raw.decode(),dict(old=config['old'],new=config['new'],rows=unchanged,expected=config['expected']),timeout=cap(90))
        assert copyproof['passed'] and copyproof['old_source_wholeCPU_and_closure_bound']
        put('PANEL210_EXISTING_VERIFIED_INPUT_COPY_METADATA_ACTUAL.json',copyproof)
        sf=client.open_sftp();sf.get_channel().settimeout(cap(30))
        try:
            for row,raw in overlay:
                assert ('/' not in row['relative'] or row['relative']=='lib/zonglin2_app_launcher.py') and row['relative'] not in ('FROZEN_CASE_TASK_TEMPLATE.json','FROZEN_CASE_TASK.json')
                if row['relative']=='lib/zonglin2_app_launcher.py':
                    try:sf.stat(config['new']+'/lib')
                    except FileNotFoundError:sf.mkdir(config['new']+'/lib',mode=0o700)
                with sf.open(config['new']+'/'+row['relative'],'wx') as f:f.write(raw)
            for name,raw in [('PANEL210_SEALED_INPUT_MANIFEST.json',manifest_raw),('PANEL210_SOURCE_EXTENSION_METADATA.json',json.dumps(config['source_extension'],sort_keys=True).encode())]:
                with sf.open(config['new']+'/'+name,'wx') as f:f.write(raw)
        finally:sf.close()
        value=d.code(client,route.PY,codes['run_CODE'],dict(job=config['new'],old=config['old'],GPU=config['GPU'],python=route.PY,
            files=[{k:row[k] for k in ('relative','bytes','SHA')} for row in manifest['files']],
            RSL_sources=manifest['RSL_sources'],SDK_math_SHA=manifest['SDK_math_SHA'],authority=authority,
            copyproof=copyproof,expected=config['expected'],source_extension=config['source_extension'],
            static_task_input=config['static_task_input'],worker=config['worker'],supervisor=config['supervisor'],input_manifest_SHA=config['input_manifest_SHA']),timeout=cap(120))
        put('PANEL210_SOURCE_SDK_METADATA_AND_FINITE_DETACHED_RETURNED_ACTUAL.json',value)
        print(json.dumps(value),flush=True)
    finally:
        secret=None;stop.set();thread.join(1)
        if client:client.close()
        transport.SESSION=previous


if __name__=='__main__':
    try:main()
    except BaseException:
        put('PANEL210_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_retry_or_Cwrite_or_source_promotion=True))
        raise
