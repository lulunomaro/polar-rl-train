"""Record actual observer outage/deferred handoff and delivered eval sources; no remote training inference."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
D=Path(__file__).resolve().parent
REPO=D.parent/'repo-lqr'
BASE='54530bba88477afe2e6ce480c871d3aadcb051bf'
TRIAL='mod4v2-e0-scut-hour-network-outage-eval-ready'
REL=Path('history/experiments/mod4v2_e0_scut_hour_network_outage_eval_ready_20261106')
DEST=REPO/REL
PREVIOUS=REPO/'history/experiments/mod4v2_e0_scut_probe5_qualified_hour_start_20261106/INDEX.json'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000'
SKIP={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle','.npz','.npy','.usd','.usda','.usdc','.zip','.xml','.obj','.stl','.ply','.dae','.mesh','.png','.jpg','.jpeg','.webp','.mp4','.pyc','.pyo','.partial','.tmp','.jsonl','.ndjson','.csv','.bin'}
def G(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:
  print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()
def read(p):return json.loads(p.read_bytes())
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'
assert not G('status','--porcelain') and not DEST.exists()
G('merge-base','--is-ancestor',BASE,'HEAD')
network=read(D/'E0_SCUT_HOUR_NETWORK_RECOVERY2_RESULT.json')
handoff=read(D/'SCUT_HOUR_EVAL_RECOVERED_HANDOFF_RESULT.json')
assert network['host72_SSH_TCP_reachable'] is False and network['network_watch_bound_seconds']==1800
assert len(network['rows'])==15 and all(x['host']=='10.24.0.72' and x['port']==22 and x['reachable'] is False and x['error_type']=='TimeoutError' for x in network['rows'])
assert network['training_or_model_or_GPU_or_canonical_operations']==0 and network['remote_training_state_not_inferred'] is True
assert handoff['training_root']==ROOT and handoff['phase']=='DEFERRED_HOST72_NETWORK_UNREACHABLE_REMOTE_TRAINING_STATE_UNKNOWN'
assert handoff['steps']==[] and handoff['training_relaunches']==0 and handoff['other_experts_scheduled'] is False and handoff['goal_complete'] is False
assert not (D/'E0_SCUT_HOUR_CLOSED_RESULT_PATH.json').exists()
assert not (D/'SCUT_E0_HOUR_FROZEN_DISPATCH_ONCE.json').exists()
for name in ('stage','parent','worker','factory','dispatch_once','collect_once'):
 assert (D/('SCUT_E0_HOUR_FROZEN_'+name+'.py')).is_file()
previous=read(PREVIOUS)
prior={r['source_path']:r for r in previous['entries'] if r.get('archive_path') and r.get('source_SHA256')}
sys.path.insert(0,str(REPO/'archive_tools'))
import record_experiment
from capture_history import redact
DEST.mkdir(parents=True)
rows=[];files=[];references=0
for p in sorted(D.rglob('*')):
 if '__pycache__' in p.parts or p.suffix.lower() in SKIP:
  if '__pycache__' not in p.parts:rows.append(dict(source_path=str(p),status='excluded_before_stat_read_hash_models_raw_geometry',source_bytes=None,source_SHA256=None,producer_metadata_reference='Existing producer/build/full-save receipts only; no model or geometry reopen'))
  continue
 if p.is_symlink():raise ValueError('Unexpected symlink in scoped text archive: '+str(p))
 if not p.is_file():continue
 raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
 old=prior.get(str(p))
 if old and old['source_SHA256']==digest and old['source_bytes']==len(raw):
  rows.append(dict(source_path=str(p),source_bytes=len(raw),source_SHA256=digest,archive_path=old['archive_path'],archive_bytes=old['archive_bytes'],archive_SHA256=old['archive_SHA256'],redactions=old.get('redactions',0),reference_commit=BASE,status='same_source_SHA_references_prior_verified_archive'))
  references+=1;continue
 try:text=raw.decode('utf-8-sig')
 except UnicodeDecodeError:
  rows.append(dict(source_path=str(p),source_bytes=len(raw),source_SHA256=digest,status='non_UTF8_not_committed'));continue
 clean,count=redact(text);assert redact(clean)[0]==clean
 target=DEST/'files'/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);archived=clean.encode('utf8');target.write_bytes(archived)
 rp=target.relative_to(REPO).as_posix();files.append(rp)
 rows.append(dict(source_path=str(p),source_bytes=len(raw),source_SHA256=digest,archive_path=rp,archive_bytes=len(archived),archive_SHA256=hashlib.sha256(archived).hexdigest(),redactions=count,status='complete_sanitized_text' if count else 'complete_text',time_scope='last_received_point_in_time_not_remote_completion' if p.name=='LATEST_METADATA.json' else 'actual_saved_source_or_report_not_automatically_runtime_validated'))
index=dict(kind='SCUT_E0_NETWORK_OBSERVER_FAILURE_AND_DEFERRED_EVAL_SOURCE_DELIVERY',epoch=time.time(),training_root=ROOT,last_actual_received_new_updates=18,remote_training_final_state='UNKNOWN',actual_network_probe_failures=15,network_bound_seconds=1800,evaluation_stage_dispatch_or_controls=0,training_relaunches=0,other_experts_scheduled=False,goal_complete=False,skill_graduation=None,prior_archive_commit=BASE,unchanged_text_references=references,model_raw_geometry_stat_read_hash_runtime_or_old_once_replay=False,entries=rows)
(DEST/'INDEX.json').write_text(json.dumps(index,indent=2,allow_nan=False),encoding='utf8')
(DEST/'.gitattributes').write_text('* -text\n',encoding='utf8')
note=(D/'CURRENT_PROGRESS_V11_SCUT_HOUR_NETWORK_UNREACHABLE.md').read_text(encoding='utf8')+'\n\n归档阶段：原observer SSH10054中断、recovery1连接超时、15次/1800秒TCP不可达与条件交接延期，均为观测证据而非远端训练失败。记录六评测source的原定位失败、AST坐标缩进修复、未执行publisher。远端最终保存/实际wait/账结清/lease仍unknown，未重启训练或派发评测。相同sourceSHA内容引用54530bba既有归档，新增/变化文本按当前实际字节冻结；不重放旧record/once/物理/模型，不修改main或canonical。\n'
note,_=redact(note);assert redact(note)[0]==note
(DEST/'NOTE.md').write_text(note,encoding='utf8')
files +=[(REL/'INDEX.json').as_posix(),(REL/'.gitattributes').as_posix(),(REL/'NOTE.md').as_posix()]
assert len(files)==len(set(files))
record_path=[]
def scoped(*args):
 if args[:2]==('add','--'):
  rp=args[2]
  assert Path(rp).parent.as_posix()=='history/experiments' and Path(rp).stem.endswith('-'+TRIAL)
  assert set(args[3:])==set(files) and json.loads((REPO/rp).read_bytes())['tag'].endswith('-'+TRIAL)
  record_path.append(rp);G('add','--',REL.as_posix(),rp)
  assert set(G('diff','--cached','--name-only').splitlines())==set(files)|{rp}
  return ''
 return G(*args)
record_experiment.git=scoped
sys.argv=['record_experiment.py','--id',TRIAL,'--title','E0 SCUT hour observation lost: 15 bounded TCP timeouts; six post-close eval sources ready, remote final state unknown','--kind','diagnostic','--note-file',str(DEST/'NOTE.md'),'--validation','original-SSH-observer-failure-preserved;15actual-network-timeouts-no-remote-training-inference;deferred-handoff-zero-stage-dispatch-relaunch;6eval-sources-generated-with-actual-AST-indentation-only-repair-original-resource-wait-functions-preserved;publisher-unexecuted;source-byte-SHA-archive-byte-SHA-redaction-prior-archive-reference;full-original-recorder-validation-exact-short-stagedset;featureonly-mainreadonly-no-model-raw-geometry-or-runtime-replay','--files',*files]
record_experiment.main()
assert len(record_path)==1
record=json.loads((REPO/record_path[0]).read_bytes());tag=record['tag'];head=G('rev-parse','HEAD');obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag' and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in (line.split() for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,index_entries=len(rows),unchanged_text_references=references,new_changed_text_files=len(files)-3,original_record_validation_redaction_hashes_retained=True,exact_staged_set=True,no_model_raw_geometry_runtime_or_old_record_replay=True,main_push_or_reset=False,remote_training_final_state='UNKNOWN',evaluation_not_dispatched=True,goal_complete=False),indent=2))
