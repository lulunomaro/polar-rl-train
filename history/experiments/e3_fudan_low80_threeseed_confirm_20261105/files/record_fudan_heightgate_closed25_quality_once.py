"""One completed fresh25 quality record through original validations and short scoped add."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_heightgate_closed25_quality_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','565c504fbe62649c31f9962c56d83f71fdac888a','HEAD')
r=json.loads((D/'FDN_HEIGHTGATE_CLOSED25_QUALITY_DECISION_V1.json').read_bytes())
assert r['training']['new_N20000']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)and all(v==0 for v in r['training']['base_counters'].values())and r['training']['inherited_old_iterations']==r['training']['bad_candidate_reads']==0
assert r['source']['sha256']=='bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2'and r['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_HEIGHTGATE_PROMOTION'and r['goal_complete']is False
assert r['original_N80']['execution_qualified']is True and r['original_N80']['actual_original_parent_qualified']is True and r['original_N80']['actual_parent_kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE'and r['original_N80']['recovery_first_episode_credits']==0 and r['original_N80']['original_request_denominator']==74
assert all(v['complete_finite_cases']==5 and v['engineering_credits']==0 for v in r['nominal_MuJoCo31']['comparison'].values())and all(r['training']['original_owner_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and r['training']['outer_wait']['original_owner_reaped']is True
err=json.loads((D/'FDN_HEIGHTGATE_FROZEN_BUILDER_V1_NEWLINE_ERRATUM.json').read_bytes());assert err['PT_SDK_SSH_GPU_C_or_native_operations']==0 and err['native_W9_owner_or_worker_changed']is False
note=(D/'CURRENT_PROGRESS_V19_HEIGHTGATE_CLOSED25_QUALITY_RESULT.md').read_text(encoding='utf8')+'\n\n'+(D/'FDN_HEIGHTGATE_CLOSED25_QUALITY_RESULTS_V1.md').read_text(encoding='utf8')
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
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual low-positive-tracking heightgate fresh1cd N20000 new25/dualAdam500/24m base0, original owner actualGO through save/SDKclose/inner+outer wait/cost/leases all closed. Full146247539B candidate bf824 kept, native1200/9600/2400/pending0. Allcore/physics/DR/commands/oldfall-normal/negative-reward/acceptance unchanged; actual constructed positive1/.2/.5 weights with installed gate proven. Immutable first11 evidence plus passive pre-reset11996400 low samples/29991 episodes distinguish peaks from reset height;99.77percent above-height peaks are not skill credit. Original N80 actual V5_HEIGHTGATE+matching collector qualified0of74, normal physical0of6; MuJoCo10 finite cases both0of5, candidateheight.195248/speed1.01209/XY7.844078 versus mother.241437/.038073/.639393, nominal only not fullDR/hardware or causalnative proof. CPU export correct names, wholeCPU once and338873B14pi artifact only, no source model for status or Git. Preserve source-only AppV6 validCRLF rejection before output and newV2 byte-preserving correction, unchanged7dependencies/3metadata adapter source. KEEP original1cd/Registryv12, no bf824 promotion or goal completion; all full candidates retained. Alltext success/failure/code/reports included; original recorder validation/redaction/hashes unchanged, only2 short exact git-add scopes+full stagedset, feature-only mainreadonly, no model/raw/JSONL/geometry stat-read-hash for Git and no once/physical replay.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-lowheightgate-closed25-quality-keep-mother')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial_id='e3-fudan-lowheightgate-closed25-quality-keep-mother'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 low positive tracking heightgate N20000 closed25; original0of74 and nominal0of5, keep mother','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation','actual-N20000-T48-fresh25-twoAdam500-24m-base0;original-GO-resource4FDs-and-all-inner-outer-waits-cost-lease-release;full146247539-bf824-1200native-9600physics-2400feedback-pending0;real-positive-tracking-heightgate-weights1-.2-.5-oldfall-normal-core-physics-DR-commands-acceptance-unchanged;first11-native-proof-and-pre-reset11996400samples-29991episode-peaks-not-acceptance;qualified-original-V5-HEIGHTGATE-matching-reader0of74-normalphysical0of6;oneCPUwhole-export-correctEXCLUDED-imports338873-14pi;ten-real-MuJoCo31-finite-both0of5-candidate-speed1.01209-XY7.844078-no-causalnative-claim;sourceCRLF-localerror-before-mkdir-and-byte-preservingV2-fix;keep1cd-nobf824-promotion-goalactive;all-current-text-original-validation-redaction-hashes-short-exact-git-add-stagedset;no-model-raw-Git-reads-featureonly-mainreadonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
