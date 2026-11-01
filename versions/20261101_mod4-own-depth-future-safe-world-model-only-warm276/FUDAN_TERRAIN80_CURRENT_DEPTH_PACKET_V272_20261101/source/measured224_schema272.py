"""New own-MOD4 measured state; no implicit missing-contact/effort defaults."""
import torch
LAYOUT={'physical73':(0,73),'contact_history18':(73,91),'applied_torque30':(91,121),'old_processed_targets6':(121,127),'L02':(127,129),'theta2':(129,131),'BODY_contact31x3_div400':(131,224)}
def pack224(root_local_wxyz,q,dq,history,torque30,old_targets6,L0,theta,contact_BODY):
 values=(root_local_wxyz,q,dq,history,torque30,old_targets6,L0,theta,contact_BODY)
 n=root_local_wxyz.shape[0];tails=((13,),(30,),(30,),(3,2,3),(30,),(6,),(2,),(2,),(31,3))
 for v,tail in zip(values,tails):
  if not torch.is_tensor(v)or v.shape!=(n,*tail)or v.dtype!=torch.float32 or not torch.isfinite(v).all():raise ValueError('Incomplete measured state224 field '+str(tail))
  if v.device!=root_local_wxyz.device:raise ValueError('Mixed state devices')
 return torch.cat([v.flatten(1)if i!=8 else v.flatten(1)/400. for i,v in enumerate(values)],-1).detach().clone()
def validate_transition(row,*,previous_tick=None,synthetic=False):
 expected='SYNTHETIC_CPU_SCHEMA_ONLY'if synthetic else'ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER'
 if row['producer_kind']!=expected or row['plant']!='own_MOD4_live_USD':raise ValueError('Wrong producer')
 if not all(row.get(k)for k in('run_id','generation','source_admission_SHA')):raise ValueError('Missing identity')
 if (row['physics_us'],row['physics_callbacks'],row['feedback_samples'],row['policy_us'])!=(2500,8,2,20000):raise ValueError('Wrong actual clock')
 if previous_tick is not None and row['physics_end_tick']!=previous_tick+8:raise ValueError('Skipped/duplicate tick')
 if not 0<=row['depth_age_seconds']<=.20:raise ValueError('Future or stale depth')
 for key,width in(('s',224),('s1',224),('xi31',31),('depth9',9),('a',6)):
  v=row[key]
  if v.ndim!=2 or v.shape[-1]!=width or v.dtype!=torch.float32 or not torch.isfinite(v).all():raise ValueError('Missing measured field '+key)
 return True
