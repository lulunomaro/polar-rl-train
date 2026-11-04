"""Prepare five unused export/evaluation entries; producer frontdoor shared exactly."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent
folder='source_fudan_frozen_native_eval_v5_lowheightgate';parents='source_fudan_frozen_parent_v5_lowheightgate'
frozen=D/folder/'frozen_sequence_mean.py';digest=hashlib.sha256(frozen.read_bytes()).hexdigest()
overlay=(D/'source_task_runtime_v3_lowheightgate/e3_fudan_task_runtime_v1.py').read_bytes();sha=hashlib.sha256(overlay).hexdigest();size=len(overlay)
old_branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8';old_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8'
OLD_MEAN_SHA='b183b7d3b0e168220ffdbdfb9d25187266ee8e62e9b289ce41af59ebc405ea0f';OLD_OVERLAY_SHA='386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2'
BAD='246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2'
names=('stage_fudan_heightgate_frozen_original_once.py','export_fudan_heightgate_pi_for_mujoco_once.py','dispatch_fudan_heightgate_frozen_original_once.py','collect_fudan_heightgate_frozen_original_once.py','evaluate_fudan_heightgate_pi_mujoco31_lowrise_once.py')
assert all(not(D/n).exists()for n in names);result={}
s=(D/'stage_fudan_fresh1cd_frozen_original_once.py').read_text(encoding='utf8').replace(old_branch,old_branch+'_HEIGHTGATE').replace(old_kind,old_kind+'_heightgate').replace(OLD_OVERLAY_SHA,sha).replace('== 8571','== '+str(size)).replace('["version"] == 4','["version"] == 5').replace('version4 fresh1cd','version5 heightgate').replace('FDNFRESH1CD_FROZEN_','FDNHEIGHTGATE_FROZEN_').replace('source_fudan_frozen_native_eval_v4_fresh1cd_timeout8',folder).replace('source_fudan_frozen_parent_v4_fresh1cd_timeout8',parents).replace('SINGLE_GPU_E3_FDN_FRESH1CD_','SINGLE_GPU_E3_FDN_HEIGHTGATE_')
a='selected["sha256"] not in (MOTHER_SHA, SOURCE_4K_SHA, LEARNER_SHA, "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e")';assert s.count(a)==1;s=s.replace(a,a[:-1]+', "'+BAD+'")')
gate='''    gate = f["task_summary"]["lowheight_tracking_gate"]
    passive = f["task_summary"]["low_rollout_summary"]
    need(gate["recipe_mask"] == "recipe>=13" and gate["zero_at_height_m"] == .1781 and
         gate["full_at_height_m"] == .23 and gate["nonlow_returns_original_value"] is True and
         set(gate["terms"]) == {"track_lin_vel", "track_lin_vel_tight", "track_ang_vel"} and
         all(t["weight"] > 0 and t["height_gate_installed"] is True for t in gate["terms"].values()),
         "Actual constructed positive tracking height gate required, not defaults")
    need(passive["dtype"] == "float64" and passive["descriptive_only_not_acceptance"] is True and
         passive["samples"] == f["task_summary"]["low_envs"] * native["actual_native_policy_steps"] and
         passive["samples"] > 0 and 0 <= passive["ge023_samples"] <= passive["samples"],
         "Actual pre-reset height evidence must cover current native controls")
'''
a='    selected = dict(';assert s.count(a)==1;s=s.replace(a,gate+a);result[names[0]]=s
# Reuse current working CPU export (the previous zero-input retry prerequisite is deliberately not part of this new purpose).
t=(D/'export_fudan_fresh1cd_pi_for_mujoco_v2_once.py').read_text(encoding='utf8');tree=ast.parse(s);selected_names=('KIND','BRANCH','BASE','COUNTERS','MOTHER_SHA','SOURCE_4K_SHA','LEARNER_SHA','SOURCE_KIND','OVERLAY_SHA','TASKS');assigns={x.id:n for n in tree.body if isinstance(n,ast.Assign)for x in n.targets if isinstance(x,ast.Name)}
header='\n'.join(ast.get_source_segment(s,assigns[n])for n in selected_names)+'\nFROZEN_SOURCE_SHA = '+repr(digest)+'\nPREFIX = "FDNHEIGHTGATE_PI_ONLY_EXPORT_"\n\n'
a=t.index('KIND = ');b=t.index('# Parsed locally');t=t[:a]+header+t[b:]
start='    closed_path = Path(args.closed)';front=s[s.index(start):s.index('    # All closure validation above')];a=t.index('    prior_export=json.loads(');b=t.index('    # Every check above');t=t[:a]+front+t[b:]
t=t.replace('FDNFRESH1CD_PI_ONLY_EXPORT_V2_','FDNHEIGHTGATE_PI_ONLY_EXPORT_').replace('source_fudan_frozen_native_eval_v4_fresh1cd_timeout8',folder).replace(OLD_MEAN_SHA,digest)
a='EXCLUDED_TIMEOUT8_PATH,EXCLUDED_TIMEOUT8_SHA\n';assert t.count(a)==1;t=t.replace(a,'EXCLUDED_TIMEOUT8_PATH,EXCLUDED_TIMEOUT8_SHA,EXCLUDED_FRESH25_PATH,EXCLUDED_FRESH25_SHA\n')
a='EXCLUDED_PREVIOUS_N20000_PATH,EXCLUDED_TIMEOUT8_PATH))';assert t.count(a)==1;t=t.replace(a,'EXCLUDED_PREVIOUS_N20000_PATH,EXCLUDED_TIMEOUT8_PATH,EXCLUDED_FRESH25_PATH))')
a='EXCLUDED_PREVIOUS_N20000_SHA,EXCLUDED_TIMEOUT8_SHA),';assert t.count(a)==1;t=t.replace(a,'EXCLUDED_PREVIOUS_N20000_SHA,EXCLUDED_TIMEOUT8_SHA,EXCLUDED_FRESH25_SHA),')
assert 'prior_export=json.loads(' not in t
remote_tree=ast.parse(t);remote=next(n.value.value for n in remote_tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='REMOTE_EXPORT'for x in n.targets));rt=ast.parse(remote);compile(rt,'heightgate-pi-export-remote','exec')
# Only frozen module top-level declarations count as imports here, not dynamic source execution.
ft=ast.parse(frozen.read_text(encoding='utf8'));declared={getattr(n,'name','')for n in ft.body}|{x.id for n in ft.body if isinstance(n,ast.Assign)for x in n.targets if isinstance(x,ast.Name)}
for n in ast.walk(rt):
 if isinstance(n,ast.ImportFrom)and n.module=='frozen_sequence_mean':assert all(x.name in declared for x in n.names)
result[names[1]]=t
for old,new in(('dispatch_fudan_fresh1cd_frozen_original_once.py',names[2]),('collect_fudan_fresh1cd_frozen_original_once.py',names[3])):
 text=(D/old).read_text(encoding='utf8').replace('FDNFRESH1CD_FROZEN_','FDNHEIGHTGATE_FROZEN_').replace('fdn_fresh1cd_frozen_outer_wait.py','fdn_heightgate_frozen_outer_wait.py').replace('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD','FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE');result[new]=text
old=(D/'evaluate_fudan_fresh1cd_pi_mujoco31_lowrise_once.py').read_text(encoding='utf8');text=old.replace('source_fudan_frozen_native_eval_v4_fresh1cd_timeout8',folder).replace(OLD_MEAN_SHA,digest).replace('FDN_FRESH1CD_MUJOCO31_','FDN_HEIGHTGATE_MUJOCO31_');assert text.count("p['schema_version']==4")==1;text=text.replace("p['schema_version']==4","p['schema_version']==5")
a="'3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e')";assert text.count(a)==1;text=text.replace(a,a[:-1]+",'"+BAD+"')")
for name in('body_contact_forces','reset_pose','run_case','MotherMean'):
 assert ast.dump(next(n for n in ast.parse(old).body if getattr(n,'name',None)==name))==ast.dump(next(n for n in ast.parse(text).body if getattr(n,'name',None)==name))
result[names[4]]=text
for name,text in result.items():ast.parse(text);compile(text,name,'exec')
for name,text in result.items():(D/name).write_text(text,encoding='utf8',newline='\n')
print('Created5 unused heightgate entries: exact closed frontdoor, true module imports and V5 collector kind; original N80 resource/actualwait and nominal physics unchanged; source-only no SSH/PT/SDK/GPU/C')
