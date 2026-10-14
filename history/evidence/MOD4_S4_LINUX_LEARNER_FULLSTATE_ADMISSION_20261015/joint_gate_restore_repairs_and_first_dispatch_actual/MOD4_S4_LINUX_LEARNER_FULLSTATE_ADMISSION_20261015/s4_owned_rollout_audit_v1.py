"""Durable original rollout buffers before update; no data/gradient mutation."""
from pathlib import Path
import hashlib,json,os,time
import numpy as np
from s4_rsl5_frozen_pair_learner_v1 import CHOICE
from s4_supported_rollout_storage_v1 import DOMAIN

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def install_rollout_audit(alg,folder,source_SHA):
    folder=Path(folder);rows=[];original=alg.update
    def update():
        s=alg.storage;t=s.num_transitions_per_env
        assert s.step==t and s.bootstrap_supported is not None
        index=len(rows);p=folder/('S4_GATE_FULL_ROLLOUT_'+str(index)+'.npz')
        assert not p.exists();part=p.with_suffix('.npz.partial')
        arrays=dict(policy35=s.observations['policy'].detach().cpu().numpy(),
            critic38=s.observations['critic'].detach().cpu().numpy(),
            sampled_z=s.observations[CHOICE].detach().cpu().numpy(),
            supported_training_metadata=s.observations[DOMAIN].detach().cpu().numpy(),
            raw_actions=s.actions.detach().cpu().numpy(),old_gate_logits=s.distribution_params[0].detach().cpu().numpy(),
            old_joint_logp=s.actions_log_prob.detach().cpu().numpy(),rewards=s.rewards.detach().cpu().numpy(),
            dones=s.dones.detach().cpu().numpy(),values=s.values.detach().cpu().numpy(),
            returns=s.returns.detach().cpu().numpy(),bootstrap_supported=s.bootstrap_supported.detach().cpu().numpy())
        # Uncompressed NPZ avoids blocking learner time on repeated compression.
        with part.open('xb') as f:np.savez(f,**arrays);f.flush();os.fsync(f.fileno())
        os.replace(part,p)
        row=dict(index=index,path=str(p),bytes=p.stat().st_size,sha256=sha(p),source_SHA=source_SHA,
            physical_controls=t,physical_envs=s.num_envs,original_buffers_before_optimizer=True,
            optimizer_update_complete=False,started_epoch=time.time())
        rows.append(row)
        def publish():
            q=folder/'S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json';tmp=q.with_suffix('.json.partial')
            with tmp.open('w') as f:json.dump(dict(rows=rows,source_SHA=source_SHA),f,indent=2);f.flush();os.fsync(f.fileno())
            os.replace(tmp,q)
        publish()
        result=original()
        row.update(optimizer_update_complete=True,finished_epoch=time.time(),selection=s.last_selection)
        publish();return result
    alg.update=update
