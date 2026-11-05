"""Record actual full55 continuation closed quality, preserve every failure and pending scope; never replay."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_resume55_admission2_closed_quality_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','698de83b7c647403183f3189fcafbe1d4b573463','HEAD')
quality=json.loads((D/'FDN_RESUME55_CLOSED_QUALITY_DECISION_V1.json').read_bytes());status=json.loads((D/'FDN_RESUME55_W14_ADMISSION2_HANDOFF_STATUS.json').read_bytes());pointer=json.loads((D/'FDN_N20000_W14_RESUME55_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closed=json.loads(Path(pointer['path']).read_bytes());m=closed['metadata'];f=m['FDN_FINAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];scope=json.loads((D/'FDNRESUME55_FROZEN_ORIGINAL_SCOPE_RESULT.json').read_bytes());export=json.loads((D/'FDNRESUME55_PI_ONLY_EXPORT_STARTED_ONCE.json').read_bytes())
assert status['phase']=='COMPLETE_ACTUAL_WINDOW_AND_INDEPENDENT_EVALUATION'and status['goal_complete']is False and closed['closed']is True and f['version']==8 and f['complete_save']is f['final']is True and f['full_learner_resume']is True and f['error']is None and f['close_errors']==[]
assert end['errors']==[]and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['actual_wait_returncode']==0 and outer['original_owner_reaped']is True and q['qualified']is True and all(q['checks'].values())
assert f['base_counters']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)and 0<f['window_counters']['updates']<=25 and all(f['counters'][k]==f['base_counters'][k]+f['window_counters'][k]for k in f['base_counters'])and f['source_checkpoint']['source_sha256']=='55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7'
assert scope['execution_qualified']is True and all(scope['execution_checks'].values())and scope['actual_parent_wait_qualification']['qualified']is True and scope['actual_parent_wait_qualification']['kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V8_RESUME55'
assert export['complete']is True and export['source']['sha256']==f['latest_complete_save']['sha256']==quality['source']['sha256']==scope['source_binding']['sha256']and quality['goal_complete']is False and quality['Registry_v12_and_selected_1cd_unchanged']is True
note=(D/'CURRENT_PROGRESS_V31_RESUME55_CLOSED25_NOMINAL_END5.md').read_text(encoding='utf8')
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
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual Root8 complete55 learner continuation and independent original E3 + nominal31 five-pose evaluation, whole-source once/cache; base/window/cumulative and all real innerouterwait/cost/release are separate from skill scores. Nominal strict terminal uses current streak>=25, not loose ever+last-good. Original74 result and fullDR holdout pending remain distinct; Registry/H1 unchanged/no auto-promotion/no goal-complete. Include prior W13 zeroGO+release, W14 actualGO-first2-close, all source-only preparation failures/pending, new fullsave/pi-export metadata, and next frozen8e27 holdout text. No new training merely for archive; models/raw/media/geometry skipped before stat/read/hash; original recorder fullvalidation/redaction/hash retained, only short2exact scoped git-add + full staged set. Feature only/main readonly; no old once/physical/model replay.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-resume55-admission2-closed-quality')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial_id='e3-fudan-resume55-admission2-closed-quality'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 full55 learner resume real new25 closed; nominal strict end5of5, original0of74, frozen8e27 holdout pending','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation','actualRoot8-fulllearner-resume55-base25-new25-cumulative50;N20000-T48-original-fullDR;twoAdam-model-STD-mutableLR-privategenerator-loaded-once;all-actualSDKclose-innerouterwait-account-settle-release;originalN80-parent8-actualqualification;nominal31-five-pose-complete-finite-ever-and-strict-current-terminal-separated;new-native-holdout-pending-null-not-zero;Registry-H1-unchanged;source-format-failures-preserved;alltext-pointtime;original-recorder-fullvalidation-redaction-hash-short-exact-stagedset;feature-only-mainreadonly-no-modelraw-Git-reads','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
