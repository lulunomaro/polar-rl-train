"""Prepare a small full-state continuation; no network, training or checkpoint decode."""
from pathlib import Path
import ast, hashlib, json, time

N = Path(__file__).resolve().parent
A = N/'attempt03'; C = N/'continuation_final60_1h'
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read = lambda p: json.loads(p.read_bytes())
H = lambda raw: hashlib.sha256(raw).hexdigest()
def put(path, value):
    with path.open('x', encoding='utf8') as stream: json.dump(value, stream, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    diagnosis = read(A/'reports/FINAL60_LEARNER_DIAGNOSIS.json')
    assert diagnosis['passed'] and diagnosis['iteration'] == 60 and diagnosis['Adam_min'] == 1200
    old = read(A/'PLAN.json'); before = read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']
    previous = read(A/'INDEX_SOURCE_FROZEN.json')
    C.mkdir(); (C/'reports').mkdir()
    remote = old['remote_root']+'/continuation_final60_1h'
    plan = dict(old)
    plan.update(run_id=Path(remote).name+'_'+str(time.time_ns()), remote_root=remote,
        package_root=old['package_root'], module_overlay=remote+'/overlay',
        guard=old['guard'], fresh_training=False, full_state_continuation=True,
        source_checkpoint=before['production/FINAL.json']['checkpoint'], source_optimizer_step=1200,
        initialization='Restore full same20k v2final60 actorcriticSTD/17Adam1200/LR/components/RNG/queues/counters; retain newconstructor nominal then one freshphysicalreset',
        human_latest='为什么只有60次ppo更新？不是20000env吗？怎么一个小时才60次ppo？继续训和回放',
        human_authorization='Existing cumulative100h with hourly fullsave/safeexit/independent80/nativeplayback; latest human explicitly continues training and playback',
        cumulative_authorized_seconds_before_this_segment=25200,
        source_profile='jump200', target_profile='jump200', task_changed=False,
        previous_training_root=str(A), previous_native_review_required=True,
        previous_native_review=str(A/'reports/FINAL60_ACTUAL_NATIVE_REVIEW.json'),
        pending_actual_resource_selection=True, train_seconds=3600, max_parent_seconds=3900,
        exit_headroom_seconds=300, shared_dependencies_from_previous_actual_INDEX=True,
        paused_old_automations=['mod4-200-rl-bptt'])
    plan.pop('GPU_UUID', None)
    put(C/'PLAN.json', plan)
    (C/'owner.py').write_bytes((A/'owner.py').read_bytes())
    entry = (A/'entry.py').read_text(encoding='utf8')
    needle="sys.path.insert(0,task['package_root'])"
    assert entry.count(needle) == 1
    entry = entry.replace(needle, needle+"\nimport mod4v2_scut\nmod4v2_scut.__path__.insert(0,task['module_overlay'])")
    needle="    runpy.run_module('mod4v2_scut.train',run_name='__main__')"
    assert entry.count(needle) == 1
    entry = entry.replace(needle,
        "    source=task['source_checkpoint']\n"
        "    sys.argv+=['--resume',source['path'],'--init-SHA',source['SHA'],'--init-bytes',str(source['bytes'])]\n"+needle)
    ast.parse(entry); (C/'entry.py').write_text(entry, encoding='utf8')
    shared = list(previous['shared_text'])
    for row in previous['files']:
        if row['relative'].startswith(('package/', 'shared/', 'hardware/')):
            shared.append(dict(path=old['remote_root']+'/'+row['relative'], bytes=row['bytes'], SHA=row['SHA']))
    shared = list({row['path']: row for row in shared}.values())
    sdk = G/'project/isaac/mod4v2_scut/sdk.py'; raw = sdk.read_bytes()
    put(C/'SOURCE_ONLY_PREPARED.json', dict(epoch=time.time(), files=[dict(path=str(sdk),
        relative='overlay/sdk.py', bytes=len(raw), SHA=H(raw))], shared_text=shared,
        source_only=True, assets_or_weights_copied=False, whole_tree_copied=False,
        prepared_before_actual_native_review=True, launch_requires_actual_native_review=True))
    source = (N/'control.py').read_text(encoding='utf8')
    start = source.index('    for path in sorted(CODE.glob(')
    end = source.index('    return rows', start)
    source = source[:start]+"    prepared=read(HERE/'SOURCE_ONLY_PREPARED.json')\n    for row in prepared['files']:add(Path(row['path']),row['relative'])\n    for name in ['PLAN.json','entry.py','owner.py']:add(HERE/name,name)\n"+source[end:]
    needle="    plan=read(HERE/'PLAN.json');job=plan['remote_root']"
    source = source.replace(needle, needle+"\n    review=read(plan['previous_native_review'])\n    assert review['all_actual_images_reviewed'] and review['complete_all80_review']\n    assert review['decision']=='CONTINUE_FULL_FINAL60_AS_HUMAN_REQUESTED'\n    assert review['checkpoint_SHA']==plan['source_checkpoint']['SHA']")
    start = source.index("        shared=read(OLD/'env20000_jump200_tuck_retraction_1h_20261105/INDEX_SOURCE_FROZEN.json')")
    end = source.index('        bypath=', start)
    source = source[:start]+"        shared=read(HERE/'SOURCE_ONLY_PREPARED.json')['shared_text']\n"+source[end:]
    source = source.replace('fresh_training=True,old_policy_loaded=False',
                            'fresh_training=False,full_state_continuation=True,old_v1_policy_loaded=False')
    source = source.replace("'production/FRESH_INITIALIZATION.json','production/STARTUP.json'",
                            "'production/FRESH_INITIALIZATION.json','production/FULL_STATE_RESTORE.json','production/STARTUP.json'")
    source = source.replace("first['iteration']==1", "first['iteration']==plan['source_checkpoint']['iteration']+1")
    needle="    valid=bool(first and"
    index=source.index(needle)
    source=source[:index]+"    restore=files.get('production/FULL_STATE_RESTORE.json')or{}\n"+source[index:]
    source=source.replace("and files.get('production/MOD4V2_NATIVE_HARDWARE.json'))",
        "and files.get('production/MOD4V2_NATIVE_HARDWARE.json')\n"
        "        and restore.get('source_iteration')==60 and restore.get('optimizer_state_entries')==17\n"
        "        and restore.get('optimizer_step_min')==restore.get('optimizer_step_max')==1200\n"
        "        and not restore.get('task_changed') and restore.get('command_profile_adaptation')==[])")
    source=source.replace("hardware=files.get('production/MOD4V2_NATIVE_HARDWARE.json'),fresh=",
                          "restore=restore,hardware=files.get('production/MOD4V2_NATIVE_HARDWARE.json'),fresh=")
    ast.parse(source)
    (N/'continuation_control.py').write_text(source, encoding='utf8')
    put(C/'reports/PREPARED_FULL_CONTINUATION60.json', dict(epoch=time.time(),
        source_checkpoint=plan['source_checkpoint'], learner_diagnosis=str(A/'reports/FINAL60_LEARNER_DIAGNOSIS.json'),
        actual_launch=False, native_review_pending=True, shared_refs=len(shared), changed_package_modules=1,
        controls_per_rollout=24, sample_count_per_update=480000, expected_FIRST_iteration=61,
        source_Adam=1200, expected_FIRST_new_Adam=20, constructor_nominal_preserved=True,
        training_reward_physics_PPO_unchanged=True,
        controller=dict(path=str(N/'continuation_control.py'),SHA=H(source.encode()))))
    print(json.dumps(dict(prepared=str(C),shared_refs=len(shared),new_package_modules=1,
        source_iteration=60,source_Adam=1200,actual_launch=False)))
