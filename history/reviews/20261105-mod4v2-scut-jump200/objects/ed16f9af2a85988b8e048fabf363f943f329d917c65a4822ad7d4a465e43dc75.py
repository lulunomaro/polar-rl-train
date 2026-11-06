"""Prepare the measured sampler only after current final/80/native review."""
from pathlib import Path
import argparse,hashlib,json,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=G/'project/isaac/mod4v2_scut'
read=lambda p:json.loads(Path(p).read_bytes())


def prepare(previous,destination):
    previous=previous.resolve();destination=destination.resolve()
    assert previous.is_relative_to(N)and destination.is_relative_to(N)
    assert read(previous/'reports/POSTROUND_COMPLETED.json')['complete']
    f=read(previous/'reports/POSTROUND_FULL_RETURNED.json')['files'];owner=f['OWNER_EXIT.json']
    assert not owner['error']and owner['all_own_waited']and owner['original_leases_released']
    assert read(previous/'reports/SUPERMIMIC_CLOSED_LEARNER_AND_ALL80.json')['passed']
    review=read(previous/'reports/ACTUAL_NATIVE_REVIEW.json')
    assert review['all_actual_images_reviewed']and review['complete_all80_review']
    assert review['decision']=='CONTINUE_SUPERMIMIC_AT_SAVED_BOUNDARY'
    assert read(N/'sampling_fusion_parity06/RESULT.json')['passed']
    assert read(N/'reports/SAMPLING_OPTIMIZATION_FULL_RESUME_TEST.json')['passed']
    assert read(N/'reports/SAMPLING_SCRIPTED_FULL_RESUME_TEST.json')['passed']
    benchmark=read(N/'sampling_scripted_isolated_ABBA11/RESULT.json')
    assert benchmark['passed']and benchmark['total_speed_ratio']>1
    assert read(N/'reports/SCRIPTED_GEOMETRY_OUTPUT_GRADIENT_PARITY.json')['passed']
    old=read(previous/'PLAN.json');ck=f['production/FINAL.json']['checkpoint']
    plan=dict(old)
    plan.update(remote_root=old['remote_root'].rsplit('/',1)[0]+'/'+destination.name,
        run_id='newton_supermimic_sampling_'+str(time.time_ns()),source_checkpoint=ck,
        source_iteration=ck['iteration'],source_BPTT_counts=ck['counts'],
        previous_overlay_paths=[old['remote_root']+'/overlay',*old['previous_overlay_paths']],
        cumulative_authorized_seconds_before_this_segment=old['cumulative_authorized_seconds_before_this_segment']+owner['actual_elapsed_seconds'],
        sampling_optimization=True,state_read_fusion_enabled=False,checkpoint_interval_seconds=300.,
        previous_native_review=str(previous/'reports/ACTUAL_NATIVE_REVIEW.json'),
        sampling_benchmark=str(N/'sampling_scripted_isolated_ABBA11/RESULT.json'),
        specific_repair='Measured Warp400Hz closure+acceptance and50Hz Fudan fusion; fused fourAdam and scripted pure learned geometry. Same fulllearner/replay/RNG/DR/residual025/H32 and physical reset; current80 evidence retained.')
    plan.pop('GPU_UUID',None)
    assert plan['cumulative_authorized_seconds_before_this_segment']+3900<=plan['cumulative_limit_seconds']
    destination.mkdir(exist_ok=False);(destination/'reports').mkdir();files=[]
    def add(path,relative):
        raw=path.read_bytes();files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    for name in ('supermimic_train.py','supermimic_speed.py','newton_sampling.py','warp_sampling.py','warp_kernels.py'):
        add(CODE/name,'overlay/'+name)
    binding=destination/'SUPERMIMIC_BINDINGS.json';binding.write_bytes((previous/'SUPERMIMIC_BINDINGS.json').read_bytes());add(binding,binding.name)
    for name,relative in [('newton_entry.py','entry.py'),('newton_owner.py','owner.py'),('newton_fudan_final620_1h/run-newton.sh','run-newton.sh')]:add(N/name,relative)
    (destination/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
    (destination/'SOURCE_PREPARED.json').write_text(json.dumps(dict(files=files,
        shared_text=read(previous/'SOURCE_PREPARED.json')['shared_text'],whole_tree_copies=0,
        checkpoint_copies=0,asset_copies=0,all_pinned_learner_source_referenced=True),indent=2),encoding='utf8')
    return dict(prepared=str(destination),source=ck,files=len(files))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--previous',required=True,type=Path)
    p.add_argument('--destination',required=True,type=Path);a=p.parse_args()
    print(json.dumps(prepare(a.previous,a.destination)))
