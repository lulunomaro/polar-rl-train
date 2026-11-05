"""Prepare one small Warp continuation after the actual Fudan final is reviewed."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import time

N = Path(__file__).resolve().parent
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE = G/'project/isaac/mod4v2_scut'
read = lambda p: json.loads(Path(p).read_bytes())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    previous = args.previous.resolve()
    assert previous.is_relative_to(N)
    review = read(args.review)
    assert review['all_actual_images_reviewed'] and review['complete_all80_review']
    assert review['decision'] == 'REPLACE_SAMPLER_WITH_WARP_AS_HUMAN_REQUESTED'
    returned = read(previous/'reports/POSTROUND_FULL_RETURNED.json')['files']
    checkpoint = returned['production/FINAL.json']['checkpoint']
    assert checkpoint['SHA'] == review['checkpoint_SHA']
    assert returned['OWNER_EXIT.json']['all_own_waited'] and not returned['OWNER_EXIT.json']['error']
    destination = N/('fudan_warp_final'+str(checkpoint['iteration'])+'_1h')
    destination.mkdir()
    (destination/'reports').mkdir()
    old = read(previous/'PLAN.json')
    remote = str(Path(old['remote_root']).parent).replace('\\', '/')+'/'+destination.name
    plan = dict(old)
    plan.update(remote_root=remote, run_id=destination.name+'_'+str(time.time_ns()),
        module_overlay=remote+'/overlay', previous_module_overlay=old['module_overlay'],
        previous_overlay_paths=[old['module_overlay'], old['previous_module_overlay']],
        source_checkpoint=checkpoint, source_optimizer_step=checkpoint['iteration']*20,
        previous_training_root=str(previous), previous_native_review=str(args.review),
        pending_actual_resource_selection=True, train_seconds=3600, max_parent_seconds=3900,
        full_state_continuation=True, fresh_training=False, human_direct_no_ledger_admission=True,
        canonical_admission_required=False, human_latest='用这套流程替换我们现在的，来加速我们训练',
        reward_recipe='Pinned Fudan16 terms; fused Warp sampler; same PhysX/PD/DC/DR/PPO',
        sampling_backend='MOD4V2_FUDAN_WARP_SAMPLING_V1',
        basic_loco_lib_commit='e4181af587330d0b70ca72e0d36b49be32e12a65',
        full_Newton_backend_migrated=False,
        cumulative_authorized_seconds_before_this_segment=old['cumulative_authorized_seconds_before_this_segment']+
            returned['OWNER_EXIT.json']['actual_elapsed_seconds'])
    assert plan['cumulative_authorized_seconds_before_this_segment']+3900 < 100*3600
    plan.pop('GPU_UUID', None)
    put(destination/'PLAN.json', plan)
    # The proven direct owner is unchanged: private GPU EX, no ledger, fixed
    # boundary, full save/close then independent80 before release.
    (destination/'owner.py').write_bytes((previous/'owner.py').read_bytes())
    entry = (previous/'entry.py').read_text(encoding='utf8')
    old_paths = "mod4v2_scut.__path__.insert(1,task['previous_module_overlay'])"
    assert old_paths in entry
    entry = entry.replace(old_paths, "for path in reversed(task['previous_overlay_paths']):\n    mod4v2_scut.__path__.insert(1,path)")
    entry = entry.replace("runpy.run_module('mod4v2_scut.train',run_name='__main__')",
                          "runpy.run_module('mod4v2_scut.warp_train',run_name='__main__')")
    ast.parse(entry)
    (destination/'entry.py').write_text(entry, encoding='utf8')
    previous_index = read(previous/'INDEX_SOURCE_FROZEN.json')
    shared = list(previous_index['shared_text'])
    for row in previous_index['files']:
        if row['relative'].startswith('overlay/'):
            shared.append(dict(path=old['remote_root']+'/'+row['relative'], bytes=row['bytes'], SHA=row['SHA']))
    files = []
    for name in ('sdk.py', 'warp_kernels.py', 'warp_sampling.py', 'warp_train.py', 'warp_tests.py', 'fudan_tests.py'):
        path = CODE/name
        files.append(dict(path=str(path), relative='overlay/'+name, bytes=path.stat().st_size, SHA=sha(path)))
    put(destination/'SOURCE_ONLY_PREPARED.json', dict(epoch=time.time(), files=files,
        shared_text=list({row['path']:row for row in shared}.values()), source_only=True,
        assets_or_weights_copied=False, whole_tree_copied=False,
        local_GPU_parity=str(N/'reports/WARP_PARITY_FINAL_LOCAL.json')))
    source = (N/'fudan_direct_collect.py').read_text(encoding='utf8')
    source = source.replace("review['decision']=='SWITCH_FULL_FINAL357_TO_FUDAN_JUMP_AS_HUMAN_REQUESTED'",
                            "review['decision']=='REPLACE_SAMPLER_WITH_WARP_AS_HUMAN_REQUESTED'")
    needle = "'production/FUDAN_REWARD_RECIPE.json','production/FULL_STATE_RESTORE.json'"
    assert needle in source
    source = source.replace(needle,
        "'production/FUDAN_REWARD_RECIPE.json','production/WARP_SAMPLING.json','production/WARP_NATIVE_PARITY.json','production/FULL_STATE_RESTORE.json'")
    source = source.replace("and restore.get('source_iteration')==plan['source_checkpoint']['iteration']",
        "and files.get('production/WARP_SAMPLING.json',{}).get('cuda_graphs') is True\n"
        "        and files.get('production/WARP_NATIVE_PARITY.json',{}).get('passed') is True\n"
        "        and restore.get('source_iteration')==plan['source_checkpoint']['iteration']")
    ast.parse(source)
    controller = N/'warp_control.py'
    assert not controller.exists()
    controller.write_text(source, encoding='utf8')
    put(destination/'reports/PREPARED_WARP_CONTINUATION.json', dict(epoch=time.time(),
        production_started=False, source_checkpoint=checkpoint, source_optimizer_step=plan['source_optimizer_step'],
        source_files=len(files)+3, shared_refs=len(shared), full_Newton_backend_migrated=False,
        controller_path=str(controller), controller_SHA=sha(controller),
        human_authorization=plan['human_latest']))
    print(json.dumps(dict(destination=str(destination), source=checkpoint, controller=str(controller))))


if __name__ == '__main__':
    main()
