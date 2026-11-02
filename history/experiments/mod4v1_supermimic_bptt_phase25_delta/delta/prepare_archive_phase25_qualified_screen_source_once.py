"""Build a new text-only Phase25 archive source; do not run Git/native here."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent
oldpath=R/'archive_phase24_first_quality_screen_dependency_eval_delta.py'
newpath=R/'archive_phase25_qualified_teacher_candidate_quality_screen_delta.py'
out=R/'reports/PHASE25_ARCHIVE_SOURCE_BUILD_V1.json'
assert not newpath.exists()and not out.exists()
s=oldpath.read_text(encoding='utf-8')
s=s.replace('mod4v1_supermimic_bptt_phase24_delta','mod4v1_supermimic_bptt_phase25_delta')
a="and G('rev-parse','HEAD')=='01232718ef0ae41207dc50315d1bdbdeaa1c60d9'and"
assert s.count(a)==1;s=s.replace(a,"and G('rev-parse','HEAD')=='60a5ee122fc45238d3c636383e0a2d5f71d0343e'and")
start=s.index('quality=json.loads(');end=s.index('known={}',start)
s=s[:start]+'''quality=json.loads((R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json').read_bytes())
assert quality['qualified_reference_execution']and quality['qualified_candidate_execution']and quality['decision']=='KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION'
assert quality['relative_improvement']is None and quality['matched_UID_pose_cohort']is None and quality['full_expert_pass_rate']is None and not quality['mother_checkpoint_registry_or_H1_mutated']and not quality['further_same_baseline_volume_scheduled_to_reach3000']
assert [(x['reference']['n'],x['reference']['N'],x['candidate']['n'],x['candidate']['N'])for x in quality['conditions']]==[(0,74,0,74),(19,63,10,69),(26,26,16,17)]
assert (R/'CURRENT_PROGRESS_v15_QUALIFIED_TEACHER_CANDIDATE_CLOSED_KEEP_MOTHERS.md').is_file()and(R/'QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md').is_file()
'''+s[end:]
a="('mod4v1_supermimic_bptt_phase23_delta','01232718ef0ae41207dc50315d1bdbdeaa1c60d9')]:"
assert s.count(a)==1;s=s.replace(a,"('mod4v1_supermimic_bptt_phase23_delta','01232718ef0ae41207dc50315d1bdbdeaa1c60d9'),('mod4v1_supermimic_bptt_phase24_delta','60a5ee122fc45238d3c636383e0a2d5f71d0343e')]:")
s=s.replace('unchanged_reference_existing_phase18_through23','unchanged_reference_existing_phase18_through24')
s=s.replace("prior_phase23_commit='01232718ef0ae41207dc50315d1bdbdeaa1c60d9'","prior_phase24_commit='60a5ee122fc45238d3c636383e0a2d5f71d0343e'")
s=s.replace('Later-created or changed progress, final, native reference source/seals and handoffs remain pending next append.','Late-created or changed bound-probe/microtrain source, seals, software receipts and handoffs remain pending next append; no native trial is repeated for Git.')
start=s.index("note='''");end=s.index("(D/'NOTE.md').write_text(note",start)
note='''# Phase25 — qualified original-teacher and candidate quality screen, keep mothers

Human 23:39 correction remains primary: original skill pass rate, robustness and retention, not update-count completion. The new reference and candidate are two genuine fresh purposes with successful real N80 original control loops, frozen pi/root/RMS guards, source identities, original close semantics, actual worker wait and private/global finite EX release. Original teacher additionally has independent external actual Popen.wait bound to its Python PARENT_STARTED pid. There is no retroactive pass label on the older V1 close failure.

Actual E3 requested first-episode recovery remains teacher0/74 and candidate0/74. Normal recipe12six excluded; physical termination0/6 vs6/6 is separately retained small-sample diagnostic, not replacement acceptance. W35 moving teacher19/63=30.1587%, partial190 vs candidate10/69=14.4928%, partial143. Standing teacher26/26, partial37 vs candidate16/17, partial33. Unknown0, original reset/timeout/physical termination and partial reasons retained. Same source A1 container, but reference uses frozen original pi.teacher mean without residual while candidate uses trained unbounded residual. Mother provenance is separate from storage SHA; no mother PT reopened, only full A1 cached root once for each distinct actual frozen-purpose. No learner/optimizer/N1024-to-N80 training restore.

Independent groups, single seed20260928, E3160/W351600 controls and N80; natural command cohort denominators unequal. Relative improvement/matched pose-UID-cohort/statistical regression/causal explanation and independent multi-seed full expert grade remain null or unproven. Execution qualification is not skill graduation. KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION. Mother/currentbest/H1 and original physics/DR/command/predicate unchanged. No further unchanged baseline volume scheduled merely to reach3000; goal remains active and 80/90 evidence unachieved.

Preserved prerequisite history: actual V2 first group expired original1800wait at01:54:38 with zero admission/noSDK/model/newscore, original TimeoutError/closure retained; independent read-only observer witnessed all relevant original resources clear at02:11:18 and no old parent extension or foreign signal/lockclear. New V2_ADMISSION2 builder42 source/fake tests checks exact zeroGO closure SHA plus postclosure release witness before marker/connector, but each original parent still rechecks all actual gates. Its new source14/dependency-complete stage3600 files has unchanged actor/accepted/physics/resource bytes. The teacher reference source16stage3602 includes source-producer all-state-equality proof, explicit policy variant and original AppV6->full Base dependency. Actual reference and candidate groups independently ran, all closed qualified, and each new W35 data artifact was graded once remotely with exact own producer data/schema/FINAL/SHA/drop0/UID binding. No original or old raw score was reread for a table or Git.

Actual CPU embedded-reference fixtureV1 failure remains historical; fixtureV2 actual RSL identity-norm schema0.0 math/RNG/std/residual checks passed with native0. It was not a skill claim. Native reference later established actual quality separately. Both new data grades, true external wait/controller source review, stage/dispatch/observers/errors/release witnesses, actual qualified baseline/comparison and v14/v15 handoffs are preserved point-in-time. Original teacher source/provenance no retrospective fake GPU trace. Low other GPU compute permission does not bypass canonical/private/finite locks; no new ledger/reserve extension/refund/clamp/source hotpatch or physical change.

Next stage is source-only: 1-2-role A1 LEGACY microtrain executor with actual loaded9counters+increment1..300, same whole4models4opts/replay/RNG and explicit fresh-env streamcut; original single-C/authority/private/finiteSH/RESERVE+7800/3900-3600-300/1800 preserved. Its20 new stdlib/fake-owner tests are not actual new Torch/native validation, and new worker identity is not automatically accepted by the old hard-pinned embedded-teacher producer guard. No source executor installed or enabled, no training queued. Separate NEW zero-update bound-only frozen probe source changes only effective .05*delta to .05*tanh(delta) on same learned parameters; it must be explicitly different actor/purpose and cannot be called training benefit. It is not yet native enabled. No bound/H32/reward factors mixed into legacy control, and no unproven horizon/sensor/reward root cause asserted. Later source/seals/software receipts appended after capture remain pending next archive.

This archive uses existing producer model/raw references and text-only deltas with phase18-through24 SHA references. Selected model files skipped before stat/read, raw and large binary only metadata, no selected PT/raw reopen or physical run for Git. Preserve real failures, collector errata, timeouts and partial sources, not only success. Feature-only unique annotated trial; main remains read-only and independently advancing. Goal not completed or blocked.
'''
s=s[:start]+'note='+repr(note)+'\n'+s[end:]
line=next(x for x in s.splitlines()if x.startswith("sys.argv=['record_experiment.py'"))
new="sys.argv=['record_experiment.py','--id','mod4v1-supermimic-qualified-original-teacher-candidate-screen-phase25','--title','Preserve qualified original teacher and candidate quality comparison, keep mothers and prepare outcome-first short stages','--kind','evaluation','--note-file',str(D/'NOTE.md'),'--validation','Outcome-first;qualified-ref-and-candidate-actual-wait-and-release;E3-0of74-both-normalterm0of6-vs6of6;W35-moving19of63-vs10of69-standing26of26-vs16of17-partials-exposed;independent-single-seed-no-matched-causal-claim;keep-mothers-no90-no-blindvolume;zeroGO-timeout-release-newpurpose;microtrain-and-zero-update-bound-source-only;no-modelraw-Git-reads','--files',*files]"
s=s.replace(line,new);ast.parse(s)
newpath.write_text(s,encoding='utf-8',newline='\n')
value=dict(kind='NEW_PHASE25_ARCHIVE_SOURCE_ONLY',source=str(newpath),bytes=len(s.encode()),SHA=hashlib.sha256(s.encode()).hexdigest(),previous_archive_not_replayed=True,remote_native_model_raw_or_git_operations=0)
out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
