"""Archive this real finite LR-scale trial once; never re-execute physics or earlier records."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_lrschedule001_closed_quality_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','f50e04481bc476934e671d23f094d259a11d5101','HEAD')
r=json.loads((D/'FDN_LRSCHEDULE001_CLOSED_QUALITY_DECISION_V1.json').read_bytes());bridge=json.loads((D/'FDN_LRSCHEDULE001_W12_HANDOFF_STATUS.json').read_bytes());assert bridge['phase']=='COMPLETE_ACTUAL_WINDOW_AND_INDEPENDENT_EVALUATION'and bridge['automatic_retry']is False
w=r['training']['new_N20000'];u=w['updates'];n=r['original_N80'];c=r['nominal_MuJoCo31']['comparison']['candidate'];cfg=r['training']['actual_fresh_learner_config']
assert 0<u<=25 and w['policy_optimizer_steps']==w['encoder_optimizer_steps']==20*u and w['transitions_seen']==960000*u and all(v==0 for v in r['training']['base_counters'].values())and r['training']['inherited_old_iterations']==r['training']['bad_candidate_reads']==0
assert cfg['initial_std']==.05 and cfg['learning_rate']==1e-5 and cfg['min_learning_rate']==1e-7 and cfg['max_learning_rate']==1e-4 and cfg['encoder_learning_rate']==.001 and r['training']['main_optimizer_LR_schedule_scale']==.01
assert r['source']['sha256']==r['candidate_full_save']['sha256']and r['Registry_v12_and_selected_1cd_unchanged']is r['all_complete_candidates_preserved']is True and r['goal_complete']is False
assert n['execution_qualified']is n['actual_original_parent_qualified']is True and n['actual_parent_kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V7_LRSCHEDULE001'and n['original_request_denominator']==74 and 0<=n['recovery_first_episode_credits']<=74
assert all(v['complete_finite_cases']==5 and 0<=v['engineering_credits']<=5 for v in r['nominal_MuJoCo31']['comparison'].values())and all(r['training']['original_owner_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and r['training']['outer_wait']['original_owner_reaped']is True
note=(D/'CURRENT_PROGRESS_V24_LRSCHEDULE001_CLOSED_QUALITY_RESULT.md').read_text(encoding='utf8')+'\n\n'+(D/'FDN_LRSCHEDULE001_CLOSED_QUALITY_RESULTS_V1.md').read_text(encoding='utf8');dest.mkdir(parents=True);files=[];rows=[]
NO={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.png','.jpg','.jpeg','.webp','.usd','.usda','.usdc','.zip','.mp4','.xml','.stl','.obj','.ply','.dae','.mesh','.pyc','.pyo','.tmp','.partial','.jsonl','.ndjson','.csv','.bin'}
for p in sorted(D.rglob('*')):
 if '__pycache__'in p.parts:continue
 row=dict(source_path=str(p))
 if p.suffix.lower()in NO or p.name=='RESULT.json':row['status']='weight_geometry_image_video_raw_or_transient_reference_only_skipped_before_stat_read_hash';rows.append(row);continue
 if not p.is_file():continue
 raw=p.read_bytes();target=dest/'files'/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);rp=target.relative_to(repo).as_posix();files.append(rp);row.update(status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=rp);rows.append(row)
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_current_text_reports_snapshot=True,models_raw_images_video_geometry_not_opened_for_Git=True,physical_or_once_replay_for_Git=False,main_push_or_reset=False,short_scoped_git_add_adapter=True),indent=2),encoding='utf8');(dest/'.gitattributes').write_text('* -text\n',encoding='utf8')
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual fresh1cd N20000/T48 finite25 main LR schedule scale0.01 relative to qualified W11 STD0.05 no-heightgate baseline: initial/min/max together 1e-5/1e-7/1e-4. Encoder LR0.001, STD0.05, exact PPO core, all original rewards/commands/timeout8/physics/fullDR/acceptance unchanged. Dynamic real counters/scores/decision, no preset success/failure. Original1cd actor8+critic8 MLP-only source once, fresh encoder/latent-cols0/Adam/private generator/counters; bad checkpoints not resumed. Preserve original owner exact budget/locks/actual GO-through-SDK-close-wait-account-release. Controlled new-purpose local bridge waits actual training qualification/inner+outer wait/cost/release before immediate original N80 stage/dispatch; original eval rechecks all gates, no cross-owner lock handoff, signals, copied ledger, automatic retries or changed physics. Native and eval actual evidence/CPU pi export/ten nominal finite cases and all preserved failures/text are included; bridge itself uses no model/raw/C IO. Source-only tools and KL diagnostic are not skill evidence. Registryv12/1cd unchanged; positive evidence if any retained for confirmation, not automatic multi-seed/hardware graduation. Original record validation/redaction/hashes and exact staged set retained; only2 short git-add scopes. Model/raw/JSONL/media/geometry skip before stat/read/hash; feature-only atomic push and main read-only, no physical or old-once replay for Git.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'));sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git;trial_id='e3-fudan-lrschedule001-closed-quality'

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/'+time.strftime('%Y%m%d')+'-'+trial_id)and set(args[3:])==set(files);answer=original_git('add','--',rel.as_posix(),record_path);assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path};return answer
 return original_git(*args)

record_experiment.git=scoped_git;sys.argv=['record_experiment.py','--id',trial_id,'--title',f'E3 main LR schedule scale0.01 N20000 closed{u}; original{n["recovery_first_episode_credits"]}of74 nominal{c["engineering_credits"]}of5; Registryv12 unchanged','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation',f'actual-N20000-T48-finite{u}-twoAdam{20*u}-optimized{960000*u}-base0;single-main-LR-schedule-factor0p01-initial1e-5-min1e-7-max1e-4-STD005-encoder001-unchanged-core;original-realGO-innerouterwait-cost-leases;controlled-immediate-postclose-N80-new-purpose-original-gates-actual-V7-LRSCHEDULE001-74plus6;one-source-CPU14pi-export-ten-real-MuJoCo31-completefinite;actual-metadata-and-KL-not-skill-allfailures-preserved;Registryv12-unchanged-goalactive-dynamic-decision;alltext-full-recorder-validation-redaction-hashes-two-exact-pathspec-stagedset;no-modelraw-Git-reads-featureonly-mainreadonly','--files',*files]
record_experiment.main();head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag);remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
