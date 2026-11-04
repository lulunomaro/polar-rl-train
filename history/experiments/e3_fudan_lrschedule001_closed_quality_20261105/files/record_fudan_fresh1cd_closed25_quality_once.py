"""One completed fresh25 quality record through original validations and short scoped add."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_fresh1cd_closed25_quality_20261105');dest=repo/rel

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists()
G('merge-base','--is-ancestor','7ee034128525a83dc3a33284bfe219eece934e26','HEAD')
r=json.loads((D/'FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json').read_bytes())
assert r['training']['new_N20000']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)and all(v==0 for v in r['training']['base_counters'].values())and r['training']['inherited_old_iterations']==r['training']['bad_candidate_reads']==0
assert r['source']['sha256']=='246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2'and r['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_246AC_PROMOTION'and r['goal_complete']is False
assert r['original_N80']['execution_qualified']is True and r['original_N80']['actual_original_parent_qualified']is True and r['original_N80']['actual_parent_kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD'and r['original_N80']['recovery_first_episode_credits']==0 and r['original_N80']['original_request_denominator']==74
assert all(v['complete_finite_cases']==5 and v['engineering_credits']==0 for v in r['nominal_MuJoCo31']['comparison'].values())and all(r['training']['original_owner_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and r['training']['outer_wait']['original_owner_reaped']is True
err=r['export_zero_input_import_failure_preserved']['old_error'];assert all(v==0 for v in err['source_IO'].values())and all(v==0 for v in err['own_save_IO'].values())
note=(D/'CURRENT_PROGRESS_V17_FRESH1CD_CLOSED25_ORIGINAL_NOT_IMPROVED.md').read_text(encoding='utf8')+'\n\n'+(D/'FDN_FRESH1CD_CLOSED25_QUALITY_RESULTS_V1.md').read_text(encoding='utf8')
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
(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nActual fresh1cd new25/dualAdam500/24m, base0 not old205 or43090, full146165047B candidate246ac, native1200/9600/2400 and0pending. W7 original1800 zero-GO timeout/allactualwait preserved, read-only release and W8 new450stage/GO/native10 proof then actual close included. Whole original N80 actual parent V4_FRESH1CD + matching collector already qualified,0/74/normal physical0of6, no reader requalification. Nominal MuJoCo10 finite cases: both0of5 but height/drift differentiated, no native causal regression or hardware/fullDR claim. Old CPUexport import failed before any model/ownsave IO; old error/source retained, newV2 only actualEXCLUDED imports/pre-read normalized path+SHA, same14pi math/CPU whole cache/solephysical read,338809B derived only. End1200 is400-timeout boundary, low_height.1781 is not whole-episode peak evidence; no unsupported reward-root-cause claim. All candidate/mother preserved, no promotion or goal completion. All current text/failures archived, original recorder validation/redaction/hash unchanged, only2 exact scoped git-add paths + staged-set equality to avoid Windows argv. No model/raw/JSONL/geometry stat/read/hash for synchronization, feature only/main readonly. Never rerun this record or physical purposes.\n',encoding='utf8')
files.extend((rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  record_path=args[2];assert record_path.startswith('history/experiments/20261105-e3-fudan-fresh1cd-closed25-quality-keep-mother')and set(args[3:])==set(files)
  answer=original_git('add','--',rel.as_posix(),record_path)
  assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{record_path}
  return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial_id='e3-fudan-fresh1cd-closed25-quality-keep-mother'
sys.argv=['record_experiment.py','--id',trial_id,'--title','E3 fresh1cd Fudan N20000 closed25; actual original0of74 and nominal0of5, keep mother','--kind','evaluation','--note-file',str(dest/'NOTE.md'),'--validation','actual-fresh25-N20000-T48-twoAdam500-24m-base0-no205-splice;fullsave-native1200-9600-2400-no-pending;actual-original-inner-outer-waits-cost-lease-release;W7-zeroGO-timeout-and-readonly-release-W8-newadmission-preserved;actual-N80-V4-FRESH1CD-qualified0of74-normal-physical0of6-no-reader-replay;CPUexport-V1-zeroinput-import-failure-and-V2-actualEXCLUDED-fix-onephysical-decode;actual-MuJoCo31-tenfinite-both0of5-height-drift-differentiated;postreset-endheight-not-whole-episode-claim;keep-1cd-no246ac-promotion;all-current-text-errors-original-recorder-validation-redaction-hashes-short-scoped-add-staged-set;no-model-raw-Git-reads;feature-only-main-readonly','--files',*files]
record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial_id;obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),original_recorder_full_validation_retained=True,staged_set_verified=True,physical_or_record_replay=False,main_push_or_reset=False),indent=2))
