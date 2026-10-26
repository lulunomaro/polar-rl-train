"""New72 sole-owner activation; no ledger initialization or installer replay."""
from pathlib import Path
import importlib.util
import json
import secrets
import sys
import time
import traceback

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))
OWNER='three_slot_finite_owner_V85M_pair_authority72.py'


def put(name,value):
    with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)


def main():
    read=lambda path:json.loads(Path(path).read_bytes())
    q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    cpu=read(R/'V85M_ONLY72_INSTALLED_SOURCE_SDK_NATIVE_CPU_FINITE_RETURNED_ACTUAL.json')
    assert set(q['specs'])=={'e2','recovery'} and q['deferred_experts']==['h1']
    assert cpu['actual_finite_returned'] and cpu['target_source_CPU_passed'] and not cpu['owner_launched'] and cpu['GO'] is False
    assert cpu['roots']==q['roots'] and all(cpu['specs'][k]['manifest_SHA']==q['specs'][k]['manifest_SHA'] for k in q['specs'])
    assert all('/H1step270_dual72_fudan_supermimic_E3_2610v85m2/' in root for root in [q['owner_root'],*q['roots'].values()])
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    module_spec=importlib.util.spec_from_file_location('existing_hidden72_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(memory)
    secret=memory.recover();client=None;cfg=None
    put('V85M2_SINGLE72_OWNER_ACTIVATION_STARTED_ACTUAL.json',dict(epoch=time.time(),only72=True,no_installer_replay=True,no_canonical_initialization_or_copy=True))
    try:
        client=d.connect72(secret);secret=None
        preflight="from pathlib import Path;import fcntl,json,psutil,socket;B=Path(v['owner']);owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();assert all(not (Path(root)/name).exists() for root in v['roots'].values() for name in ('NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','job0/GO_PRODUCTION.json'));state=owned/'state/mod4_single_canonical_authority_20261026'\nfor name in ('native_floor_supervisor.lock','autonomy_controller.lock'):\n with (state/name).open('rb+') as stream:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)\nwith socket.socket() as s:s.bind(('127.0.0.1',29754))\nB.mkdir(parents=True);print(json.dumps(dict(new_unused_owner_root=str(B),new_two_owner_locks_free=True,no_owner_or_GO=True)))"
        pre=d.code(client,d.PY72,preflight,dict(owner=q['owner_root'],roots=q['roots']),timeout=45)
        put('V85M2_SINGLE72_UNUSED_OWNER_AND_LOCKS_ACTUAL.json',pre)
        sf=client.open_sftp()
        try:
            for name in ('three_slot_common_v1.py',OWNER,'single_writer72_authority_V85M_source.py','mixed84_protocol_v1.py'):
                sf.put(str(N/'controllers'/name),q['owner_root']+'/'+name)
        finally:sf.close()
        code="from pathlib import Path;import hashlib,json,sys;sys.path.insert(0,v['root']);from single_writer72_authority_V85M_source import *;h=read_authority();c=json.loads(CANONICAL.read_bytes());assert c['active_segment'] is None and authority_tracking_schema_admitted(c) and authority_original_extension_count(c)==9 and authority_budget_GO_allowed(c);print(json.dumps(dict(authority_generation=GENERATION,budget_mode=c.get('budget_mode',c.get('mode')),remaining_tracking=c['remaining_training_seconds'],canonical_SHA=hashlib.sha256(CANONICAL.read_bytes()).hexdigest(),active_None=True,authority_activated=True,no_ledger_write=True)))"
        authority=d.code(client,d.PY72,code,dict(root=q['owner_root']),timeout=45)
        put('V85M2_ACTUAL_SINGLE_AUTHORITY_AND_CURRENT_BUDGET_GATE_ADMITTED.json',authority)
        cfg=dict(role='owner',experts=q['specs'],scheduling_authority='human_requested_available_experts',deferred_experts=['h1'],
                 run_id='DUAL72_MIGRATED_FUDAN_H1_E3_V85M2_'+str(time.time_ns()),token=secrets.token_hex(32))
        owner=d.launch(client,d.PY72,q['owner_root'],OWNER,cfg)
        code="from pathlib import Path;import json,psutil,socket,time;B=Path(v['root']);until=time.monotonic()+20\nwhile not (B/'OWNER_IDENTITY.json').exists() and time.monotonic()<until:time.sleep(.1)\np=psutil.Process(v['pid']);assert str(B/v['name']) in p.cmdline()\nwhile True:\n try:\n  with socket.create_connection(('127.0.0.1',29754),timeout=5):pass\n  break\n except ConnectionRefusedError:\n  assert time.monotonic()<until\n  time.sleep(.1)\nprint(json.dumps(dict(owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),actual_listener_ready=True)))"
        ready=d.code(client,d.PY72,code,dict(root=q['owner_root'],pid=owner['detached_pid'],name=OWNER),timeout=30)
        put('V85M2_SINGLE72_OWNER_ACTUAL_READY.json',ready)
        nodes={}
        for key in ('recovery','e2'):
            child=dict(q['specs'][key],role='node',run_id=cfg['run_id'],token=cfg['token'])
            try:nodes[key]=d.launch(client,d.PY72,q['roots'][key],'three_slot_finite_node_v1.py',child)
            finally:child.clear()
        put('V85M2_SINGLE72_OWNER_NODES_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,owner_identity=ready['owner'],nodes=nodes,
            roots=q['roots'],owner_root=q['owner_root'],specs=q['specs'],sources=q['sources'],run_id=cfg['run_id'],
            authority_generation=authority['authority_generation'],budget_mode_at_launch=authority['budget_mode'],
            deferred_experts=['h1'],sole_writer72=True,not_actual_learning_until_signed_GO_and_positive_policy_evidence=True))
        print(json.dumps(dict(owner=owner,nodes=nodes,sole_writer72=True)))
    finally:
        secret=None
        if cfg:cfg.clear()
        if client:client.close()


if __name__=='__main__':
    try:main()
    except BaseException:
        put('V85M2_SINGLE72_OWNER_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry_second_writer_refund_or_account_reinitialization=True));raise
