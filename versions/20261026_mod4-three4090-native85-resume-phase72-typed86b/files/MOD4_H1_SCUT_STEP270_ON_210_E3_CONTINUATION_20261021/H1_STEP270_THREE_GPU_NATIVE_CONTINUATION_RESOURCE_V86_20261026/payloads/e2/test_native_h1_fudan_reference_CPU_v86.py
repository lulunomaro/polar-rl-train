"""UNEXECUTED native86 target CPU source template: reference/loss/dimensions, no learner.

Uses the explicit offline CPU mapping API. Actual robot.joint_names is checked
after environment construction and before first physical step/Pi, outside preGO.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
import time

import torch

B = Path(__file__).resolve().parent
sys.path[:0] = [str(B), str(B / 'source')]
from mixed84_protocol_v1 import (SOURCES, require_native_manifest_pins,
                                 validate_objective_contract, validate_reference_preparation)
from supermimic_reference_adapter_v1 import read_json_reference, PartialReferenceImitationMdp
from supermimic_vendor_v2.geometry import invariant_features, unflatten_state

read = lambda path: json.loads(Path(path).read_bytes())
H = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    torch.set_num_threads(1)
    assert not torch.cuda.is_initialized()
    manifest = read(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    manifest_sha = H(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    bundle = read(B / 'MIXED84_REFERENCE_BINDING_ACTUAL.json')
    validate_reference_preparation(bundle)
    sdk = read(B / 'TARGET_NATIVE86_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json')
    assert sdk['passed_CPU_only'] and sdk['manifest_SHA'] == manifest_sha
    assert sdk['bootstrap_SHA'] == SOURCES['h1']['SHA'] and sdk['all17Adam'] == SOURCES['h1']['Adam']
    assert sdk['source_SHA'] == manifest['source_SHA'] == '94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af'
    adapter = B / 'source/supermimic_reference_adapter_v1.py'
    assert H(adapter) == bundle['adapter_CPU']['adapter_source_SHA']
    artifact = B / bundle['reference']['artifact_relative']
    assert H(artifact) == bundle['reference']['reference_artifact_SHA']
    # This reads only the newly authorized exported own-reference JSON on target,
    # never any old raw/NPZ/pilot checkpoint. Source preparation does not run it.
    reference = read_json_reference(artifact)
    names = reference.joint_names
    assert len(names) == len(set(names)) == 30
    reference = reference.for_offline_joint_order(names)
    assert reference.metadata['sdk_joint_order_verified'] is False
    assert reference.metadata['clock_alignment']['native_frame_anchor'] == 100
    assert reference.metadata['clock_alignment']['reference_time_anchor_s'] == .5
    tree = ast.parse((B / 'source/h1_supermimic_bridge_v1.py').read_text('utf8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'H1GoalMdp')
    scope = dict(torch=torch, invariant_features=invariant_features)
    exec(compile(ast.Module(body=[cls], type_ignores=[]), 'actual_installed_H1GoalMdp_AST_only', 'exec'), scope)
    base = scope['H1GoalMdp'](torch.zeros(30), float(reference.states[0, 2]))
    mdp = PartialReferenceImitationMdp(base, reference.torch_provider('cpu', offline_cpu_only=True))
    frames = torch.tensor([0, 100], dtype=torch.int32)
    goal = mdp.goal(frames, 1)
    assert goal.shape == (2, 73) and torch.isfinite(goal).all()
    raw = mdp.provider.raw_reference_at_frames(frames)
    state = unflatten_state(raw)
    actions = torch.zeros(2, 6)
    result = mdp.reward(state, frames, actions, actions)
    assert result.shape == (2,) and torch.isfinite(result).all()
    context = torch.zeros(2, 49)
    assert mdp.obs(state, actions, context, frames).shape == (2, 128)
    contract = mdp.contract_manifest()
    validate_objective_contract(contract)
    phase = contract['phase_mask']
    offset = reference.metadata['native_frame_zero_reference_time_s']
    after = int((phase['demo_height_vz_active_through_reference_time_s'] - offset) / .01) + 10
    phase_frames = torch.tensor([max(0, after - 20), after], dtype=torch.int32)
    phase_goal = mdp.goal(phase_frames, 1)
    assert phase_goal[1, 2] == 0 and phase_goal[1, 9] == 0, 'Post-apex source-floor Z/Vz must be masked'
    phase_state = list(unflatten_state(mdp.provider.raw_reference_at_frames(phase_frames)))
    phase_state[0] = phase_state[0].clone()
    phase_state[0][:, 0] = phase['own_task_step_edge_x_m'] + phase['own_task_support_region_transition_m']
    own_top = phase['own_task_nominal_chassis_height_m'] + phase['own_task_platform_height_m']
    phase_state[0][:, 2] = own_top - .1
    terms = mdp.objective_terms(tuple(phase_state), phase_frames, actions, actions)
    assert terms['demo_height_cost'][1] == 0 and terms['demo_vertical_velocity_cost'][1] == 0
    assert terms['own_task_landing_height_cost'][1] > 0
    phase_state[0][:, 2] = own_top
    corrected = mdp.objective_terms(tuple(phase_state), phase_frames, actions, actions)
    assert corrected['own_task_landing_height_cost'][1] == 0
    proof_path = B / 'NATIVE_FINALIZATION_CPU_PROOF_ACTUAL.json'
    assert H(proof_path) == bundle['finalization_CPU']['report_SHA']
    proof = read(proof_path)
    assert proof['passed'] and proof['passed_count'] == proof['count'] >= 21 and proof['CPU_only']
    assert proof['source_SHA']['native_finalization_v1.py'] == bundle['candidate_pins']['finalization_source_SHA']
    assert not proof['CUDA_initialized'] and not proof['real_model_or_pilot_checkpoint_content_read']
    assert H(B / 'source/native_finalization_v1.py') == bundle['candidate_pins']['finalization_source_SHA']
    contract_path = B / 'reports/NATIVE_FUDAN_REFERENCE_TARGET_CPU_OBJECTIVE_CONTRACT_ACTUAL.json'
    with contract_path.open('x', encoding='utf8', newline='') as stream:
        stream.write(json.dumps(contract, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n')
    assert H(contract_path) == bundle['adapter_CPU']['objective_contract_SHA']
    value = dict(epoch=time.time(), passed=True, actual_installed_CPU_passed=True,
                 CUDA_initialized=False, manifest_SHA=manifest_sha, source_SHA=manifest['source_SHA'],
                 reference_artifact_SHA=bundle['reference']['reference_artifact_SHA'],
                 adapter_CPU_report_SHA=bundle['adapter_CPU']['report_SHA'],
                 objective_contract_SHA=bundle['adapter_CPU']['objective_contract_SHA'],
                 offline_objective_contract_SHA=H(contract_path), offline_objective_contract=contract,
                 offline_named_mapping_verified=True, actual_runtime_order_readback=False,
                 candidate_pins=read(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json')['candidate_pins'], original_physics_and_success_unchanged=True,
                 finalization_lifecycle_CPU_passed=True, partial_mask_objective_actual_CPU_admitted=True,
                 ascent_phase_mask_and_own_step_support_loss_CPU_passed=True,
                 no_environment_learner_actor_forward_or_optimizer_step=True,
                 reused_actual_finalization21_CPU_proof_not_rerun=True,
                 not_dynamic_actuation_step270_or_skill_proof=True)
    assert not torch.cuda.is_initialized()
    with (B / 'reports/NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V86_ACTUAL.json').open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2)
    print(json.dumps(dict(passed=True, actual_installed_reference_loss_CPU=True,
                          offline_objective_contract_SHA=value['offline_objective_contract_SHA'])))


if __name__ == '__main__':
    main()
