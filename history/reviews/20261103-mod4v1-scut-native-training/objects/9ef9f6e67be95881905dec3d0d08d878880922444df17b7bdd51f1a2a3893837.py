"""Prepare only the changed sources for the authorized SCUT stair hour."""
from pathlib import Path
import ast
import hashlib
import json
import time

N = Path(__file__).resolve().parent
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P = N/'env20000_target_axis_repair_1h_20261104'
A = N/'env20000_scut_stairs_1h_20261104'
read = lambda path: json.loads(Path(path).read_bytes())
H = lambda value: hashlib.sha256(value).hexdigest()


def put(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def prepare():
    previous = read(P/'PLAN.json')
    final = read(P/'reports/POSTROUND_FULL_RETURNED.json')['files']
    closed = final['OWNER_EXIT.json']
    assert closed['all_own_waited'] and closed['original_cost_settled'] and closed['original_leases_released']
    review = read(P/'reports/ACTUAL_TARGET_AXIS_FINAL_REVIEW.json')
    assert final['production/FINAL.json']['passed_execution']
    A.mkdir()
    (A/'reports').mkdir()
    remote = previous['remote_root'].rsplit('/', 1)[0]+'/'+A.name
    keys = ('baseline_git', 'source_SCUT_commit', 'GPU_UUID', 'assets', 'runtime',
            'runtime_manifest', 'guard', 'support', 'original_strictreserve', 'package_root')
    plan = {key: previous[key] for key in keys}
    plan.update(run_id='MOD4V1_SCUT_SAVED_STAIRS_20000ENV_1H_'+str(time.time_ns()),
        remote_root=remote, module_overlay=remote+'/overlay',
        module_overlays=[remote+'/overlay']+previous['module_overlays'],
        profile='scut_stairs', num_envs=20000, seed=66,
        train_seconds=3600, exit_headroom_seconds=300, max_parent_seconds=3900,
        source_checkpoint=final['production/FINAL.json']['checkpoint'],
        initialization='SCUT weights-only actor35/critic78 transfer to the selected stair course; fresh Adam and iteration0; no output or STD reset',
        source_optimizer_loaded=False, resized_learning_continuation=False,
        repair_first_axis=False, same_original_canonical=True, new_budget_or_refund=False,
        light_GPU_occupancy_allowed=True,
        human_latest='找张空闲卡开训；跳台阶不再强求270mm 按照华南虎的来就行',
        stair_branch='inv_stair_slope_for_rm_mid',
        position='Original SCUT generator origins including z; MOD4 root .38m above origin, zero velocity, existing feasible joint bank and roll/pitch/yaw sampling',
        fixed_height270_required=False, first_flight_required=False, full_rough_restored=False,
        task_differences=['Enhanced MOD4v1 instead of SCUT robot',
            'Only the saved inverse-mid stair branch; other rough tasks omitted',
            'Selected MOD4 source weights instead of public flat model8000'],
        exact_published_full_training_reproduction=False,
        independent_evaluation='Original owner full-save and safe-close, then independent80 firstepisodes capped400controls/8s seed9137/newDR/actual400Hz, recorded actual poses and terrain',
        diagnostic_before_training=str(P/'scut_stairs_eval1/reports/FULL_RETURNED.json'),
        previous_final_review=str(P/'reports/ACTUAL_TARGET_AXIS_FINAL_REVIEW.json'),
        preserved=['Enhanced USD/contract, physical solver and fullD0-D7',
            'Original PD/DC/clip6/contract target limits/CAD difference/D4 queue',
            'Saved26 nonzero rewards, commands/height .2-.42,20s episodes/random initial clock',
            'Saved ordinaryPPO and original canonical/reserve/fullsave boundaries'],
        live_GO=False, pending_actual_resource_selection=True)
    put(A/'PLAN.json', plan)
    for name in ('owner.py', 'entry.py'):
        value=(P/name).read_bytes()
        ast.parse(value)
        (A/name).write_bytes(value)
    names=('config.py','stairs.py','sdk.py','train.py','evaluate.py','finetune.py')
    files=[]
    for name in names:
        path=G/'project/isaac/mod4v1_scut'/name
        value=path.read_bytes();ast.parse(value)
        files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(value),SHA=H(value)))
    oldindex=read(P/'INDEX_SOURCE_FROZEN.json')
    shared=list(oldindex['shared_text'])
    for row in oldindex['files']:
        if row['relative'].startswith('overlay/'):
            shared.append(dict(path=previous['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
    put(A/'SOURCE_ONLY_PREPARED.json',dict(epoch=time.time(),files=files,shared_text=shared,
        source_only=True,whole_tree_model_asset_copy=False,
        native_started=False,training_budget_changes=0,
        next='After sole diagnostic releases: review actual native result, fresh four-card read, select GPU and freeze index, then original launch/FIRST and sole postround binding'))
    print(json.dumps(dict(prepared=str(A),source_modules=len(files),shared_refs=len(shared),
        model_reads=0,physics=0,GO=False)))


if __name__=='__main__':
    prepare()
