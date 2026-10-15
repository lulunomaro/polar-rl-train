"""Record this new genuine S5 cell once; old retention trial is not retagged."""
from pathlib import Path
import importlib,json,subprocess,sys,time,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
RET=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='s4-retention-complete-s5-single-w35-first-matched-cell'
DEST=REPO/'history/evidence'/D.name/'first_original35_three_way_actual'
cap.a.FOLDERS=(RET,D)
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 assert not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 final=json.loads((R/'S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json').read_bytes());assert final['passed_actual_first_matched_three_configurations'] and not final['S5_overall_complete']
 assert json.loads((R/'S4_RETENTION_COMPLETE_S5_FIRST_CELL_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json').read_bytes())['passed']
 assert json.loads((RET/'reports/FINAL_SCOPE_V1_NATURAL_COMPLETION_AND_V2_GROUPED_COUNTS_EXACT_CPU_REVIEW.json').read_bytes())['all_actual_grouped_counts_and_continuous_metrics_exact']
 old=cap.a.gitio.refs();save('S5_FIRST_MATCHED35_STAGE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,prior_main=cap.g('rev-parse','HEAD'),oldtags=len(old),GPU_and_training_not_blocked_by_Git=True))
 note=D/'ACTUAL_S4_RETENTION_COMPLETE_AND_S5_FIRST_MATCHED35_STAGE_NOTE.txt';assert not note.exists()
 text='''Complete first S4 retention pairs and the first missing S5 single-policy original35 cell.

The original first gate source148 remains02718c with both registered frozen experts E0b109/W35b026 and originalSTD. All nine new retention cases (three gate native120 and six rule/gate full1500) are genuinely closed with source-bound fullraw/query, original physical-query1e-6/contactintegral/COMhardware and all original failed-valid-prefix reviews. Actual firstphysics rootq30, allparams, staticrecipes/assignments/capturedRNGqueues and loadedDLL identity pair exact. Rule and gate pure+/-4pi each8/8, world64/64 each, ordinary0 in all three fullpairs. Straight-1.5 meanabs error .0226493031->.0222289115, +1.5 .0399439670->.0475208387. Strict flat/spin oldfalse retained. No allskill/hardware/50/70 or unique-cause claim. Gate advantage over rule is not established merely by preserved counts. Finite12232 and launchhelper40800 actually absent; original launchreceipt naturally appeared. Nine frozen parents1320.2303178310394s are evidence, not canonical charges.

The completed data permit a limited S4 firstprototype practicalcloseout and actual S5 comparison work under the unchanged approved master812a4b. This is not a second gatePPO window. Missing single-policyA was not substituted by the older Linux WAVE143 scores from a different backend/data contract. A genuinely new namespace runs the complete original W35b026 singleA0 actor9/std only. No secondexpert or gate forward in A. Same normal35 currentcommand/previousactualclipped6 and selectedreset semantics. Single pure CPU source102float plus actual80 saved35 all6 math/caching/reset/negative tests and unchangedCPU RNG passed. Original35 physicalmain AST is identical after only declared adapter import/source metadata normalization. Actualnew targetCPU495source/sharedSDK/source binding passed; new native120/480 and full1500/6000 are independently saved and closed before full CPU/source/history/contact allprefix review. Every source/std initial-final exact; alltick CPUmean reconstructions checked with disclosed CPU-GPU numerical differences. Shared query/geometry and actual initialrootq30/all physicalparams/staticrecipes/capturedRNGqueues strict match existing ruleB and gateC before calling this cell matched.

Original EXIT_NATURAL remains missing where absent; independent wholedata+EXIT0+SimulationContextcleared+actualPIDout/sharedmsvcrtfree closure is retained alongside it. No false marker or fulltrainingDRGPUrestore claim. Single source file includes its intact originalcritic/Adam/DR/RNG on disk; only frozenactor9 executes in this evaluation. Both pair modes retain unusedcritic/emptyAdam fixture costs separately. Host chainlatency is not a hardwareboard deadline. Original expert ancestry costs are not erased or asserted equal; firstgate additional actual parent2668.750717163086s remains once charged. Allcurrent neweval0PPO/native/CPU do not touch solecanonical1188000s, sevenextensions, oldWindows pendingmatching or unknownOS tail.

CPU review V1 high-cardinality per-command repeated-mask grouping was slow. It completed naturally withoutkill/hotpatch and remains preserved; independent V2 groupedinverse/counts computes all diagnostic values exactly equal, both source/results retained. Readonly missingfilename and earlyfuture-report lookups are separately recorded, not physical faults. Original JSON/Path/schema/launchreceipt false and allunusedsource remain archived. The original retention stageb513 is not rerecorded or retagged; its later fullresults and reports are included as ordinary evidence in this new genuinely S5 stage. All sources/errors/false/rawindexes/workorders/monitor/currentreceipts captured; largePT/NPZ/USD/ZIP actualpath-size-SHA only, originals retained, credentials excluded. Later Gitreceipt requires ordinarysupplement. Pushfailure continues existingobjects, never repeatsrecord/tag/commit.

This single cell is not S5 overall completion or architecture selection. Missing singlepolicy flat/spin/world counterpart, seconddevelopmentseed/profile/combinedDR/tasktransition/switch evidence and finalheldout remain explicit. No automatic gate retraining/thirdBODY-left duration/70/S8/hardware grant. Protected Wave50f51626/26, all ancestors and E0/W35/CURB/SLOPE originals unchanged. S3 overall remains separate. Root sole sequential210/249transport after actual finitehandoff; laptopGPUpaused/Linux repairtraining authorized/3060 evaluation only. Exact consumed Tasks/leases/once never replayed. Same mod4-10 ACTIVE/hourly/target, no secondwatcher or auto budget.

Actual three-way counts, continuous means/worstenvs, all prefixes, source/inference latency and own closure are bound by the first matched-cell report below; no result inferred from a prepared package.
'''
 text+=json.dumps(dict(actual_metrics=[{k:x[k] for k in ('configuration','forward','reverse','ordinary','truncation','groups')} for x in final['metrics']],comparison_report='S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json'),indent=2)
 note.write_text(text,encoding='utf8');rows,files=cap.capture_streaming(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   x=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in args[2:]),capture_output=True,check=True);return x.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g;sys.argv=['record_experiment.py','--id',ID,'--title','Complete S4 retention and first matched S5 single-policy rule-gate cell','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','All fixednine retention actualclosed/wholephysical/source24/originalsameinitial pair reviewed; S4 limitedcloseout only. New completeW35 singleactor sourceCPU/native120/full1500 closes missing original35 singlepolicyA with same35/rootq/physicalparams/recipes/RNG/query before matched three-way comparison. Allraw/source/std/actualaction/reset originalcontact>1N before-after200mm allvalidprefixes CPU passed. No newPPO, budgets or oldGPUreplay; oldfalse/readerperformance errors preserved; same hourlymonitor actualUTF8 target verified. S5 broadermatrix and architectureselection remain pending.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 result=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_and_oldtags_verified=True,oldtags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,later_receipt_needs_ordinary_supplement=True)
 save('S5_FIRST_MATCHED35_STAGE_GIT_RECORDED_ACTUAL.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:save('S5_FIRST_MATCHED35_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),push_failure_continue_existing_objects_no_rerecord_tag_commit=True));raise
