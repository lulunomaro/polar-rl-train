"""Pure low80 task wrapper; original locks, timeouts, parent and asset bindings retained."""
import os
from worker_sources.parent.task_contract import make_task as _original_make_task

def make_task(role,plan,deadline,fds):
 assert role['role']=='E3_LOW80_'+str(role['seed'])and role['seed']in(20261002,20261003,20261004)and role['controls']==400
 assert role['source_training_execution_qualified']is True and len(fds)==2 and fds[0]!=fds[1]
 t=_original_make_task(role,plan,deadline,fds)
 for name in('source_iteration','source_Adam17','source_LR'):t.pop(name,None)
 kind='E3_FDN_FROZEN_LOW80_HOLDOUT_RESUME55_V2'
 t.update(kind=kind,purpose=kind,owner_parent_pid=os.getpid(),policy_interface='fudan_sequence_raw35_history5_latent3_clipped_mean_v1',evaluation_scope='LOW80_FIVE_POSE16_8S_FULLDR_HOLDOUT_FIRSTEPISODE_CONFIRM',source_training_execution_qualified=True,expert_role='E3',seed=role['seed'],controls=400,physics_callbacks=3200,feedback_samples=800,eval_members=[r['role']for r in plan['roles']])
 return t
