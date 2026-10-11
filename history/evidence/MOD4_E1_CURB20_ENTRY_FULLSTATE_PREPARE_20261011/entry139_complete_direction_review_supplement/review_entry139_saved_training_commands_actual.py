"""Audit source410 saved complete command traces on CPU; never replay physics/PPO."""
from pathlib import Path
import sys,json,time,shlex,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io

def main():
 review=json.loads((R/'CURB139_FINAL_RESET_SCHEMA_REVIEW_1791709852083172200.json').read_bytes());own=review['own'];run=own['run']
 n,w=io.connect_both()
 try:
  code=r'''from pathlib import Path
import json,hashlib,time,numpy as np
P=Path(RUN);receipt=json.loads((P/'RETENTION_COMMAND_ACTUAL.json').read_bytes());files=receipt['trace_files'];assert receipt['actual_controls']==168 and receipt['pre_reset_roots_no_teleport']
H=lambda b:hashlib.sha256(b).hexdigest();rows=[];indices=[];cols=None
for name in files:
 p=P/name;b=p.read_bytes();indices.append(dict(path=str(p),bytes=len(b),sha256=H(b)))
 with np.load(p) as z:
  c=z['columns'].tolist();assert cols is None or cols==c;cols=c;rows.append(z['rows'].copy())
a=np.concatenate(rows,axis=0);assert a.shape==(168,20000,16)
assert cols==['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
assert np.isfinite(a).all();family=a[...,10].astype(int);curb=family==4;assert (curb.sum(1)==2820).all()
vx=a[...,7];vy=a[...,8];yaw=a[...,9];standing=(vx==0)&(vy==0)&(yaw==0);h=a[...,6];worldx=vx*np.cos(h)-vy*np.sin(h)
# Actual grid query is centered at (-180,-180); all9m cells have center at(...+4.5).
cx=(np.floor(a[...,0]/9)+.5)*9;dx=a[...,0]-cx;outside=np.abs(dx)>.075
approach=worldx*dx<0;leave=worldx*dx>0
assert not a[...,11][curb].any() and not a[...,12][curb].any() and not a[...,13][curb].any()
assert (np.abs(vx[curb])<=.3000001).all() and (vy[curb]==0).all() and (yaw[curb]==0).all()
signed=[]
for side,mask in [('left',dx<-.075),('right',dx>.075)]:
 m=curb&mask;move=m&~standing
 signed.append(dict(side=side,controls=int(m.sum()),positive_BODY_vx=int((move&(vx>0)).sum()),negative_BODY_vx=int((move&(vx<0)).sum()),standing=int((m&standing).sum()),toward_center_world_velocity=int((move&approach).sum()),away_from_center_world_velocity=int((move&leave).sum())))
report=dict(epoch=time.time(),trial_id='ENTRY139-SOURCE410-SAVED-CURB-COMMAND-EXPOSURE-01',run=str(P),actual_controls=168,actual_envs=20000,actual_CURB_environments_per_step=2820,trace_indices=indices,receipt=dict(path=str(P/'RETENTION_COMMAND_ACTUAL.json'),bytes=(P/'RETENTION_COMMAND_ACTUAL.json').stat().st_size,sha256=H((P/'RETENTION_COMMAND_ACTUAL.json').read_bytes())),
 CURB_controls=int(curb.sum()),CURB_positive_BODY_vx=int((curb&(vx>0)).sum()),CURB_negative_BODY_vx=int((curb&(vx<0)).sum()),CURB_standing=int((curb&standing).sum()),CURB_nonplane_retained_modes=0,CURB_yaw_command_zero_exact=True,CURB_vx_range=[float(vx[curb].min()),float(vx[curb].max())],
 actual_CURB_root_side_command_histograms=signed,ordinary_controls=int((curb&(a[...,14]!=0)).sum()),truncated_controls=int((curb&(a[...,15]!=0)).sum()),
 facts='Actual saved training has positive and negative gentle commands and standing on both world-X sides. Root-side world-X velocity toward/away from the center is reported directly; it does not certify a full curb crossing, actual contact support, or a causal source of139 direction failures.',
 all_steps_prereset_roots_no_teleport=True,no_missing_CURB_sign_coverage_claim=True,no_complete_circle_or_route_claim_from168_control_prefix=True,no_GPU_or_PPO_or_budget_actions=True)
print(json.dumps(report))
'''.replace('RUN',repr(run))
  stdin,stdout,stderr=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=90);out=stdout.read();err=stderr.read();exitcode=stdout.channel.recv_exit_status()
  assert exitcode==0,(exitcode,err.decode('utf8','replace'))
  result=json.loads(out);result['formal_own_checkpoint']=own['checkpoint'];result['selected_source_SHA']='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
  p=save('ENTRY139_SAVED_TRAINING_COMMAND_EXPOSURE_ACTUAL_REVIEW.json',result)
  print(json.dumps(dict(report=str(p),CURB_controls=result['CURB_controls'],side_histograms=result['actual_CURB_root_side_command_histograms'],no_new_training=True),ensure_ascii=True))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY139_SAVED_COMMAND_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True,no_GPU_replay=True));raise
