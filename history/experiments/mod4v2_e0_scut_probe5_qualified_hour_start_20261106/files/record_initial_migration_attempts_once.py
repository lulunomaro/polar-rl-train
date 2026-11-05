"""One meaningful migration stage: genuine startup failures, repairs and pending A3; no runtime replay."""
from pathlib import Path
import json,sys,hashlib,subprocess,time
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v2_nine_initial_migration_attempts_20261105');dest=repo/rel

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')and not dest.exists();G('merge-base','--is-ancestor','e8e159472cae4543282cc9789aa9592dee2bef9f','HEAD')
a2=json.loads(Path(json.loads((D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());end=a2['metadata']['OWNER_EXIT_ACTUAL.json'];assert a2['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and all(v.get('V2_LEARNER_LOADED.json')is None for v in a2['cases'].values())
stage=json.loads((D/'STAGE_NINE_ADMISSION3_RESULT.json').read_bytes());dispatch=json.loads((D/'DISPATCH_NINE_ADMISSION3_RESULT.json').read_bytes());assert stage['returncode']==stage['owner_import_only_preflight_rc']==dispatch['returncode']==0
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
dest.mkdir(parents=True);rows=[];files=[];skip={'.pt','.pth','.ckpt','.onnx','.safetensors','.npz','.npy','.usd','.usda','.usdc','.zip','.obj','.stl','.ply','.png','.jpg','.webp','.mp4','.pyc','.pyo','.partial','.tmp','.jsonl','.ndjson','.bin'}
for p in sorted(D.rglob('*')):
 if '__pycache__'in p.parts or p.suffix.lower()in skip:
  rows.append(dict(source=str(p),status='binary_model_raw_or_transient_skipped_before_stat_read_hash'));continue
 if not p.is_file():continue
 raw=p.read_bytes()
 try:text=raw.decode('utf-8-sig')
 except UnicodeDecodeError:rows.append(dict(source=str(p),status='non_UTF8_not_archived'));continue
 text,count=redact(text);data=text.encode('utf8');rp=rel/'files'/p.relative_to(D);out=repo/rp;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);files.append(rp.as_posix());rows.append(dict(source=str(p),source_bytes=len(raw),source_SHA256=hashlib.sha256(raw).hexdigest(),archive=rp.as_posix(),archive_bytes=len(data),archive_SHA256=hashlib.sha256(data).hexdigest(),redactions=count,status='point_in_time_live_metadata'if p.name=='LATEST_METADATA.json'else'complete_text'))
(dest/'INDEX.json').write_text(json.dumps(dict(rows=rows,stage='A1_import_failure_A2_native_launch_failures_A3_gate_submission',PT_or_old_raw_reads_for_Git=False,old_mothers_and_Registry_unchanged=True,host86_excluded=True,no_skill_pass_or_new_learner_success_claimed=True),indent=2),encoding='utf8');files.append((rel/'INDEX.json').as_posix());(dest/'.gitattributes').write_text('* -text\n',encoding='utf8');files.append((rel/'.gitattributes').as_posix())
note=(D/'CURRENT_PROGRESS_V1_A3_SHARED_NATIVE_GATE.md').read_text(encoding='utf8')+'\n\nAll current text/real failures/pins are a point-in-time snapshot; A3 source staging/import-only and dispatch do not prove native limits, source loading, PPO or skill. Original record validation/redaction/hashes retained, exact staged set, no main writes or runtime/model replay. Later actual A3 evidence belongs to the next meaningful stage.\n';note,count=redact(note);(dest/'NOTE.md').write_text(note,encoding='utf8');files.append((rel/'NOTE.md').as_posix())
orig=record_experiment.git
def scoped(*args):
 if args[:2]==('add','--'):
  rp=args[2];assert rp.startswith('history/experiments/20261105-mod4v2-nine-initial-migration-attempts')and set(args[3:])==set(files);orig('add','--',rel.as_posix(),rp);assert set(orig('diff','--cached','--name-only').splitlines())==set(files)|{rp};return ''
 return orig(*args)
record_experiment.git=scoped;trial='mod4v2-nine-initial-migration-attempts';sys.argv=['record_experiment.py','--id',trial,'--title','Nine V2 migration: first dependency failure, six startup failures before learner, repaired native-gated A3 submitted','--kind','training','--note-file',str(dest/'NOTE.md'),'--validation','formal9-source-metadata-only-includingH1;original-two4090-singlewriter-charge_values-actualGOthroughwait-tail-preserved;firstpreimport0GO-error-and-actualreap;A2-allclosewaitsettledreleased-sixnative-or-launchererrors0learner0PPO-threeunstarted;H1rc0notnativepass;newworker2launcher-isolation-and-before-assert-limitreadback;A3H1sharednativegate-before-other-families;original-gpu-account-resource-functions-exact;all-local-source-generator-errors-and-sources-retained;source-stage-and-dispatch-not-training-or-skill;original-recordvalidation-redaction-hashes-exact2scopedstagedset;featureonly-mainreadonly-no-modelraw-runtime-replay','--files',*files];record_experiment.main();head=G('rev-parse','HEAD');tag='trial-'+time.strftime('%Y%m%d')+'-'+trial;obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head;G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag);remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain');print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,index_entries=len(rows),original_recorder_full_validation_redaction_hashes_retained=True,exact_staged_set=True,no_model_or_raw_or_runtime_or_old_record_replay=True,main_push_or_reset=False),indent=2))
