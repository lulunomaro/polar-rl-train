"""Unique directly authorized100h transaction at an actual idle, saved boundary."""
from pathlib import Path
import fcntl
import hashlib
import json
import os
import time
from budget_retrain_contract import EXTENSION_ID, BEFORE_TOTAL, AFTER_TOTAL, extend_once

D = Path(__file__).resolve().parent
R = D / 'reports'
E = Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports')
B = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
P = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
MASTER = '812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
H = lambda raw: hashlib.sha256(raw).hexdigest()
J = lambda p: json.loads(p.read_bytes())


def atomic_cas(path, old, new):
    assert path.read_bytes() == old, 'Concurrent change; do not overwrite'
    tmp = path.with_name(path.name + '.seventh-' + str(time.time_ns()))
    with tmp.open('xb') as handle:
        handle.write(new)
        handle.flush()
        os.fsync(handle.fileno())
    assert path.read_bytes() == old
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def exclusive_json(path, value):
    with path.open('xb') as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2).encode())
        handle.flush()
        os.fsync(handle.fileno())


def identity(pid):
    path = Path('/proc') / str(pid)
    try:
        fields = (path / 'stat').read_text().rsplit(') ', 1)[1].split()
        return dict(pid=int(pid), state=fields[0], start_ticks=int(fields[19]),
                    argv=(path / 'cmdline').read_bytes().decode(errors='replace').split('\0')[:-1])
    except (FileNotFoundError, ProcessLookupError): return None


def main():
    approval = J(R / 'DIRECT_HUMAN_APPROVAL.json')
    assert approval['human_message'] == '预算再给你100小时，没毕业的可以复训'
    assert approval['historical_master_sha256'] == MASTER
    assert H((E / 'MOD4_MOE_MASTER_PLAN.md').read_bytes()) == MASTER
    assert not (R / 'TRANSACTION_STARTED.json').exists(), 'Once entry already attempted; inspect actual receipt'
    assert not (E / (EXTENSION_ID + '_APPLIED.json')).exists()
    locks = []
    try:
        for path in (P / 'autonomy_controller.lock', B.parent / 'native_floor_supervisor.lock'):
            handle = path.open('r')
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locks.append(handle)
        before = B.read_bytes()
        budget = json.loads(before)
        assert budget['active_segment'] is None and budget['authorized_training_seconds'] == BEFORE_TOTAL
        autonomy = J(P / 'reports/AUTONOMY_STATE.json')
        assert not autonomy.get('active_training'), 'Autonomy active authority must settle itself'
        current_before = (E / 'MOE_PLAN_EXECUTION_CURRENT.json').read_bytes()
        current = json.loads(current_before)
        rev = current['terrain_subexpert_revision004']
        assert rev['approved'] and rev['active_next_expert'] == 'E1_CURB'
        assert rev['active_next_phase'] == 'CURB20_direction_entry_CPU_contract_preparation'
        assert not rev['curb20_direction_entry_repair_scope']['learning_executor_deployed']
        # Actual latest fullsave and own PID, then all parent/guardian/child identities.
        root = Path(rev['slope5_independent_scope']['root'])
        state = J(root / 'reports/E1_STATE.json')
        assert state['phase'] == 'E1_SLOPE5_independent_saved_review_ready' and state['child'] is None
        passed = J(root / 'reports/e1_SLOPE5_independent_observation_PASSED.json')
        assert passed['checkpoint']['sha256'] == '24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
        checkpoint = Path(passed['checkpoint']['path'])
        assert H(checkpoint.read_bytes()) == passed['checkpoint']['sha256']
        assert len(passed['unique_completed_segment']) == 1
        assert passed['unique_completed_segment'][0] in budget['completed_segments']
        guardian = J(root / 'reports/E1_GUARDIAN_STARTED.json')
        own_pid = passed['own_PID_bound_receipt']['pid']
        locators = [state['owner'], guardian, dict(pid=own_pid, start_ticks=83699658)]
        identities = []
        for locator in locators:
            actual = identity(locator['pid'])
            assert not actual or actual['state'] == 'Z' or actual['start_ticks'] != locator['start_ticks']
            identities.append(dict(locator=locator, actual=actual, original_identity_exited=True))
        live_authorities = []
        for path in Path('/proc').glob('[0-9]*'):
            actual = identity(path.name)
            if not actual or actual['state'] == 'Z' or actual['pid'] == os.getpid(): continue
            scripts = [a for a in actual['argv'] if a.endswith('.py') and '/rl_candidates/MOD4' in a]
            if any(Path(a).name.startswith(('train_', 'supervise_')) for a in scripts):
                live_authorities.append(actual)
        assert not live_authorities, 'Existing MOD4 trainer/supervisor; wait saved boundary'
        protected_names = ('MOD4_MOE_MASTER_PLAN.md', 'EXECUTION_TRACKS.json',
                           'MOD4_RM_TERRAIN_TRAINING_REVISION.json',
                           'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json',
                           'MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json')
        protected = {name: (E / name).read_bytes() for name in protected_names}
        ap_path = E / 'PLAN_APPROVAL.json'
        ap_before = ap_path.read_bytes()
        ap = json.loads(ap_before)
        assert ap['approved'] and ap['authorized_budget_ceiling_seconds'] == BEFORE_TOTAL
        assert ap['approved_plan_sha256'] == MASTER and not ap['S8_authorized']
        contract_path = E / 'MOD4_MOE_EXECUTION_CONTRACT.json'
        contract_before = contract_path.read_bytes()
        contract = json.loads(contract_before)
        assert contract['budget']['authorized_seconds'] == BEFORE_TOTAL
        receipt_path = str(E / (EXTENSION_ID + '_APPLIED.json'))
        after = extend_once(budget, approval, time.time(), receipt_path)
        exclusive_json(R / 'TRANSACTION_STARTED.json', dict(epoch=time.time(), extension_id=EXTENSION_ID,
            before_sha256=H(before), expected_after_total=AFTER_TOTAL, direct_human_authorization=True,
            two_OS_locks_acquired=True, actual_own_fullsave_and_exit=identities,
            old_completed_segment_count=len(budget['completed_segments']), no_learning_launch=True))
        after_raw = json.dumps(after, ensure_ascii=False, indent=2).encode()
        atomic_cas(B, before, after_raw)
        assert J(B) == after
        proof = dict(epoch=time.time(), extension_id=EXTENSION_ID, applied_once=True, added_seconds=360000,
                     authorized_before=BEFORE_TOTAL, authorized_after=AFTER_TOTAL, total_hours=330,
                     charged_seconds=after['charged_training_seconds'], charged_unchanged=True,
                     remaining_seconds=after['remaining_training_seconds'],
                     remaining_hours_snapshot=after['remaining_training_seconds']/3600,
                     active_segment=after['active_segment'], completed_segments_unchanged=True,
                     old_six_extensions_unchanged=True, extension_records=7,
                     old_accounting_history_digest=H(json.dumps(budget['completed_segments'],sort_keys=True).encode()),
                     before_sha256=H(before), after_sha256=H(B.read_bytes()),
                     two_original_OS_locks_acquired=True, latest_own_fullsave_PASSED_SHA=passed['checkpoint']['sha256'],
                     own_unique_completed_segment_already_settled=True, actual_original_processes_exited=identities,
                     no_learning_GPU_launch_or_old_once_replay=True)
        exclusive_json(E / (EXTENSION_ID + '_APPLIED.json'), proof)
        exclusive_json(R / 'BUDGET_APPLIED.json', proof)
        amendment = dict(approved=True, authorization_basis='direct_human_user_message',
                         approval=str(E / 'MOD4_BUDGET_RETRAIN_100H_005_APPROVAL.json'),
                         plan=str(E / 'MOD4_BUDGET_RETRAIN_100H_REVISION_005.json'),
                         extension_receipt=receipt_path, new_budget_seconds=360000,
                         authorized_training_seconds=AFTER_TOTAL, expert_retraining_authorized=True,
                         same_scope_prior_failures_not_reclassified=True, no_new_S8_or_hardware_interface=True)
        ap['authorized_budget_ceiling_seconds'] = AFTER_TOTAL
        ap.setdefault('execution_amendments', {})['MOD4-BUDGET-RETRAIN-100H-005'] = amendment
        assert ap['allowed_stages'] == json.loads(ap_before)['allowed_stages'] and not ap['S8_authorized']
        atomic_cas(ap_path, ap_before, json.dumps(ap,ensure_ascii=False,indent=2).encode())
        contract['budget'].update(authorized_seconds=AFTER_TOTAL, ledger_authorized_seconds_current=AFTER_TOTAL,
             total_plan_authorized_seconds_after_pending_extension=AFTER_TOTAL, extension_records_applied_once=7,
             latest_explicit_extension=amendment, current_remaining_seconds_snapshot=after['remaining_training_seconds'],
             current_snapshot_epoch=time.time())
        contract.setdefault('execution_amendments', {})['MOD4-BUDGET-RETRAIN-100H-005'] = amendment
        atomic_cas(contract_path, contract_before, json.dumps(contract,ensure_ascii=False,indent=2).encode())
        current['budget_retrain_revision005'] = amendment
        rev['retraining_revision005'] = amendment
        rev['curb20_direction_entry_repair_scope']['direct_human_retraining_authorized'] = True
        atomic_cas(E / 'MOE_PLAN_EXECUTION_CURRENT.json',current_before,json.dumps(current,ensure_ascii=False,indent=2).encode())
        h = E / 'LATEST_HANDOFF.md'
        hb = h.read_bytes()
        note = '\n\n2026-10-11 direct human: 预算再给你100小时，没毕业的可以复训。New unique seventh extension USER_ADD100H_20261011_7TH applied at own saved/actual exited/two OS locks/idle canonical boundary. Total1188000s330h; charged history unchanged; remaining676797.5426192284s188.0h snapshot. Read MOD4_BUDGET_RETRAIN_100H_REVISION_005 and approval/applied receipts. Unqualified CURB/WAVE may be retrained in isolated bounded repair scopes; next CURB20 entry-direction contract preparation remains pending actual footprint/histograms/SDK/fullrestore/PPO admission. Existing qualified observed SLOPE5/8/10 scopes and E0 frozen; no automatic repeat of old failed or completed once entries. New time does not authorize S8 dangerous resets or alter hardware/DR/clock/reward/interface. Seven extensions exactly once; all later budget guards derive registered1188000 total and actual remaining, old828000 assertions are historical and require new isolated wrapper before launch. All new reports/errors/sync/monitor require Git.\n'
        atomic_cas(h,hb,hb+note.encode())
        assert all((E / name).read_bytes() == raw for name,raw in protected.items())
        assert B.read_bytes() == after_raw and J(B)['charged_training_seconds'] == budget['charged_training_seconds']
        sync = dict(epoch=time.time(), metadata_synced=True, extension_id=EXTENSION_ID,
                    PLAN_APPROVAL_budget_ceiling=AFTER_TOTAL, execution_contract_budget_total=AFTER_TOTAL,
                    historical_master_tracks_RM_revision004_bytes_unchanged=True,
                    active_next_expert='E1_CURB', active_next_phase=rev['active_next_phase'],
                    training_executor_not_started=True, canonical_sha256=H(B.read_bytes()),
                    resulting_metadata_sha256={name:H((E/name).read_bytes()) for name in
                        ('PLAN_APPROVAL.json','MOD4_MOE_EXECUTION_CONTRACT.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md')})
        exclusive_json(E / 'MOD4_BUDGET_RETRAIN_100H_005_METADATA_SYNCED.json',sync)
        exclusive_json(R / 'METADATA_SYNCED.json',sync)
        print(json.dumps(dict(budget=proof,metadata=sync)))
    finally:
        for handle in reversed(locks): handle.close()


if __name__ == '__main__': main()
