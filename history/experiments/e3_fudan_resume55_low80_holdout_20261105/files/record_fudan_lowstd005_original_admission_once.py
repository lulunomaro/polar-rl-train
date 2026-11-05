"""Record this staged original admission, not fabricated native updates; never replay."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_lowstd005_original_admission_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','b8be2526473b439b9b6c529a3ce35da7a320395a','HEAD')
r=json.loads((D/'FDN_N20000_W10_LOWSTD005_STAGE_RESULT.json').read_bytes());dispatch=json.loads((D/'FDN_N20000_W10_LOWSTD005_ORIGINAL_OWNER_DISPATCH_RESULT.json').read_bytes());launch=json.loads(dispatch['stdout']);staged=json.loads(r['stdout'])
assert r['returncode']==r['owner_source_preflight_rc']==r['source_PT_reads']==r['SDK_GPU_GO_C_or_lock_operations']==0 and r['num_envs']==20000 and staged['source_file_count']==450
assert r['warm_source']['initial_policy_gaussian_std']==.05
assert r['warm_source']['sha256']=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'and r['warm_source']['mode']=='ACTOR_CRITIC_MLP_ONLY_FRESH_FDN_LEARNER'and r['warm_source']['new_window_updates']==25 and r['warm_source']['all_new_learner_counters_start_zero']is True and r['warm_source']['bad_candidate_not_continued']is True
assert dispatch['returncode']==0 and launch['controller_pid']==1633589 and launch['root']==r['root']==dispatch['root'] and launch['original_owner_resource_wait_max_seconds']==1800
assert (D/'source_fudan_frozen_native_eval_v6_lowstd005/frozen_sequence_mean.py').exists()and(D/'collect_fudan_lowstd005_frozen_original_once.py').exists()
note=(D/'CURRENT_PROGRESS_V20_LOWSTD005_STAGED_ORIGINAL_WAIT.md').read_text(encoding='utf8')
dest.mkdir(parents=True);files=[];rows=[]
NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.png','.jpg','.jpeg','.webp','.usd','.usda','.usdc','.zip','.mp4','.xml','.stl','.obj','.ply','.dae','.mesh','.pyc','.pyo','.tmp','.partial','.jsonl','.ndjson','.csv','.bin'}
for p in sorted(D.rglob('*')):
 if '__pycache__'in p.parts:continue
 row=dict(source_path=str(p))
 if p.suffix.lower()in NO or p.name=='RESULT.json':
  row['status']='weight_geometry_image_video_raw_or_transient_reference_only_skipped_before_stat_read_hash';rows.append(row);continue
 if not p.is_file():continue
 raw=p.read_bytes();target=dest/'files'/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);rp=target.relative_to(repo).as_posix();files.append(rp);row.update(status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=rp);rows.append(row)
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_current_text_reports_snapshot=True,models_raw_images_video_geometry_not_opened_for_Git=True,physical_or_once_replay_for_Git=False,main_push_or_reset=False,short_scoped_git_add_adapter=True),indent=2),encoding='utf8')
(dest/'.gitattributes').write_text('* -text\n',encoding='utf8')
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual450-source lowSTD005 new-purpose stage/preflight0 and original bounded controller1633589 submission. Single policy initial Gaussian STD0.5-to0.05 relative to prior W8 no-heightgate baseline; failed heightgate branch not compounded. Fresh1cd8+8MLP-only with fresh encoder/STD/Adam/LR/counters; cap25/N20000/T48. Original reward, physics/fullDR, commands, action scale, original N80 and nominal joint acceptance unchanged. Passive pre-reset height/peaks/seven criteria do not affect reward/credit. All source metadata bridges/actual-wait closure/resources retained; six native adapters/ten frozen modules/five future evaluation entries prepared without model/SDK/physics checks. Preserve child pre-publication memory-anchor error and parent native-builder V1 indentation error plus V2 correction, original failures unchanged. Source checks are not native input-weight equivalence or skill passes. Staged title claims no completed native updates; actual own metadata is frozen point-in-time, including later phases if observed. Previous V19 postpush verification captured. All text/error reports included; model/raw suffix skipped before stat/read/hash; original recorder validation, redaction, exact staged set and feature-only atomic annotated push remain, main read-only. No source/physical/old once rerun for Git.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-lowstd005-original-admission')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial_id='e3-fudan-lowstd005-original-admission'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 initial policy STD005 finite25 N20000 original admission; original physics and acceptance retained','--kind','training','--note-file',str(dest/'NOTE.md'),'--validation','actual450-nonPT-stage-preflight0-original-controller1633589-bounded1800;single-initial-Gaussian-STD005-relative-W8-no-heightgate-baseline;fresh1cd-MLP-only-N20000-T48-cap25-base0-no-bad-resume;passive-seven-pre-reset-criteria-not-acceptance;original-owner-core-physics-DR-commands-actualwait-budget-unchanged;V6-frozen-metadata-three-changed-seven-byte-identical-correct-reader-kind;source-local-errors-preserved-before-publication-no-native-replay;all-text-pointtime-original-recorder-validation-short-exact-pathspec-main-readonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
