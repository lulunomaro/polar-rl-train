"""Continue the SAME validated precommit trial after a midnight add-scope guard error; no recorder replay."""
from pathlib import Path
import json,sys,hashlib,subprocess
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/mod4v2_serial_e0_scut_source_probe_20261106');dest=repo/rel;rp=Path('history/experiments/20261106-mod4v2-serial-e0-scut-source-probe.json');meta=repo/rp;idx=dest/'INDEX.json'
sys.path.insert(0,str(repo/'archive_tools'));from capture_history import redact

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='9c2dcd2e3a06ffc03105fed9329d758700b2938e'and not G('diff','--cached','--name-only')
record=json.loads(meta.read_bytes());tag=record['tag'];assert record['id']=='20261106-mod4v2-serial-e0-scut-source-probe'and tag=='trial-'+record['id']and not G('tag','--list',tag)
assert set(G('status','--porcelain').splitlines())=={'?? '+rp.as_posix(),'?? '+rel.as_posix()+'/'}
# The original recorder already validated and wrote this record; verify every prepared byte before augmenting it.
for name,sha in record['source_and_evidence_sha256'].items():
 p=repo/name;assert p.resolve().is_relative_to(dest.resolve());raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;assert redact(raw.decode('utf8'))[0]==raw.decode('utf8')
index=json.loads(idx.read_bytes());assert 'precommit_date_guard_continuation'not in index
closed_path=Path(json.loads((D/'E0_SCUT_PROBE_CLOSED_RESULT_PATH.json').read_bytes())['path']);closed=json.loads(closed_path.read_bytes());m=closed['metadata'];assert closed['closed']is True and all(m['OWNER_EXIT_ACTUAL.json'][k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and m['OUTER_OWNER_WAIT_ACTUAL.json']['original_owner_reaped']is True
assert closed['cases']['E0']['V2_LEARNER_LOADED.json']is None and closed['cases']['E0']['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']is None
extras=[D/'SCUT_SERIAL_PRECOMMIT_DATE_GUARD_FAILURE_V1.md',Path(__file__).resolve(),closed_path,D/'E0_SCUT_PROBE_CLOSED_RESULT_PATH.json'];added=[]
for p in extras:
 raw=p.read_bytes();text,count=redact(raw.decode('utf8'));q=dest/'precommit_addendum'/p.name;assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text,encoding='utf8');name=q.relative_to(repo).as_posix();record['source_and_evidence_sha256'][name]=hashlib.sha256(q.read_bytes()).hexdigest();added.append(name);index['rows'].append(dict(source=str(p),source_bytes=len(raw),source_SHA256=hashlib.sha256(raw).hexdigest(),archive=name,archive_bytes=q.stat().st_size,archive_SHA256=record['source_and_evidence_sha256'][name],redactions=count,status='same_trial_precommit_addendum_original_preserved'))
index['precommit_date_guard_continuation']=dict(existing_record_id=record['id'],previous_record_entrypoint_replayed=False,original_all_file_validation_redaction_hashes_retained=True,initial_checkpoint_and_one_update_not_admitted=True,addition_paths=added,model_or_GPU_or_C_operations=0)
idx.write_text(json.dumps(index,indent=2),encoding='utf8');record['source_and_evidence_sha256'][idx.relative_to(repo).as_posix()]=hashlib.sha256(idx.read_bytes()).hexdigest()
record['title']='Serial E0: D6 repair and STOP26 retained; SCUT probe closed pre-PT on joint_acc ABI, no promotion'
record['repair_or_experiment_note']+='\n\nPrepared midnight guard failed before git staging/commit. Same record continuation keeps original evidence hashes, revalidates every archive byte and original redact, appends failure/source and actual closed probe metadata. Probe failed at reward bind joint_acc type-or-shape guard, native/learner/initial checkpoint acceptance absent; actual wait, cost settlement, release true; rc0 is not execution success. No recorder/SDK/model/old-purpose replay. SDK source now establishes a ProxyArray interface gap; no formula or numerical threshold change.\n'
record['validation']+=';same-prepared-record-midnight-guard-prestage-failure-preserved;all-archive-files-original-redactor-revalidated;SCUT-probe-real-closed-failed-before-PT-initial-acceptance-and-PPO;current-shape-not-observed-type-shape-error-disambiguation-required'
assert redact(record['repair_or_experiment_note'])[0]==record['repair_or_experiment_note'];meta.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Reapply the original recorder's complete selected-file path/artifact/size/UTF8-redaction/hash protection.
for name,sha in record['source_and_evidence_sha256'].items():
 p=(repo/name).resolve();assert p.is_relative_to(repo.resolve())and p.is_file()and not p.name.startswith(('.env','id_rsa','id_ed25519'))and p.suffix.lower()not in('.pt','.pth','.onnx','.npz','.npy','.pem','.key');raw=p.read_bytes();assert len(raw)<=50000000 and hashlib.sha256(raw).hexdigest()==sha;assert redact(raw.decode('utf8'))[0]==raw.decode('utf8')
G('add','--',rel.as_posix(),rp.as_posix());assert set(G('diff','--cached','--name-only').splitlines())==set(record['source_and_evidence_sha256'])|{rp.as_posix()}
G('commit','-m',record['title']+'\n\nExperiment: '+tag+'\nValidation: '+record['validation']);G('tag','-a',tag,'-m',record['title']+'\n\n'+record['repair_or_experiment_note']);head=G('rev-parse','HEAD');obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag);remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==remote['refs/tags/'+tag+'^{}']==head and remote['refs/tags/'+tag]==obj and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,index_entries=len(index['rows']),original_validation_redaction_hashes_retained=True,staged_set_verified=True,prepared_record_only_continuation=True,original_recorder_or_model_or_physics_replay=False,main_push_or_reset=False),indent=2))
