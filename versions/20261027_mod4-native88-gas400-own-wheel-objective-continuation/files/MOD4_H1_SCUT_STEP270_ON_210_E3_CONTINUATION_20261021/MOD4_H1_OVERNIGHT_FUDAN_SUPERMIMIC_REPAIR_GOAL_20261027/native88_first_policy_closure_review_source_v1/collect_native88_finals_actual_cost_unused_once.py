"""UNUSED one-shot native88 two-native close collector. No call before original900 gate."""
from pathlib import Path,PurePosixPath
import argparse,base64,hashlib,importlib.util,json,os,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
from native88_closing_protocol_v1 import validate_detached,closing_gate,active_keys,validate_actual_GO_binding,bind_prepared_detached
KEYS=()
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(R,name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)


def extract_go(value):
 if isinstance(value.get('go'),dict):return value['go']
 if 'current' in value:return value['current']['go']
 if 'owner' in value:return value['owner']['current']['go']
 return value['authority72']['cohort']['go']


def capture(c,receipt,models,key,py,N,code):
 sf=c.open_sftp();sf.get_channel().settimeout(90);texts=[];saved=[]
 try:
  for row in receipt['text_files']:
   rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0]==key
   path=N/'current_native88_closed_text'/Path(*rel.parts);path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
   sf.get(row['path'],str(path))
   if path.stat().st_size==row['bytes'] and H(path)==row['SHA']:texts.append(dict(row,local_path=str(path)))
   else:
    # Exactly the old once-only exception. Every other mismatch is terminal;
    # preserve the original bytes, never silently replace their classification.
    assert rel.as_posix() in {k+'/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log' for k in KEYS},'Unexpected text mismatch; original retained'
    original=dict(row,local_path=str(path),transferred_bytes=path.stat().st_size,transferred_SHA=H(path),manifest_time_bytes_not_captured=True)
    source="from pathlib import Path;import base64,hashlib,json;p=Path(v['path']);a=p.stat();raw=p.read_bytes();b=p.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns);print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),mtime_ns=b.st_mtime_ns,base64=base64.b64encode(raw).decode())))"
    fresh=code(c,py,source,dict(path=row['path']),timeout=45);raw=base64.b64decode(fresh.pop('base64'))
    assert len(raw)==fresh['bytes'] and hashlib.sha256(raw).hexdigest()==fresh['SHA']
    target=path.with_name('omni.processlifetime.fresh_after_manifest_mismatch.log')
    with target.open('xb') as stream:stream.write(raw)
    put(N/'reports','NATIVE88_'+key+'_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),original=original,fresh=dict(fresh,local_path=str(target)),cause_unknown=True,original_manifest_time_bytes_unavailable=True,no_training_failure_or_refund_inferred=True))
    texts.append(dict(row,bytes=fresh['bytes'],SHA=fresh['SHA'],local_path=str(target),original_manifest_and_transferred_log_preserved=original,one_fresh_snapshot_only=True))
  for row in models:
   rel=PurePosixPath(row['path']);assert rel.suffix=='.pt'
   path=N/'current_native88_method_fullstate'/key/('formal' if row['formal_manifest_passed'] else 'failed_partial')/rel.name
   path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
   part=path.with_suffix('.pt.partial');assert not part.exists();sf.get(row['path'],str(part))
   assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'],'Full model SHA/bytes differ; partial retained'
   part.replace(path);saved.append(dict(row,local_path=str(path),twohost_complete_SHA=True))
 finally:sf.close()
 return texts,saved


def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--go-report',required=True);p.add_argument('--detached-report',required=True);p.add_argument('--prepared-report',required=True);args=p.parse_args()
 N=Path(args.stage).resolve();assert N.name=='H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027';R=N/'reports';q=json.loads(Path(args.detached_report).read_bytes())
 prepared=json.loads(Path(args.prepared_report).read_bytes());q=bind_prepared_detached(q,prepared);validate_detached(q,prepared);global KEYS;KEYS=active_keys(q);go=extract_go(json.loads(Path(args.go_report).read_bytes()))
 # Local gate precedes transport import, credential recovery and every SSH.
 assert max(x['nominal_end_epoch'] for x in go.values())-time.time()<=900,'Original <=900 closing boundary retained'
 closing_gate(go,time.time());assert set(go)==set(KEYS);validate_actual_GO_binding(go,q)
 put(R,'NATIVE88_CLOSING_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,owner_root=q['owner_root'],owner_identity=q['owner_identity'],go_report=str(Path(args.go_report)),go_report_SHA=H(Path(args.go_report)),no_new_GO_or_fee=True))
 W=N.parent.parent;T=N.parent
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
 import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'))
 import strict_user_forwarded_original210_transport_v1 as route
 spec=importlib.util.spec_from_file_location('closing86b_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
 memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory)
 remote=(D/'native88_closing_protocol_v1.py').read_text('utf8')+'\n'+(D/'native88_close_readonly_remote_v1.py').read_text('utf8')
 secret=memory.recover();c=None;texts=[];complete={k:[] for k in KEYS};nodes={};errors={}
 try:
  c=d.connect72(secret)
  authority=d.code(c,d.PY72,remote+"\nprint(__import__('json').dumps(close_owner_readonly(v)))",dict(q=q,original_go=go),timeout=900)
  put(R,'NATIVE88_CLOSED_AUTHORITY72_ORIGINAL_COST_ACTUAL.json',authority)
  owner_texts,_=capture(c,authority,[],'owner',d.PY72,N,d.code);texts.extend(owner_texts);c.close();c=None
  # The original owner wait850 is followed by exactly one sequential bounded
  # read for each source210 H1-native and72 recovery H1-native node, each wait180.
  for key in KEYS:
   try:
    c=route.connect() if key=='h1' else d.connect72(secret);py=route.PY if key=='h1' else d.PY72
    receipt=d.code(c,py,remote+"\nprint(__import__('json').dumps(close_node_readonly(v)))",dict(q=q,key=key),timeout=210)
    nodes[key]=receipt;put(R,'NATIVE88_CLOSED_NODE_'+key.upper()+'_ACTUAL.json',receipt)
    owner_row=authority['cohort']['rows'][key];node_row=receipt['node_terminal']['row']
    assert owner_row['final']==node_row['final'] and owner_row['returncode']==node_row['returncode'],'Owner/node original final differs'
    final=(node_row.get('final') or {}).get('final');models=[]
    if final:
     assert PurePosixPath(final['path']).is_relative_to(PurePosixPath(q['roots'][key])/'job0/production')
     models=[dict(final,formal_manifest_passed=(node_row.get('final') or {}).get('passed') is True)]
    part,saved=capture(c,receipt,models,key,py,N,d.code);texts.extend(part);complete[key]=saved
   except BaseException:
    errors[key]=traceback.format_exc();put(R,'NATIVE88_'+key.upper()+'_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=errors[key],raw_partial_and_healthy_other_nodes_retained=True,no_auto_retry_or_fee_repair=True))
   finally:
    if c:c.close();c=None
  result=dict(schema='mod4.H1_native88.closed_transport.v1',epoch=time.time(),run_id=q['run_id'],
   actual_finite_transport_returned=True,all_active_node_collection_passed=not errors,authority72=authority,
   nodes=nodes,native_H1_method_fullstate=complete,active_keys=list(KEYS),deferred_experts=q.get('deferred_experts',[]),
   all_texts=texts,collection_errors=errors,original_canonical_cost_settled=authority['cohort']['original_cost_settled'],
   original_fee_validation_error=authority.get('original_fee_validation_error'),not_skill_qualification=True,
   no_new_ledger_write_or_refund=True,detached=q,prepared=prepared,prepared_report_SHA=H(Path(args.prepared_report)),detached_report_SHA=H(Path(args.detached_report)),actual_GO_report_SHA=H(Path(args.go_report)))
  put(R,'NATIVE88_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(collected=True,complete_models={k:len(v) for k,v in complete.items()},partial_errors=list(errors),source_CPU_review_not_yet_run=True)))
 finally:
  secret=None
  if c:c.close()


if __name__=='__main__':
 try:main()
 except BaseException:
  # This path creates only an error receipt; it never retries a consumed once.
  stage=Path(sys.argv[sys.argv.index('--stage')+1]) if '--stage' in sys.argv else D
  put(stage/'reports','NATIVE88_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay_refund_or_midwindow_PT=True))
  raise
