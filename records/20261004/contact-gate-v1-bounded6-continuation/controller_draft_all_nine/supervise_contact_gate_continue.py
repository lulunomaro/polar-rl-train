"""Explicit contact-measurement continuation; never reruns the rolling entry.

No reward, physics, hardware, DR or PPO change. Original full-time mesh gates
remain in every raw report and decision, alongside the versioned loaded gate.
"""
import argparse,json,os,subprocess,sys,time,traceback
from pathlib import Path
import supervise_rolling_repair as repair
ctl=repair.ctl;base=ctl.base;rate=ctl.rate;helpers=ctl.helpers
C=repair.D;CODE=repair.CODE;ROOT=repair.ROOT;R=repair.R
sys.path.insert(0,str(CODE))
from contact_gate import assess,VERSION as GATE_VERSION
from continuation_contract import validate as validate_evidence
J=R/'CONTACT_CONTINUATION_STATE.json'
CAL=Path('/home/egde/rl_candidates/MOD4_SPIN_CONTACT_GATE_CALIBRATION_20261004')
SOURCE=CAL/'reports/CONTACT_CALIBRATION_REVIEW.json'
read=repair.read
ctl.PROBES=tuple(ctl.PROBES)+('/contact_calibration_probe.py',)
ctl.spin.PROBES=ctl.PROBES
original_probe=ctl.probe
def phase(stage,**kw):
 x=read(J) if J.exists() else {};x.update(phase=stage,updated_epoch=time.time(),gate_version=GATE_VERSION,**kw);base.atomic_json(J,x)
 repair.phase(stage,contact_gate_version=GATE_VERSION,contact_continuation_state=str(J),**kw)
def status(stage=None,**kw):
 repair.status(stage,acceptance_version=GATE_VERSION,contact_continuation_state=str(J),original_mesh015_shadow_retained=True,**kw)
 base.status(autonomy_version='contact_gate_v1_bounded',scope='Versioned loaded-report-point slip acceptance; original full-time mesh/legacy shadows retained. Rollingv1 reward/white_v2/physics/hardware/PPO unchanged.')
ctl.status=status
def freeze_run(run):
 repair.freeze_run(run)
 p=run/'rolling_source_freeze.json';x=read(p)
 if x.get('acceptance_version')==GATE_VERSION:return
 x.update(acceptance_version=GATE_VERSION,evaluation_measurement_changed=True,only_added_contact_reward=False,
          policy_reward_same_as_rolling_v1=True,original_mesh015_shadows_retained=True)
 base.atomic_json(p,x)
rate.freeze_run=ctl.spin.freeze_run=freeze_run
def probe(ck,label,kind='spin',profile=None,seed=20261002,steps=1500):
 if kind!='spin':return original_probe(ck,label,kind,profile,seed,steps)
 ctl.idle();repair.verify();out=ctl.REPORTS/(label+'.json');assert not out.exists()
 args=[str(CODE/'contact_calibration_probe.py'),'--headless','--contact-readback','--checkpoint',str(ck),
       '--output',str(out),'--steps',str(steps),'--num_envs',str(22 if steps<1500 else 88),'--seed',str(seed),
       '--dr-profile',profile or ctl.S['profile'],'--max-rate',str(rate.current_limit())]
 p=base.spawn(args,out.with_suffix('.log'));ctl.LIVE=p
 status('frozen_contact_spin_evaluation',training_pid=None,evaluation_pid=p.pid,active_log=str(out.with_suffix('.log')),evaluation_path=str(out))
 r=base.wait_probe(p,out);ctl.LIVE=None
 status(evaluation_pid=None,latest_contact_spin_decision=assess(r),latest_spin_evaluation=ctl.spin.compact_spin(r))
 return r
ctl.probe=probe
def gate(r,kind):
 return (assess(r)['pass_'] if kind=='spin' else rate.assess(r)['eligible_for_mild_dr_trial']) and ctl.safety_veto(r)
ctl.gate=gate
def decision(ck):
 label=ctl.fresh_label('contact_assessment');flat=probe(ck,label+'_flat','flat',seed=20260927);yaw=probe(ck,label+'_rate')
 physical=gate(flat,'flat') and yaw['physical_smoke_pass'] and ctl.safety_veto(yaw)
 a=assess(yaw);passed=physical and a['pass_']
 result=dict(continue_current_rate=physical,current_rate_skill_pass=passed,acceptance_version=GATE_VERSION,
             original_rate_skill_pass=yaw['spin_skill_pass'],legacy_rate_skill_pass=yaw['spin_skill_pass_legacy_reference'],
             loaded_contact_assessment=a,original_flat_admission=rate.assess(flat),checkpoint=base.checkpoint(ck),cap=rate.current_limit(),profile='white_v2',flat_seed=20260927,rate_seed=20261002,different_protocols_not_a_paired_experiment=True)
 base.atomic_json(ctl.REPORTS/(label+'_decision.json'),result);status(latest_rate_decision=result);return physical,passed
ctl.current_decision=decision
def pairs(ck,label):
 rows=[];passed=True
 for seed in (20261002,20261003):
  for kind in ('flat','spin'):
   rs=[probe(ck,f'{label}_{kind}_{profile}_{seed}',kind,profile,seed) for profile in ('nominal','white_v2')]
   exact=all(rs[0][k]==rs[1][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
   audits=[]
   for profile,r in zip(('nominal','white_v2'),rs):
    initial=r.get('initial_parameter_audit') or r.get('mild_initial_parameters');final=r.get('final_parameter_audit') or r.get('mild_final_parameters')
    audits.append((profile=='nominal' and initial is None and final is None) or bool(initial and final and initial['actual_parameters_pass'] and final['actual_parameters_pass']))
   gs=[gate(r,kind) for r in rs];passed &= exact and all(gs) and all(audits)
   rows.append(dict(seed=seed,kind=kind,initial_root_q_exact=exact,versioned_gates=gs,actual_parameter_readbacks=audits,
                    original_spin_booleans=[r.get('spin_skill_pass') for r in rs],legacy_spin_booleans=[r.get('spin_skill_pass_legacy_reference') for r in rs]))
 receipt=dict(pass_=bool(passed),pairs=rows,checkpoint=base.checkpoint(ck),cap=rate.current_limit(),acceptance_version=GATE_VERSION,profiles=['nominal','white_v2'],real_robot_certified=False)
 base.atomic_json(ctl.REPORTS/(label+'_paired_decision.json'),receipt);return passed
def finish(ck,outcome):
 ctl.idle();label=ctl.fresh_label('contact_final')
 flat=probe(ck,label+'_flat','flat');white=probe(ck,label+'_rate');nom=probe(ck,label+'_rate_nominal',profile='nominal')
 x=dict(checkpoint=base.checkpoint(ck),cap=rate.current_limit(),profile='white_v2',acceptance_version=GATE_VERSION,
        flat=rate.assess(flat),spin_active_DR=assess(white),spin_nominal=assess(nom),
        original_spin_active_DR=ctl.spin.compact_spin(white),original_spin_nominal=ctl.spin.compact_spin(nom),
        actual_budget=base.budget_state(),outcome=outcome,target_not_assumed_achieved=True,world_spin_translation_terrain_cloud_MoE_not_deployed=True)
 base.atomic_json(ctl.REPORTS/'AUTONOMY_FINISHED.json',x);status('finished',training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=x,outcome=outcome)
def hold(m,reason):
 repair.hold(Path(m['checkpoint']),m['cap'],reason);phase('repair_hold',reason=reason,last_paired_mature=m)
def controller():
 assert not J.exists(),'Explicit continuation already began; inspect receipts, do not repeat'
 ctl.S=read(ctl.STATE_PATH);ctl.idle();repair.verify()
 helpers.acquire(ROOT/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert read(repair.J)['phase']=='repair_hold' and read(ROOT/'status.json')['stage']=='targeted_repair_hold'
 evidence=read(SOURCE);flat=read(CAL/'reports/retained_flat/RETAINED_FLAT_COMPLETED.json')
 source=evidence['source_selection']['latest6'];ck=Path(source['path']);assert base.checkpoint(ck)==source==flat['source']
 last=read(ctl.STATE_PATH)['mature'];assert last==dict(checkpoint=evidence['source_selection']['mature5']['path'],cap=5.,profile='white_v2')
 validate_evidence(evidence,flat,base.checkpoint(ck),last,GATE_VERSION,base.sha(CODE/'contact_gate.py'))
 assert ctl.S['chosen_checkpoint']==last['checkpoint'] and ctl.S['active_training'] is None
 phase('contact_gate_continuation_preflight6',source=source,last_paired_mature=last,historical_rejections=ctl.S['rate_rejected'],first_formal_policy_under_new_gate=source,original_skill_claim=False)
 owner=helpers.identity(os.getpid())
 with (C/'contact_guardian.log').open('x') as log:
  g=subprocess.Popen([base.PY,str(C/'supervise_contact_gate_continue.py'),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 base.atomic_json(R/'CONTACT_GUARDIAN_STARTED.json',helpers.identity(g.pid))
 if not repair.preflight_rate(ck,6.):hold(last,'Versioned-contact continuation6 preflight rejected; preserve exact mature5 and all new weights');return
 ctl.S['chosen_checkpoint']=str(ck);ctl.persist()
 base.atomic_json(R/'CONTACT_GATE_ACCEPTED_FOR_BOUNDED6_TRIAL.json',dict(source=source,version=GATE_VERSION,evidence=str(SOURCE),flat_regression=str(CAL/'reports/retained_flat/RETAINED_FLAT_COMPLETED.json'),old_booleans_retained=True,reward_DR_hardware_physics_PPO_unchanged=True,preflight_weights_discarded=True,not_original_mesh_gate_graduation=True))
 consecutive=1;failures=0;last_sha=source['sha256'];duration=2700
 while ctl.remaining()>120:
  phase('contact_rate_trial_or_continued',cap=rate.current_limit(),source=base.checkpoint(ck),last_paired_mature=last,consecutive=consecutive,failed_blocks=failures)
  ck=ctl.training(ck,'contact_rate_trial_or_continued',duration=min(duration,ctl.remaining()))
  phase('contact_rate_assessment',cap=rate.current_limit(),checkpoint=base.checkpoint(ck))
  physical,skilled=decision(ck);current=base.checkpoint(ck)
  if not physical:hold(last,'Physical or original-flat regression under contact-version rate learning');return
  different=current['sha256']!=last_sha;last_sha=current['sha256'];consecutive=(consecutive+int(different)) if skilled else 0;failures=0 if skilled else failures+1
  phase('contact_rate_assessed',cap=rate.current_limit(),checkpoint=current,consecutive=consecutive,failed_blocks=failures)
  if failures>=3:
   ctl.S['rate_rejected']=list(dict.fromkeys(ctl.S['rate_rejected']+[rate.current_limit()]));ctl.persist();hold(last,'Three versioned contact skill failures; preserve all policies and budget');return
  if consecutive>=2 and ctl.remaining()>3600:
   if pairs(ck,ctl.fresh_label('contact_rate_mature_multiseed')):
    last=dict(checkpoint=str(ck),cap=rate.current_limit(),profile='white_v2');ctl.S['mature']=last;ctl.persist()
    base.atomic_json(R/f'CONTACT_RATE{rate.current_limit():g}_MATURE_ACCEPTED.json',dict(checkpoint=current,cap=rate.current_limit(),profile='white_v2',acceptance_version=GATE_VERSION,two_different_formal_policies=True,two_seed_nominal_DR_pair=True,original_mesh_shadow_retained=True,real_robot_certified=False))
    target=rate.next_limit(rate.current_limit())
    if target is None:phase('target_rate_accepted',checkpoint=current);finish(ck,'Measured target4pi under versioned contact gate; original mesh shadows separately reported');return
    if target in ctl.S['rate_rejected'] or not repair.preflight_rate(ck,target):hold(last,'Next rate rejected; no repeated mature-cap PPO');return
    consecutive=0;failures=0;last_sha=None;duration=2700;continue
   consecutive=0;failures+=1
   if failures>=3:hold(last,'Repeated current-rate paired review failed; preserve budget');return
  duration=7200
 phase('budget_final_assessment',checkpoint=base.checkpoint(ck));finish(ck,'Effective canonical budget reached; report contact-version and original-mesh capabilities separately')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2,type=int);a=p.parse_args()
 if a.guardian:repair.guardian(*a.guardian);sys.exit()
 __import__('torch').set_num_threads(1);base.STATE.update(read(ROOT/'status.json'))
 try:controller()
 except BaseException:
  status('attention_required',error=traceback.format_exc(),instructions='Preserve actual children and canonical ledger; do not repeat contact continuation or old entries.');raise
