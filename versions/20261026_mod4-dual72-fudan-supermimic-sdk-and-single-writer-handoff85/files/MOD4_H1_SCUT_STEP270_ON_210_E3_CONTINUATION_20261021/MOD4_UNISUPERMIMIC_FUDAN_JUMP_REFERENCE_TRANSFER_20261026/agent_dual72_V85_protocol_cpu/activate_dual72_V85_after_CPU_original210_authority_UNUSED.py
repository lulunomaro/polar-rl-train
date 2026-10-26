"""UNEXECUTED original-authority activation only after successful72-only CPU.

This is intentionally blocked while original210 identity/canonical is absent.
It never re-runs the consumed installer, copies a canonical, or approves a72
authority migration. Such a migration needs a distinct reviewed protocol.
"""
from pathlib import Path
import importlib.util
import json
import secrets
import sys
import time
import traceback

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))
OWNER_NAME='three_slot_finite_owner_V85_pair_source_only.py'


def put(name,value):
    with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)


def main():
    read=lambda path:json.loads(Path(path).read_bytes())
    q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    cpu=read(R/'V85_ONLY72_INSTALLED_SOURCE_SDK_NATIVE_CPU_FINITE_RETURNED_ACTUAL.json')
    receipt=read(R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
    assert q['passed'] and set(q['specs'])=={'e2','recovery'} and q['deferred_experts']==['h1']
    assert cpu['actual_finite_returned'] and cpu['target_source_CPU_passed']
    assert cpu['original_live_account_checked'] is False and cpu['owner_launched'] is False and cpu['GO'] is False
    assert cpu['roots']==q['roots']
    assert all(cpu['specs'][key]['manifest_SHA']==q['specs'][key]['manifest_SHA'] for key in q['specs'])
    assert receipt['passed'] and receipt['remaining_after']==595256.8240613937
    from mixed84_protocol_v1 import validate_reference_preparation
    validate_reference_preparation(q['reference_preparation'])
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'))
    import strict_user_forwarded_original210_transport_v1 as route
    d.OWNER=d.OWNER.replace('1548000','2268000').replace("len(c['budget_extensions'])==8","len(c['budget_extensions'])==9").replace('10.24.4.210','127.0.0.1')
    needle="c['remaining_training_seconds']>7800+9912.860692501068+64800"
    assert d.OWNER.count(needle)==1;d.OWNER=d.OWNER.replace(needle,"c['remaining_training_seconds']>86412.86069250107",1)
    put('V85_ORIGINAL210_AUTHORITY_ACTIVATION_STARTED_ACTUAL.json',dict(epoch=time.time(),no_installer_replay=True,
        source_CPU_not_live_account_evidence=True,original_authority_required=True,no_migration_approval=True))
    client=None;cfg=None;password=None;secret=None
    try:
        # Original pin rejection stops here before target nodes/worker/GO.
        client=route.connect()
        boundary=d.code(client,route.PY,d.OWNER,dict(root=q['owner_root'],receipt=receipt),timeout=90)
        assert boundary['remaining_actual_snapshot']>86412.86069250107
        put('V85_FRESH_ORIGINAL_CANONICAL_TWO_LOCKS_UNUSED_OWNER_ROOT_ACTUAL.json',boundary)
        sf=client.open_sftp()
        try:
            for name in ('three_slot_common_v1.py',OWNER_NAME,'mixed84_protocol_v1.py'):
                sf.put(str(N/'controllers'/name),q['owner_root']+'/'+name)
        finally:sf.close()
        cfg=dict(role='owner',experts=q['specs'],scheduling_authority='human_requested_available_experts',
                 deferred_experts=['h1'],run_id='DUAL72_NATIVE_H1_E3_ORIGINAL_V85_'+str(time.time_ns()),token=secrets.token_hex(32))
        owner=d.launch(client,route.PY,q['owner_root'],OWNER_NAME,cfg)
        code="from pathlib import Path;import json,psutil,socket,time;B=Path(v['root']);until=time.monotonic()+20\nwhile not (B/'OWNER_IDENTITY.json').exists() and time.monotonic()<until:time.sleep(.1)\np=psutil.Process(v['pid']);assert str(B/v['owner_name']) in p.cmdline()\nwhile True:\n try:\n  with socket.create_connection(('127.0.0.1',29754),timeout=5):pass\n  break\n except ConnectionRefusedError:\n  assert time.monotonic()<until\n  time.sleep(.1)\nprint(json.dumps(dict(owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),actual_listener_ready=True)))"
        ready=d.code(client,route.PY,code,dict(root=q['owner_root'],pid=owner['detached_pid'],owner_name=OWNER_NAME),timeout=30)
        put('V85_ORIGINAL_OWNER_ACTUAL_READY.json',ready)
        client.close();client=None
        module_spec=importlib.util.spec_from_file_location('existing_hidden72_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
        memory=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(memory)
        secret=memory.recover();client=d.connect72(secret);secret=None
        # Fresh unused node roots are checked; source/CPU installation is not repeated.
        unused=d.code(client,d.PY72,"from pathlib import Path;import json;roots=v['roots'];assert all(not (Path(root)/name).exists() for root in roots.values() for name in ('NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','job0/GO_PRODUCTION.json'));print(json.dumps(dict(no_prior_node_or_GO=True)))",dict(roots=q['roots']),timeout=30)
        put('V85_ACTUAL_TWO_NODES_UNUSED_BEFORE_LAUNCH.json',unused)
        sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
        from reuse_authorized_session_transport import recover
        password,_=recover('RM_SSH_PASSWORD');assert password
        nodes={}
        for key in ('recovery','e2'):
            child=dict(q['specs'][key],role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=password)
            try:nodes[key]=d.launch(client,d.PY72,q['roots'][key],'three_slot_finite_node_v1.py',child)
            finally:child.clear()
        put('DUAL72_V85_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json',dict(
            epoch=time.time(),owner=owner,owner_identity=ready['owner'],nodes=nodes,roots=q['roots'],owner_root=q['owner_root'],
            specs=q['specs'],sources=q['sources'],run_id=cfg['run_id'],deferred_experts=['h1'],
            original210_authority_only=True,not_actual_learning_until_signed_GO_and_positive_native_Pi_E3_PPO=True))
        print(json.dumps(dict(owner=owner,nodes=nodes,no210_GPU_task=True)))
    finally:
        password=None;secret=None
        if cfg:cfg.clear()
        if client:client.close()


if __name__=='__main__':
    try:main()
    except BaseException:
        put('V85_ORIGINAL_AUTHORITY_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(
            epoch=time.time(),error=traceback.format_exc(),no_auto_retry_refund_or_second_writer=True,
            no_pin_override_or_authority_migration=True));raise
