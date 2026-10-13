"""Full valid pre-reset command prefixes; separate audit, unchanged actor inputs."""
from pathlib import Path
import json,numpy as np,torch
from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
from retention_flat_runtime import tensor
class RetentionLearningEnv(E1ResetEvidenceLearningEnv):
 def __init__(self,*a,**k):
  super().__init__(*a,**k);self._retention_trace=[];self._retention_trace_written=0;self._retention_trace_files=[]
 def step(self,action):
  cmd=self.command_manager.get_term('twist');before=tensor(self.scene['robot'].data.root_pos_w).clone();heading=tensor(self.scene['robot'].data.heading_w).clone();command=cmd.command.clone();modes=torch.stack((cmd.family,cmd.eligible_flat.long(),cmd.linear.long(),cmd.moving.long()),1).clone()
  result=super().step(action);after=self._e1_pre_reset_frame['root'][:,:3]
  # Each transition uses the command that produced it and pre-reset root.
  row=torch.cat((before,after,heading[:,None],command,modes.float(),self.termination_manager.terminated[:,None],self.termination_manager.time_outs[:,None]),1)
  self._retention_trace.append(row.cpu().numpy());return result
 def write_retention_trace(self,directory):
  p=Path(directory);p.mkdir(exist_ok=True);end=len(self._retention_trace)
  if end>self._retention_trace_written:
   name='retention_prefix_'+str(self._retention_trace_written)+'_'+str(end)+'.npz';q=p/name;assert not q.exists()
   np.savez_compressed(q,rows=np.stack(self._retention_trace[self._retention_trace_written:end]),columns=np.array(['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']))
   self._retention_trace_files.append(name);self._retention_trace_written=end
  (p/'RETENTION_COMMAND_ACTUAL.json').write_text(json.dumps(dict(actual_controls=end,trace_files=self._retention_trace_files,audit=self.command_manager.get_term('twist').audit_retention(),pre_reset_roots_no_teleport=True,complete_cycles_not_claimed_from_truncated_prefixes=True),indent=2))
