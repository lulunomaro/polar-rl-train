"""Ordinary saved-text acceptance and E3 numerical/source supplement; no new tag."""
from pathlib import Path
import json,runpy,subprocess,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/"polar-rl-train";L=T/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027";R=S/"reports"
ID="mod4-native111-coherent-reward-frozen-motion-wm-diagnostic112"
old=runpy.run_path(str(S/"archive_E0_full1000_after112_ORDINARY_once.py"),run_name="definitions_only");s=old["s"]
for a,b in [("ordinary_E0_full1000_and_final_source_supplements","ordinary_E0_acceptance_review_E3_reset34_numerics"),("E0_FULL1000_ORDINARY_GIT_NOTE.md","E0_REVIEW_E3_NUMERICS_ORDINARY_GIT_NOTE.md"),("E0_FULL1000_ORDINARY_CAPTURE_STARTED_ACTUAL.json","E0_REVIEW_E3_NUMERICS_ORDINARY_CAPTURE_STARTED_ACTUAL.json")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
ns=dict(__name__="ordinary_final_reviews_definitions_only",__file__=old["ns"]["__file__"],same_sha_entries={});exec(compile(s,ns["__file__"],"exec"),ns)
def git(*args,input=None):
 p=subprocess.run(["git","-c","http.sslBackend=openssl","-C",str(G),*args],input=input,capture_output=True)
 assert p.returncode==0,p.stderr.decode("utf8","replace")
 return p.stdout.decode("utf8").rstrip("\r\n")
ns["git"]=git
def main():
 assert git("rev-parse","HEAD")=="97567c285477e14597573fc4c87d88311a63e51c" and len(git("tag","--list").splitlines())==1478 and not git("status","--porcelain")
 prior=G/("versions/20261029_"+ID)/"ordinary_E0_full1000_and_final_source_supplements/ORDINARY_CAPTURE_INDEX.json";ns["prior"](prior)
 for row in ns["prior_entries"].values():ns["same_sha_entries"].setdefault(row["SHA"],row)
 a=L/"E0_82_NEW86_FULL1000_SAVED_TEXT_ACCEPTANCE_REVIEW_20261029_V1";b=L/"E3_97_RESET34_NUMERICAL_AND_ORIGINAL_QUERY_DIAGNOSTIC_SOURCE_20261029_V1"
 assert a.is_dir() and b.is_dir()
 selection=dict(epoch=time.time(),roots=[str(S),str(a),str(b)],E0_review_INDEX_SHA="0a3d45de96850c4e490fa482777ad14684b9087b66d615ff8872b3efb54dbc1a",E3_q34_hook_INDEX_SHA="a5b47c8ac017418626b5bea6a2aae2530b7e6beafab7df21fbd12a41b7da1edc",active_new_E0_observer_SOURCE="EXPLICIT_PENDING excluded until frozen; only local exact event lifecycle analysis, no new remote/model/raw purpose.",no_new_GPU_learning_or_case=True)
 for p,h in [(a/"FROZEN_E0_FULL1000_SAVED_TEXT_REVIEW_INDEX_ACTUAL.json",selection["E0_review_INDEX_SHA"]),(b/"FROZEN_E3_Q34_NUMERICAL_AND_DIAGNOSTIC_SOURCE_INDEX_V1.json",selection["E3_q34_hook_INDEX_SHA"])]:
  import hashlib
  assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 with (R/"ORDINARY_E0_REVIEW_E3_Q34_FROZEN_SELECTION_AND_PENDING.json").open("x",encoding="utf8") as f:json.dump(selection,f,indent=2)
 note="""Ordinary supplement to consumed111/112 phases and prior completeE0 terminal supplement, no record_experiment or retag. NewE0 full1000 saved-text acceptance review,226 denominator/clock/source consistencychecks: actual sampled>=2pi moving windows progress.501780355m/s vs integratedreference.498146326, referror.016576535 only68.33percent movingexposure. Zero non-timeout and20000 originaltimeout in20s, not futurefailureprobability. Completeobservedresample-to-resample commandinstances0,60000closed events includeinitialleftcensor/resetend/windowend andpossiblezero-control records; no closed-event successrate. Originalnormalreader omittedindependentE0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl; bytes/SHAunknown, no host/raw/Gitcontentread tofillit. Model/STD/norm/17Adam unchanged,no newPPO; fullskill/WMdataset remainpending. This validates execution andobservedwindowprogress, not fullcommandacceptance.
NewnecessaryE3 q34 numerical CPU purpose was authorized from concrete actualclosure failures, afteroldresumeverified74-bank thenfallplacementusedseparate34-bank. Exactlyone producer-bound32,022,178B NPZ byte-read and selectedfour arrayreads for numerical qualification, NOT forGit/stats. All30 hardlimits valid, bothgasF32-.0171862114m withinnew400limits; sameownF32 contracttreeFK13poses/oldanchors maxclosure6.143906e-8m passesoriginal2mm.34sampled authoredsupport minima9.1956e-5..1.00005e-4m (~.092..100? exact0.091956..0.100005mm), notcooked/manifold/PhysXafterwrite. Correctambiguity inmonitorV30prose recordedV30B, originalV30retained. This excludes that narrow numerichypothesis, never provespolicyonlycause. Actualoriginalqueryobserver sourceCPU positive/negative/singlegetter/originalwriteerrorpassthrough/INVALIDnoresultchange/restorationpassed; hook SOURCE UNUSED, newcaller/targetSDK/resources/GPUadmission stillpending,no actualnewphysics.
OnlyONEexistingsequentialchild; activeE0 initialresample-constructor timing observer followup source explicitlypending/notcaptureduntilfreeze. No extraRNG/calls/oldcase mutation/2mmguardrelaxation/FP64/1umtrianglegates/newsourcepromotion. RootnextH1 actual-action WM worldX/Vx newsealedCPU-onlypurpose andthenreward-designdecision asV29/V30B; no unchangedblindlearning or speculativecheckpointstats.
All actualnewreports/source/errors/frozenhandoffs/automationreceipts retained, originalbinaryq34/PT/raw/USD/NPZ/media onlyactualpathbytesexistingproducerSHA/unknown inGit; no binarycontent/model/hostGPUread FORTHISARCHIVE. Protect1478oldobjects/peels, pushfailurecontinueexistingcommit,no newtag. PostGitverification conversationonly.
"""+json.dumps(selection,ensure_ascii=False)
 ns["run_stage"]("fudan",[S,a,b],[Path(__file__)],note,"Record E0 command coverage gaps and E3 reset-bank numerical qualification")
if __name__=="__main__":
 try:main()
 except BaseException:
  with (R/("ORDINARY_FINAL_REVIEWS_ARCHIVE_ORIGINAL_ERROR_"+str(time.time_ns())+".json")).open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),traceback=traceback.format_exc(),continue_existing_objects_no_retag=True),f,indent=2)
  raise

