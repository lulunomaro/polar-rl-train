"""One meaningful completed-quality record using the original recorder and short git-add pathspecs."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_timeout8_closed72_quality_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:
  print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','cce218551eba7d527e4b611a41bc6536c1f75039','HEAD')
r=json.loads((D/'FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json').read_bytes())
assert r['training']['new_N20000']['updates']==72 and r['training']['cumulative']['updates']==205 and r['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION'and r['goal_complete']is False
assert r['original_N80']['execution_qualified']is True and r['original_N80']['actual_original_parent_qualified']is True and r['original_N80']['recovery_first_episode_credits']==0 and r['original_N80']['original_request_denominator']==74
assert all(v['complete_finite_cases']==5 and v['engineering_credits']==0 for v in r['nominal_MuJoCo31']['comparison'].values())
assert all(r['training']['original_owner_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and r['training']['outer_wait']['original_owner_reaped']is True
note=(D/'CURRENT_PROGRESS_V13_TIMEOUT8_CLOSED72_QUALITY_NOT_IMPROVED.md').read_text(encoding='utf8')+'\n\n'+(D/'FDN_TIMEOUT8_CLOSED72_QUALITY_RESULTS_V1.md').read_text(encoding='utf8')
dest.mkdir(parents=True);files=[];rows=[]
NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.png','.jpg','.jpeg','.webp','.usd','.usda','.usdc','.zip','.mp4','.xml','.stl','.obj','.ply','.dae','.mesh','.pyc','.pyo','.tmp','.partial'}
for p in sorted(D.rglob('*')):
 if '__pycache__'in p.parts:continue
 row=dict(source_path=str(p))
 if p.suffix.lower()in NO or p.name=='RESULT.json':
  row['status']='weight_geometry_image_video_raw_or_transient_reference_only_skipped_before_stat_read_hash';rows.append(row);continue
 if not p.is_file():continue
 raw=p.read_bytes();target=dest/'files'/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);rp=target.relative_to(repo).as_posix();files.append(rp);row.update(status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=rp);rows.append(row)
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_current_text_reports_snapshot=True,models_raw_images_video_geometry_not_opened_for_Git=True,physical_or_once_replay_for_Git=False,main_push_or_reset=False,short_scoped_git_add_adapter=True),indent=2),encoding='utf8')
(dest/'.gitattributes').write_text('* -text\n',encoding='utf8')
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual W6 N20000/T48 closed72/full learner cumulative205; both Adam1440 new, 69120000 optimized transitions, 48 pending controls fully saved but not optimized. Candidate3e64 preserved, no promotion. Actual original N80 parent qualification was already true; local collector stale V2 kind misread V3 as false. Both false output and exact metadata-only kind correction preserved, no physical replay/requalification. Actual five-pose nominal MuJoCo has both0/5 but candidate stays low/drifts3.020520m and mother raises body. Do not equate actor behaviors or claim causal native regression. Training79,976 low episodes credit0 is descriptive, not zero reward. No effective reward decomposition proof; next fresh1cd learner-start hypothesis remains source preparation, not deployed. Preserve host file-observation edit denial corrected by read-before-edit; no native effect. All text and failures snapshot; original recorder validations retained, only git-add invocation shortened to its exact two scoped paths and full staged-set checked to avoid prior Windows argv error. Main untouched. Never rerun this record or physical tasks for synchronization.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-timeout8-closed72-quality-keep-mother')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git
trial_id='e3-fudan-timeout8-closed72-quality-keep-mother'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 timeout8 N20000 closed72; actual original and nominal quality not improved; keep frozen mother','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation','actual-N20000-T48-72PPO-bothAdam1440;full-save-and-48-unoptimized-controls;actual-inner-outer-waits-cost-leases;actual-parent-qualified-original-N80-0of74-normal-physical0of6;stale-collector-kind-V2-vs-V3-false-and-metadata-only-correction-preserved-no-physical-replay;actual-MuJoCo31-ten-finite-cases-both0of5-height-drift-distinguished;keep-1cd-no-3e64-promotion;all-current-text-failures-source-hypotheses-point-in-time;original-recorder-redaction-hash-validation-with-short-exact-pathspecs;no-model-raw-status-Git-reads;feature-only-main-readonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
