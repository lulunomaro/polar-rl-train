"""Archive actual P0 repair, superseded assumptions and all text evidence; no physics/model replay."""
from pathlib import Path
import json,sys,hashlib,subprocess,time
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v2_p0_hw300n60_local_release_20261105');dest=repo/rel

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','c2fdea824af71ce35d0947ae189626b07c2ccd35','HEAD')
C=D/'candidates/HW300N60';v=json.loads((C/'VALIDATION.json').read_bytes());t=json.loads((C/'RUNTIME_TARGET_CPU_VALIDATION.json').read_bytes());stop=json.loads((C/'MECHANICAL_STOP_ENGINE_VALIDATION.json').read_bytes());delivery=json.loads((D/'DELIVERY_INDEX.json').read_bytes());spec=json.loads((D/'MECHANICAL_LIMITS_SPEC_V2_HW300N60.json').read_bytes())
assert v['passed']is t['passed']is stop['passed']is True and all(v['checks'].values())and all(t['checks'].values())and len(v['checks'])==100 and len(t['checks'])==9 and spec['hardware_configuration']['extended_eye_length_m']==.2 and spec['hardware_configuration']['compressed_eye_length_m']==.14 and spec['hardware_configuration']['nominal_extension_force_N']==300 and spec['gas_law']['force_curve_calibrated']is False and delivery['physical_target_PhysX_verified']is False and delivery['old_models_Registry_or_budget_modified']is False
known={str((C/x['path']).relative_to(D)):dict(bytes=x['bytes'],sha256=x['sha256'],producer='DELIVERY_INDEX.json')for x in delivery['files']};known[Path(delivery['artifact']).name]=dict(bytes=delivery['bytes'],sha256=delivery['sha256'],producer='DELIVERY_INDEX.json')
old=json.loads((D/'BUILD_RECEIPT.json').read_bytes())
for row in old['outputs'].values():known.setdefault(str(Path(row['path'])),dict(bytes=None,sha256=row['sha256'],producer='superseded BUILD_RECEIPT.json; bytes not recorded'))
# Both asset builders proved the source mesh copies byte-identical. The old copy
# can reference the same delivery-index mesh identity without re-opening geometry.
for x in delivery['files']:
 if x['path'].startswith('package/mjcf/assets/'):known.setdefault(str(Path(x['path'])),dict(bytes=x['bytes'],sha256=x['sha256'],producer='both builder copy invariants + DELIVERY_INDEX.json same source mesh'))
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
dest.mkdir(parents=True);rows=[];files=[]
NO={'.pt','.pth','.ckpt','.onnx','.npz','.npy','.safetensors','.pt2','.pkl','.pickle','.usd','.usda','.usdc','.zip','.obj','.stl','.ply','.dae','.mesh','.png','.jpg','.jpeg','.mp4','.webp','.bin','.pyc','.pyo','.tmp','.partial','.jsonl','.ndjson','.csv'}
for p in sorted(D.rglob('*')):
 rp=p.relative_to(D)
 if '__pycache__'in rp.parts:continue
 row=dict(source_path=str(p))
 if p.suffix.lower()in NO:
  row.update(status='binary_geometry_weight_raw_or_transient_reference_only_skipped_before_stat_read_hash',producer_identity=known.get(str(rp),dict(bytes=None,sha256=None,producer='not recorded; no new binary read for Git')));rows.append(row);continue
 if not p.is_file():continue
 raw=p.read_bytes();text,n=redact(raw.decode('utf8'));data=text.encode('utf8')if n else raw;target=dest/'files'/rp;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);ar=target.relative_to(repo).as_posix();files.append(ar);row.update(status='text_redacted_original_retained'if n else 'complete_text',original_bytes=len(raw),original_SHA256=hashlib.sha256(raw).hexdigest(),archive_path=ar,archive_bytes=len(data),archive_SHA256=hashlib.sha256(data).hexdigest(),redactions=n);rows.append(row)
(dest/'INDEX.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_P0_text_reports_included=True,canonical_MJCF_XML_is_small_text_source_included=True,original_validation_and_redaction_retained=True,models_geometry_or_ZIP_not_reopened_for_Git=True,physics_training_or_old_record_replayed=False,main_push_or_reset=False),indent=2),encoding='utf8')
(dest/'.gitattributes').write_text('* -text\n',encoding='utf8');note=(D/'MOD4V2_P0_RELEASE_REPORT_V1.md').read_text(encoding='utf8');(dest/'NOTE.md').write_text(note+'\n\n## Archive boundary\nIncludes superseded400N candidate/source/receipts and unit-default capability probe note, user-confirmed300N60 stroke pivot, new hardware builder/assets references and portable source XML, continuous IK/runtime, relative target unwrap before-snapshot+fix, actual full-model100 and targetCPU9 checks, separate120-step physical-stop recovery, delivery index and all reports. No actual Isaac/PhysX or100Hz/hardware claim. No old expert/Registry/production hot replacement or extraPPO. Original record validates/redacts/hashes; only two short scoped add paths with exact staged-set. Large artifacts indexed only; no model/raw/oldonce/physics replay for Git.\n',encoding='utf8');files.extend((rel/x).as_posix()for x in('INDEX.json','.gitattributes','NOTE.md'))
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  rp=args[2];assert rp.startswith('history/experiments/20261105-mod4v2-p0-hw300n60-local-release')and set(args[3:])==set(files);answer=original_git('add','--',rel.as_posix(),rp);assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{rp};return answer
 return original_git(*args)

record_experiment.git=scoped_git;trial='mod4v2-p0-hw300n60-local-release';sys.argv=['record_experiment.py','--id',trial,'--title','MOD4v2 HW300N60 P0 mechanical limits repair; local model and target layer pass; native PhysX pending','--kind','repair','--note-file',str(dest/'NOTE.md'),'--validation','confirmed140-200mm60mm300N;continuous8active-follower-nooperatingbox;CAD-equivalent-one-sided-stop-not-realmesh-contact-claim;full-MuJoCo31body100checks-and-bounded-dynamics;CPUtargetABI9checks-relative-periodic-unwrap;engine-stop-recovery120steps;portable292fileZIPknownSHA;force-curve-k2000d3-unmeasured-engineering300to420N;208mm-screenshot-rejected-not-forcefit;superseded400N-and-all-source-errors-retained;noPhysX100Hz-hardware-or-oldexpert-graduation;noasset-v1-weights-Registry-budget-productionedit;original-recordvalidation-redaction-hashes-exactstagedset-featureonly','--files',*files];record_experiment.main()
head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head;G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,index_entries=len(rows),all_text_reports_snapshot=True,original_recorder_validation_redaction_hashes_retained=True,staged_set_verified=True,physics_models_or_old_once_replayed_for_Git=False,native_PhysX_verified=False,main_push_or_reset=False),indent=2))
