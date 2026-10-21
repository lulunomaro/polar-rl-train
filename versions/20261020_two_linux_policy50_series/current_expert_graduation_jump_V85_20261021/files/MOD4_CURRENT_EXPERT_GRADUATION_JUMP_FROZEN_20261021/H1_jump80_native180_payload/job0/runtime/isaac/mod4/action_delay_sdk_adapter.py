"""Isolated D4 SDK adapter: delay processed targets at physical application.

This module patches only action terms of its newly constructed candidate env.
It has no imports of Isaac, no standalone training entry and no host authority.
The original process_actions retains scale/default-offset/CAD projection, and
the original apply_actions retains articulation target and actuator paths.
"""
import torch,types
from action_delay_physics_queue import PhysicsActionQueue,WIDTHS

def as_tensor(value):
    return value.torch if hasattr(value,'torch') else value

class PhysicalActionDelayAdapter:
    def __init__(self,env,enabled,seed,collect=False):
        assert env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4
        assert not getattr(env.sim,'_physics_handles_decimation',False)
        self.env=env;self.queue=PhysicsActionQueue(env.num_envs,env.device,seed,enabled=enabled)
        self.collect=collect;self.rows={k:[] for k in WIDTHS};self.calls={k:0 for k in WIDTHS}
        self.reset_rows=[];self.formula_max_error=0.;self.terms={}
        for key,width in WIDTHS.items():
            term=env.action_manager.get_term(key);assert term.action_dim==width and term._max_lag==0
            self.terms[key]=term
            self._wrap(key,term)
    def ids(self,env_ids):
        allids=torch.arange(self.env.num_envs,device=self.env.device)
        return allids if env_ids is None else allids[env_ids] if isinstance(env_ids,slice) else torch.as_tensor(env_ids,device=self.env.device,dtype=torch.long)
    def neutral(self,key):
        term=self.terms[key]
        if key=='legs':return as_tensor(term._asset.data.default_joint_pos)[:,term._joint_ids].clone()
        return torch.zeros((self.env.num_envs,2),device=self.env.device)
    def _wrap(self,key,term):
        original_process=term.process_actions;original_apply=term.apply_actions;original_reset=term.reset
        adapter=self
        def process(this,actions):
            original_process(actions)
            adapter.queue.submit(key,this.processed_actions.clone(),int(adapter.env._sim_step_counter))
        def apply(this):
            # Installed SDK increments the counter immediately before this call;
            # the integration interval has not begun yet.
            tick=int(adapter.env._sim_step_counter)-1
            original=this._processed_actions
            value=adapter.queue.apply(key,tick)
            this._processed_actions=value
            try:original_apply()
            finally:this._processed_actions=original
            field='joint_pos_target' if key=='legs' else 'joint_vel_target'
            actual=as_tensor(getattr(this._asset.data,field))[:,this._joint_ids]
            error=float((actual-value).abs().max());adapter.formula_max_error=max(adapter.formula_max_error,error)
            assert error<=1e-6,'Actual articulation target differs from selected delayed target'
            adapter.calls[key]+=1
            if adapter.collect:
                row={name:(item.detach().cpu().tolist() if torch.is_tensor(item) else item) for name,item in adapter.queue.receipt(key,tick).items()}
                row.update(requested_processed_target=original.detach().cpu().tolist(),actual_processed_target=value.detach().cpu().tolist(),actual_articulation_target=actual.detach().cpu().tolist())
                adapter.rows[key].append(row)
        def reset(this,env_ids=None):
            original_reset(env_ids)
            selected=adapter.ids(env_ids)
            old=adapter.queue.state_dict() if adapter.collect else None
            adapter.queue.reset(key,selected,adapter.neutral(key))
            if adapter.collect:
                others=torch.ones(adapter.env.num_envs,dtype=torch.bool,device=adapter.env.device);others[selected]=False
                g=adapter.queue.groups[key]
                assert all(torch.equal(g[f][others],old['groups'][key][f][others]) for f in g)
                assert torch.equal(g['last_apply_tick'],old['groups'][key]['last_apply_tick'])
                assert torch.equal(g['applied'][selected],adapter.neutral(key)[selected]) and not bool(g['pending_valid'][selected].any())
                adapter.reset_rows.append(dict(group=key,env_ids=selected.cpu().tolist(),unselected_exact=True,global_physics_clock_preserved=True,selected_stale_pending_cleared=True,neutral_target_from_actual_default_q_or_zero_wheel=True))
        term.process_actions=types.MethodType(process,term);term.apply_actions=types.MethodType(apply,term);term.reset=types.MethodType(reset,term)
        self.queue.reset(key,self.ids(None),self.neutral(key))
    def state_dict(self):return self.queue.state_dict()
    def load_state_dict(self,state):self.queue.load_state_dict(state)
    def audit(self):
        return dict(recipe=self.queue.recipe(),callback_counts=self.calls,application_formula_max_error=self.formula_max_error,rows=self.rows,reset_rows=self.reset_rows,policy_requested_processed_targets_restored_after_apply=True,original_legacy_delay_remains_disabled=True,actual_apply_time_is_before_integration=True,actual_apply_time_counter_minus1=True,not_training_or_full_DR_graduation=True)

