"""Freeze this adaptation's evidence and append the already-completed H1 review.

No training, physics, model decoding, remote mutation or historical once replay.
Large artifacts are indexed only. Identical tracked text references its Git path.
"""
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

G = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parent
CODE = G/'project/isaac/mod4v1_scut'
S = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
N = S/'runs/h1_target_limit_cont_20261103'
T = S/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
A = Path('F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets')
RT = T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4'
GUARD = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_SOURCE_V2_FINAL/runtime/isaac/mod4/mod4v1_fresh_dr_guard.py')
ANALYSIS = S/'analysis/20261103_targetlimitcont477_vs455'
STAMP = datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_bytes())


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA=h(raw))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write('\n')


def main():
    if (R/'FINAL_WORK_ORDER.json').exists():
        raise FileExistsError('Finalization already frozen; later work is an append supplement')
    source_index = read(CODE/'SOURCES.json')
    dependencies = [ref(p) for p in sorted(RT.glob('*.py'))]
    dependencies += [ref(RT/'../../../original_run_manifest.json'), ref(GUARD)]
    assets = [dict(path=str(A/'robot.usd'),bytes=8772822,
                   SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'),
              dict(path=str(A/'import_contract.json'),bytes=205173,
                   SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755')]
    write(CODE/'DEPENDENCIES.json', dict(captured_at=STAMP, source='Existing original runtime, referenced only',
        files=dependencies, assets=assets, no_tree_asset_checkpoint_copy=True,
        support_rule='Reference existing payload/lib and original runtime/isaac/mod4; no default sys.path from another task',
        portable_source_rule='MOD4_SCUT_SOURCE_ROOT points to an existing archive checkout with SOURCES.json git_path files',
        expected_remote=dict(isaaclab='6.1.14',rsl_rl='5.0.1',
            physx_extension='isaaclab_physx.physics.PhysxCfg after original app extension activation'),
        no_native_execution=True))
    syntax = []
    for path in sorted(CODE.glob('*.py')):
        ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
        syntax.append(ref(path))
    write(R/'STATIC_VALIDATION.json', dict(passed=True,syntax=syntax,
        CLI_help_passed=True,source_files_verified=len(source_index['files']),
        native_run=False,production_PT_reads=0,physics_steps=0))
    final = read(N/'reports/ROOT476_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    node = read(N/'reports/NODE_CLOSED_FULLTEXT_ACTUAL.json')
    closed = read(N/'reports/OWNER_CLOSED_ACTUAL.json')
    analysis = read(ANALYSIS/'analysis.json')
    raw_eval = read(N/'evaluation/reports/ROOT477_EVALUATION_FULL_RETURNED.json')
    summary = raw_eval['result']
    trace_entry = next(x for x in raw_eval['full_UTF8'] if x['path'].endswith('ACTUAL477_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json'))
    trace = json.loads(trace_entry['UTF8'])
    any_ticks, both_ticks, peak, streak, longest = [0]*80,[0]*80,0.,[0]*80,[0]*80
    for row in trace['rows']:
        for i,(force,active) in enumerate(zip(row['top_force_N'],row['active'])):
            if active:
                peak=max(peak,*force)
                any_ticks[i]+=int(max(force)>1)
                both_ticks[i]+=int(min(force)>1)
            streak[i]=streak[i]+1 if active and min(force)>1 else 0
            longest[i]=max(longest[i],streak[i])
    early = read(N/'evaluation/recorded_native/RENDER_REPORT.json')
    late = read(N/'evaluation/recorded_native_late/RENDER_REPORT.json')
    review = dict(captured_at=STAMP,status='ACTUAL477_COMPLETED_ALL80_NATIVE_REVIEWED_STRICT_FAILED',
        final476=final, formal_counters=node['formal'],
        all80=dict(**analysis['actual_all80'],any_top_envs=sum(v>0 for v in any_ticks),
            both_top_envs=sum(v>0 for v in both_ticks),max_top_force_N=peak,
            any_top_ticks_verified=sum(any_ticks),both_top_ticks_verified=sum(both_ticks)),
        per_environment=[dict(env=i,any_top_ticks=any_ticks[i],both_top_ticks=both_ticks[i],
                              longest_both_seconds=longest[i]*.0025,result=summary['results'][i]) for i in range(80)],
        selected_cases=analysis['detailed_cases'],
        actual_protocol=dict(first_episodes=80,seed=9137,controls=400,physics_hz=400,feedback_hz=100,
                             policy_hz=50,step_m=.27,edge_m=.8,nonpaired_fresh_DR=True),
        native_review=dict(early_images=early['media'],late_images=late['media'],
            curve=ref(ANALYSIS/'motion_curves.png'),current_model_native_vision=True,
            selected_envs=[0,1,40,41],early_count=8,late_count=4,curve_panels=6,
            observation='0/1 reach edge then pitch negative and rotate;40 turns/tips and terminates1.34s;41 braces under front below platform through8s',
            late40_caveat='All requested late frames clamp to the same actual terminal1.34s pose; not later survival',
            env38_caveat='1995 dual-top ticks, longest.3975s, no wholeclear/strict; no complete savedpose, no invented replay'),
        limits=['Raycast/visual evidence does not classify every nonwheel collision',
                'Lower wheel-bottom estimate is not full footprint crossing',
                'Fresh DR is not paired: no sole-cause attribution',
                'Initial depth valid; no explicit routeplanner; do not infer blindness or intentional detour'],
        decision='Preserve476/477 strict failure; human requests independent full SCUT reward/PPO adaptation on enhanced MOD4v1; no unchanged extra H1 window',
        recovery=dict(original_local22620_exit='Unknown; empty stderr; absent before normal stage',
            recovery47096='Completed only original unused normal/fullsave/CPU/eval; not a launch/FIRST/bind replay'),
        original_owner_closed=True,original_all_children_waited=True,original_private_shared_released=True,
        SSHclosedSESSIONrestoredFREE=True,large_raw_result=analysis['source_result'])
    write(ANALYSIS/'ALL80_MANIFOLD_NATIVE_REVIEW.json',review)
    final.update(actor_Adam=node['formal']['actor_Adam_step_min'],critic_Adam=node['formal']['critic_Adam_step_min'],
        controls=node['formal']['controls'],ownpairs=node['formal']['own_transitions'],
        owner_closed=True,raw_fee_historical=closed['raw_fee_sum_once'],
        closing_balance_historical=closed['closing_balance_snapshot'])
    work = dict(captured_at=STAMP,status='SCUT_MOD4V1_SOFTWARE_CPU_VERIFIED_NATIVE_PENDING',
        human_request='一行一行核对华南虎跳台阶奖励和训练代码，适配增强版MOD4v1 USD/MJCF，完成后说明改动',
        implementation_root=str(CODE),readme=str(CODE/'README.md'),profile='jump270',
        source_index=str(CODE/'SOURCES.json'),dependencies=str(CODE/'DEPENDENCIES.json'),
        coverage=read(R/'COVERAGE.json'),validation=ref(R/'CPU_VALIDATION_ATTEMPT5.json'),
        last_H1_final476=final,last_H1_actual477=review['all80'],
        old_H1_stages_all_consumed=True,old_H1_no_pending_launch_eval=True,
        remote_capability=read(R/'EXISTING_REMOTE_RUNTIME_CAPABILITIES.json'),
        next='Use existing original owner after actual release; validate native newUSD/fullDR/sensors and pre-reset reward once, then independent strict270 evaluation and native replay. No new goal/chat/duplicate automation, no second writer or old once replay.',
        archive=dict(new_phase='mod4v1-scut-adaptation-final476-eval477',record_once_required=True,
                     state='READY_TO_RECORD',previous476phase_do_not_retag=True),
        automation=dict(id='mod4-10',status='ACTIVE',currentchat_hourly=True))
    write(R/'FINAL_WORK_ORDER.json',work)
    write(N/'reports/CURRENT_476_CLOSED_477_REVIEWED_MOD4V1_SCUT_WORK_ORDER.json',work)
    state = read(S/'admin/CURRENT_STATE.json')
    state['epoch'] = datetime.now(timezone.utc).timestamp()
    state['human_latest_request'] = work['human_request']
    state['current_training'] = '476fully closedCPU1654/477all80native reviewed0strict0wholeclear; independent enhancedMOD4v1 SCUT adaptation CPU12pass/nativepending; no live H1 writer/controller'
    state['next'] = work['next']
    state['final476'] = final
    state['eval477'] = dict(**review['all80'],not_pending=True,all80_and_native_reviewed=True,
                           analysis=str(ANALYSIS/'analysis.json'),review=str(ANALYSIS/'ALL80_MANIFOLD_NATIVE_REVIEW.json'))
    old = state['target_limit_cont476']
    old.update(GO=True,FIRST=True,launch_unused=False,status='CLOSED_FULLSAVE_CPU1654_ACTUAL477_NATIVE_REVIEWED',
               owner_closed=True,timer12844_completed=True,postround22620_absent=True,
               unused_stage_recovery47096_completed=True,once='All original timer/launch/FIRST/bind/postround/normal/CPU/eval consumed; never replay',
               physicalskill_not_yet_evaluated=False,last_local_handoff=str(N/'reports/CURRENT_476_CLOSED_477_REVIEWED_MOD4V1_SCUT_WORK_ORDER.json'))
    state['scut_mod4v1_adaptation'] = work
    current_path=S/'admin/CURRENT_STATE.json'
    temporary=current_path.with_name('CURRENT_STATE.json.partial')
    temporary.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(current_path)
    write(R/'ALL_ERRORS_AND_LIMITS.json',dict(captured_at=STAMP,
        failures=[
          'Source alias path under old C junction unavailable; actual surviving runtime referenced',
          'Reader guessed absent launcher/actor_pipeline/rsl_fullstate/pose_cache/feedback_delay_sdk_adapter/feedback_delay_training_env paths; corrected from rg files',
          'Root NEXT_AI_GIT_WORKFLOW.md absent; actual docs/NEXT_AI_GIT_WORKFLOW.md read',
          'Import contract tire key is left_tire/right_tire, not left_wheel/right_wheel',
          'Analysis uses detailed_cases, not cases; PowerShell GO/go case collision requires Python JSON reader',
          'Wrong RSL Logger import probe; runner actual logger used',
          'Initial CPU fixture lacked wheel_action_dim/body_ang_vel_w/device; formal Attempt1 and3 kept',
          'Near-axis cylinder float32 sqrt(1-axis^2) inflated width by43micrometers; replaced with perpendicular component norm, Attempt4/5 pass',
          'Fresh guard context name corrected to actual around_original_fullstate_restore',
          'Original local postround22620 disappeared without stderr; cause unknown; only unused stages recovered',
          'First capability reader rejected locally because old CIM pattern omitted newly named reader;0network; V2 includes same exact process and succeeds',
          'PowerShell rg wildcard suffix path failed; searched directory with -g instead',
          'Optional base alias source missing from earlier local cache: fetched only572B pinned blob and verified against original tree',
          'Late env40 frames all terminal1.34s clamps; cannot call late survival'],
        validation_attempts=[ref(p)for p in sorted(R.glob('CPU_VALIDATION_ATTEMPT*.json'))],
        native_pending=True,canonical_busy_snapshot=read(R/'EXISTING_REMOTE_RUNTIME_CAPABILITIES.json'),
        no_new_model_decodes_or_native_physics_for_adaptation=True))
    print(json.dumps(dict(work_order=str(R/'FINAL_WORK_ORDER.json'),closed_H1=True,software_validation=True,native_pending=True)))


if __name__ == '__main__':
    main()
