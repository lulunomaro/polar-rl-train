"""Record this staged original admission, not fabricated native updates; never replay."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_resume55_original_admission_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','d264fd6e5af3e19d92f9505a6374c27be07d928b','HEAD')
r=json.loads((D/'FDN_N20000_W13_RESUME55_STAGE_RESULT.json').read_bytes());dispatch=json.loads((D/'FDN_N20000_W13_RESUME55_ORIGINAL_OWNER_DISPATCH_RESULT.json').read_bytes());launch=json.loads(dispatch['stdout']);staged=json.loads(r['stdout'])
assert r['returncode']==r['owner_source_preflight_rc']==r['source_PT_reads']==r['SDK_GPU_GO_C_or_lock_operations']==0 and r['num_envs']==20000 and staged['source_file_count']==451
assert r['learner_source']['sha256']=='55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7'and r['learner_source']['bytes']==146247985 and r['learner_source']['counters']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)and r['learner_source']['source_envs']==20000 and r['learner_source']['actual_native_policy_steps']==1200 and r['learner_source']['unoptimized_pending_controls']==0
assert dispatch['returncode']==0 and launch['controller_pid']==1645903 and launch['root']==r['root']==dispatch['root'] and launch['original_owner_resource_wait_max_seconds']==1800
assert (D/'source_fudan_frozen_native_eval_v8_resume55/frozen_sequence_mean.py').exists()and(D/'collect_fudan_resume55_frozen_original_once.py').exists()
z=json.loads((D/'reports/FDN_N20000_W13_RESUME55_20261105_091611/CLOSED_RESULT.json').read_bytes());zm=z['metadata'];ze=zm['OWNER_EXIT_ACTUAL.json'];zo=zm['OUTER_OWNER_WAIT_ACTUAL.json'];a2=json.loads((D/'FDN_N20000_W14_RESUME55_ADMISSION2_STAGE_RESULT.json').read_bytes())
assert z['closed']is True and zm['COHORT_FINAL.json']is None and all(v is None for k,v in zm.items()if k.startswith('FDN_'))and all(ze[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and zo['actual_wait_returncode']==0 and zo['original_owner_reaped']is True and zo['original_owner_pid']==1645910 and zo['controller_pid']==1645903 and 'Original preGOresourcewait1800expired'in json.dumps(ze['errors'])and a2['returncode']==a2['owner_source_preflight_rc']==0
note=(D/'CURRENT_PROGRESS_V29_W13_ZERO_GO_W14_STAGED.md').read_text(encoding='utf8')
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
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual W13 original1800 resource timeout ZERO-GO, allFDN/null and actual innerouterwait/costrelease preserved. New W14 separate-purpose451 nonPT stage only, not yetlearning; readonly canonical release summary is not a GPU lease. Root7 whole55afa full learner source (25/500/24m) loader is prepared for unchanged core clone, NOT PHYSICALLY LOADED OR RESTORED IN THIS ATTEMPT. Planned source mutableLR2.562890625e-6, learnedSTD and bothAdam/privategenerator continuation remain pending actual admission; new freshN20000/T48 env/history/queues/globalenvRNG stream-cut, notsource projection or PhysX bitwise resume. Root8/base25/newwindow<=25/cumulative separate. Hyperparams/rewards/core/PD/fullD0D7 and Registry unchanged. Submission and preGO wait are not actual PPO or skill count. Read actual GO/INIT/UPDATE/CLOSED before advancing status. FrozenRoot8 three metadata+seven unchanged files and five unused original-eval/nominal CLIs prepared; new lowholdout strict-current-streak worker/integration are source-only until actual declared purpose. Preserve original local metadata anchor failures and new-source-only corrections, interpreter9009/spawnENAMETOOLONG preexecution errors, and optional observation static tool-attempt history; no model/SDK/GPU/C operations by those source preparations. Original record validation/redaction/hashes and exact staged-set retained, only2 short git-add pathspecs avoid oldWin206. Allcurrenttextpointtime, weight/raw/media/geometry skip beforestat/read/hash. Featureonly/mainreadonly/no oldphysical-or-once replay.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-resume55-original-admission')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial_id='e3-fudan-resume55-original-admission'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 complete55afa finite25 continuation prepared; W13 original resource timeout zeroGO fully waited, W14 new unused admission staged','--kind','training','--note-file',str(dest/'NOTE.md'),'--validation','actual451-nonPT-source-stage-owner-preflight-modelSDKGO0;original-controller1645903-bounded1800-resource-wait;completeRoot7-source55-25-500-24m-exact-learner-not-rewarm-1cd;Root8-currentwindow-base-cumulative-separate;freshN20000-T48-noDRhistorypendingprojection;unchangedPPO-hyperparams-originalresource-account-wait;preparation-errors-preserved;Root8-frozen7plus3-and-correct-parent8-ready;alltextpointtime;original-recorder-redaction-hashes-and-short-exact-stagedset;feature-only-mainreadonly-no-modelraw-Git-reads','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
