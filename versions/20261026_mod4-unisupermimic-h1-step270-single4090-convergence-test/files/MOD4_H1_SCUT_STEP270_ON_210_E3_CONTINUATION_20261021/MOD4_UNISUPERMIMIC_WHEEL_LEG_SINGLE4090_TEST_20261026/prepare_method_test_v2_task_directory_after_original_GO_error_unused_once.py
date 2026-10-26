"""Preserve V1 actual GO/fee/error. New unused roots include an explicit task file."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

J=Path(__file__).resolve().parent;R=J/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=read(R/'ONE_CARD_METHOD_TEST_FULL_TEXT_ORIGINAL_COST_RETURNED_ACTUAL.json')
assert receipt['actual_finite_returned'] and receipt['original_canonicalNone']
terminal=receipt['target72']['terminal'];assert terminal['original_error'] and terminal['returncode']==1 and not terminal.get('worker')
assert receipt['original_fee']['charged_seconds']==1.2145142555236816 and receipt['original_fee']['duration_bound_passed']
assert not (J/'actual_returned_text/e2/job0/production_STARTED_ACTUAL.json').exists()
q=read(R/'REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_ACTUAL.json')
B=J/'payload_v2';assert not B.exists();shutil.copytree(J/'payload',B)
task=dict(kind='UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_FINITE_OFFLINE_CORE_TEST',
    upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',
    source_SHA=q['spec']['source_SHA'], GPU_UUID=q['spec']['GPU_UUID'],
    world_model_updates=200,policy_core_updates=5,imagination_horizon=8,
    world_model_hidden=[2048,2048,2048],FP32=True,
    state_joint_count=30,action_dimension=6,
    not_a_production_E2_source_or_online_robot_policy=True,
    original3900_lifecycle3600save300exit=True,own_worker_self_bound240s=True)
with (B/'job0/TASK.json').open('x',encoding='utf8') as f:json.dump(task,f,indent=2)
manifest=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
assert not any(r['relative']=='job0/TASK.json' for r in manifest['files'])
manifest['files'].append(dict(relative='job0/TASK.json',bytes=(B/'job0/TASK.json').stat().st_size,SHA=H(B/'job0/TASK.json')))
(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),'utf8')
q['payload']=str(B);q['root']=q['root'].replace('_20261026/e2','_20261026_V2/e2');q['owner_root']=q['owner_root'].replace('_20261026/owner','_20261026_V2/owner')
q['spec']['manifest_SHA']=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
q.update(previous_method_owner_root=receipt['source210']['owner_exit'].get('root',read(R/'ONE_CARD_METHOD_TEST_ORIGINAL_OWNER_AND_NODE_DETACHED_ACTUAL.json')['owner_root']),previous_method_original_fee=receipt['original_fee'],latest_original_closed_remaining_snapshot=receipt['original_closed_remaining_snapshot'],V1_GPU_worker_not_started=True)
with (R/'REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
s=(J/'run_pinned_single4090_method_test_original_owner_finite_unused_once.py').read_text('utf8')
assert s.count("with (R/name).open('x'")==1
s=s.replace("with (R/name).open('x'","with (R/('V2_'+name)).open('x'",1)
s=s.replace("J/'actual_returned_text'","J/'actual_returned_text_v2'")
s=s.replace('REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_ACTUAL.json','REVIEWABLE_FINITE_SINGLE_GPU_METHOD_TEST_PAYLOAD_AND_ORIGINAL_WRITER_PLAN_V2_ACTUAL.json')
s=s.replace('UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/e2','UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026_V2/e2').replace('UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/owner','UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026_V2/owner')
s=s.replace("upload(c,J/'payload',q['root'])","upload(c,J/'payload_v2',q['root'])")
needle="assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))"
assert s.count(needle)==1
extra="\nfailed=owned/'research/UNISUPERMIMIC_MOD4_WHEELLEG_TEST_20261026/e2';fe=json.loads((failed/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((failed/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and fr['original_error'] and fr['returncode']==1 and not (failed/'job0/production_STARTED_ACTUAL.json').exists()\nassert not any(p.pid!=os.getpid() and any(a.startswith(str(failed)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))"
s=s.replace(needle,needle+extra,1);ast.parse(s)
with (J/'run_pinned_single4090_method_test_v2_original_owner_finite_unused_once.py').open('x',encoding='utf8') as f:f.write(s)
with (R/'V1_ACTUAL_GO_NO_GPU_WORKER_AND_V2_TASK_DIRECTORY_FIX_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),V1_original_GO_fee=receipt['original_fee'],V1_original_error=read(J/'actual_returned_text/e2/NODE_ORIGINAL_ERROR.json'),V1_owner_node_children_actual_out=True,V1_canonicalNone_and_original_locks_free=True,V1_no_GPU_worker_or_numerical_result=True,V2_new_root=q['root'],V2_owner_root=q['owner_root'],V2_only_payload_change='Explicit job0/TASK.json ensures SFTP creates task directory before original GO receipt is written',original_worker_common_node_source_unchanged=True,original_fee_not_refunded_or_overwritten=True),f,indent=2)
print(json.dumps(dict(new_unused_V2_prepared=True,V1_original_error_and_fee_retained=True)))
