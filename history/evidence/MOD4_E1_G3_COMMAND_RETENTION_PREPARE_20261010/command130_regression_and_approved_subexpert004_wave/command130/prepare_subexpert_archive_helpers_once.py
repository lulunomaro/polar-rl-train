"""Prepare new unique archive helpers; never invoke prior executed record scripts."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;M=D.parent/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010'
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 target=D/'record_subexpert004_and_command130_stage_once.py';assert not target.exists()
 s=(D/'record_matched_command_stage_once.py').read_text(encoding='utf8')
 s=replace(s,"ID='e1-command-retention-complete-review-and-matched900s-continuation'","ID='e1-terrain-subexperts-approved-wave-isolation-and-retention-regression'\nM=W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010'")
 s=s.replace('MATCHED_ARCHIVE','COMMAND130_ARCHIVE').replace('MATCHED_STAGE_GIT_RECORDED','COMMAND130_STAGE_GIT_RECORDED')
 s=replace(s,"assert json.loads((R/'COMMAND_MATCHED_TARGET_CPU_ADMITTED.json').read_bytes())['passed']\n assert json.loads((R/'COMMAND129_COMPLETE_RETENTION_DECISION.json').read_bytes())['continuation_admitted']","assert json.loads((R/'COMMAND130_COMPLETE_METADATA_SYNCED.json').read_bytes())['complete130_decision_synced']\n assert json.loads(sorted(R.glob('CANDIDATE_130_REVIEW_[0-9]*.json'))[-1].read_bytes())['review_complete']\n assert json.loads((M/'reports/REVISION_APPROVED.json').read_bytes())['approved']\n assert json.loads((M/'reports/WAVE_TARGET_CPU_ADMITTED.json').read_bytes())['passed']\n assert json.loads((M/'reports/WAVE_DISPATCH_ACTUAL_RECEIPT.json').read_bytes())['only_new_isolated_wave_entry']")
 s=replace(s,"'trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair']","'trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair','trial-20261010-e1-command-retention-complete-review-and-matched900s-continuation']")
 s=replace(s,"'matched129_to900s_continuation'","'command130_regression_and_approved_subexpert004_wave'")
 s=replace(s,"((D,'stage'),)","((D,'command130'),(M,'subexpert004'))")
 s=replace(s,"for p in sorted(R.glob('CANDIDATE_129_COLLECTED_*.json')):","for p in sorted([*R.glob('CANDIDATE_129_COLLECTED_*.json'),*R.glob('CANDIDATE_130_COLLECTED_*.json')]):")
 s=replace(s,"idx=dest/'REPORT_CAPTURE_INDEX.json';", "for p in sorted((M/'reports').glob('WAVE_ACTUAL_*.json')):\n  large.extend(json.loads(p.read_bytes()).get('large_originals_index_only',[]))\n idx=dest/'REPORT_CAPTURE_INDEX.json';")
 s=replace(s,"'Record E1 command retention complete matched review and bounded same-scope continuation'","'Record approved terrain subexpert split, isolated Wave execution and full retention regression'")
 s=replace(s,"'--kind','training'","'--kind','deployment'")
 s=replace(s,"str(R/'COMMAND129_COMPLETE_REPORT.md')","str(M/'reports/MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md')")
 start=s.index("'--validation',")+len("'--validation',");end=s.index(",'--push']",start)
 s=s[:start]+repr('130 all4 actualcomplete/errorfree and direct129 selectedsource matched fullroot30q/parameters/ground-contact-COMlink/6000callbacks/signedcircles; terrain24to25of27 reverse27of27 ordinary0 while negative4pi7to1of8 world63to59of64 maxcross.074235078; allfalse rawcost2validuncompletedprefixes retained; actualoldstraightworld8.2599802percentcoverage, no pure and no causalclaim; persistentlockfile guard pre-CAS rejection retained and independent realOSlock repair actualsynced; V3pureCPU candidate unused notphysicalfailure; human explicitly approved finer Wave Curb Slope Stair experts in revision004 with historical master preserved; new366 all365sourcebytes plusone independent expert controller, complete129source3643c97 CPU102 and17actualcopytensors separated; actualnewWave300s dispatched same35mm sameconditionedcommands exactsame-scope contracts reused noSDK native PPOpreflight clock replay; fullCUDArestore and ownfullsave actualreceipts govern final and131behavior remains independent; E0frozen gateuntrained hardtop1 unchanged nootherexpert overwrite; allnewreports/errors/monitor/approval/sync/reader/source and largeindices Gitaccounted; no budgetextension oldonce replay S8 teacher or permanentclaim')+s[end:]
 s=replace(s,"original_two_tags_unchanged=True","original_five_tags_unchanged=True")
 ast.parse(s);target.write_bytes(s.encode())
 # The single ordinary post-stage supplement captures the stage receipt and
 # new final/source/monitor snapshots without creating another trial tag.
 target=D/'capture_subexpert004_final_supplement_once.py';assert not target.exists()
 s=(D/'capture_final_command_supplement_once.py').read_text(encoding='utf8')
 s=replace(s,"E='/home/egde/rl_candidates", "M=W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010'\nE='/home/egde/rl_candidates")
 s=s.replace('MATCHED_STAGE_GIT_RECORDED','COMMAND130_STAGE_GIT_RECORDED').replace('COMMAND_FINAL_SUPPLEMENT','SUBEXPERT004_FINAL_SUPPLEMENT').replace('COMMAND_FINAL_PUSH_ERROR','SUBEXPERT004_FINAL_PUSH_ERROR')
 s=replace(s,"'E1-G3-COMMAND-MATCHED-900S-POST-STAGE-REPORTS-01'","'E1-SUBEXPERT004-POST-STAGE-REPORTS-01'")
 s=replace(s,"'final_formal_and_monitor_supplement'","'subexpert004_final_and_monitor_supplement'")
 s=replace(s,"for p in sorted(D.rglob('*')):","for p in sorted([*D.rglob('*'),*M.rglob('*')]):")
 s=replace(s,"out=dest/'post_stage'/p.relative_to(D)","out=dest/'post_stage'/('command130' if p.is_relative_to(D) else 'subexpert004')/p.relative_to(D if p.is_relative_to(D) else M)")
 s=replace(s,"assert new\n index", "for q in (M/'reports').glob('WAVE_ACTUAL_*.json'):\n  index['large_originals_index_only'].extend(json.loads(q.read_bytes()).get('large_originals_index_only',[]))\n assert new\n index")
 s=replace(s,"'Record command retention actual fullsave, preserved refusals, raw indices and monitor receipts'","'Record isolated Wave final receipts, expert plan and monitoring with retained regression evidence'")
 s=replace(s,"('STAGE_GIT_RECORDED.json','EPISODE_STAGE_GIT_RECORDED.json')","('STAGE_GIT_RECORDED.json','EPISODE_STAGE_GIT_RECORDED.json','MATCHED_STAGE_GIT_RECORDED.json')")
 s=s.replace('own_source365_formal_final_and_actual130_partial_review=True','approved_subexpert004_wave_actual_final_and_full130_review=True')
 ast.parse(s);target.write_bytes(s.encode())
 print('Prepared new unique stage and ordinary supplement; no previous record or training replay')
if __name__=='__main__':main()
