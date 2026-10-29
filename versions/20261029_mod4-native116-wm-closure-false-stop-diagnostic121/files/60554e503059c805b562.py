"""Freeze completed121 numerical evidence; derived text only, no model/raw read."""
from pathlib import Path
import hashlib
import json
import time
import tomllib

T=Path(__file__).resolve().parent
S=T/'H1_NATIVE116_WM_CLOSURE_FALSE_STOP_CPU_V121_20261029'
R=S/'reports'


def read(p):
    return json.loads(Path(p).read_bytes())


def put(path,value):
    assert not path.exists(), str(path)
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))


def main():
    done=read(R/'NEW121_WM_CLOSURE_FALSE_STOP_CALIBRATION_COMPLETE_ACTUAL.json')
    binding=read(S/'PURPOSE121_TYPED_WM_CLOSURE_BINDING.json')
    assert done['passed_execution'] and done['counts']==dict(control_raw_reads=1,checkpoint_decodes=1,checkpoint_integrity_passes=1)
    assert done['actual_body_closure_cached_mismatch_count']==done['actual_q_FK_cached_mismatch_count']==0
    terminal=[]
    for h in [1,8,32]:
        report=read(R/f'NEW121_HORIZON_{h}_ALL_ACTUAL_ACTION_CLOSURE_PREDICTIONS.json')
        final=[r for r in report['rows'] if r['end_control']==431]
        assert len(final)==1
        row=final[0];last=row['steps'][-1]
        assert last['actual_cached_closure'] and not last['predicted_closure_stop']
        assert report['summary']['predicted_closure_on_cached_nonclosure_window_count']==0
        terminal.append(dict(horizon=h,start_control=row['start_control'],end_control=431,
            predicted_closure_m=last['predicted_max_closure_m'],
            actual_body_closure_m=.00223560375161469,actual_q_FK_closure_m=.002235641237348318,
            actual_original_failure_missed_by_candidate_stop=True))
    decision=dict(epoch=time.time(),phase='actual121_CPU_closure_calibration_complete',
        terminal_predictions=terminal,counts=done['counts'],all_window_summaries=done['summary'],
        original_body_anchor_vs_cached_flags_match431=True,actual_q_FK_vs_cached_flags_match431=True,
        no_predicted_closure_stop_any_1_8_32_window_in_this_case=True,
        source120_stop_rule_on_actual_failure_valid_but_insufficient_on_predicted_states=True,
        do_not_train_with_naive_source120_as_solved=True,
        candidate120_NOT_selected_as_sufficient_H1_jump_fix=True,
        latest_qualified_method_remains116=True,new_H1_learning_or_Task_GO=False,
        limits='Previously observed frozen low-flight431control case only; predicted-counterfactual versus actual errors are not a population failure classifier or proof of a unique policy cause.',
        next='Resolve learned failure prediction and valid takeoff/cross/landing process objective together. New source/typed producer/actual SDK/fullstate/reward readback/resource/single72 TaskGO required before learning.')
    put(R/'CURRENT_ACTUAL121_PREDICTED_CLOSURE_MISSED_ALL_FINAL_HORIZONS_NO_GO.json',decision)
    handoff=(
        'The human-observed stand-tall, forward charge and closure termination is not jump270 success. '
        'Source119 initial-X cue remains secondary and not selected as a jump fix.\n\n'
        'NEW121 necessary CPU diagnostic is complete and consumed. Exactly one existing118 controls read '
        '(producer f3e23d8e38c881d9401b837b290e1130b827dda616c5a3fe4ae08fa8ec3d028b,14686495B) '
        'and one qualified116h1 checkpoint decode/integrity pass were admitted after source fixtures and typed data checks. '
        'Only WM was constructed/forwarded. No Pi/Critic/optimizer/normal86/SDK/GPU/physics/SSH/account/GO. '
        'Saved116 WM and all its norm buffers remained literal; CPU Torch2.7.0+cu128 versus producer2.10/TF32 '
        'is explicit, no bitwise claim. CPU one-step saved-GPU rootZ maximum difference2.9802322388e-8m '
        'is a consistency readout, not a new physical precision gate.\n\n'
        'All431 true body-anchor classifications and true-q native FK classifications match the original cached '
        'closure flags (zero mismatches). The true final431stcontrol4.31s has2.23560375mm left-proximal closure error; '
        'the physical original2mm guard correctly terminates. Actual-q FK gives2.23564124mm. '
        'Original imagined-stop omission remains real.\n\n'
        'However, adding the original2mm predicate to predicted q-FK is insufficient: '
        'all431/424/400 eligible1/8/32 windows produce no predicted closure stop at any offset. '
        'There were zero predicted stops on actual cached nonclosure records in this single case, '
        'but all three windows ending at the true failure miss it. Their final predicted closure errors are '
        +', '.join(f"H{x['horizon']}={x['predicted_closure_m']*1000:.9f}mm" for x in terminal)
        +', each below2mm. Thus source120 catches the supplied true failure state but not these WM-predicted states. '
        'Do not present zero false-stops as successful failure prediction or readiness to train.\n\n'
        'Windows use actual executed action6 at every offset, exact normalized episode-fixed xi31, '
        'native127/dynamic54 last-processed queue state, original clocks/frames and terminal-before-reset labels. '
        'After the first actual input they are open-loop, no future actual state injection or actor action resampling. '
        'Request-off/request-on windows are partitioned; onset-crossing windows are separate. '
        'All31body pose closure, actual q-FK and predicted q-FK remain distinct. '
        'Overlapping windows are not independent trials, and this is sub-centimetre/low-flight stand-charge evidence, '
        'not27cm/general counterfactual WM accuracy or a unique causal attribution.\n\n'
        'No new learning was launched. Latest qualified native formal remains116. '
        'Next: typed closure/outcome prediction repair and a validated jump-process objective/reference. '
        'A static endpoint bonus cannot by itself enforce a takeoff history. Do not blindly add tuck, lower/relax '
        'the physical2mm threshold, cold restart, script forces or fake airborne resets. '
        'SOURCE120 is not selected as a sufficient jump fix. See NEXT_JUMP_PROCESS_ALIGNMENT_REQUIREMENTS_SOURCE_ONLY.md.\n\n'
        'This is a real new CPU diagnostic121, not a GPU training phase. Record its unique diagnostic tag once, '
        'protect1484 old tag objects/peels, preserve every source/receipt/error. Model/raw/USD/NPZ/media are '
        'path/bytes/existing producer SHA only for Git, with no binary reread. Prior119/120 ordinary supplement '
        'is already pushed at21c35f2b9120916fc253e190dde3179cd22a2a17; never replay its consumed capture. '
        'Do not rerun121 model/raw for stats or Git. After Git verification conversation only.\n')
    (S/'HANDOFF_FROZEN_ACTUAL121_WM_CLOSURE_FALSE_NEGATIVE_NO_GO.md').write_bytes(handoff.encode('utf-8'))
    next_doc='''This document is a source/design requirement, not an installed reward, payload, SDK admission or GO.

The endpoint-history counterexample is unresolved. Current116 selected optimization terms are state-based; quiet supported top placement gets the same reward for differing takeoff/cross histories. Merely enabling the old diagnostic tuck/extension terms is not a verified solution. The actual118 trajectory rises and charges with little wheel clearance, then ends on closure.

The intended trace is: approach under the real world command; physically lift both wheels with whole-body contact/clearance evidence; clear the actual270mm leading edge and full footprint; achieve original top contact12 and stable200 physics callbacks=.5s. A stand/climb path and a valid jumping path ending at the same pose must be distinguishable if the task requires jumping. Do not invent a fixed motor trajectory or use external Fudan dynamics as own truth.

Runtime signal availability must be explicit. Native127 has root/q30/dq30 and dynamic54 (wheel contact history18, torques30, last processed6); it does not contain all31body contact forces or a retained valid-takeoff latch. Wheel-force zero alone is not whole-body flight. Actual original physical counters and the newly recorded31body poses/contact snapshots are available in the diagnostic, not automatically as Markov WM state. Do not silently fabricate missing nonwheel contact, inject real future flags into imagined branches, or hide a history-dependent reward behind unchanged state semantics.

The current32control imagination is.32s, shorter than the required.5s stability period alone. Requiring the entire takeoff-to-stability trace inside each32step rollout would suppress legitimate partial progress. Any process memory, imagined-event update or phase-conditioned value design needs its own typed state/replay/normalizer/learner compatibility and counterexample audit. No state width, architecture, norm tensor, three optimizers or horizon has been changed by this document.

Before selecting a change, specify which own-plant physical events and attainable wheel-clearance/leg-geometry targets drive each phase, how that phase is carried consistently through real collection and counterfactual imagination, and how forward motion/landing remains rewarded without a stationary small-hop or moving-top reward valley. Preserve original request200..1999/20s/private4096/age_seconds and the true270 success counter. Source119 initial neutral-X cue is secondary and must not be passed off as resolving the jump process.

Required before-use cases include equal endpoints with differing valid jump histories; floor/one-wheel/low-flight contact release; lateral edge miss; supported top moving-to-quiet continuity; actual world-forward command and heading; physically attainable own-FK poses; finite gradients/bounds and source inverses; and original physical failure versus model-predicted failure. Source121 shows that simply copying the2mm hard check into imagination does not catch the observed failure because predicted q stays below it. Resolve this model/failure-boundary gap without lowering or relaxing the physical guard. Any new closure/outcome prediction or loss change must retain warm full state and have a bounded own-data admission; no blind repeat of116.

No new model/raw read, SDK, physics, remote job, source installation, Task, GO, fee or training is authorized by this design document. A new selected source must satisfy the human reward-before-use condition and existing typed source/producer, actual target SDK/fullstate, own geometry/reset/preload/reward readback, fresh light resources and single72 writer admission before a finite learning window.
'''
    (S/'NEXT_JUMP_PROCESS_ALIGNMENT_REQUIREMENTS_SOURCE_ONLY.md').write_bytes(next_doc.encode('utf-8'))
    put(S/'EXTERNAL_INPUTS_METADATA_ONLY_FOR_GIT.json',dict(
        model=dict(path=binding['formal_local_path'],bytes=binding['formal_bytes'],SHA=binding['formal_SHA'],
            provenance='existing qualified producer plus actual121 necessary integrity pass; no reread for Git'),
        controls=binding['raw_control_producer'],checkpoint_and_controls_content_excluded_from_Git=True,
        no_binary_model_or_raw_content_read_for_Git=True))

    automation_path=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
    current=tomllib.loads(automation_path.read_text(encoding='utf-8'))
    assert current['id']=='mod4-10' and current['kind']=='heartbeat' and current['status']=='ACTIVE'
    assert current['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    prefix=f'''CURRENT_ACTUAL121_WM_CLOSURE_CALIBRATION_ZERO_FALSE_STOPS_BUT_MISSED_REAL_FAILURE_ALL_HORIZONS_20261029 overrides source120-ready/pending121/119jumpfix and pre21c35Git wording. Same hourly mod4-10 ACTIVE original target; no continuousGoal/create/resume/new automation. Read actual files/toolreceipts/HEAD/index first, never replay consumed once.

FIRST READ S121/HANDOFF_FROZEN_ACTUAL121_WM_CLOSURE_FALSE_NEGATIVE_NO_GO.md and reports/CURRENT_ACTUAL121_PREDICTED_CLOSURE_MISSED_ALL_FINAL_HORIZONS_NO_GO.json, plus NEXT_JUMP_PROCESS_ALIGNMENT_REQUIREMENTS_SOURCE_ONLY.md. S121={S.as_posix()}.

NEW121 necessary CPU actual-action closure diagnostic COMPLETE/CONSUMED. Exactly one qualified116h1 whole checkpoint decode/integrity pass and one NEW118 controls read, only WM constructed/forwarded. No Pi/Critic/optimizer/normal86/SDK/GPU/physics/SSH/account/TaskGO. Source fixtures and typed raw domains preceded model load. All431 original31body-anchor and actual30q-FK classifications match recorded closure flags (0mismatch). All1/8/32 physically contiguous windows431/424/400 used actual executed6 and normalized staticxi31 at every offset, no future actual state injection or policy resampling. Same-request-phase and request-onset crossing windows separated; first input phase unknown retained.

Critical result: zero predicted closure stops anywhere in these windows, therefore zero predicted stops on actual cached nonclosure, BUT all three forecasts ending at genuine4.31s/431 closure failure miss it. Real closure2.23560375mm, actualqFK2.23564124mm; H1/H8/H32 predictions1.30721601/1.77261292/1.24487188mm, allbelow original2mm. SOURCE120 catches a supplied true failure state but does not catch these predicted states. Do not call zero false-stops successful failure prediction or GO. WM/norm literal/RNG unchanged; CPU2.7 versus originalGPU2.10 explicit, one-step rootZ CPU-GPUmax2.98e-8 is consistency only, not a new precision gate. One low-flight trajectory/overlapping windows, not27cm/generalWM qualification or unique cause.

No new H1 learning. LatestqualifiedMETHOD116 stays. Human focus remains stand-tall→charge→closure, not actual jumping. SOURCE119 neutral-X secondary NOTSELECTED as jumpfix. SOURCE120 naive hard-stop NOTSELECTED as sufficient fix. NEXT resolve learned failure/closure prediction and valid takeoff→clearance/cross→landing/stability reward/reference process. Current native127 lacks full nonwheel-contact/history latch, H32=.32s shorter than.5s recovery; do not fake signals, inject future real flags, or require whole skill inside everyH32. Freeze a new typed source design/own geometry/counterexamples before any model/data/runtime change. No blind tuck bonus/unchanged116window/coldrestart/forces/script/fakeairreset or physical2mm relaxation. Human reward-before-use and actualSDK/fullstate/reset/preload/rewardreadback/newsourceTaskGO/freshlightresource/single72 authority still required.

121 selected numerical entry run_NEW121_actual_action_WM_closure_CPU_UNUSED_once.py is CONSUMED, never reread116PT/118raw for stats/Git. All errors/source/receipts/fullUTF8 archived. Actual121CPU phaseID mod4-native116-wm-closure-false-stop-diagnostic121 fixedtag trial-20261029-mod4-native116-wm-closure-false-stop-diagnostic121 via record_experiment ONCE; actual refs/toolreceipt outrank pending. Prior ordinary119120 already pushed21c35f2b9120916fc253e190dde3179cd22a2a17/1484oldtags. Protect all old objects/peels; no retag115/116/117/118/121, pushfailure continue existing objects. New source/design-only requirement gets no separate GPU tag. Binaries model/raw/USD/NPZ/media only actualpathbytes existingproducerSHA/unknown; no binary/model/hostGPU read FORGit. PostGit conversation only, no report chasingHEAD.

3060known original viewer was OUT in V8, no restart or repeated refresh without fresh human request. Preserve existing MuJoCo user window, no auto reopen/kill. Existing old-expert child remains single/sequential/idle; no new/nested/parallel helpers or four-active-training claim. Original security, budget, ONEglobalserialSSH/freshLOCALCIM,400N/2.5msTGS32/4/F32/2mmperenv,20s/request/private4096 and true270 acceptance constraints below retained. Goal UNACHIEVED.
'''
    request=dict(mode='update',id=current['id'],kind=current['kind'],name=current['name'],
        status=current['status'],rrule=current['rrule'],targetThreadId=current['target_thread_id'],
        prompt=prefix+'\n\nPREVIOUS_SOURCE120_AND118_HISTORICAL_STATUS_ONCE_ONLY; UNOVERRIDDEN HARD CONSTRAINTS RETAINED:\n'+current['prompt'])
    put(R/'AUTOMATION_CURRENT121_UPDATE_EXACT_REQUEST.json',request)
    files=[]
    for p in sorted(S.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            b=p.read_bytes();files.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
    put(S/'FROZEN_ACTUAL121_COMPLETE_TEXT_INDEX.json',dict(epoch=time.time(),files=files,
        status='ACTUAL_CPU_COMPLETE_NO_RUNTIME_USE_NO_GO',later_app_Git_receipts_to_append=True))
    print(json.dumps(dict(passed_complete121_freeze=True,text_files=len(files),
        terminal_predictions=terminal,naive_source120_not_sufficient=True,no_new_learning=True)),flush=True)


if __name__=='__main__':
    main()
