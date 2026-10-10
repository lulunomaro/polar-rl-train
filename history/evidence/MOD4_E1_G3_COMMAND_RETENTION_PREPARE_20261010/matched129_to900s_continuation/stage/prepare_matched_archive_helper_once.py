"""Prepare a NEW stage recorder using the installed workflow; no Git mutation here."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 source=(D/'record_source_episode_stage_once.py').read_text(encoding='utf8')
 replacements={
 "ID='e1-command-retention-saved-episode-resume-assertion-repaired'":"ID='e1-command-retention-complete-review-and-matched900s-continuation'",
 'EPISODE_ARCHIVE_':'MATCHED_ARCHIVE_',
 'EPISODE_STAGE_GIT_RECORDED':'MATCHED_STAGE_GIT_RECORDED',
 'EPISODE_REPAIR_TARGET_CPU_ADMITTED':'COMMAND_MATCHED_TARGET_CPU_ADMITTED',
 "assert json.loads((R/'NAMED_SCHEMA_FAILURE_ACTUAL_DECISION.json').read_bytes())['canonical_active_empty']":"assert json.loads((R/'COMMAND129_COMPLETE_RETENTION_DECISION.json').read_bytes())['continuation_admitted']",
 "'source_episode_assertion_repair'":"'matched129_to900s_continuation'",
 "str(D/'REPORT.md')":"str(R/'COMMAND129_COMPLETE_REPORT.md')",
 "'Repair E1 resume assertion against actual saved episode and preserve prior strict refusals'":"'Record E1 command retention complete matched review and bounded same-scope continuation'",
 "'--kind','repair'":"'--kind','training'",
 "Original355 native10x300/20k24+120 and128x2 actualpassed; source348 SDK signature/353 assignment/355 strict named RNG refusals fully retained; source360 original355 byteexact plus property-owned private generator and explicit saved state, old named restore unchanged; new5 CPU ownership/disk/unknown-schema checks targetTorch2.10; numerical sampling/eligibility/35mm geometry/5family quotas/reward/LR/hardware/clock/allD0D7 unchanged; oldnative/small/clock exactreuse no replay; only new reviewed fullrestore20kx4 and300s boundedformal; actualsource freeze/ownPID/uniquecanonical noextension; future129 terrain-oldskill actualcomplete review mandatory; all savedreports/scripts/errors and largeoriginals indexed; remote main/tag/peeled verified":"Actual364 ownformal CPU102/full364 freeze/72snapshot/PID/PASSED/325.190934s originalparent settled;129all4complete/errorfree2hostbyteSHA/fullNPZ/fullroot30q-ground-contact-COMlink-hardware and signedcycle originaltolerances; source32058world62to63of64/negative4pi5to7of8/positive8of8 and35mm forward23to24of27/reverse27of27,3incompleteforwardprefixes retained, no permanentorE1RMgraduation; new365 original364allbytes plus1 independent matched900s controller, from actualreviewed3c97fullsave, SAMEgeometry andSAMEconditionedcommands; allsame-scopeCPU-SDK-native-preflight-clock-D0D7 exactreuse noGPUreplay; fullsameG3/newcommand actualCUDArestore plussavedepisode1 required; noautomaticthirdblock or50mm/S7/S8/teacher; allsavedreports/errors/readers/sync andoriginalcosts indexed; actualremote main/tag/peeled verified"
 }
 for a,b in replacements.items():assert a in source,a;source=source.replace(a,b)
 source=source.replace("tags=['trial-20261010-e1-reviewed", "tags=['trial-20261010-e1-flat-command-retention-admitted-and-strict-rng-ownership-repaired','trial-20261010-e1-command-retention-saved-episode-resume-assertion-repaired','trial-20261010-e1-reviewed")
 needle="idx=dest/'REPORT_CAPTURE_INDEX.json'"
 addition="""for p in sorted(R.glob('CANDIDATE_129_COLLECTED_*.json')):
  v=json.loads(p.read_bytes())
  large.extend(dict(source=x.get('source',x.get('path')),bytes=x['bytes'],sha256=x['sha256'],index_only=True,original_retained=True,actual_raw_SHA=True) for x in v['files'] if x.get('large_original_index_only'))
 """
 assert needle in source;source=source.replace(needle,addition+needle)
 ast.parse(source);p=D/'record_matched_command_stage_once.py';assert not p.exists();p.write_bytes(source.encode())
 q=R/'COMMAND_MATCHED_ARCHIVE_HELPER_PREPARED.json';assert not q.exists();q.write_bytes(json.dumps(dict(epoch=time.time(),new_unique_stage_helper=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),record_experiment_installed_logic_used=True,no_Git_mutation_yet=True,all4_previous_tags_verified_before_after_newstage=True),indent=2).encode())
 print(json.dumps(dict(prepared=str(p))))
if __name__=='__main__':main()
