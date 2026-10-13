"""A smaller single-axis factor justified by center candidate's20 ordinary failures."""
from pathlib import Path
import sys,json,hashlib,time,shutil,torch,zipfile
D=Path(__file__).resolve().parent;W=D.parent;O=W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014';N=W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014';Q=N/'payload';R=N/'reports'
sys.path.insert(0,str(O));from left_joint_domain_cpu_component import candidate_initialization,CPU_mean,guarded_targets,SOURCE_SHA
assert not N.exists();Q.mkdir(parents=True);R.mkdir();H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((D/'reports/JOINT_CANDIDATE_FULL1500_PAIRED17B_CPU_ACTUAL_REVIEW.json').read_bytes())
assert prior['passed'] and prior['ordinary_events']==20 and prior['actual_shared_OSlock_free']
replay=json.loads((O/'reports/LEFT_JOINT_CANDIDATE_SAVED_ACTUAL_OBS_CPU_REPLAY.json').read_bytes());sourcepath=Path(replay['source']['path']);assert H(sourcepath)==SOURCE_SHA
source=torch.load(sourcepath,map_location='cpu',weights_only=False);offset=torch.tensor(source['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']['actual_GPU_API_offset_and_default_q_leg_order'],dtype=torch.float32)
desired=-1.0843+.14
candidate=candidate_initialization(source,source_sha=SOURCE_SHA,actual_offset_witness=offset,desired_difference=desired)
# The tested center changed target difference by almost1rad. This factor preserves
# the same initializer form and all other fields, reducing only the stated margin.
oldmanifest=json.loads((D/'payload/JOINT_CANDIDATE_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
for x in oldmanifest['file_rows']:
 p=D/'payload'/x['relative'];assert H(p)==x['sha256'];q=Q/x['relative'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
q=Q/'source/source512_left_joint_interior_candidate.pt';torch.save(candidate,q);SHA=H(q)
oldSHA='2fa8902f907fd226752c552e3e8792c7308e44b1ed6f6028aab91121b9161295'
for n in ('paired_direct3060_joint_candidate_v1.py','factor_runtime_3060_joint_candidate_v1.py','run_direct3060_joint_candidate_parent_v1.py'):
 p=Q/n;s=p.read_text(encoding='utf8').replace('MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014','MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014').replace(oldSHA,SHA);compile(s,n,'exec');p.write_bytes(s.encode())
rows=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file()]
m=dict(epoch=time.time(),file_rows=rows,source_candidate_sha256=SHA,reference_source_sha256=SOURCE_SHA,prior_center_factor_rejected_for20ordinary=True,one_time_left_initial_mean_only=True,desired_crank_minus_hip_rad=desired,interior_lower_margin_rad=.14,only_same_axis_margin_changed_relative_to_center=True,no_PPO=True,no_production_adoption=True)
mf=Q/'JOINT_CANDIDATE_SOURCE_BUNDLE_MANIFEST.json';mf.write_text(json.dumps(m,indent=2),encoding='utf8')
z=N/'JOINT_CANDIDATE_SOURCE_PACKAGE.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(Q.rglob('*')):
  if p.is_file():f.write(p,p.relative_to(Q).as_posix())
proof=dict(epoch=time.time(),CPU_prepared_only=True,checkpoint=dict(path=str(q),sha256=SHA,bytes=q.stat().st_size),manifest=dict(path=str(mf),sha256=H(mf)),worker=dict(path=str(Q/'paired_direct3060_joint_candidate_v1.py'),sha256=H(Q/'paired_direct3060_joint_candidate_v1.py')),runtime=dict(path=str(Q/'factor_runtime_3060_joint_candidate_v1.py'),sha256=H(Q/'factor_runtime_3060_joint_candidate_v1.py')),package=dict(path=str(z),sha256=H(z),bytes=z.stat().st_size),prior_center_review=dict(path=str(D/'reports/JOINT_CANDIDATE_FULL1500_PAIRED17B_CPU_ACTUAL_REVIEW.json'),sha256=H(D/'reports/JOINT_CANDIDATE_FULL1500_PAIRED17B_CPU_ACTUAL_REVIEW.json')),desired_crank_minus_hip_rad=desired,lower_margin_rad=.14,target_fullstate_and_native_API_still_required=True,source512_not20k=True,no_current_trainer_modified=True,no_GPU_or_PPO_during_CPU=True)
(R/'JOINT_CANDIDATE_FACTOR_SOURCE_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
actorrows=[dict(name=k,shape=list(v.shape),dtype=str(v.dtype),sha256=hashlib.sha256(v.contiguous().numpy().tobytes()).hexdigest()) for k,v in candidate['actor_state_dict'].items()]
(R/'JOINT_CANDIDATE_ACTOR_ROWS_CPU_ACTUAL.json').write_text(json.dumps(dict(actual_actor_nine_CPU_rows=actorrows,checkpoint_sha256=SHA,CPU_only=True),indent=2),encoding='utf8')
for filename in ('deploy_joint_candidate_frozen1500_unique_once.py','collect_joint_candidate_actual_readonly.py','review_joint_candidate_fullraw_paired17b_CPU.py'):
 s=(D/filename).read_text(encoding='utf8').replace('MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014','MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014').replace('native3060_joint_interior_bodypos_worldpos1500_v1','native3060_joint_margin014_bodypos_worldpos1500_v1').replace('MOD4_LeftJointInteriorFactor_20261014_Frozen1500_v1','MOD4_LeftJointMargin014Factor_20261014_Frozen1500_v1').replace(oldSHA,SHA)
 compile(s,filename,'exec');(N/filename).write_bytes(s.encode())
assert not torch.cuda.is_initialized()
print(json.dumps(dict(newroot=str(N),candidate_SHA=SHA,desired=desired,CPU_prepared_not_GPU_pass=True)))
