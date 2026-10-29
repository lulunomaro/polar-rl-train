"""NEW112 actual frozen diagnostic phase once; no original raw or model content for Git."""
from pathlib import Path
import json,runpy,subprocess,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/"polar-rl-train";N=T/"MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029";R=S/"reports"
ID="mod4-native111-coherent-reward-frozen-motion-wm-diagnostic112"
p=runpy.run_path(str(N/"archive_actual111_coherent_reward_first_learning_unique_once.py"),run_name="definitions_only")
s=p["s"]
for a,b in [("'fudan':'mod4-native-fudan270-coherent-world-reward-and-heading111'","'fudan':'"+ID+"'"),("nr=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029'/'reports'","nr=T/"+repr(S.name)+"/'reports'"),("'--kind','training'","'--kind','diagnostic'")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
a="  if suffix not in {"
assert s.count(a)==1
s=s.replace(a,"  if "+repr(S.name)+" in p.parts and 'actual_case_text' in p.parts and p.name.endswith(('ACTUAL_100HZ_CONTROLS.jsonl','ACTUAL_400HZ_31BODY_FRAMES.jsonl')):suffix='.mod4_raw_external'\n"+a,1)
ns=dict(__name__="new112_unique_capture_definitions_only",__file__=p["ns"]["__file__"],same_sha_entries={})
exec(compile(s,ns["__file__"],"exec"),ns)
def git(*args,input=None):
 q=subprocess.run(["git","-c","http.sslBackend=openssl","-C",str(G),*args],input=input,capture_output=True)
 assert q.returncode==0,q.stderr.decode("utf8","replace")
 return q.stdout.decode("utf8").rstrip("\r\n")
ns["git"]=git
def main():
 assert len(git("tag","--list").splitlines())==1477 and git("tag","--list","trial-20261029-mod4-native-fudan270-coherent-world-reward-and-heading111") and not git("status","--porcelain")
 prior=G/"versions/20261029_mod4-native-fudan270-coherent-world-reward-and-heading111/COMPLETE_FILE_CAPTURE_INDEX.json"
 ns["prior"](prior)
 for row in ns["prior_entries"].values():ns["same_sha_entries"].setdefault(row["SHA"],row)
 work=json.loads((R/"CURRENT_ACTUAL112_COHERENT_REWARD_FROZEN_MOTION_AND_NEXT_WORK_ORDER.json").read_bytes())
 note="""NEW purpose112 uses qualified111 h1 formal24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12/256235849B/global18597iter185970WM17893Pi exactly once in an own-plant fixedseed20260928 frozenmean20s N1 case. This is a separate actual physical diagnostic from111 learning, not a training window or skill success from total reward. No old107/108 model/raw was reread; no normal86 witness reread. Newsource/closed111 formalinitialCPU proof/newproducerlineage/fresh SDK/RSL/400backend/reset/preload/20s/request200..1999/private4096/newheading/norm/3opts source bindings retained. All selected source/fixture proof/original failures/full actual texts/raw paths and existing producerSHAs/derived reports are retained. Previous actual terminal is each contiguous window INPUT label; first input unknown, supported ground is not inferred from absent air. CPU synthetic source phase label and teacherforced8/32 checks are explicitly source-only. All model/norm tensors frozen, no learner/optimizer/account/GO or pseudoair reset/force/script. Exact physical270 dualwheelcross/fullfootprint/topcontact12+stable200callbacks=.5s unchanged.
Original111 training passed its declared counterexamples and targetreadback but wholecurves still showed rising total reward and declining velocity rewards withzero platform events. This motivates the NEW112 measured trajectory/command/worldheading/contact/reward/actual8and32WM comparison, not a universal reward correctness or unique WM failure assertion. Rawcontrols/400Hzbodies and anyPT/USD/NPZ/media are indexed only from existing producer metadata, never reread/hashed for Git. No host/GPU/experiment/model action for this archive; all1477 oldtagobjects/peels protected, new112 annotatedtrial once, pushfailure resumesobjects. PostGitverification conversationonly.
Authoritative actual result and boundaries:
"""+json.dumps(work,ensure_ascii=False)
 selection=json.loads((R/"ARCHIVE112_FROZEN_ROOT_SELECTION_AND_ACTUAL_STATUS.json").read_bytes())
 roots=[Path(x) for x in selection['roots']];extras=[Path(__file__),*[Path(x) for x in selection['new_N111_actual_error_report_extras']]]
 note+='\nActual E0/E3/geometry clarification and frozen-root selection:\n'+json.dumps(selection,ensure_ascii=False)
 ns["run_stage"]("fudan",roots,extras,note,"Measure qualified111 fixed20s own-plant motion and paired world model")
if __name__=="__main__":
 try:main()
 except BaseException:
  with (R/("UNIQUE112_ARCHIVE_ORIGINAL_ERROR_"+str(time.time_ns())+".json")).open("x",encoding="utf8") as f:json.dump(dict(epoch=time.time(),traceback=traceback.format_exc(),continue_existing_objects_no_rerecord_retag=True),f,indent=2)
  raise

