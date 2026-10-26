"""UNEXECUTED: create only new local V85 pair payloads from reviewed unused84.

Existing N85/reports is allowed. No old weights are opened/hashed for planning;
already-qualified binary producer SHAs are preserved from the84 manifest.
"""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

HERE=Path(__file__).resolve().parent
T=HERE.parent.parent.parent
OLD=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026'
N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026'
NS='H1step270_dual72_fudan_supermimic_E3_2610v85m'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path,value):
    with Path(path).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)


def main():
    assert H(N/'reports/HUMAN_SINGLE_WRITER72_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json')=='fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf'
    assert not (N/'payloads').exists() and not (N/'controllers').exists()
    assert not list(N.glob('**/GO_PRODUCTION.json')) and not list(N.glob('**/OWNER_IDENTITY.json'))
    N.mkdir(exist_ok=True);(N/'reports').mkdir(exist_ok=True)
    old=read(OLD/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    assert old['passed'] and set(old['specs'])=={'e2','recovery'}
    assert old['sources']['e2']['source_expert']=='h1'
    proof=read(OLD/'payloads/e2/CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json')
    assert proof['passed'] and set(proof['models'])=={'h1','e2','recovery'}
    assert proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
    assert proof['remaining_actual_snapshot']==595256.8240613937
    assert proof['models']['h1']['Adam']==829700 and proof['models']['e2']['Adam']==857460 and proof['models']['recovery']['Adam']==860800
    q=dict(old,epoch=time.time(),payloads={},specs={},sources={},roots={},
           owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/'+NS+'/owner',
           scheduled_experts=['e2','recovery'],deferred_experts=['h1'],
           strict_three_cap_remaining=86412.86069250107,
           preparation_scope='SOURCE_PREPARED_PAIR_NOT_LIVE_ACCOUNT_ADMITTED',
           normal_H1_deferred=True,original_live_account_checked=False,
           authority_migration_approved=True,authority_generation='MOD4_SINGLE_WRITER72_20261026',
           current_budget_mode_selected_from_actual72_C=True,no_GO_or_new_fee_yet=True)
    shutil.copytree(HERE/'controllers',N/'controllers')
    for key in ('e2','recovery'):
        base=Path(old['payloads'][key]);out=N/'payloads'/key
        shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        # Narrow independently authorised72-control delta; model/runtime are unchanged.
        role='closed_production_continuation_CPU_v2.py' if key=='e2' else 'original_account_policy50_source_CPU.py'
        before_control={};after_control={}
        for control in ('three_slot_common_v1.py','forwarded_original_owner_control_v1.py'):
            original=out/control
            before_control[control]=H(original)
            reference=out/'reference_sources'/('V85M_ORIGINAL_'+control+'.txt')
            assert not reference.exists();shutil.copy2(original,reference)
            candidate=HERE/'controllers'/control
            if key=='recovery' and control=='three_slot_common_v1.py':
                text=original.read_text('utf8')
                text=text.replace("C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')","C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')",1)
                text=text.replace("LOCKS=(C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'))","LOCKS=(C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock')",1)
                original.write_text(text,'utf8')
            else:shutil.copy2(candidate,original)
            after_control[control]=H(original)
        shutil.copy2(HERE/'guards'/(key+'_'+role),out/role)
        if key=='recovery':
            authpath=out/'MIXED84_NORMAL_PRODUCTION_SOURCE_AUTH_ACTUAL.json';auth=read(authpath)
            auth['guard_SHA']=H(out/role);auth['migration72_control_only_guard_scope']=True
            authpath.write_text(json.dumps(auth,indent=2),'utf8')
        put(out/'MIGRATION72_CONTROL_SCOPE_V85M_ACTUAL.json',dict(authorised=True,
            authority_generation='MOD4_SINGLE_WRITER72_20261026',
            authorization_file_SHA256='fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf',
            candidate_delta='only_common_C_LOCKS_forwarder_send_close_and_source_guard',
            before=before_control,after=after_control,
            no_physics_reward_optimizer_sampling_trace_retention_change=True))
        before=read(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
        rows_by_rel={row['relative']:row for row in before['files']}
        hist=out/'prebind85M_exact_history';hist.mkdir()
        for name in ('job0/TASK.json','THREE_SLOT_COMPLETE_MANIFEST_V1.json'):
            shutil.copy2(out/name,hist/(Path(name).name+'.original_bytes.txt'))
        task=read(out/'job0/TASK.json');task['id']=N.name+'_'+key
        (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
        rows=[]
        for path in sorted(out.rglob('*')):
            if not path.is_file() or path.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in path.parts:continue
            rel=path.relative_to(out).as_posix()
            if path.suffix=='.py':ast.parse(path.read_text('utf8'))
            # Only known producer metadata for qualified binary copies. Actual
            # target SDK/manifest checking remains mandatory after upload.
            digest=rows_by_rel[rel]['SHA'] if path.suffix in ('.pt','.npz','.usd','.stl') else H(path)
            rows.append(dict(relative=rel,bytes=path.stat().st_size,SHA=digest))
        manifest=dict(before,files=rows)
        (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),'utf8')
        spec=dict(old['specs'][key],manifest_SHA=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
        assert spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
        if key=='e2':
            assert spec['source_SHA']==proof['models']['h1']['final']['SHA'] and spec['source_Adamstep']==829700
            assert spec['previous_runtime_root'].endswith('/H1step270_three_experts_2610v83b/e2')
            assert spec['finite_method_test'] and spec['h1_step270_method_test'] and spec['source_bootstrap_kind']=='qualified83B_H1_frozen_PPO_core_only'
        else:
            assert spec['source_SHA']==proof['models']['recovery']['final']['SHA'] and spec['source_Adamstep']==860800
            assert spec['policy_hz']==50 and not spec.get('finite_method_test')
        q['payloads'][key]=str(out);q['specs'][key]=spec;q['sources'][key]=old['sources'][key]
        q['roots'][key]='/home/lc01/Zonglin Li/zonglin2/tasks/'+NS+'/'+key
    for name in ('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',):
        source=OLD/'reports'/name;target=N/'reports'/name
        assert not target.exists();shutil.copy2(source,target)
    put(N/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',q)
    for name in ('install_dual72_V85M_source_SDK_native_CPU_only_UNUSED.py',
                 'dual72_V85M_resource_install_source_v1.py'):
        assert not (N/name).exists();shutil.copy2(HERE/name,N/name)
    assert not (N/'mixed84_protocol_v1.py').exists()
    shutil.copy2(HERE/'controllers/mixed84_protocol_v1.py',N/'mixed84_protocol_v1.py')
    put(N/'reports/DUAL72_V85_PAIR_SOURCE_PREPARED_NOT_LIVE_ACCOUNT_ADMITTED_ACTUAL.json',dict(
        epoch=time.time(),source_preparation_passed=True,slots=['e2','recovery'],deferred=['h1'],
        qualified_source_proof='healthy closed83B three normal sources',
        native_H1_frozen_bootstrap=proof['models']['h1']['final']['SHA'],
        physical_e2_resource_normal_source=proof['models']['e2']['final']['SHA'],
        E3_source=proof['models']['recovery']['final']['SHA'],
        original_live_account_checked=False,canonical_copied=False,owner_or_GO=False,
        budget_authority_migration=False,binary_copy_hashes_reused_from_producer_metadata=True))
    print(json.dumps(dict(local_source_pair_prepared=True,stage=str(N),no_owner_or_GO=True,original_live_account_checked=False)))


if __name__=='__main__':main()
