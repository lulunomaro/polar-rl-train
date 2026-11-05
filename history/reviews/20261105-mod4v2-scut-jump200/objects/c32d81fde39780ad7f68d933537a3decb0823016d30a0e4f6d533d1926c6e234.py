"""Prepare the next saved-boundary segment; never launches or contacts SSH."""
from pathlib import Path
import argparse,hashlib,json,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut'
read=lambda p:json.loads(Path(p).read_bytes())


def prepare(previous,destination):
    previous=previous.resolve();destination=destination.resolve()
    assert previous.is_relative_to(N)and destination.is_relative_to(N)
    done=read(previous/'reports/POSTROUND_COMPLETED.json')
    assert done['complete']
    report=previous/'reports/LOCAL_COMPLETE_RETURNED.json'
    if not report.exists():report=previous/'reports/POSTROUND_FULL_RETURNED.json'
    returned=read(report)['files']
    owner=returned['OWNER_EXIT.json']
    assert not owner['error']and owner['all_own_waited']and owner['original_leases_released']
    review=read(previous/'reports/ACTUAL_NATIVE_REVIEW.json')
    assert review['all_actual_images_reviewed']and review['complete_all80_review']
    assert review['decision']=='CONTINUE_SUPERMIMIC_AT_SAVED_BOUNDARY'
    assert read(N/'supermimic_cli04/FINAL.json')['verified_BPTT_steps']==2
    assert read(N/'supermimic_cli_resume05/FINAL.json')['verified_BPTT_steps']==3
    assert read(N/'supermimic_cli04/evaluation80/RESULT.json')['passed_execution']
    old=read(previous/'PLAN.json');checkpoint=returned['production/FINAL.json']['checkpoint']
    destination.mkdir(exist_ok=False);(destination/'reports').mkdir()
    plan=dict(old)
    plan.update(remote_root=old['remote_root'].rsplit('/',1)[0]+'/'+destination.name,
        run_id='newton_supermimic_'+str(time.time_ns()),learner='SuperMimic',
        source_checkpoint=checkpoint,source_iteration=checkpoint['iteration'],
        previous_overlay_paths=[old['remote_root']+'/overlay',*old['previous_overlay_paths']],
        cumulative_authorized_seconds_before_this_segment=
            old['cumulative_authorized_seconds_before_this_segment']+owner['actual_elapsed_seconds'],
        previous_native_review=str(previous/'reports/ACTUAL_NATIVE_REVIEW.json'),
        replay_steps=64,replay_estimated_bytes=2261760000,
        new_BPTT_optimizers_not_PPO_optimizer_resume=True,
        source_PPO_complete_state_preserved=True,
        specific_repair='Switch to tested learned-state/reward/context H32 BPTT, excluding numerical-invalid replay; fixed scan cache and aggregate native solver warnings',
        next='Fullsave/safeclose/immediate independent80/saved-pose playback; genuine200mm acceptance before next terrain')
    assert plan['cumulative_authorized_seconds_before_this_segment']+3900<=360000
    plan.pop('GPU_UUID',None)
    binding=read(CODE/'SUPERMIMIC_BINDINGS.json')
    local_binding_root=Path(binding['root']);binding['root']=plan['remote_root']+'/learner_source'
    files=[]
    def add(path,relative):
        raw=Path(path).read_bytes();files.append(dict(path=str(path),relative=relative,
            bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    # A small pinned learner package is transferred once; no model/assets or
    # producer tree is copied, and all its original source identities remain.
    for row in binding['files']:add(local_binding_root/row['relative'],'learner_source/'+row['relative'])
    localbinding=destination/'SUPERMIMIC_BINDINGS.json'
    localbinding.write_text(json.dumps(binding,indent=2),encoding='utf8')
    add(localbinding,'SUPERMIMIC_BINDINGS.json')
    for name in ('newton_env.py','newton_model.py','newton_checkpoint.py','newton_evaluate.py',
                 'supermimic_newton.py','supermimic_train.py','supermimic_evaluate.py'):
        add(CODE/name,'overlay/'+name)
    add(N/'newton_entry.py','entry.py');add(N/'newton_owner.py','owner.py')
    add(N/'newton_fudan_final620_1h/run-newton.sh','run-newton.sh')
    (destination/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
    (destination/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,
        shared_text=read(previous/'SOURCE_PREPARED.json')['shared_text'],
        whole_tree_copies=0,checkpoint_copies=0,asset_copies=0,
        learner_small_pinned_source_files_only=True),indent=2),encoding='utf8')
    return dict(prepared=str(destination),files=len(files),source=checkpoint)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--previous',required=True,type=Path)
    p.add_argument('--destination',required=True,type=Path);a=p.parse_args()
    print(json.dumps(prepare(a.previous,a.destination)))
