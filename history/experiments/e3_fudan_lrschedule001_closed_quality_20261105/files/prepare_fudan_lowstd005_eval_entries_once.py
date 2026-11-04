"""Prepare five unused followups with an identical actual-closed metadata frontdoor."""
from pathlib import Path
import ast,hashlib
D=Path(__file__).resolve().parent;folder='source_fudan_frozen_native_eval_v6_lowstd005';parents='source_fudan_frozen_parent_v6_lowstd005';frozen=D/folder/'frozen_sequence_mean.py';digest=hashlib.sha256(frozen.read_bytes()).hexdigest()
overlay=(D/'source_task_runtime_v4_passive_lowstd/e3_fudan_task_runtime_v1.py').read_bytes();sha=hashlib.sha256(overlay).hexdigest();size=len(overlay)
old_branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_HEIGHTGATE';branch='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005';old_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8_heightgate';kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005';old_sha='a89ff5487e76a5d7256b4cf9e60d5c7292047e3d70ca681f02d8c9900f0c4c35';old_mean='83673fd3838ad36d87ae25cef9537371e8b4909ec1582bcd783a35a6d0addff4';bad='bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2'
names=('stage_fudan_lowstd005_frozen_original_once.py','export_fudan_lowstd005_pi_for_mujoco_once.py','dispatch_fudan_lowstd005_frozen_original_once.py','collect_fudan_lowstd005_frozen_original_once.py','evaluate_fudan_lowstd005_pi_mujoco31_lowrise_once.py');assert all(not(D/n).exists()for n in names);result={}
def ns(s):return s.replace('source_fudan_frozen_native_eval_v5_lowheightgate',folder).replace('source_fudan_frozen_parent_v5_lowheightgate',parents).replace('FDNHEIGHTGATE_FROZEN_','FDNLOWSTD005_FROZEN_').replace('FDNHEIGHTGATE_PI_ONLY_EXPORT_','FDNLOWSTD005_PI_ONLY_EXPORT_').replace('FDN_HEIGHTGATE_MUJOCO31_','FDN_LOWSTD005_MUJOCO31_').replace(old_mean,digest)
s=ns((D/'stage_fudan_heightgate_frozen_original_once.py').read_text(encoding='utf8')).replace(old_branch,branch).replace(old_kind,kind).replace(old_sha,sha).replace('["version"] == 5','["version"] == 6').replace('version5 heightgate','version6 lowstd005').replace('== 12723','== '+str(size)).replace('SINGLE_GPU_E3_FDN_HEIGHTGATE_','SINGLE_GPU_E3_FDN_LOWSTD005_')
a=s.index('    gate = f["task_summary"]');b=s.index('    selected = dict(',a)
front='''    need(init["learner_config"]["initial_std"] == .05, "Actual fresh learner initial policy STD0.05 required")
    summary=f["task_summary"];tracking=summary["tracking_reward_config"];passive=summary["low_rollout_summary"];criteria=summary["low_criterion_summary"]
    need(tracking["height_gate_enabled"] is False and
         set(tracking["terms"]) == {"track_lin_vel","track_lin_vel_tight","track_ang_vel"} and
         all(t["height_gate_installed"] is False for t in tracking["terms"].values()),
         "Actual original positive tracking functions without heightgate required")
    samples=summary["low_envs"]*native["actual_native_policy_steps"]
    need(passive["dtype"] == "float64" and passive["descriptive_only_not_acceptance"] is True and
         passive["samples"] == criteria["samples"] == samples and samples>0 and
         0<=passive["ge023_samples"]<=samples, "Actual pre-reset passive sample clock required")
    criterion_names={"height_ok","upright_ok","speed_ok","angular_ok","wheels_ok","chassis_ok","joint_good"}
    need(criteria["descriptive_only_not_acceptance"] is True and set(criteria["counts"])==criterion_names and
         set(criteria["fractions"])==criterion_names and all(0<=v<=samples for v in criteria["counts"].values()) and
         all(criteria["counts"]["joint_good"]<=v for v in criteria["counts"].values()),
         "Actual seven passive criteria bounded; not acceptance or a new grader")
'''
s=s[:a]+front+s[b:];needle='"246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2") and';assert s.count(needle)==1;s=s.replace(needle,needle.replace(') and',', "'+bad+'") and'));result[names[0]]=s
# Current working export; exact new frontdoor precedes every marker/connector/input access.
t=ns((D/'export_fudan_heightgate_pi_for_mujoco_once.py').read_text(encoding='utf8'));tree=ast.parse(s);keys=('KIND','BRANCH','BASE','COUNTERS','MOTHER_SHA','SOURCE_4K_SHA','LEARNER_SHA','SOURCE_KIND','OVERLAY_SHA','TASKS');assigns={x.id:n for n in tree.body if isinstance(n,ast.Assign)for x in n.targets if isinstance(x,ast.Name)}
header='\n'.join(ast.get_source_segment(s,assigns[k])for k in keys)+'\nFROZEN_SOURCE_SHA = '+repr(digest)+'\nPREFIX = "FDNLOWSTD005_PI_ONLY_EXPORT_"\n\n';a=t.index('KIND = ');b=t.index('# Parsed locally');t=t[:a]+header+t[b:]
start='    closed_path = Path(args.closed)';front=s[s.index(start):s.index('    # All closure validation above')];a=t.index(start);b=t.index('    # Every check above');t=t[:a]+front+t[b:]
for a,b in(('EXCLUDED_FRESH25_PATH,EXCLUDED_FRESH25_SHA\n','EXCLUDED_FRESH25_PATH,EXCLUDED_FRESH25_SHA,EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_HEIGHTGATE_SHA\n'),('EXCLUDED_TIMEOUT8_PATH,EXCLUDED_FRESH25_PATH))','EXCLUDED_TIMEOUT8_PATH,EXCLUDED_FRESH25_PATH,EXCLUDED_HEIGHTGATE_PATH))'),('EXCLUDED_TIMEOUT8_SHA,EXCLUDED_FRESH25_SHA),','EXCLUDED_TIMEOUT8_SHA,EXCLUDED_FRESH25_SHA,EXCLUDED_HEIGHTGATE_SHA),')):
 assert t.count(a)==1,(a,t.count(a));t=t.replace(a,b)
rtree=ast.parse(t);remote=next(n.value.value for n in rtree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='REMOTE_EXPORT'for x in n.targets));rt=ast.parse(remote);compile(rt,'lowstd005-pi-export-remote','exec');ft=ast.parse(frozen.read_text(encoding='utf8'));declared={getattr(n,'name','')for n in ft.body}|{x.id for n in ft.body if isinstance(n,ast.Assign)for x in n.targets if isinstance(x,ast.Name)}
for n in ast.walk(rt):
 if isinstance(n,ast.ImportFrom)and n.module=='frozen_sequence_mean':assert all(x.name in declared for x in n.names)
result[names[1]]=t
for old,new in(('dispatch_fudan_heightgate_frozen_original_once.py',names[2]),('collect_fudan_heightgate_frozen_original_once.py',names[3])):
 text=ns((D/old).read_text(encoding='utf8')).replace('fdn_heightgate_frozen_outer_wait.py','fdn_lowstd005_frozen_outer_wait.py').replace('FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE','FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V6_LOWSTD005');result[new]=text
old=(D/'evaluate_fudan_heightgate_pi_mujoco31_lowrise_once.py').read_text(encoding='utf8');text=ns(old);assert text.count("p['schema_version']==5")==1;text=text.replace("p['schema_version']==5","p['schema_version']==6");needle="'246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2')";assert text.count(needle)==1;text=text.replace(needle,needle[:-1]+",'"+bad+"')")
for name in('body_contact_forces','reset_pose','run_case','MotherMean'):assert ast.dump(next(n for n in ast.parse(old).body if getattr(n,'name',None)==name))==ast.dump(next(n for n in ast.parse(text).body if getattr(n,'name',None)==name))
result[names[4]]=text
for name,text in result.items():ast.parse(text);compile(text,name,'exec')
for name,text in result.items():(D/name).write_text(text,encoding='utf8',newline='\n')
print('Created5 unused lowSTD005 entries; exact actual-closed frontdoor, correct V6 collector/import names; N80 resources/wait and four nominal case physics functions unchanged; no SSH/model/SDK/GPU/C')
