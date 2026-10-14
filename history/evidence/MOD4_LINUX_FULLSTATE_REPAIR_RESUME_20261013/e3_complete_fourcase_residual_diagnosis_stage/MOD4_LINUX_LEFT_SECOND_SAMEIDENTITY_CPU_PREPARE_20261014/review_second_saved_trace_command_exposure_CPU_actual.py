"""Saved-command exposure CPU counts, not contact/causal or new learning proof."""
import json
import second_root_owned_transport_common_v1 as t
CODE=r'''
from pathlib import Path
import json,numpy as np,time,hashlib
R=Path(CONTEXT['proposed_root']);ready=json.loads((R/'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json').read_bytes());p=Path(ready['own_checkpoint']);meta=json.loads((p.parent/'RETENTION_COMMAND_ACTUAL.json').read_bytes());assert ready['actual_saved_updates']==191 and meta['actual_controls']==4584
hist={str(f):dict(total=0,eligible=0,standing=0,pure_yaw_positive=0,pure_yaw_negative=0,pure_positive_at_least10rad=0,pure_negative_at_most_minus10rad=0,yaw_abs_max=0.,linear_abs_max=0.) for f in range(-1,5)};counts=0;pieces=[]
for name in meta['trace_files']:
 path=p.parent/name;assert path.resolve().is_relative_to(p.parent.resolve())
 with np.load(path,allow_pickle=False) as z:
  col=z['columns'].tolist();x=z['rows'];assert x.shape[1:]==(20000,16) and np.isfinite(x).all()
  fam=x[:,:,col.index('family')];vx=x[:,:,col.index('BODY_vx')];vy=x[:,:,col.index('BODY_vy')];yaw=x[:,:,col.index('signed_yaw')];eligible=x[:,:,col.index('eligible')];pure=(abs(vx)<=1e-7)&(abs(vy)<=1e-7)&(abs(yaw)>1e-7);standing=(abs(vx)<=1e-7)&(abs(vy)<=1e-7)&(abs(yaw)<=1e-7)
  for f in range(-1,5):
   m=fam==f;v=hist[str(f)];v['total']+=int(m.sum());v['eligible']+=int((m&(eligible==1)).sum());v['standing']+=int((m&standing).sum());v['pure_yaw_positive']+=int((m&pure&(yaw>0)).sum());v['pure_yaw_negative']+=int((m&pure&(yaw<0)).sum());v['pure_positive_at_least10rad']+=int((m&pure&(yaw>=10)).sum());v['pure_negative_at_most_minus10rad']+=int((m&pure&(yaw<=-10)).sum())
   if m.any():v['yaw_abs_max']=max(v['yaw_abs_max'],float(abs(yaw[m]).max()));v['linear_abs_max']=max(v['linear_abs_max'],float(np.hypot(vx[m],vy[m]).max()))
  counts+=len(x)
 pieces.append(dict(path=str(path),bytes=path.stat().st_size))
assert counts==4584 and sum(v['total'] for v in hist.values())==91680000
print(json.dumps(dict(epoch=time.time(),passed_CPU_saved_command_counts=True,own_final_SHA=ready['checkpoint_sha256'],actual_controls=counts,total_envsteps=91680000,histogram=hist,all_saved_trace_files=pieces,commands_beforephysics_not_root_contact_causality=True,no_actor_gate_teacher_newRNG_or_learning=True,no_PPO_GPU_or_budgetwrite=True)))
'''
def main():
 c=t.connect()
 try:
  result=t.run(c,CODE,'LEFT_SECOND_COMMAND_EXPOSURE_SAVED_TRACE_CPU_ACTUAL',dict(proposed_root=t.ROOT))
  out=t.REPORTS/'LEFT_SECOND_COMPLETE_SAVED_COMMAND_EXPOSURE_CPU_ACTUAL.json';t.write_once(out,result)
  print(json.dumps(dict(report=str(out),histogram=result['histogram'],CPU_only=True)))
 finally:c.close()
if __name__=='__main__':main()
