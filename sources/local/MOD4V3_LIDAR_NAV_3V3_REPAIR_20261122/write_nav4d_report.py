"""Publish measured acceptance and closure facts; never equate execution with graduation."""
from nav_common import HERE, put, sha256
from datetime import datetime
import json


def read(path, default=None):
    p=HERE/path
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default


def main():
    combined={}
    for part in ('cruise','ramps','stairs','jumps','missions'):
        combined.update(read(f'evidence/ACCEPTANCE_{part}.json',{}))
    combined['assembly_note']='Acceptance components were executed separately with the selected expert for each component; no test outcomes were changed during assembly.'
    put(HERE/'evidence/ACCEPTANCE_all.json',combined)
    candidate=read('CANDIDATE_NAV4D.json',{})
    stair=read('evidence/final_stairs/SUMMARY.json',{})
    jump=read('evidence/JUMP_56_AUDIT.json',{})
    perc_jump=read('evidence/PERCEPTION_JUMP_380_BRIDGE_AUDIT.json',{})
    flat=read('evidence/FLAT60_NAV4D.json',{})
    fast=read('evidence/HIGH_SPEED_NAV4D.json',{})
    ramp=read('evidence/RAMP17_NAV4D.json',{})
    missions=[read(f'evidence/MISSION_{c}.json',{}) for c in ('suite_rmul2027','suite_rmuc2027')]
    binary=read('evidence/BINARY_ARENA_AUDIT.json',[])
    core=read('evidence/LOCKED_CORE_FINAL_VERIFICATION.json',{})
    protected=read('evidence/PROTECTION_FINAL.json',{})
    donor=read('evidence/DONOR_FINAL.json',{})
    donor_static=read('evidence/DONOR_STATIC_FINAL.json',donor)
    geometry=read('evidence/RMUL2027_3V3_GEOMETRY_AUDIT.json',{})
    video=read('evidence/VIDEO_VERIFICATION.json',{})
    encoding=read('evidence/VIDEO_ENCODING_AUDIT.json',{})
    external_warp=read('evidence/EXTERNAL_WARP_STATUS.json',{})
    external_warp_final=read('evidence/EXTERNAL_WARP_FINAL_CANONICAL.json',{})
    smoke=read('evidence/SMOKE.json',{})
    ui=read('evidence/UI_SMOKE.json',{})
    interactive=read('evidence/UI_INTERACTION_PRETRAIN.json',{})
    baseline_jump=read('evidence/jump_r10_all_cpu/SUMMARY.json',{})
    selections={'stair':read('evidence/STAIR_WARP_R5_SELECTION.json',read('evidence/STAIR_WARP_R3_SELECTION.json',read('evidence/STAIR_CHECKPOINT_SELECTION.json',{}))),
                'jump':read('evidence/JUMP_CHECKPOINT_SELECTION.json',{})}
    gpu_final=read('evidence/GPU0_FINAL.json',{})
    jobs={}
    for job in ('stair_probe_r1_api2','stair_train_r1_api2','jump_probe_r2','jump_alignment_r2','jump_train_r2','stair_warp_probe_r3','stair_warp_train_r3','stair_warp_probe_r4','stair_warp_train_r4','stair_warp_probe_r5','stair_warp_train_r5','jump_warp_probe_r3','jump_warp_train_r3','jump_warp_probe_r4','jump_warp_train_r4'):
        folder='evidence/'+job+'/'
        exit_info=read(folder+'worker_EXIT.json',{})
        closed=read(folder+'SAFE_CLOSED.json',{})
        launch=read(folder+'worker_LAUNCH.json',{})
        start=read(folder+'TRAIN_START.json',{})
        error_file=HERE/folder/'ERROR.txt'
        jobs[job]=dict(exit=exit_info,closed=closed,probe=read(folder+'PROBE.json'),
            latest=read(folder+'LATEST.json'),
            launch=launch,training_start=start,final_checkpoint_metadata=read(folder+'model_final.pt.json'),
            worker_wall_elapsed_s=exit_info.get('epoch',0.)-launch.get('epoch',0.) if exit_info and launch else None,
            clean=bool(exit_info.get('exit_code')==0 and not exit_info.get('hard_kill',True)
                and exit_info.get('own_gpu_process_released') and closed.get('scene_closed')
                and not closed.get('error') and not error_file.exists()))
    single=[c for c in stair.get('cases',[]) if c['course'] in ('step_20','oblique_20','oblique_20_negative')]
    rmul=[c for c in stair.get('cases',[]) if c['course']=='suite_rmul2027' and c['lift']==.20 and 'side250' not in c['name']]
    fast_stairs=[c for c in stair.get('cases',[]) if c.get('speed',0.)>=2.4]
    invalid=[c['name'] for c in stair.get('cases',[]) if c.get('failure')=='invalid_evaluation_geometry']
    rates=dict(stair_total=dict(passed=stair.get('passed',0),total=stair.get('total',0)),
        single200=dict(passed=sum(c['passed'] for c in single),total=len(single)),
        rmul200=dict(passed=sum(c['passed'] for c in rmul),total=len(rmul)),
        highspeed_stair200=dict(passed=sum(c['passed'] for c in fast_stairs),total=len(fast_stairs)),
        stair_by_course=stair.get('by_course',{}),
        jump=dict(groups=jump.get('group_count',0),groups_liftoff=jump.get('groups_liftoff',0),
            groups_passed=jump.get('groups_passed',0),replays=jump.get('actual_replays',0),
            liftoff=jump.get('replays_liftoff',0),flips=jump.get('flips'),
            max_air_pitch_deg=jump.get('max_air_pitch_deg'),max_air_roll_deg=jump.get('max_air_roll_deg')),
        perception_jump=dict(
            rmul_bridge_270x352={k:v for k,v in perc_jump.get('rmul_bridge_270x352',{}).items() if k!='cases'},
            solid_platform_380mm={k:v for k,v in perc_jump.get('solid_platform_380mm',{}).items() if k!='cases'},
            rmul_sheer_200mm={k:v for k,v in perc_jump.get('rmul_sheer_200mm',{}).items() if k!='cases'}))
    rates['single200_by_height']={str(height):dict(passed=sum(c['passed'] for c in single if c['height']==height),
        total=sum(c['height']==height for c in single)) for height in sorted({c['height'] for c in single})}
    rates['jump_by_release']={str(release):dict(liftoff=sum(c['liftoff'] for c in jump.get('cases',[]) if c['release']==release),
        flips=sum(c['flip'] for c in jump.get('cases',[]) if c['release']==release),
        total=sum(c['release']==release for c in jump.get('cases',[]))) for release in (False,True)}
    gates=dict(geometry=bool(geometry.get('passed')),
        official_binaries=len(binary)==2 and all(r['load_under_400ms'] and r['stiffness_exact'] and r['friction_exact'] and r['physics_dt']==.0025 for r in binary),
        immutable_core=bool(core) and all(r['passed'] for r in core.values()),
        protected_assets=bool(protected.get('passed')) and bool(donor_static.get('passed')),
        gpu_clean_closure=all(j['clean'] for j in jobs.values()),
        gpu_hard_deadlines=all(jobs[name]['closed'].get('epoch',1e20)<=jobs[name]['training_start'].get('hard_stop_epoch',0.)
            for name in ('stair_train_r1_api2','jump_train_r2','stair_warp_train_r3','stair_warp_train_r4','stair_warp_train_r5','jump_warp_train_r3','jump_warp_train_r4')),
        gpu_idle_final=gpu_final.get('uuid')=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
            and gpu_final.get('memory_mib',99999)<150 and gpu_final.get('utilization_percent',100)==0,
        flat60=flat.get('passed')==60 and flat.get('total')==60 and flat.get('false_stair_ticks')==0,
        high_speed_no_false_stairs=bool(fast.get('passed')),
        ramp17_no_false_stairs=bool(ramp.get('passed')),
        single200_nonregression=bool(single) and all(c['passed'] for c in single),
        rmul200=bool(rmul) and all(c['passed'] for c in rmul),
        highspeed_stair200=bool(fast_stairs) and all(c['passed'] for c in fast_stairs),
        stair_all=bool(stair.get('total')) and stair.get('passed')==stair.get('total'),
        jump56_liftoff_zero_flips=jump.get('group_count')==56 and jump.get('groups_liftoff')==56 and jump.get('flips')==0,
        jump_level_pitch_10deg=bool(jump) and jump.get('max_air_pitch_deg',999.)<=10.,
        autonavigation=all(m.get('passed',False) for m in missions),
        smoke=bool(smoke.get('passed')),ui_smoke=bool(ui.get('passed')),
        verification_videos_1x=bool(encoding.get('passed')) and bool(video.get('stairs')) and bool(video.get('jumps'))
            and all(r['video']['video_speed']==1. for r in video.get('stairs',[])+video.get('jumps',[])))
    core_gates=('geometry','official_binaries','immutable_core','protected_assets','gpu_clean_closure',
        'gpu_hard_deadlines','gpu_idle_final','flat60','high_speed_no_false_stairs','ramp17_no_false_stairs',
        'single200_nonregression','rmul200','highspeed_stair200','jump56_liftoff_zero_flips','autonavigation','smoke','ui_smoke','verification_videos_1x')
    overall=all(gates[k] for k in core_gates)
    result=dict(status='accepted_200mm_priority_and_all_regime_jump' if overall else 'not_accepted',passed=overall,
        strict_all_auxiliary_gates=all(gates.values()),
        written_at=datetime.now().astimezone().isoformat(),priority='Stable 200 mm RMUL 3v3 stairs + All-regime zero-flip jump',
        selected_checkpoints=candidate,gates=gates,failed_gates=[k for k,v in gates.items() if not v],
        measurements=rates,missions=missions,gpu_jobs=jobs,
        final_gpu0=gpu_final,
        donor_full_inventory=donor,donor_static_integrity=donor_static,
        separately_launched_stair_warp=dict(status=external_warp,final_canonical_screen=external_warp_final,
            adopted=False,dispatched_by_this_pipeline=False),
        checkpoint_screen_counts={kind:len(s.get('all_checkpoints',[])) for kind,s in selections.items()},
        donor_jump_baseline=dict(replays=baseline_jump.get('actual_replays'),liftoff=baseline_jump.get('replays_liftoff'),flips=baseline_jump.get('flips')),
        invalid_geometry_cases=invalid,interactive_ui=interactive,
        count_note=jump.get('count_note'),
        limitations=['The original 56-case expression expands to 112 keep/release replays; group and replay counts are reported separately.',
            'RMUL side250 approaches originally requested an absent 450 mm deck. These remain explicit invalid-coverage failures.',
            'Official RMUC surveyed corridors include a 350 mm crest and 300 mm deck; ideal 400 mm double fixtures are evaluated separately.',
            'Locked stair reset distribution actually uses 0.26..0.40 m stance and 0.50..2.15 m/s commands; requested wider limits are evaluated on CPU.',
            'The locked jump GPU environment smooths command perturbations with /12; the raw CPU operator-release matrix applies abrupt commands. No external smoothing or command latch was added to hide this distribution difference.',
            'The human jump matrix is evaluated on flat road. GPU 200 mm platform training counters are not independent platform-jump acceptance.',
            'An initial final RMUC binary timing under concurrent work reached 0.4016 s; the retained idle recheck measured 0.2856..0.3435 s. Both measurements are preserved.',
            'Physical held-W input was not reproduced by the short-tap desktop automation; native Space, focus in both windows, map-click and path rendering were observed.'])
    if donor.get('changed'):
        result['limitations'].append('The separate pre-existing manual-player process updates donor PLAYER_LIVE_STATUS.json. The full-inventory difference is retained in DONOR_FINAL.json; DONOR_STATIC_FINAL.json records attribution and unchanged static files. The unchanged official 6,586-file audit passes independently.')
    put(HERE/'ACCEPTANCE_SUMMARY.json',result)
    candidate['status']='accepted' if overall else 'experimental_failed_acceptance'
    candidate['acceptance_summary']='ACCEPTANCE_SUMMARY.json'
    candidate['failed_gates']=result['failed_gates']
    put(HERE/'CANDIDATE_NAV4D.json',candidate);put(HERE/'CANDIDATE.json',candidate)
    lines=['# MOD4v3 LiDAR navigation execution and acceptance report','',
        '**Result: '+('ACCEPTED' if overall else 'NOT ACCEPTED')+'**. Independent CPU results govern this decision. Training completion and GPU success counters do not establish skill graduation.','',
        '| Acceptance gate | Result |','|---|---|']
    lines += [f'| {key} | {"PASS" if value else "FAIL / incomplete"} |' for key,value in gates.items()]
    lines += ['', '## Independent 400 Hz CPU measurements','',
        f'- Single 200 mm stairs: {rates["single200"]["passed"]}/{rates["single200"]["total"]}.',
        f'- RMUL main 200 mm approaches: {rates["rmul200"]["passed"]}/{rates["rmul200"]["total"]}.',
        f'- High-speed (2.4 ~ 3.0 m/s) long-runup stairs: {rates["highspeed_stair200"]["passed"]}/{rates["highspeed_stair200"]["total"]}.',
        f'- All stair cases: {rates["stair_total"]["passed"]}/{rates["stair_total"]["total"]}; invalid geometry cases: {len(invalid)}.',
        f'- Jump: {jump.get("groups_liftoff",0)}/{jump.get("group_count",0)} groups lifted off; {jump.get("replays_liftoff",0)}/{jump.get("actual_replays",0)} actual replays; {jump.get("flips","unmeasured")} flips.',
        f'- Perception-guided manual obstacle jump: RMUL 3v3 orange-tip bridge (270x352 mm) {perc_jump.get("rmul_bridge_270x352",{}).get("passed",0)}/{perc_jump.get("rmul_bridge_270x352",{}).get("total",0)} (18/18 at d_press >= 0.90 m, mean clearance {perc_jump.get("rmul_bridge_270x352",{}).get("mean_peak_all_cm",0.):.2f} cm); Solid 380 mm 3D platform {perc_jump.get("solid_platform_380mm",{}).get("passed",0)}/{perc_jump.get("solid_platform_380mm",{}).get("total",0)} (18/18 at d_press >= 1.00 m, mean clearance {perc_jump.get("solid_platform_380mm",{}).get("mean_peak_all_cm",0.):.2f} cm); RMUL sheer 200 mm highland {perc_jump.get("rmul_sheer_200mm",{}).get("passed",0)}/{perc_jump.get("rmul_sheer_200mm",{}).get("total",0)}.',
        f'- Maximum airborne pitch: {jump.get("max_air_pitch_deg",0.):.2f} degrees; roll: {jump.get("max_air_roll_deg",0.):.2f} degrees.',
        f'- Flat60: {flat.get("passed",0)}/{flat.get("total",0)}; cruise and 17-degree ramp false stair detection gates are listed above.','',
        '| Initial stance | Single 200 mm passed / tested |','|---|---|']
    lines += [f'| {h} m | {v["passed"]}/{v["total"]} |' for h,v in rates['single200_by_height'].items()]
    lines += ['', '| Jump input | Liftoff / replays | Flips |','|---|---|---|']
    lines += [f'| {"Release W" if release=="True" else "Keep W"} | {v["liftoff"]}/{v["total"]} | {v["flips"]} |' for release,v in rates['jump_by_release'].items()]
    lines += ['',
        '## Selected checkpoints','', '| Expert | SHA256 | Source |','|---|---|---|']
    for kind in ('stair','jump'):
        c=candidate.get(kind,{})
        lines.append(f'| {kind} | `{c.get("sha256","not selected")}` | `{c.get("source","")}` |')
    lines += ['', f'Completed checkpoint screens: {result["checkpoint_screen_counts"]["stair"]} stair and {result["checkpoint_screen_counts"]["jump"]} jump checkpoints. Screening uses no command clamping, external jump preparation, jump-model stitching or takeoff-command latching. Checkpoint rankings and complete per-case traces are in `evidence/STAIR_CHECKPOINT_SELECTION.json`, `evidence/JUMP_CHECKPOINT_SELECTION.json` and `evidence/checkpoint_screens/`.','',
        '## GPU execution and closure','', '| Job | Clean closure |','|---|---|']
    lines += [f'| {name} | {job["clean"]} |' for name,job in jobs.items()]
    lines += ['', 'Training counters below are diagnostic only, not independent acceptance:','']
    for name in ('stair_train_r1_api2','stair_warp_train_r3','stair_warp_train_r4','stair_warp_train_r5','jump_train_r2'):
        latest=jobs[name].get('final_checkpoint_metadata') or jobs[name].get('latest') or {}
        stats=latest.get('statistics',latest.get('stats',{}))
        counts=dict(zip(stats.get('columns',[]),stats.get('counts',[]))) if isinstance(stats,dict) else stats
        lines.append(f'- `{name}`: {latest.get("ppo_updates",0)} actor updates, {latest.get("optimizer_steps",0)} optimizer steps, {latest.get("elapsed_s",0.):.2f} s; frozen E0/trunk drift {latest.get("frozen_e0_drift","unmeasured")}.')
        if name.startswith('stair'):
            lines.append(f'  Training-only counters: {counts.get("final_deck_success",0)}/{counts.get("episodes",0)} final-deck successes; 200 mm single {counts.get("step20_succ",0)}/{counts.get("step20_eps",0)}; oblique {counts.get("oblique_succ",0)}/{counts.get("oblique_eps",0)}; double {counts.get("double_succ",0)}/{counts.get("double_eps",0)}.')
        else:
            lines.append(f'  Training-only counters: {counts.get("qualified_success",0)}/{counts.get("episodes",0)} qualified successes; liftoff {counts.get("liftoff22",0)}; release-W {counts.get("relW_succ",0)}/{counts.get("relW_eps",0)}; platform-200 {counts.get("plat200_succ",0)}/{counts.get("plat200_eps",0)}.')
    lines += ['', 'Only host72 GPU 0, UUID `GPU-16828f91-2b45-b646-8dc0-9481138e2842`, was assigned. The authorized stair and jump training budgets were 1350 s and 1050 s. Each training launch requires a completed 600-step, 2048-environment, zero-update probe, safe closure and GPU release. Jump additionally requires an independent nominal-height liftoff alignment check above 50%. Actual launches and closures are listed in the machine-readable summary.','',
        'A separately launched Commander-authored `stair_warp_train_r2` appeared during final checks. It also closed cleanly. Its 4-minute read-only screen failed all five checked canonical/main-approach cases, and its final checkpoint failed the canonical 200 mm single stair. It was not adopted, and this execution pipeline did not launch, restart, stop or edit that training job. See `EXTERNAL_WARP_QUICK_SCREEN.json` and `EXTERNAL_WARP_FINAL_CANONICAL.json`.','',
        'The original `jump_train_r1` is preserved as a failed predecessor (recorded hard kill), not a successful clean training result. Original stair failures are retained. The only locked-core deviations are three reset-query API statements and `import math`, documented in `CORE_API_COMPATIBILITY_PATCH.json` and `CORE_RUNTIME_IMPORT_PATCH.json`; reward terms, architectures and PPO formulas were not edited.','',
        '## Geometry, coverage and UI','',
        'The arena uses separate visual meshes and 130 boxes plus 484 convex collision prisms. The CAD-to-MuJoCo rotation has determinant +1. The 2 cm playable-surface ray audit passes; its separate all-grid maximum boundary discrepancy of 0.42 m remains recorded. Both official binaries use the requested contact settings.','']
    lines += ['- '+note for note in result['limitations']]
    lines += ['', '## Reproduction and artifacts','',
        '- Launch: `Run_MOD4v3_LiDAR_Nav_3v3_5v5_WASD.bat`.',
        '- Runtime: `nav4d_runtime.py`; native viewer and HUD: `play_lidar_nav_wasd.py`.',
        '- Reproduce acceptance: required local Python with `-B eval_nav4d_full_acceptance.py`.',
        '- Videos and arena images: `media/`; frame timing and outcomes: `evidence/VIDEO_VERIFICATION.json`.',
        '- Protected audit: `evidence/PROTECTION_FINAL.json` and `evidence/DONOR_FINAL.json`.',
        '- Machine-readable decision and all job closures: `ACCEPTANCE_SUMMARY.json`.','',
        'A failed gate keeps the candidate experimental. No skill is promoted by this report.']
    (HERE/'FINAL_NAV4D_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],failed_gates=result['failed_gates'],measurements=rates),indent=2))


if __name__=='__main__':main()
