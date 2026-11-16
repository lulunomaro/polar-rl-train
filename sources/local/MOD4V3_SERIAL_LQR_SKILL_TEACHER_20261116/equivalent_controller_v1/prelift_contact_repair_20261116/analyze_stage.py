from pathlib import Path
import json,sys,hashlib,ast,subprocess
import numpy as np
E=Path(__file__).resolve().parent.parent;P=Path(__file__).resolve().parent;Q=E/'motion_quality_audit_20261116';A=E/'sampled_contact_repair_20261116'
sys.path.insert(0,str(Q));from analyze_motion import source,native,metrics

def row(d):
 r=json.loads((d['path']/'RESULT.json').read_text());out=metrics(d)
 ph=d['phases'];i=int(np.flatnonzero(ph=='lift')[0]);j=max(0,i-1)
 t0=r['entry'].get('t',r['entry'].get('time'))
 mask=(d['t']>=t0)&(d['t']<d['t'][i]);capture=out['capture_s'];window=(d['t']>=d['t'][i])&(d['t']<=capture+.25)
 out.update(stable_hold_s=r.get('max_continuous_top_hold_s',r.get('top_hold_s')),
  scoring_pass=r.get('pass_teacher_stair',r.get('pass_stair')),
  prelift_pitch_peak_deg=float(np.rad2deg(np.abs(d['pitch'][mask])).max()),
  prelift_min_z_m=float(d['z'][mask].min()),
  first_lift_sample=dict(time=float(d['t'][i]),base_x=float(d['x'][i]),base_z=float(d['z'][i]),vx=float(d['vx'][i]),pitch_deg=float(np.rad2deg(d['pitch'][i]))),
  last_pre_lift_sample=dict(time=float(d['t'][j]),base_x=float(d['x'][j]),base_z=float(d['z'][j]),vx=float(d['vx'][j]),pitch_deg=float(np.rad2deg(d['pitch'][j]))),
  climb_min_vx=float(d['vx'][window].min()),
  negative_vx_duration_s=float(np.sum(d['vx'][window]<0.)*d['physics_dt' if d['name'].startswith('source') else 'control_dt']))
 return out

candidate=P/'step200_prelift_candidate_clean_center_v2'
rows=[row(source('source_reference_v047')),row(native(E/'tests/step200_capture_phaseplane_center','MOD4 baseline')),row(native(candidate,'MOD4 prelift candidate'))]
trials=[]
for root in [A,P]:
 for f in sorted(root.glob('*/RESULT.json')):
  r=json.loads(f.read_text());trials.append(dict(path=str(f.relative_to(E)),case=r['case'],scoring_pass=r.get('pass_teacher_stair',False),stable_hold_s=r.get('max_continuous_top_hold_s'),pitch_peak_deg=r.get('pitch_peak_deg'),heading_peak_deg=r.get('post_2s_heading_peak_deg'),error=r.get('error'),actor_calls=r.get('actor_calls',0),student_optimizer_steps=r.get('optimizer_steps',0),wall_seconds=r.get('wall_seconds'),phase_transitions=r.get('phase_transitions')))

base=E/'sampled_contact_repair_20261116/baseline_code'
step=(E/'sim/step_climb.py').read_text();old=(base/'sim/step_climb.py').read_text();section_marker='        self.elapsed += dt'
unchanged=dict(Cartesian_step_climb_after_idle=step[step.index(section_marker):]==old[old.index(section_marker):],native_runtime_bytes=(E/'native_runtime.py').read_bytes()==(base/'native_runtime.py').read_bytes(),native_actuation_bytes=(E/'native_actuation.py').read_bytes()==(base/'native_actuation.py').read_bytes())
ct=(E/'sim/controller.py').read_text();oc=(base/'sim/controller.py').read_text();a='            if climb_ctrl is not None:';b='        climb_capture ='
unchanged['Cartesian_controller_branch']=ct[ct.index(a):ct.index(b)]==oc[oc.index(a):oc.index(b)]
previous=np.load(P/'step200_blocked_reference_gate_center_v1/trace.npz');current=np.load(candidate/'trace.npz')
checks=dict(unchanged=unchanged,clean_reproduction_trace_exact=bool(np.array_equal(previous['trace'],current['trace'])),clean_reproduction_actions_exact=bool(np.array_equal(previous['actions'],current['actions'])),same_scene_xml_sha256=hashlib.sha256((candidate/'scene.xml').read_bytes()).hexdigest()==hashlib.sha256((E/'tests/step200_capture_phaseplane_center/scene.xml').read_bytes()).hexdigest(),scene_sha256=hashlib.sha256((candidate/'scene.xml').read_bytes()).hexdigest(),default_pointer=json.loads((E.parents[3]/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json').read_text()) if (E.parents[3]/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json').exists() else None)
assert all(unchanged.values()),checks
assert checks['clean_reproduction_trace_exact'] and checks['same_scene_xml_sha256']
report=dict(status='SINGLE_CASE_CANDIDATE_NOT_MOTION_ACCEPTED',protocol='Same 1x playback and first-contact alignment. Source actual entry 0.530 vs native 0.518; not a strict equal-speed success pair. Source is independent reproduction, not user historical replay.',rows=rows,trials=trials,checks=checks,student_optimizer_steps=0,ppo_updates=0,matrix_expanded=False,remaining=['Native pre-lift pitch still exceeds source (+2.75 vs +1.25 deg)','Native lift ingress speed remains lower than source','Native base still briefly retreats during lift/landing; positive forward source trajectory is not matched'],strict_matched_source_failure_preserved=str(Q/'source_matched_entry/RESULT.json'))
(P/'RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for r in rows:print(json.dumps({k:r[k]for k in ['name','prelift_pitch_peak_deg','pitch_peak_climb_window_deg','first_lift_sample','last_pre_lift_sample','root_x_change_lift_to_capture_m','climb_min_vx','stable_hold_s']},ensure_ascii=False))
print('checks',json.dumps(checks,ensure_ascii=False))
