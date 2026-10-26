"""Source/text/small JSON only. Creates no payload, TASK, GO or model copy."""
from pathlib import Path
import ast
import hashlib
import json
import sys
import time
import traceback

D=Path(__file__).resolve().parent;T=D.parent.parent
H1=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
E3=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
sys.path.insert(0,str(D/'source'))
from normal86_source_guard_v1 import SOURCES, exact_worker_delta, validate_origin, allowed_overlay_paths


def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fresh(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(raw)


def main():
    lineage=[]
    for key,base in (('h1',H1),('recovery',E3)):
        old=base/'payloads'/key;B=D/'candidate_overlays'/key
        metadata={
            'source_cpu':(base/'reports'/('THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json' if key=='h1' else 'V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json'),'SOURCE_ORIGIN_CPU_ACTUAL.json'),
            'source_terminal':(base/'current_three_closed_text'/key/'NODE_TERMINAL_ACTUAL.json','SOURCE_ORIGIN_NODE_TERMINAL_ACTUAL.json'),
            'source_exit':(base/'current_three_closed_text'/key/'NODE_EXIT_ACTUAL.json','SOURCE_ORIGIN_NODE_EXIT_ACTUAL.json'),
            'source_final':(base/'current_three_closed_text'/key/'job0/production/FINAL.json','SOURCE_ORIGIN_FINAL_ACTUAL.json'),
            'latest_cpu':(E3/'reports/V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json','CURRENT85_CPU_ACTUAL.json'),
            'latest_collector':(E3/'reports/V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_RETURNED_ACTUAL.json','CURRENT85_COLLECTOR_ACTUAL.json')}
        if key=='recovery':
            metadata['source_clock']=(E3/'current_three_closed_text/recovery/job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json','SOURCE_ORIGIN_POLICY50_CLOCK_ACTUAL.json')
        binding=dict(schema='mod4.normal86.typed_origin_binding.v1',key=key,
            source_SHA=SOURCES[key]['SHA'],source_Adamstep=SOURCES[key]['Adam'],
            source_updates=SOURCES[key]['updates'],source_model_bytes=SOURCES[key]['bytes'],
            source_only=True,actual_installed86_SDK_CPU=False,metadata={})
        decoded={}
        for name,(source,filename) in metadata.items():
            assert source.suffix=='.json';raw=source.read_bytes();relative='normal86_metadata/'+filename
            fresh(B/relative,raw)
            binding['metadata'][name]=dict(relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
            decoded[name]=json.loads(raw)
            lineage.append(dict(key=key,relative=relative,source_path=str(source),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
        validate_origin(binding,decoded)
        fresh(B/'NORMAL86_SOURCE_BINDING_ACTUAL.json',(json.dumps(binding,indent=2)+'\n').encode())
        fresh(B/'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json',(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
        if key=='h1':
            fresh(B/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json',
                (T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026/reports/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json').read_bytes())
        for name in ('normal86_source_guard_v1.py','normal86_closed_source_CPU_v1.py'):
            fresh(B/name,(D/'source'/name).read_bytes())
        role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
        dispatcher=(old/role).read_bytes()+b"\n\n# Exact normal86 dispatch; every preceding original source byte is retained.\n_normal86_preceding_load = load\n\ndef load(spec, B):\n    if spec.get('normal86_continuation') is True:\n        from normal86_closed_source_CPU_v1 import load as normal_load\n        return normal_load(spec, B)\n    return _normal86_preceding_load(spec, B)\n"
        fresh(B/role,dispatcher)
        worker_name='h1_step270_production_worker_v1.py' if key=='h1' else 'recovery_worker.py'
        original_worker=(old/worker_name).read_text('utf8');worker=original_worker
        if key=='h1':
            marker="assert H(src)==go['source_SHA'];assert not (J/phase).exists()"
            assert worker.count(marker)==1
            worker=worker.replace(marker,"assert H(src)==go['source_SHA'];from normal86_source_guard_v1 import check_payload,validate_task_go;check_payload(B,'h1');validate_task_go(task,go,'h1',H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'));assert not (J/phase).exists()")
            cpu_original='target_H1_step270_closed_source_sdk_cpu_review_v1.py'
        else:
            assert worker.count("src=J/'source/RECOVERY_auto_source.pt'")==1
            worker=worker.replace("src=J/'source/RECOVERY_auto_source.pt'","src=J/'source'/task['source_filename']")
            assert worker.count('assert steps=={860800+20*updates}')==1
            worker=worker.replace('assert steps=={860800+20*updates}','assert steps=={862540+20*updates}')
            marker="assert H(src)==task['source_SHA']";assert worker.count(marker)==1
            worker=worker.replace(marker,marker+";from normal86_source_guard_v1 import check_payload,validate_task_go;check_payload(B,'recovery');validate_task_go(task,json.loads((J/'GO_PRODUCTION.json').read_bytes()),'recovery',H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')) if not native else None")
            cpu_original='target_two50_source_sdk_cpu_review.py'
        exact_worker_delta(original_worker,worker,key)
        fresh(B/worker_name,worker.encode('utf8'))
        cpu_name='target_normal86_'+key+'_source_sdk_cpu_review_v1.py'
        cpu=(old/cpu_original).read_bytes()+b"\n\n# Reuse original one-load source object only after every original installed check.\nfrom normal86_source_guard_v1 import complete_installed_CPU\nnormal86_complete_CPU = complete_installed_CPU(B, m, s, v)\nprint(json.dumps(normal86_complete_CPU))\n"
        fresh(B/cpu_name,cpu)
        for p in B.rglob('*.py'):ast.parse(p.read_text('utf8'))
        rows=[dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(B.rglob('*')) if p.is_file()]
        assert {r['relative'] for r in rows}==allowed_overlay_paths(key)
        c=dict(schema='mod4.normal86.exact_source_contract.v1',key=key,source_only=True,
            original_manifest_SHA=H(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),binding_SHA=H(B/'NORMAL86_SOURCE_BINDING_ACTUAL.json'),
            overlay_files=rows,controller_replacements=[],controller_additions=[],metadata_replacements=[],removed_files=[],
            original_worker_utf8_hex=original_worker.encode('utf8').hex(),
            original_worker_SHA=H(old/worker_name),original_guard_SHA=H(old/role),
            original_CPU_source_SHA=H(old/cpu_original),original_CPU_script=cpu_original,new_CPU_script=cpu_name,
            source_filename='H1_normal83B_final130.pt' if key=='h1' else 'RECOVERY_normal85M2_final87.pt',
            preserve_all_old_PT_and_83B_proofs_as_history=True,actual_installed86_SDK_CPU=False,
            root_must_finalize=dict(controller_replacements=sorted(('three_slot_common_v1.py','forwarded_original_owner_control_v1.py','three_real_gpu_resource_v1.py')),
                controller_additions=['mixed86_protocol_v1.py'],metadata_replacements=['job0/TASK.json'],
                spec_fields=['normal86_continuation=true','normal_source_contract_SHA','manifest_SHA'],
                TASK_no_circular_hashes=True,GO_manifest_SHA_required=True))
        fresh(B/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json',(json.dumps(c,indent=2)+'\n').encode())
        lineage.append(dict(key=key,worker_original=str(old/worker_name),worker_original_SHA=H(old/worker_name),
            worker_candidate_SHA=H(B/worker_name),guard_original=str(old/role),guard_original_SHA=H(old/role),
            guard_candidate_SHA=H(B/role),CPU_original=str(old/cpu_original),CPU_original_SHA=H(old/cpu_original),
            CPU_candidate_SHA=H(B/cpu_name),prefix_bytes_exact=True))
    report=dict(epoch=time.time(),passed=True,source_only=True,lineage=lineage,
        reader_errors=[dict(id='NORMAL86_READER_001',kind='guessed E3 worker filename missing',
            attempted='recovery50_worker_v1.py',result='Get-Content path not found; corrected using rg to recovery_worker.py')],
        no_actual_PT_NPZ_read_hash_copy=True,no_remote_GPU_Git_Task_GO=True,Git_status='pending root ordinary supplement')
    fresh(D/'reports/NORMAL86_SOURCE_OVERLAY_LINEAGE_AND_READER_ERRORS_ACTUAL.json',(json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True,keys=['h1','recovery'],source_only=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        fresh(D/'reports'/('NORMAL86_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),
            (json.dumps(dict(epoch=time.time(),passed=False,error=traceback.format_exc(),no_real_PT_NPZ=True),indent=2)+'\n').encode())
        raise
