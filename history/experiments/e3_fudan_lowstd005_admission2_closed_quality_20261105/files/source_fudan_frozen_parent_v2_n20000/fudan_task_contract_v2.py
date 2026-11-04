"""Pure original task wrapper for an actually closed positive N20000 save; no I/O."""
import os
from worker_sources.parent.task_contract import make_task as _original_make_task

def make_task(role, plan, deadline, fds):
    assert role['role']=='E3' and role['controls']==160
    assert role['source_training_execution_qualified'] is True
    assert len(fds)==2 and fds[0]!=fds[1]
    t=_original_make_task(role, plan, deadline, fds)
    for name in ('source_iteration','source_Adam17','source_LR'):
        t.pop(name,None)
    kind='E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1'
    t.update(kind=kind,purpose=kind,owner_parent_pid=os.getpid(),
             policy_interface='fudan_sequence_raw35_history5_latent3_clipped_mean_v1',
             evaluation_scope='ORIGINAL_E3_74_PLUS_6_NORMAL',source_training_execution_qualified=True)
    return t
