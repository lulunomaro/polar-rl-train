"""Assign concrete source-bound jobs; extract retained originals without deletion."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,time
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'payload';ROOT='/home/lc01/Zonglin Li/zonglin2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 assert not Q.exists();Q.mkdir()
 source=json.loads((R/'SOURCE210_CHECKPOINTS_CANONICAL_AND_ORIGINAL_CONTRACT_ACTUAL.json').read_bytes())
 stream=json.loads((R/'ORIGINAL_JOB_SOURCE_ARCHIVE_STREAM_ACTUAL.json').read_bytes());z=Path(stream['path']);assert H(z)==stream['sha256'] and stream['rc']==0
 meta=json.loads((R/'ORIGINAL_JOB_SOURCE_FILES_ACTUAL.json').read_bytes());by={x['archive']:x for x in meta['rows']}
 with tarfile.open(z,'r:gz') as a:
  for m in a:
   p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts
   out=Q.joinpath(*p.parts);assert out.resolve().is_relative_to(Q.resolve());b=a.extractfile(m).read()
   if m.name in by:assert len(b)==by[m.name]['bytes'] and hashlib.sha256(b).hexdigest()==by[m.name]['sha256']
   out.parent.mkdir(parents=True,exist_ok=True)
   if out.exists():assert out.read_bytes()==b
   else:
    with out.open('xb') as f:f.write(b)
 jobs=[]
 for gpu,name,axis in ((0,'E1_CURB20_reset_bound_command_coverage','Keep20mm/150mm geometry; explicitly cover original and mirrored ascending/descending with reset-bound normal command direction. This is a command-coverage repair, not blind repetition of133/139 or a higher step.'),
                      (1,'E1_SLOPE5_flat_slope_flat_continuity','Keep original5degree/2m geometry; audit and repair complete approach/ramp/platform valid-prefix exposure within original20s. No mechanical10degree PPO or slope-height increase.')):
  x=source['checkpoints'][gpu];snap=source['original_snapshots'][gpu]
  job_root=ROOT+'/tasks/'+D.name+'/job'+str(gpu)
  job=dict(task_id=name+'_first1800s_v1',physical_GPU=gpu,GPU_UUID={0:'GPU-16828f91-2b45-b646-8dc0-9481138e2842',1:'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}[gpu],
   host='10.24.0.72',root=job_root,expert_family='E1 terrain branch',task_axis=axis,training_requested_by_human=True,
   original_source={k:x[k] for k in ('path','bytes','sha256','terrain_metadata','optimizer_states')},target_source=job_root+'/source/source.pt',
   original_snapshot_manifest=snap['path'],original_snapshot_source_count=len(snap['source_map']),
   original_entrypoint='isaac/mod4/'+('train_curb20_entry_resume_ppo.py' if gpu==0 else 'train_slope5_snapshot_reviewed_resume_ppo.py'),
   fullstate_contract=dict(num_envs=20000,seed=20260928,actor35_critic38_action6=True,steps_per_update=24,learning_rate=.0001,
    schedule='adaptive',KEEP_STD=1,physics_dt=.0025,decimation=4,solver_position=32,solver_velocity=4,
    full_D0_D7_and_noise=True,original_reward_hardware_unchanged=True,episode_limit_seconds=20),
   learning_window=dict(max_parent_load_learn_save_exit_seconds=1800,exit_headroom_seconds=60),
   launch_order='GPU0 learning thenGPU1 learning, original solecanonical sequential intervals; native/fullrestore0PPO uncharged',
   canonical=source['canonical'],extra_budget_seconds=0,scope_no_airborne_jump_S8_or_second_gate_PPO=True,
   training_admitted=False,status='ASSIGNED_SOURCE_PINNED_NATIVE_FULLSTATE_AND_CANONICAL_BRIDGE_REQUIRED',
   required_before_PPO=['Actual own20k original-source CPU/STD/17Adam/sourcefreeze and geometry binding',
    'Own new-task command or route candidate CPU inverse/source negatives; no deploy oracle or live correction',
    'Own physical native and all8typed/globalnamed/privateCPUCUDA disk restore/sourceepisode+1/readback',
    'Actual physicalGPU UUID/free resource/own fcntl lease, parent/guardian/child identities',
    'Original remote canonical210 owner holds both locks, one active segment, no overlapping charge'],
   selected_source_limit='GPU0 source3c97 is G3WAVE35 fullstate to be explicitly migrated to CURB; not an already qualified CURB source' if gpu==0 else 'GPU1 source24b is stored5degree fullstate; 8/10degree were only observed frozen evaluations')
  put(Q/('job'+str(gpu))/'TASK_ASSIGNMENT.json',job);jobs.append(job)
 put(R/'TWO_PHYSICAL_GPU_TASKS_SOURCE_PINNED_CPU_ACTUAL.json',dict(epoch=time.time(),jobs=jobs,all822_original_runtime_source_asset_bytes_SHA_exact=True,
   no_CUDA_PPO_budget_target_upload_or_admission_yet=True,source_originals_and_failed_candidates_preserved=True))
 existing=Path('MOD4_S5_SINGLE_W35_MATCHED35_20261015/reports/S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json');v=json.loads(existing.read_bytes())
 assert v['cell']['seed']==20260928
 put(R/'ORIGINAL35_ACTUAL_SEED_SCOPE_CORRECTION_CPU_ACTUAL.json',dict(epoch=time.time(),original_report=str(existing.resolve()),original_SHA=H(existing),actual_seed=20260928,
   original_matched_A_B_C27_27_remains_valid=True,not_development_seed20261002_credit=True,
   corrected_missing_matrix='All six devseed02/03 x nominal/white_v2/white_v3 original35 A/B/C cells remain unexecuted; old60928/white_v3 is a separate historical matched cell.',
   no_old_source_report_flag_or_GPU_case_overwritten_or_rerun=True))
 print(json.dumps(dict(assigned_tasks=[x['task_id'] for x in jobs],physical_GPUs=[0,1],original_files=len(meta['rows']),actual_training_not_yet_admitted=True,actual35seed_corrected=20260928)),flush=True)
if __name__=='__main__':main()
