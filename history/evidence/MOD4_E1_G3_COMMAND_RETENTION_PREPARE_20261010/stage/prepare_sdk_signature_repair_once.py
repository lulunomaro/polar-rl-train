"""Preserve failed source348; create distinct SDK signature shim and frozen entries."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload';V=D/'signature_repair_payload';C=V/'isaac/mod4';C.mkdir(parents=True,exist_ok=True)
def main():
 assert not (R/'SDK_SIGNATURE_REPAIR_PREPARED.json').exists()
 wrapper='''"""Explicit installed SDK reward signature; original contribution stays zero."""
from retention_flat_runtime import configure_retention as original_configure
from retention_flat_runtime import inactive_retention_rolling
def inactive_retention_rolling_sdk(env,speed_scale=.15,yaw_min=3.5,support_weight=.25):
 return inactive_retention_rolling(env,speed_scale=speed_scale,yaw_min=yaw_min,support_weight=support_weight)
def configure_retention(cfg):
 recipe=original_configure(cfg)
 cfg.rewards.spin_contact_consistency.func=inactive_retention_rolling_sdk
 recipe['SDK_reward_signature_repair']='Explicit speed_scale,yaw_min,support_weight parameters; same zero contribution, no reward change.'
 return recipe
'''
 (C/'retention_flat_runtime_sdk_reviewed.py').write_text(wrapper,encoding='utf8')
 names=('train_e1_retention_sdk_reviewed_resume_ppo.py','train_e1_retention_sdk_reviewed_fresh_preflight_ppo.py')
 for old,new in zip(('train_e1_retention_resume_ppo.py','train_e1_retention_fresh_preflight_ppo.py'),names):
  s=(P/'isaac/mod4'/old).read_text();assert s.count('from retention_flat_runtime import configure_retention as configure_intro')==1
  s=s.replace('from retention_flat_runtime import configure_retention as configure_intro','from retention_flat_runtime_sdk_reviewed import configure_retention as configure_intro')
  insertion="    for name in "+repr(('retention_flat_runtime_sdk_reviewed.py',)+names)+":\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n"
  s=s.replace('    manifest["src_sha256"] = snapshot',insertion+'    manifest["src_sha256"] = snapshot');ast.parse(s);(C/new).write_text(s,encoding='utf8')
 s=(P/'native_e1_retention_probe.py').read_text().replace('from retention_flat_runtime import configure_retention as configure_intro','from retention_flat_runtime_sdk_reviewed import configure_retention as configure_intro');ast.parse(s);(V/'native_e1_retention_sdk_reviewed_probe.py').write_text(s,encoding='utf8')
 s=(P/'supervise_e1_command_retention_once.py').read_text()
 s=s.replace('train_e1_retention_resume_ppo.py',names[0]).replace('train_e1_retention_fresh_preflight_ppo.py',names[1]).replace('native_e1_retention_probe.py','native_e1_retention_sdk_reviewed_probe.py')
 s=s.replace("MOD4_S3_E1_G3_REVIEWED_20261010/reports/SOURCE_FREEZE.json","MOD4_S3_E1_G3_COMMAND_RETENTION_20261010/reports/SOURCE_FREEZE.json")
 s=s.replace('len(old)==338 and len(f)==338+','len(old)==348 and len(f)==348+')
 # The original fullsaved338 boundary remains necessary. Add closed failed348
 # identity checks; its SDK refusal produced no PPO segment or own checkpoint.
 old="    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')"
 assert s.count(old)==1
 extra="""    failed=Path('/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_20261010/reports')
    fs=read(failed/'E1_STATE.json');fg=read(failed/'E1_GUARDIAN_STARTED.json');fa=read(failed/'E1_ATTENTION.json')
    assert fa['active_segment'] is None and not fa['own_child_still_alive']
    for locator in (fs['owner'],fs['child'],fg):
        v=identity(locator['pid']);assert not v or v['state']=='Z' or v['start_ticks']!=locator['start_ticks']
"""
 s=s.replace(old,extra+old)
 # Keep historical entries recognized, in addition to the new unique ones.
 s=s.replace("    names={","    names={'train_e1_g3_reviewed_resume_ppo.py','train_e1_g3_fresh_preflight_ppo.py','train_e1_retention_resume_ppo.py','train_e1_retention_fresh_preflight_ppo.py',",1)
 ast.parse(s);(V/'supervise_e1_command_retention_sdk_reviewed_once.py').write_text(s,encoding='utf8')
 files={p.relative_to(V).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in V.rglob('*') if p.is_file() and '__pycache__' not in p.parts};assert len(files)==5
 report=dict(epoch=time.time(),trial_id='E1-G3-COMMAND-RETENTION-SDK-SIGNATURE-REPAIR-01',genuinely_new_command_scope=True,new_file_count=5,sha256=files,source348_retained_byteexact=True,only_SDK_explicit_callable_signature_changed=True,reward_numeric_formula_and_weights_unchanged=True,failed348_no_PPO_or_budget_charge=True,old_CPU14_state_math_evidence_exactly_reused=True,new_SDK_and_later_actuals_pending=True,new_budget_seconds=0)
 (R/'SDK_SIGNATURE_REPAIR_PREPARED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(files=5,old348_untouched=True,new_GPU_not_launched=True)))
if __name__=='__main__':main()
