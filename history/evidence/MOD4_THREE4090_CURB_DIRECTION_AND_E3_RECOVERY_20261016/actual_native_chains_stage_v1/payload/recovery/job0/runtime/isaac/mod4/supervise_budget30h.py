"""Continue the current stage with an explicitly extended canonical budget.

No one-time initial handover/preflight is repeated. To resume after a reboot,
first reconcile the existing active segment from actual shutdown evidence.
"""
import json
import os
import traceback
from pathlib import Path

import supervise_mild_trial as mild

base = mild.base
ROOT = mild.ROOT
RECEIPT = ROOT/'reports/USER_ADD20H_20261001_2341_APPLIED.json'


def main():
    mild.acquire(ROOT/'mild_trial_supervisor.lock')
    mild.acquire(mild.OLD/'native_floor_supervisor.lock')
    assert not base.trainers(), 'existing trainer; refuse double start'
    b = base.budget_state()
    assert not b.get('active_segment'), 'reconcile previous segment before resuming'
    assert b['authorized_training_seconds'] == 108000
    assert b.get('owner_root') == str(ROOT)
    receipt = mild.read(RECEIPT)
    assert receipt['extension_id'] == 'USER_ADD20H_20261001_2341'
    assert b['remaining_training_seconds'] > 120
    ck = base.latest(ROOT/'logs')
    assert ck is not None
    info = base.checkpoint(ck)
    decision = mild.read(ROOT/'reports/trial_multiseed_decision.json')
    assert decision['continue_mild'], 'mild trial admission must remain recorded'
    mild.environment()
    prior = mild.read(ROOT/'status.json')
    base.STATE.update(prior)
    base.status(stage='starting_budget_extended_training', supervisor_pid=os.getpid(),
                training_pid=None, evaluation_pid=None, validation_pid=None,
                authorized_training_seconds=b['authorized_training_seconds'],
                budget_seconds=b['authorized_training_seconds'],
                budget_extension_receipt=str(RECEIPT), resume_checkpoint=info,
                canonical_budget=str(mild.CANONICAL), error=None)
    final = mild.training(ck, 20000, 'continued_mild', ROOT/'logs', 'white_v1')
    final_info = base.checkpoint(final)
    name = 'budget30h_model'+str(final_info['iteration_stored'])
    nominal = mild.frozen(final, 'final_nominal_'+name, 20261001, 'nominal')
    randomized = mild.frozen(final, 'final_mild_'+name, 20261001, 'white_v1')
    base.status(stage='finished', training_pid=None, evaluation_pid=None,
        final_checkpoint=final_info, final_evaluation={'nominal': nominal, 'mild': randomized},
        latest_evaluation=randomized,
        outcome='Explicit effective-time budget exhausted; report capabilities and unpassed criteria honestly')


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        mild.update_stage('attention_required', error=traceback.format_exc(),
            child_pid=mild.LIVE.pid if mild.LIVE and mild.LIVE.poll() is None else None,
            instructions='Inspect actual child and canonical active segment; no blind restart or budget reset.')
        raise

