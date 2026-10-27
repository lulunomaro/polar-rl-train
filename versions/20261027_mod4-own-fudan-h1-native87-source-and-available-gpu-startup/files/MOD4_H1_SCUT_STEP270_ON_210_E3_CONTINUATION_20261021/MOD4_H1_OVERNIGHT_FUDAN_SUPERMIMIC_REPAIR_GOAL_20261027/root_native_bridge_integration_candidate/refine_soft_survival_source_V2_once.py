from pathlib import Path
import ast,json,traceback
D=Path(__file__).resolve().parent;L=D.parent
report=L/'reports/SOFT_SURVIVAL_SOURCE_REFINEMENT_V2_ACTUAL.json'
assert not report.exists()
p=D/'converted_MOD4_jump_mdp_v4.py'
try:
 old_raw=p.read_bytes()
 backup=D/'converted_MOD4_jump_mdp_v4_before_soft_temperature_and_norm_review.py.txt'
 assert backup.is_file() and backup.read_bytes()==old_raw
 s=p.read_text('utf8')
 a='pos_error=masked_mean((p-target[...,:3]).square(),mask[...,:3])'
 b='pos_error=((p-target[...,:3]).square()*mask[...,:3]).sum(-1)'
 assert s.count(a)==1;s=s.replace(a,b,1)
 a='vel_error=masked_mean((v-target[...,7:10]).square(),mask[...,7:10])'
 b='vel_error=((v-target[...,7:10]).square()*mask[...,7:10]).sum(-1)'
 assert s.count(a)==1;s=s.replace(a,b,1)
 a='return (torch.sigmoid((.12-state[0][...,2])*20)+\n                torch.sigmoid((.3-state[1][...,2,2])*10)).clamp(0,1)'
 b='height_failure=torch.sigmoid((.12-state[0][...,2])/.02)\n        tilt_failure=torch.sigmoid((.3-state[1][...,2,2])/.04)\n        return 1-(1-height_failure)*(1-tilt_failure)'
 assert s.count(a)==1;s=s.replace(a,b,1)
 s=s.replace('# Retain the original native analytic low-height/tilt surrogate. It is an\n        # approximation; original hard callback truth is logged independently.',
 '# Original absolute physical low-height/tilt thresholds, using source-style\n        # .02/.04 temperatures; actual hard callback truth remains independent.',1)
 s=s.replace("            termination='original hard callbacks unchanged; retained analytic native soft approximation',",
 "            position_and_velocity_errors='masked squared coordinate sums',\n            soft_survival=dict(height_threshold=.12,tilt_Rzz_threshold=.3,height_temperature=.02,tilt_temperature=.04),\n            termination='original hard callbacks unchanged; calibrated analytic native soft approximation',",1)
 ast.parse(s);p.write_text(s,'utf8')
 result={'passed':True,'source_only':True,'previous_failure':'Initial inline source rewrite used raw CRLF bytes with LF literal and asserted before write; originalsource preserved. Dependent first CPU test saw unchanged old source and correctly failed, original report retained. New builder uses universal-newline read and exact count checks.','original_hard_physics_and_success_changed':False,'original_source_backup':str(backup)}
except BaseException:
 result={'passed':False,'error':traceback.format_exc(),'all_partials_retained':True}
 report.write_text(json.dumps(result,indent=2),'utf8');raise
report.write_text(json.dumps(result,indent=2),'utf8');print(json.dumps(result))

