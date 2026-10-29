"""Ordinary supplement after actual112 tag: full E0 terminal, no retag or model/raw content reads."""
from pathlib import Path
import json,runpy,subprocess,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/"polar-rl-train";L=T/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027";R=S/"reports"
ID="mod4-native111-coherent-reward-frozen-motion-wm-diagnostic112"
old=runpy.run_path(str(T/"H1_NATIVE107_COHERENT20S_FROZEN_MOTION_WM_N1_V108_20261029/archive_reward_counterexample110_and_panel210_v2_failure_ordinary_once.py"),run_name="definitions_only");s=old["s"]
for a,b in [("'fudan':'mod4-native107-coherent20s-frozen-motion-wm-diagnostic108'","'fudan':'"+ID+"'"),("ordinary_reward_counterexample110_and_panel210_v2_failure","ordinary_E0_full1000_and_final_source_supplements"),("nr=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'/'native110_task_reward_contact_semantics_source_v4'/'reports'","nr=T/"+repr(S.name)+"/'reports'"),("REWARD110_AND_PANEL210_V2_ORDINARY_GIT_NOTE.md","E0_FULL1000_ORDINARY_GIT_NOTE.md"),("REWARD110_AND_PANEL210_V2_ORDINARY_CAPTURE_STARTED_ACTUAL.json","E0_FULL1000_ORDINARY_CAPTURE_STARTED_ACTUAL.json")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
a="  if suffix not in {";assert s.count(a)==1
s=s.replace(a,"  if "+repr(S.name)+" in p.parts and 'actual_case_text' in p.parts and p.name.endswith(('ACTUAL_100HZ_CONTROLS.jsonl','ACTUAL_400HZ_31BODY_FRAMES.jsonl')):suffix='.mod4_raw_external'\n"+a)
ns=dict(__name__="ordinary_E0_after112_definitions_only",__file__=old["ns"]["__file__"],same_sha_entries={});exec(compile(s,ns["__file__"],"exec"),ns)
def git(*args,input=None):
 p=subprocess.run(["git","-c","http.sslBackend=openssl","-C",str(G),*args],input=input,capture_output=True)
 assert p.returncode==0,p.stderr.decode("utf8","replace")
 return p.stdout.decode("utf8").rstrip("\r\n")
ns["git"]=git
def main():
 assert git("rev-parse","HEAD")=="a4c8bb9848dd80d29694008a945dcf9346957f85" and len(git("tag","--list").splitlines())==1478 and not git("status","--porcelain")
 assert git("rev-parse","trial-20261029-"+ID)=="7e4fd933ee7aed6fd8d31454527d67fe0bfc40a4"
 p=G/("versions/20261029_"+ID)/"COMPLETE_FILE_CAPTURE_INDEX.json";ns["prior"](p)
 for row in ns["prior_entries"].values():ns["same_sha_entries"].setdefault(row["SHA"],row)
 work=json.loads((R/"ACTUAL_NEW86_E0_V1_FULL1000_TERMINAL_ALL_OUT_AND_ACCEPTANCE_PENDING.json").read_bytes())
 assert work["actual_full1000_controls"] and work["private_EX_released"] and work["all_original_own_out"] and not work["errors"] and not work["integrity"]
 roots=[S,L/"E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1"]
 selection=R/"ORDINARY_E0_FULL1000_FROZEN_SELECTION_AND_PENDING.json"
 with selection.open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),roots=[str(x) for x in roots],active_child_E3_reset34_and_query_source="EXPLICIT_PENDING excluded until frozen. New one-NPZ-read numerical qualification purpose authorized for concrete q34 compatibility, not for stats/Git. No new remote/SDK/model authorization.",E0_saved_text_instance_review_pending=True,no_more_actual_GPU_case_or_learning=True),f,indent=2)
 note="""Ordinary supplement to consumed real112 diagnostic tag; no record_experiment, new tag, oldtrial rerun or model/host/GPU read for Git. New original E0V1 normal850 reader executed once only after original local+remote supervisor1800remaining<=900. Full20k1000controls20s/100warm900steady actually completed, no walltimepartial, originalworkerwait0/supworkerout/privateEXreleased/errors[]/integrity[]. Original actor/critic/STD/norm/17Adam641200/finalLR.00038443359375000017 literal; actual400N50Hz/native24queue alreadypassed. No optimizer/norm/PPO/accountwrite/learningGO. User-authorized old-expert qualification remains pending perprofile/complete-command-instance thresholds and coverage; exact report profile_report is a path string, original wholeUTF8 collected. Do not call20s completion or scalar errors fullskillgraduation or completeWMdataset.
All root finite handles nowreturned/globalserialSSHleasefree; no4trainingGPUsactive/permanentfree claims. E2V4full900 andE3V4full600 alreadyrecorded; E3 originalfailure340textchecks141credits/414048exposures andhugeclosure resets remainfailures, no skillpromotion. Child same one sequentialsource-only branch is auditing post-original74-reset nearest34 placement/closed-chain/limits and passive originalquery hooks; pure q34 numericalnewpurpose may readone necessaryproducer-boundNPZ, not forGit/stats, no originalcase mutation/guard relaxation. Active source excluded untilfreeze, nextordinarysupplement. Root H1 next explicit actual-action WM worldX/Vx CPUvalidation purpose needs newsource/admission/counting, not replayformalreview or modelstats. Original111/112 allphysics/rewardbadtradeoffs/failedsourcehelpers/one targetedmechanicalfrontgap purpose remainpreserved, no universalrewardcorrectness or270success.
V29 existinghourlyautomation update/noGoal duplicatedtask retained. All saved actualterminal/rootnormal/source/receipts/errors included; originalraw/PT/USD/NPZ/media onlystat/existingproducerSHA/unknown and priorfullcapture references; old148? authoritative1478tagobjects/peels unchanged. PostGitverification conversationonly.
"""+json.dumps(work,ensure_ascii=False)
 ns["run_stage"]("fudan",roots,[Path(__file__)],note,"Record complete E0 1000-control frozen evaluation and remaining acceptance gaps")
if __name__=="__main__":
 try:main()
 except BaseException:
  with (R/("ORDINARY_E0_FULL1000_ARCHIVE_ORIGINAL_ERROR_"+str(time.time_ns())+".json")).open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),traceback=traceback.format_exc(),continue_existing_commit_objects_no_retag=True),f,indent=2)
  raise

