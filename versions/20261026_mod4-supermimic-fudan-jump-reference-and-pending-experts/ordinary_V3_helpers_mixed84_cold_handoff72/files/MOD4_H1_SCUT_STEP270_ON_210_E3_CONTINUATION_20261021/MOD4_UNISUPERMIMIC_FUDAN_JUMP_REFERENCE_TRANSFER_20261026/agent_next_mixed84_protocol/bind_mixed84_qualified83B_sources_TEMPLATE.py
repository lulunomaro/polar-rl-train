"""UNEXECUTED SOURCE TEMPLATE. Root must integrate actual inputs before invoking.

This template's execution would build a NEW payload. This preparation task does
not invoke it, copy any model, create TASK/GO, or assert actual target admission.
"""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import sys
import time

from mixed84_protocol_v1 import (LOCAL_STAGE, NAMESPACE, SOURCES, METADATA_BYTES,
    METADATA_SHA, validate_closed83B, validate_reference_preparation, require_native_manifest_pins)

HERE = Path(__file__).resolve().parent
T = HERE.parent.parent
NORMAL = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
NATIVE = T / 'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026'
read = lambda path: json.loads(Path(path).read_bytes())
H = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    with Path(path).open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2)


def bind_new_payloads(integration):
    assert integration['status'] == 'ROOT_REVIEWED_ACTUAL_INPUTS_READY_FOR_NEW_BINDING'
    assert integration['source_only_authorization']['approved']
    assert integration['source_only_authorization']['no_new_training_or_GO_authorization']
    bundle = integration['reference_bundle']
    validate_reference_preparation(bundle)
    proof_path = NORMAL / 'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
    proof = read(proof_path)
    oldq = read(NORMAL / 'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    identity = read(NORMAL / 'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_identity']
    validate_closed83B(proof, identity)
    nativeq = read(NATIVE / 'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
    N = T / LOCAL_STAGE
    assert not N.exists(), 'New namespace only; preserve every prior stage'
    N.mkdir()
    (N / 'reports').mkdir()
    shutil.copytree(HERE / 'owner_controller_templates', N / 'controllers')
    rec = read(NORMAL / 'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json')
    rec.update(remaining_after=proof['remaining_actual_snapshot'],
               source_current_cohort_original_cost_summary=proof,
               latest_actual83B_original_all3_cost_closure=proof,
               original83B_cost_not_recharged=True)
    put(N / 'reports/ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json', rec)
    q = dict(epoch=time.time(), passed=True, preparation_scope='SOURCE_PREPARED_NOT_TARGET_ADMITTED',
             payloads={}, specs={}, sources={}, roots={},
             owner_root='/mnt/mod4_linux_durable_20261013/' + NAMESPACE + '/owner',
             previous_owner_root=oldq['owner_root'], previous_owner_identity=identity,
             strict_three_cap_remaining=86412.86069250107,
             reference_preparation=bundle,
             normal_E2_83B_preserved_paused=SOURCES['e2'], no_GO_or_new_fee_yet=True)
    for key in ('h1', 'recovery', 'e2'):
        native = key == 'e2'
        origin = nativeq if native else oldq
        base = Path(origin['payloads'][key])
        out = N / 'payloads' / key
        shutil.copytree(base, out, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        prior = read(out / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
        before = {row['relative']: row for row in prior['files']}
        hist = out / 'prebind84_exact_history'
        hist.mkdir()
        role = 'closed_production_continuation_CPU_v2.py' if key in ('h1', 'e2') else 'original_account_policy50_source_CPU.py'
        for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json', 'job0/TASK.json', role):
            shutil.copy2(out / name, hist / (Path(name).name + '.original_bytes.txt'))
        source_key = 'h1' if native else key
        model = proof['models'][source_key]
        final = model['final']
        assert final['SHA'] == SOURCES[source_key]['SHA'] and final['twohost_complete_SHA']
        spec = dict(origin['specs'][key])
        spec.update(source_SHA=final['SHA'], source_Adamstep=model['Adam'],
                    previous_runtime_root=oldq['roots'][key], previous_exit_kind='node',
                    reward_migration=False, cross_host_qualified_source=False,
                    closed_production_continuation=True, reuse_completed_native=False,
                    max_parent_seconds=3900, exit_headroom_seconds=300)
        if native:
            spec.update(finite_method_test=True, h1_step270_method_test=True,
                        policy_hz=100, source_policy_hz=100,
                        source_origin_runtime_root=oldq['roots']['h1'],
                        displaced_runtime_root=oldq['roots']['e2'],
                        source_bootstrap_kind='qualified83B_H1_frozen_PPO_core_only',
                        production_script='h1_unisupermimic_step270_worker_v1.py',
                        reference_artifact_SHA=bundle['reference']['reference_artifact_SHA'],
                        adapter_CPU_report_SHA=bundle['adapter_CPU']['report_SHA'],
                        objective_contract_SHA=bundle['adapter_CPU']['objective_contract_SHA'],
                        runtime_objective_contract_SHA=None,
                        objective_contract_runtime_basename='NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json',
                        candidate_pins=bundle['candidate_pins'])
            # Root supplies these exact reviewed candidate bytes only after the
            # actual Fudan reference/adapter CPU proofs exist. No old native .pt.
            overlay = integration['native_candidate_files']
            required = {'source/h1_supermimic_bridge_v1.py', 'source/native_finalization_v1.py',
                        'source/supermimic_reference_adapter_v1.py',
                        'h1_unisupermimic_step270_worker_v1.py',
                        'test_native_h1_fudan_reference_CPU_v84.py'}
            assert required <= set(overlay)
            allowed = required | {'source/own_usd_closed_chain_ik_v1.py',
                                  'source/h1_fudan_reference_integration_v84.py'}
            assert set(overlay) <= allowed, 'No runtime/assets/lib/vendor/action/trace overlay'
            for rel, row in overlay.items():
                from mixed84_protocol_v1 import relative
                relative(rel)
                assert Path(rel).suffix == '.py' and H(row['local_path']) == row['SHA']
                target = out / rel
                assert target.resolve().is_relative_to(out.resolve())
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(row['local_path'], target)
            for source, dest in (
                ('native_source_guard_TEMPLATE.py', role),
                ('mixed84_protocol_v1.py', 'mixed84_protocol_v1.py'),
                ('native_controller_templates/three_slot_common_v1.py', 'three_slot_common_v1.py'),
                ('native_controller_templates/three_real_gpu_resource_v1.py', 'three_real_gpu_resource_v1.py')):
                shutil.copy2(HERE / source, out / dest)
            for rel, input_key in ((bundle['reference']['artifact_relative'], 'reference_artifact_path'),
                                   ('FUDAN_REFERENCE_PROVENANCE_ACTUAL.json', 'reference_provenance_path'),
                                   ('FUDAN_ADAPTER_CPU_ACTUAL.json', 'adapter_CPU_report_path'),
                                   ('FUDAN_PARTIAL_OBJECTIVE_CONTRACT_ACTUAL.json', 'objective_contract_path'),
                                   ('NATIVE_FINALIZATION_CPU_PROOF_ACTUAL.json', 'finalization_CPU_proof_path')):
                target = out / rel
                assert target.resolve().is_relative_to(out.resolve())
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(integration[input_key], target)
            assert H(out/'FUDAN_PARTIAL_OBJECTIVE_CONTRACT_ACTUAL.json') == bundle['adapter_CPU']['objective_contract_SHA']
            put(out / 'MIXED84_REFERENCE_BINDING_ACTUAL.json', bundle)
            put(out / 'MIXED84_PREVIOUS_OWNER_IDENTITY_ACTUAL.json', identity)
            for name in ('NODE_TERMINAL_ACTUAL.json', 'NODE_EXIT_ACTUAL.json'):
                shutil.copy2(NORMAL / 'current_three_closed_text/h1' / name,
                             out / ('SOURCE_ORIGIN83B_H1_' + name))
        else:
            assert not spec.get('finite_method_test') and not spec.get('h1_step270_method_test')
            shutil.copy2(HERE / ('normal_' + key + '_source_guard_TEMPLATE.py'), out / role)
            if key == 'recovery':
                path = out / 'recovery_worker.py'
                text = path.read_text('utf8')
                needle = '{' + str(oldq['specs'][key]['source_Adamstep']) + '+20*updates}'
                assert text.count(needle) == 1
                path.write_text(text.replace(needle, '{' + str(model['Adam']) + '+20*updates}', 1), 'utf8')
        assert (out / 'same_optimized_source_contract_metadata_candidate_v1.py').stat().st_size == METADATA_BYTES
        assert H(out / 'same_optimized_source_contract_metadata_candidate_v1.py') == METADATA_SHA
        # Actual qualified83B model transfer occurs only if root later invokes
        # this reviewed binder. No model is copied by source-template generation.
        assert Path(final['local_path']).stat().st_size == final['bytes']
        shutil.copy2(final['local_path'], out / 'job0/source' / spec['source_filename'])
        task = read(Path(oldq['payloads']['h1']) / 'job0/TASK.json') if native else read(out / 'job0/TASK.json')
        task.update(id=LOCAL_STAGE + '_' + key, source_SHA=final['SHA'], source_Adamstep=model['Adam'],
                    source_owned_updates=model['updates'], source_owned_completed_updates=model['updates'],
                    exact_closed_source_updates=model['updates'], source_parent_production_root=oldq['roots'][source_key])
        if key in ('h1', 'e2'):
            task.update(source_H1_actual_latest_Adamstep=model['Adam'], reward_recipe_version='step270_sampled_leg_excess_v8_reward_only')
        if native:
            task.update(native_Fudan_reference_method=True,
                        reference_artifact_SHA=bundle['reference']['reference_artifact_SHA'],
                        adapter_CPU_report_SHA=bundle['adapter_CPU']['report_SHA'],
                        not_production_E2_source=True)
        (out / 'job0/TASK.json').write_text(json.dumps(task, indent=2), 'utf8')
        for name, value in (('QUALIFIED_RUNTIME_BASE_MANIFEST.json', prior),
                            ('CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json', proof),
                            ('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json', rec)):
            (out / name).write_text(json.dumps(value, indent=2), 'utf8')
        if not native:
            put(out / 'MIXED84_NORMAL_PRODUCTION_SOURCE_AUTH_ACTUAL.json', dict(
                epoch=time.time(), approved=True, kind='actual_closed83B_healthy_three_same_V8_baseline',
                source_SHA=final['SHA'], source_Adam=model['Adam'], guard_SHA=H(out / role),
                metadata_SHA=METADATA_SHA, source_production_window='83B',
                no_reward_actor_PPO_physics_or_success_change=True, no_native_checkpoint_promoted=True))
        rows = []
        artifact_rel = bundle['reference']['artifact_relative'] if native else None
        for path in sorted(out.rglob('*')):
            if not path.is_file() or path.name == 'THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in path.parts:
                continue
            rel = path.relative_to(out).as_posix()
            if path.suffix == '.py':
                ast.parse(path.read_text('utf8'))
            if rel == 'job0/source/' + spec['source_filename']:
                value = final['SHA']
            elif rel == artifact_rel:
                value = bundle['reference']['reference_artifact_SHA']
            elif path.suffix in ('.pt', '.npz', '.usd', '.stl'):
                value = before[rel]['SHA']
            else:
                value = H(path)
            rows.append(dict(relative=rel, bytes=path.stat().st_size, SHA=value))
        manifest = dict(prior, key=key, source_SHA=final['SHA'], source_Adamstep=model['Adam'], files=rows)
        if native:
            require_native_manifest_pins(manifest, bundle)
        (out / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest, indent=2), 'utf8')
        spec['manifest_SHA'] = H(out / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
        q['specs'][key] = spec
        q['payloads'][key] = str(out)
        q['sources'][key] = dict(SHA=final['SHA'], bytes=final['bytes'], Adam=model['Adam'],
                                 updates=model['updates'], path=final['path'], source_expert=source_key)
        q['roots'][key] = ('/mnt/mod4_linux_durable_20261013/' if key == 'h1' else '/home/lc01/Zonglin Li/zonglin2/tasks/') + NAMESPACE + '/' + key
    put(N / 'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json', q)
    for name in ('deploy_mixed84_original_writer_TEMPLATE.py',
                 'observe_mixed84_baselines_native_first_finite_TEMPLATE.py',
                 'collect_mixed84_finals_original_cost_TEMPLATE.py',
                 'review_mixed84_baselines_native_fullstate_CPU_TEMPLATE.py',
                 'e2_healthy83B_physical_resource_install84_TEMPLATE.py',
                 'DEPLOYER_REUSED_H1_HELPER_84_EXACT_SOURCE_TEMPLATE.py',
                 'mixed84_protocol_v1.py'):
        shutil.copy2(HERE / name, N / name)
    return q


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Root must supply reviewed actual integration JSON; default PENDING must reject'
    bind_new_payloads(read(sys.argv[1]))
