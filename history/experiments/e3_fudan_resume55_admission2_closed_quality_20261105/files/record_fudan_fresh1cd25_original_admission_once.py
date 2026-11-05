"""Record this staged original admission, not fabricated native updates; never replay."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_fresh1cd25_original_admission_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','7ad15203471201e1534dbc82ba85ee6bfc99f69c','HEAD')
r=json.loads((D/'FDN_N20000_W7_FRESH1CD_STAGE_RESULT.json').read_bytes());dispatch=json.loads((D/'FDN_N20000_W7_FRESH1CD_ORIGINAL_OWNER_DISPATCH_RESULT.json').read_bytes());launch=json.loads(dispatch['stdout']);staged=json.loads(r['stdout'])
assert r['returncode']==r['owner_source_preflight_rc']==r['source_PT_reads']==r['SDK_GPU_GO_C_or_lock_operations']==0 and r['num_envs']==20000 and staged['source_file_count']==450
assert r['warm_source']['sha256']=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'and r['warm_source']['mode']=='ACTOR_CRITIC_MLP_ONLY_FRESH_FDN_LEARNER'and r['warm_source']['new_window_updates']==25 and r['warm_source']['all_new_learner_counters_start_zero']is True and r['warm_source']['bad_candidate_not_continued']is True
assert dispatch['returncode']==0 and launch['controller_pid']==1625502 and launch['root']==r['root']==dispatch['root'] and launch['original_owner_resource_wait_max_seconds']==1800
assert (D/'source_fudan_frozen_native_eval_v4_fresh1cd_timeout8/frozen_sequence_mean.py').exists()and(D/'collect_fudan_fresh1cd_frozen_original_once.py').exists()
note=(D/'CURRENT_PROGRESS_V14_FRESH1CD25_STAGED_ORIGINAL_WAIT.md').read_text(encoding='utf8')
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
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual new450-source stage and original bounded-parent submission only. Fresh1cd actor8+critic8 MLP warm, fresh random encoder/new latent columns0/STD.5/twoAdam/LR/private-generator/counters; no bad205 lineage continuation or inherited updates. New N20000/T48 finite25 cap is not completed25. Initial original preGO resource wait and null worker/init/update remain evidence of phase, not skill failure or native training. Later metadata may advance; consult actual GO/INIT/UPDATE/closed fields, not this point-time title. Root4 inference sources and matching V4_FRESH1CD reader prepared; no physical assessment/export executed for this trial yet. Preserve local owner-builder indentation anchor failure before SSH and new-source-only correction; preserve plant normalizer false negative with unchanged real20000us queue. Original budget/locks/physics/DR/commands/acceptance unchanged. All reports and failures snapshot, model/raw suffixes skipped before stat/read/hash. Original record_experiment redaction/validation/hash/tag remains, only git-add uses exact2 scoped paths plus staged-set equality. Feature only; main read-only. No record or physical replay for synchronization.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-fresh1cd25-original-admission')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial_id='e3-fudan-fresh1cd25-original-admission'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 fresh1cd MLP-only Fudan N20000 finite25 pilot staged; original bounded admission submitted, no fabricated native count','--kind','training','--note-file',str(dest/'NOTE.md'),'--validation','actual450-nonPT-source-stage-owner-preflight-no-model-SDK-GO;original-parent-controller1625502-bounded1800-resource-admission;fresh1cd-MLP-only-not-205-resume-N20000-T48-cap25-counts-zero;single-AST-native-source-unchanged-core-math-and-timing;local-indent-anchor-failure-and-source-only-v2-fix-preserved;new-root4-frozen7plus3-and-exact-V4-FRESH1CD-reader-prepared-not-physically-run;all-current-text-point-in-time;original-recorder-redaction-hashes-and-short-exact-git-add-staged-set;no-model-raw-Git-reads;feature-only-main-readonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
