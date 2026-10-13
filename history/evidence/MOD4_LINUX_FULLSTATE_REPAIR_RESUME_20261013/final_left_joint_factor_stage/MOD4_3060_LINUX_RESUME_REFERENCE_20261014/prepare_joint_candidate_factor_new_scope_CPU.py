"""Prepare a genuinely new frozen single-factor scope; no network, GPU or training."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile,torch
D=Path(__file__).resolve().parent;N=D.parent/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014';Q=N/'payload';R=N/'reports'
assert not N.exists();Q.mkdir(parents=True);R.mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
replay=json.loads((D/'reports/LEFT_JOINT_CANDIDATE_SAVED_ACTUAL_OBS_CPU_REPLAY.json').read_bytes())
assert replay['existing_raw_CPU_replay_complete'] and replay['represented_original_processor_vs_actual_guarded_targets_max_error_rad']==0
assert replay['five_other_CPU_mean_heads_same_obs_byteexact'] and replay['no_production_adoption']
candidate=Path(replay['candidate']['path']);assert H(candidate)==replay['candidate']['sha256']
ck=torch.load(candidate,map_location='cpu',weights_only=False)
assert ck['LEFT_JOINT_DOMAIN_INTERIOR_CANDIDATE']['source_SHA']=='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
assert not torch.cuda.is_initialized()
oldmanifest=json.loads((D/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
for x in oldmanifest['file_rows']:
    p=D/'payload'/x['relative'];assert H(p)==x['sha256']
    if x['relative'] in ('paired_direct3060_reference17b_v1.py','factor_runtime_3060_reference17b_v1.py','run_direct3060_reference17b_parent_v1.py'):continue
    q=Q/x['relative'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('EXPECTED_INSTALLED_3060_BACKEND_V2.json',):
    if not (Q/name).exists():shutil.copy2(D/'payload'/name,Q/name)
q=Q/'source/source512_left_joint_interior_candidate.pt';shutil.copy2(candidate,q)
NEW_SHA=H(q);assert NEW_SHA=='2fa8902f907fd226752c552e3e8792c7308e44b1ed6f6028aab91121b9161295'
for old,new in [('paired_direct3060_reference17b_v1.py','paired_direct3060_joint_candidate_v1.py'),('factor_runtime_3060_reference17b_v1.py','factor_runtime_3060_joint_candidate_v1.py'),('run_direct3060_reference17b_parent_v1.py','run_direct3060_joint_candidate_parent_v1.py')]:
    s=(D/'payload'/old).read_text(encoding='utf8')
    s=s.replace('MOD4_3060_LINUX_RESUME_REFERENCE_20261014','MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014').replace('17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9',NEW_SHA)
    s=s.replace('paired_direct3060_reference17b_v1.py','paired_direct3060_joint_candidate_v1.py').replace('factor_runtime_3060_reference17b_v1','factor_runtime_3060_joint_candidate_v1').replace('run_direct3060_reference17b_parent_v1.py','run_direct3060_joint_candidate_parent_v1.py').replace('REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','JOINT_CANDIDATE_SOURCE_BUNDLE_MANIFEST.json')
    if old.startswith('factor_runtime'):
        anchor=' actual_actor=policy.__closure__[0].cell_contents';assert s.count(anchor)==1
        witness=r'''
 # Re-measure the native action API before candidate inference; no reset/reinit.
 mark=source['LEFT_JOINT_DOMAIN_INTERIOR_CANDIDATE']
 assert mark['profile']=='left_final_row0_interior_reset_pose_difference_CPU_candidate_v1'
 assert mark['source_SHA']=='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
 assert mark['only_left_final_weight_bias_row0_changed'] and mark['five_other_mean_heads_shared_trunk_std_critic_exact'] and mark['no_live_action_coupling']
 native_legs=e.action_manager.get_term('legs');offset=native_legs._offset.detach().cpu()
 expected_offset=torch.tensor(mark['actual_reference_offset'],dtype=offset.dtype)
 assert offset.shape==(N,4) and torch.equal(offset,expected_offset[None].expand(N,4))
 joint_ids=[r.joint_names.index(x) for x in ('left_crank','left_hip','right_crank','right_hip')]
 default_q=r.data.default_joint_pos[:,joint_ids].detach().cpu()
 assert torch.equal(default_q,offset) and task.LEG_ACTION_SCALE==.5
 assert native_legs.diff_min==-1.0843 and native_legs.diff_max==.85
 save('CANDIDATE_NATIVE_ACTION_API_WITNESS.json',dict(checkpoint_sha256=args.checkpoint_sha,actual_offset=offset.tolist(),actual_default_joint_q=default_q.tolist(),leg_order=['left_crank','left_hip','right_crank','right_hip'],scale=task.LEG_ACTION_SCALE,lower=native_legs.diff_min,upper=native_legs.diff_max,source_CPU_initializer_not_repeated=True,installed_processor_unchanged=True,no_live_output_coupling=True,no_RNGdraw=True))
'''
        s=s.replace(anchor,witness+'\n'+anchor)
    compile(s,new,'exec');(Q/new).write_bytes(s.encode())
rows=[]
for p in sorted(Q.rglob('*')):
    if p.is_file():rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)))
m=dict(epoch=time.time(),file_rows=rows,source_candidate_sha256=NEW_SHA,unchanged_runtime_and_geometry_and_backend=True,source_reference_sha256=replay['source']['sha256'],only_single_initial_left_row0_factor=True,no_training512_DR_restore_or_PPO=True,laptop_GPU_paused=True,original_frozen_fixture=True,not_80env_qualification=True)
mf=Q/'JOINT_CANDIDATE_SOURCE_BUNDLE_MANIFEST.json';mf.write_text(json.dumps(m,indent=2),encoding='utf8')
z=N/'JOINT_CANDIDATE_SOURCE_PACKAGE.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
    for p in sorted(Q.rglob('*')):
        if p.is_file():f.write(p,p.relative_to(Q).as_posix())
proof=dict(epoch=time.time(),CPU_prepared_only=True,checkpoint=dict(path=str(q),sha256=NEW_SHA,bytes=q.stat().st_size),manifest=dict(path=str(mf),sha256=H(mf)),worker=dict(path=str(Q/'paired_direct3060_joint_candidate_v1.py'),sha256=H(Q/'paired_direct3060_joint_candidate_v1.py')),runtime=dict(path=str(Q/'factor_runtime_3060_joint_candidate_v1.py'),sha256=H(Q/'factor_runtime_3060_joint_candidate_v1.py')),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),all_source_files=len(rows),existing_raw_replay_report_SHA=H(D/'reports/LEFT_JOINT_CANDIDATE_SAVED_ACTUAL_OBS_CPU_REPLAY.json'),actual_GPU_nativeoffset_defaultq_and_behavior_not_passed_yet=True,old_GPU_case_not_replayed=True,no_production_adoption=True)
(R/'JOINT_CANDIDATE_FACTOR_SOURCE_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(dict(new_root=str(N),files=len(rows),candidate_SHA=NEW_SHA,package_bytes=z.stat().st_size,source_prepared_not_GPU_pass=True)))
