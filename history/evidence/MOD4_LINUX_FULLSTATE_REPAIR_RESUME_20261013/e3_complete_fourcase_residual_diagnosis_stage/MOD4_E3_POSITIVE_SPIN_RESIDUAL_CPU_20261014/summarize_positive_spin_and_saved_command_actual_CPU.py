"""Independent supplement; original failed readers and raw report unchanged."""
from pathlib import Path
import json,torch,hashlib,time,numpy as np
D=Path(__file__).resolve().parent;W=D.parent
def read(p):return json.loads(p.read_bytes())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=read(D/'reports/E3_POSITIVE_4PI_ALL_PREFIX_MOTOR_CONTACT_ACTUAL_CPU_REVIEW.json')
paths={
 '2b':W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt',
 'e3':W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/0_model_32825.pt'}
states={}
for name,path in paths.items():
 ck=torch.load(path,map_location='cpu',weights_only=False)
 keys=[k for k in ck if 'COMMAND' in k or 'command' in k];rows={}
 for k in keys:
  if not isinstance(ck[k],dict):continue
  row={key:ck[k][key] for key in ('profile','num_envs','version') if key in ck[k]}
  for key in ('control_histogram','sample_histogram'):
   if key in ck[k]:row[key]=ck[k][key].tolist()
  if 'signed_yaw' in ck[k]:
   x=ck[k]['signed_yaw'];row['saved_signed_yaw_minmax']=[float(x.min()),float(x.max())];row['saved_abs_yaw_gt2_count']=int((x.abs()>2).sum());row['saved_12p566_yaw_count']=int(torch.isclose(x.abs(),torch.tensor(4*np.pi)).sum())
  if 'BODY_command' in ck[k]:
   x=ck[k]['BODY_command'];row['saved_BODY_yaw_minmax']=[float(x[:,2].min()),float(x[:,2].max())];row['saved_BODY_pure4pi_count']=int(((x[:,0]==0)&(x[:,1]==0)&torch.isclose(x[:,2].abs(),torch.tensor(4*np.pi))).sum())
  rows[k]=row
 states[name]=dict(path=str(path),bytes=path.stat().st_size,sha256=h(path),saved_command_state=rows)
def facts(kind,i):
 row=next(x for x in review[kind]['positive'] if x['env_id']==i)
 probe=read(Path(review[kind]['probe']['path']))
 keys=('left_slip','right_slip','spin_translation_speed','peak_wheel_speed_rad_s','peak_wheel_applied_torque_nm','tilt','height_error','guide_force','base_force')
 return dict(original_prefix_means={k:probe['per_environment'][k][i] for k in keys},row=row,
 actual_motor_bound_pct_CORRECTED=[v*100 for v in row['actual_motor_near_bound_1e6_pct']],
 original_raw_report_field_units_notice='actual_motor_*bound_pct in original diagnostic contains fraction 0..1, not percent; this supplement multiplies by 100 explicitly. Raw untouched.')
summary=dict(epoch=time.time(),no_SSH_GPU_PPO_budget_newcandidate=True,checkpoint_saved_command_actual=states,
 key_positive_cases={str(i):{kind:facts(kind,i) for kind in ('baseline','candidate')} for i in (51,62,73,84)},
 findings=[
  'env51 (positive 4pi sample4) continuous 15s no reset: yaw mean11.656861→.682724, yaw10..15s11.839727→.227417. Cannot attribute giant degradation to reset or mean after reset.',
  'env51 scored bothwheel1N53.03%→23.86%; wheels still spin mean[-36.86,49.24]rad/s; right actor raw>6 100%, actual right motor at bound92.31% of substeps. Coupled action/contact/traction problem observed, not proved sole cause.',
  'env73 (sample6) bad_orientation at control96; old15s mean11.964866 vs candidate46scoredcontrols mean8.420647. This is balance loss before1s, not a valid15s sustained yaw speed comparison. Left wheel0N throughout scoredprefix; max tilt42.728deg.',
  'env84 (sample7) bad_orientation at299. Oldenv62 failed68 but newenv62survives1500. All first-failure prefixes preserved.',
  'Original retained plane training command profile samples signed yaw1..2rad/s with projectedBODYtranslation; it has no pure±4pi command. Whole saved command state corroborates endpoint range; full all-episode exposure causal proof remains unknown.'
 ],
 minimal_testable_single_axis_proposal=dict(axis='training conditional command exposure only',proposal='CPU prepare an isolated explicit pure-spin retention command curriculum on already eligible physically clear plane; keep geometry, physics, DR, reward, LR, hardware, standing proportion, all non-plane commands, actor architecture and frozen evaluation unchanged. Sign-balanced tested yaw-rate progression should be separately authorized/reviewed before any executor or training; do not turn this report into a deployment.',initial_test='compare bounded low-rate pure-spin exposure versus current projected-world-only command exposure; require saved episode histogram/control trace and same initial fullstate; inspect positiveyaw balance failures and wave/straight/world regressions.',production_adopted=False,newscope_CPU_candidate_created=False,newPPO_recommended_without_admission=False),
 no_unique_cause_claim=True,no_mechanical0of8_graduation_line=True,original_absolute_yaw_tolerance_rad_s=.2,
 missing_requested_preclip_motor_torque='not captured; exact bound occupancy is not an independent proof requested torque saturation caused failure',
 original_readonly_errors_preserved=['source_freeze/sourcefreeze manifest KeyError','NumPy int64 JSON serializer TypeError','PowerShell Python -c quote SyntaxError before file write','initial source_snapshot/mod4_task path rg missing before correct frozen source lookup'])
out=D/'reports/E3_POSITIVE_SPIN_SAVED_COMMAND_SCOPE_AND_MINIMAL_AXIS_CPU_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(dict(output=str(out),saved=states),indent=2))
