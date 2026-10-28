"""Future target-only1800s worker. Stdin is public sealed request, never credentials."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,signal,sys,time,traceback
ROOT=Path('/data/robemo/polar-rl-train');BASE=ROOT/'runtime_migrations/proven72_20261028_v1';ATTEMPT=BASE/'direct_pull_attempt_v1';DEST=BASE/'runtime_copy_v1';B=Path(__file__).resolve().parent
PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'

def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def emit(**v):
 value=dict(epoch=time.time(),**v)
 with (B/'EXTRACT_RELOCATE_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(value)+chr(10))
 print(json.dumps(value),flush=True)

def checked_envelope(envelope):
 raw=envelope['raw_UTF8'].encode('utf8');assert hashlib.sha256(raw).hexdigest()==envelope['SHA'];return json.loads(raw)

def known_out(row):
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));creation=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return dict(out=True,expected=row,reason='known original PID absent')
 if creation!=row['creation']:return dict(out=True,expected=row,reason='PID reused; new exe/argv not inspected')
 return dict(out=a[0]=='Z',expected=row,creation=creation,state=a[0],reason='known original nonexecuting zombie' if a[0]=='Z' else 'known original still executing')

def main():
 req=json.loads(sys.stdin.readline());assert req['kind']=='MOD4_VERIFIED_PROVEN72_NEW_COPY_EXTRACT_RELOCATE_V1' and req['maximum_seconds']==1800 and req['destination']==str(DEST)
 assert ROOT.resolve()==ROOT and BASE.resolve()==BASE and B.resolve()==B and B==BASE/'extract_relocate_stage_v1' and not DEST.exists()
 marker=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert marker['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and marker['authorized_root']==str(ROOT)
 assert json.loads((B/'OWN_EXTRACT_RELOCATE_STAGE_MARKER.json').read_bytes())['request_id']==req['request_id']
 caller=checked_envelope(req['actual_direct_caller']);source=checked_envelope(req['fresh_actual_source_allout']);assert caller['passed_all_artifacts_only'] and caller['source_and_target_SSH_sequential_and_closed'] and caller['worker_waited']['actual_waited'] and caller['worker_waited']['returncode']==0 and not caller['primary_error']
 assert source['kind']=='MOD4_PROVEN72_EXPORT_AND_TLS_SOURCE_ALL_OWNOUT_ACTUAL_V1' and source['passed'] and source['all_known_recorded_out'] and source['caller_receipt_SHA']==req['actual_direct_caller']['SHA'] and source['producer_SHA']==PRODUCER and source['source_service_terminal']==caller['source_service_ending']['terminal']
 assert caller['producer_SHA']==PRODUCER and caller['receiver_complete']['whole_ordered_archive_SHA']==PRODUCER and caller['receiver_complete']['passed_all_artifact_chunks_only'] and caller['receiver_terminal']['passed_artifact_only'] and caller['receiver_terminal']['all_HTTP_connections_closed']
 assert json.loads((ATTEMPT/'DIRECT_RECEIVER_ALL29_CHUNKS_FULL_SHA_COMPLETE_ACTUAL.json').read_bytes())==caller['receiver_complete'] and json.loads((ATTEMPT/'DIRECT_PULL_TERMINAL_ACTUAL.json').read_bytes())==caller['receiver_terminal']
 identity=json.loads((ATTEMPT/'DIRECT_PULL_WORKER_IDENTITY_AND_BUDGET_ACTUAL.json').read_bytes())['identity'];assert identity==caller['receiver_terminal']['identity'] and identity['cwd']==str(ATTEMPT) and identity['exe']==os.path.realpath('/usr/bin/python3') and identity['argv']==['/usr/bin/python3','-u','-B',str(ATTEMPT/'target86_owned_direct_HTTPS_pull_candidate_v1.py')]
 out=known_out(identity);assert out['out'],'original target pull worker must be nonexecuting before extraction'
 producer=req['producer'];assert producer['passed'] and producer['producer_SHA']==PRODUCER and producer['compressed_bytes']==15158703068 and len(producer['chunks'])==29
 receipts=caller['receiver_complete']['chunks'];assert len(receipts)==29
 paths=[]
 for i,(row,receipt) in enumerate(zip(producer['chunks'],receipts)):
  expected=(BASE/'chunks' if i==0 else ATTEMPT/'chunks')/('runtime72_chunk'+str(i).zfill(4)+'.gz');assert receipt['passed'] and receipt['receiver_full_SHA_equal_producer'] and receipt['chunk_index']==i and receipt['path']==str(expected) and receipt['SHA']==row['SHA'] and receipt['bytes']==row['bytes'];paths.append(expected)
 corepath=B/'strict_archive_and_narrow_relocation_core_v1.py';assert hashlib.sha256(corepath.read_bytes()).hexdigest()==req['core_SHA'];spec=importlib.util.spec_from_file_location('strict_new_copy_core',corepath);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
 bindingraw=(B/'EXACT_ORIGINAL_LAUNCHERS_AND_FIVE_EDITABLE_BINDING_V1.json').read_bytes();assert hashlib.sha256(bindingraw).hexdigest()==req['portability_binding_SHA'];binding=json.loads(bindingraw)
 logical=req['logical_input_bytes'];assert logical==source['logical_input_bytes'] and logical>0 and shutil.disk_usage(BASE).free>logical+1024**3
 put('ACTUAL_ALL_PROOFS_BEFORE_ARCHIVE_CONTENT_OR_COPY_CREATION.json',dict(epoch=time.time(),request_id=req['request_id'],caller_receipt_SHA=req['actual_direct_caller']['SHA'],fresh_source_allout_SHA=req['fresh_actual_source_allout']['SHA'],target_pull_known_out=out,actual_free_bytes=shutil.disk_usage(BASE).free,required_new_copy_bytes=logical+1024**3,destination=str(DEST),no_existing_venv_or_runtime_or_model_change=True))
 def expired(signum,frame):raise TimeoutError('owned extraction/relocation original1800s bound')
 signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,1800);result=None
 try:
  snapshots=core.verify_chunks(paths,producer['chunks'],PRODUCER,emit);put('ALL29_CHUNKS_AND_ORDERED_GZIP_SHA_REVERIFIED_BEFORE_NEW_COPY.json',dict(epoch=time.time(),passed=True,producer_SHA=PRODUCER,compressed_bytes=15158703068,chunk_stat_snapshots=[list(x) for x in snapshots],destination_not_yet_created=not DEST.exists()))
  extracted=core.extract_stream_new(paths,producer['chunks'],snapshots,DEST,logical,PRODUCER,emit);put('SAFE_NEW_COPY_TAR_AND_PYTHON_SOURCE_EXTRACT_ACTUAL.json',dict(epoch=time.time(),**extracted))
  originals=[]
  def preserve(rel,raw):
   original=dict(relative_path=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),original_UTF8=raw.decode('utf8'));put('RELOCATION_ORIGINAL_SMALL_TEXT_'+str(len(originals)).zfill(4)+'.json',original);originals.append(original)
  relocation=core.narrow_relocate_new_copy(DEST,binding,extracted['python_source_hash_rows'],preserve);put('EXACT_SMALL_RELOCATION_ORIGINAL_BYTES_AND_SHAS_ACTUAL.json',dict(epoch=time.time(),originals=originals));put('NARROW_FIVE_FINDERS_BIN_SHEBANG_RELATIVE_WRAPPERS_RELOCATION_ACTUAL.json',dict(epoch=time.time(),**relocation))
  result=dict(passed_verified_extract_and_declared_relocation_only=True,epoch=time.time(),destination=str(DEST),producer_SHA=PRODUCER,source_and_target_prior_workers_out=True,tar_summary={k:v for k,v in extracted.items() if k!='python_source_hash_rows'},relocation=relocation,original_working_versions=binding['original_expected_working_versions'],original_dependency_metadata_conflicts_preserved=True,no_SDK_CUDA_or_fullstate_native24_or_training_readiness_proved=True,no_existing_source_runtime_venv_or_model_modified=True);put('VERIFIED_NEW_COPY_EXTRACT_AND_NARROW_RELOCATION_COMPLETE_ACTUAL.json',result)
 except BaseException:
  result=dict(passed_verified_extract_and_declared_relocation_only=False,epoch=time.time(),error=traceback.format_exc(),partial_new_copy_preserved=True,original_inputs_old_venvs_source72_unchanged=True,no_retry_or_cleanup=True);put('EXTRACT_RELOCATE_ORIGINAL_ERROR_ACTUAL.json',result)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);put('EXTRACT_RELOCATE_TERMINAL_ACTUAL.json',dict(epoch=time.time(),request_id=req['request_id'],passed_extract_and_relocate_only=bool(result and result.get('passed_verified_extract_and_declared_relocation_only')),new_destination=str(DEST),no_GPU_SDK_model_or_canonical_operation=True));print(json.dumps(dict(passed_extract_and_relocate_only=bool(result and result.get('passed_verified_extract_and_declared_relocation_only')),SDK_ready=False)),flush=True)
 if not result or not result.get('passed_verified_extract_and_declared_relocation_only'):raise SystemExit(2)

if __name__=='__main__':
 try:main()
 except SystemExit:raise
 except BaseException:put('EXTRACT_RELOCATE_PRE_ARCHIVE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
