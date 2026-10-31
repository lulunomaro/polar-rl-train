"""Only saved JSON/source metadata; never read either E0 or W35 PT."""
from pathlib import Path
import hashlib
import json
import time
from contract218 import SHA, GENERATION, CANONICAL, validate_closed_facts

T = Path(__file__).resolve().parents[2]
N210 = T / 'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
P218 = T / 'W35_SHARED_MATERIAL_NEXT_SOLO_SOURCE_V218_20261101'
CLOSING = N210 / 'reports/ROOT210_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'
CPU = N210 / 'reports/ROOT210_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json'
E0_CLOSE_SOURCE_SHA = '38e302f4146b7b58e25317d3c7db01ae3910d87630a61956882b185adb094801'


def read_ref(path):
    path = Path(path)
    assert path.suffix == '.json' and not path.name.endswith(('.partial','.active'))
    raw = path.read_bytes()
    return json.loads(raw), dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def load_closed_e0(closing=CLOSING, cpu=CPU, *, synthetic_fixture=False):
    # This is the FIRST admission in the launcher, before CIM/network/assets/PT.
    c, cr = read_ref(closing); u, ur = read_ref(cpu)
    assert synthetic_fixture or (not c.get('synthetic_fixture_only') and not u.get('synthetic_fixture_only'))
    assert c['passed_collection'] and u['passed'] and u['old_model_reads'] == 0
    o = c['owner_closed']; r = c['roles']['e0_72']; f = c['formals']['e0_72']; q = u['roles']['e0_72']
    assert o['canonical_None'] and o['shared_locks_free']
    assert o['cohort_final']['original_cost_settled'] and o['owner_exit']['original_cost_settled']
    assert r['qualified_formal'] and r['private_EX_free'] and r['errors'] == []
    assert r['original_node_terminal']['row']['returncode'] == 0
    assert r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released']
    assert r['final']['passed'] and f['transfers'] == 1 and f['two_host_SHA_equal']
    final = r['final']['final']; updates = r['final']['actual_new_PPO_updates']
    assert updates > 0 and final['SHA'] == f['SHA'] == q['SHA'] and f['SHA'] != SHA
    assert not f['source'].endswith('.partial') and not f['path'].endswith('.partial')
    assert q['passed'] and q['new_PPO_updates'] == updates
    assert q['saved_iteration'] == final['saved_iteration'] == 32066 + updates
    assert q['Adam17_step'] == final['Adam_min'] == final['Adam_max'] == 642840 + 20*updates
    assert q['actor35_critic38_STD6'] and q['complete_task_and_DR_state_present']
    assert q['save_at_or_after_requested_deadline']
    assert u['epoch'] >= c['epoch']
    return dict(closing=c, cpu=u, role=r, formal=f, cpu_role=q, refs=[cr,ur])


def closed_bridge(e0, authority, cim):
    c=e0['closing'];u=e0['cpu'];r=e0['role'];f=e0['formal'];q=e0['cpu_role']
    m, mr = read_ref(P218 / 'reports/ACTUAL217_SELECTED_READBACK_AND_SOURCE_SCOPE.json')
    actual217, a217r = read_ref(m['report']['path'])
    assert a217r['SHA']==m['report']['SHA'] and a217r['bytes']==m['report']['bytes']
    n=m['native_selected']
    assert m['passed'] and m['returncode']==0 and m['phase_evidence_complete']
    assert m['actual_material_limit_error_count']==0 and m['all_own_children_waited'] and m['private_EX_released']
    assert n['own20k_restore']['original_physical_parameter_audit_passed']
    assert n['own20k_restore']['original_episode_incremented_once']
    assert authority['CNone'] and authority['generation']==GENERATION and authority['canonical_path']==CANONICAL
    assert authority['active_segment'] is None and authority['total_authorized_seconds']==2268000
    assert authority['new_authority_budget_extensions']==[] and not authority['account_write']
    assert cim['passed'] and cim['other_known_control_finites']==[]
    facts=dict(material217_passed=m['passed'], material217_num_envs=n['num_envs'],
        material217_controls=n['controls'], material217_physics=n['physics_callbacks'],
        material217_feedback=n['feedback_samples'], material217_model_opens=n['model_opens'],
        material217_actor_calls=n['actor_calls'], material217_optimizer_updates=n['optimizer_updates'],
        material217_own_restore_new_episode_and_setter_phases_complete=bool(m['phase_evidence_complete'] and n['actual_D0_D7_own20k_restore_then_new_episode_native_integration']),
        material217_owned_stdout_scan_complete=m['passed'], material217_limit64K_errors=m['actual_material_limit_error_count'],
        material217_waited_RC=m['returncode'], material217_App_closed=True,
        material217_all_own_children_waited_out=m['all_own_children_waited'],
        material217_private_EX_released_and_actual_FREE=m['private_EX_released'],
        material217_closed_epoch=actual217['epoch'],
        E0_210_complete_final_saved=r['final']['passed'], E0_210_App_closed=True,
        E0_210_worker_and_all_own_children_waited_out=r['original_node_exit']['all_own_children_waited'],
        E0_210_waited_RC=r['original_node_terminal']['row']['returncode'],
        E0_210_original_owner_closed_and_cost_settled=c['owner_closed']['owner_exit']['original_cost_settled'],
        E0_210_closed_epoch=c['epoch'], E0_210_final_SHA=f['SHA'],
        E0_210_actual_new_PPO_updates=r['final']['actual_new_PPO_updates'],
        E0_210_final_iteration=q['saved_iteration'], E0_210_final_Adam_step=int(q['Adam17_step']),
        E0_new_formal_CPU_passed=q['passed'],
        E0_new_formal_CPU_whole_finite_35_38_6_STD_17Adam_DR=bool(u['passed'] and q['actor35_critic38_STD6'] and q['complete_task_and_DR_state_present']),
        E0_new_formal_CPU_model_SHA=q['SHA'], E0_new_formal_CPU_iteration=q['saved_iteration'],
        E0_new_formal_CPU_Adam_step=int(q['Adam17_step']), E0_new_formal_CPU_finished_epoch=u['epoch'],
        canonical_generation=authority['generation'], canonical_path=authority['canonical_path'], canonical_active=authority['active_segment'],
        canonical_total_authorized_seconds=authority['total_authorized_seconds'], fresh_CNone_checked_epoch=authority['epoch'],
        fresh_LOCAL_exact_CIM_passed=cim['passed'], fresh_LOCAL_exact_CIM_checked_epoch=cim['epoch'],
        fresh_control_snapshot_id='ROOT219_CNONE_'+authority['SHA']+'_'+str(authority['epoch']),
        no_new_writer_grant_copy_refund_or_210_hotadd=True)
    #Only the original217 saved JSON epoch is projected here;no log inspection.
    validate_closed_facts(facts)
    return dict(schema='mod4.219.closed_bridge_actual.v1', epoch=time.time(), passed=True,
        facts=facts, original_refs=e0['refs']+[mr,m['report']], actual_authority=authority, exact_LOCAL_CIM=cim,
        Appclose_inference=dict(
            E0=dict(source=str(N210/'package/run210_mixed_E0_JUMP_worker.py'), SHA=E0_CLOSE_SOURCE_SHA,
                method='Complete FINAL + original worker waitRC0 + errors[];pinned source finally real.close then ns[app].close. No independent APP_CLOSED marker invented.'),
            material217=dict(source='frozen214/material0pt214.py', SHA='dc105696ae3c65702d963d7d91650cec656d471fcc3a478d62b5b27dc17a29d5',
                method='Actual217 RC0/allownwaited/EXreleased and pinned finally envclose then Appclose;not a fake marker.')),
        source_model='W35 ad504/32336/17Adam648360 only;E0 artifact is closure evidence',
        source_model_reads=0, no_new_budget_writer_or_grant=True)
