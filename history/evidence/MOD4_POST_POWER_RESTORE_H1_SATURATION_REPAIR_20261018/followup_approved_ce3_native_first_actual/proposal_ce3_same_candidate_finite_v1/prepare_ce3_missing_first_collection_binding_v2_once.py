"""Prior900s ended normally after native; prepare new bounded read only missing PT."""
from pathlib import Path
import json,ast,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 prior=R/'CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json';v=json.loads(prior.read_bytes());assert v['actual_transport_returned'] and not v['target']['immutable_first_present'] and not v['target']['errors'];assert {x['kind'] for x in v['downloaded_models']}=={'own_native_startup0','own_native_complete'}
 text=(B/'collect_ce3_own_native_and_first_missing_finite_once.py').read_text('utf8')
 needle=" d.put('CE3_NATIVE_FIRST_FINITE_COLLECTOR_STARTED_ACTUAL.json'"
 insert=" prior=json.loads((R/'CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert prior['actual_transport_returned'] and not prior['target']['immutable_first_present'];assert all(x['twohost_complete_SHA'] and Path(x['local_path']).stat().st_size==x['bytes'] for x in prior['downloaded_models'])\n"
 assert needle in text;text=text.replace(needle,insert+needle)
 text=text.replace("c=None;models=[]","c=None;models=list(prior['downloaded_models'])")
 text=text.replace("dest.mkdir();requested=[]","dest.mkdir(exist_ok=True);requested=[];known={x['kind'] for x in models}")
 text=text.replace("requested.append(dict(native[key],kind=kind))","requested.extend([] if kind in known else [dict(native[key],kind=kind)])")
 text=text.replace('if present:requested.append','if present and kind not in known:requested.append')
 text=text.replace('CE3_NATIVE_FIRST_FINITE_','CE3_MISSING_FIRST_V2_FINITE_').replace('CE3_NATIVE_FIRST_COLLECTION_ORIGINAL_ERROR_','CE3_MISSING_FIRST_V2_COLLECTION_ORIGINAL_ERROR_').replace('>=900','>=600').replace('900-','600-').replace('max900s','max600s')
 text=text.replace("d.put('CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json',dict(","d.put('CE3_OWN_NATIVE_FIRST_COMPLETE_MERGED_MISSING_V2_BOUND_COLLECTION_ACTUAL.json',dict(previous_complete_model_references=prior['downloaded_models'],prior900s_collection_original_pending_preserved=True,")
 new=B/'collect_ce3_only_missing_first_nativeCPU_existing_chain_v2_once.py';ast.parse(text)
 with new.open('x',encoding='utf8') as f:f.write(text)
 text=(B/'review_ce3_own_native_and_first_complete_local_CPU_once.py').read_text('utf8').replace('CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json','CE3_OWN_NATIVE_FIRST_COMPLETE_MERGED_MISSING_V2_BOUND_COLLECTION_ACTUAL.json').replace('CE3_OWN_NATIVE_FIRST_COMPLETE_LOCAL_CPU_ACTUAL.json','CE3_OWN_NATIVE_FIRST_COMPLETE_LOCAL_CPU_V2_ACTUAL.json').replace('CE3_OWN_NATIVE_FIRST_LOCAL_CPU_ORIGINAL_ERROR_','CE3_OWN_NATIVE_FIRST_LOCAL_CPU_V2_ORIGINAL_ERROR_')
 reader=B/'review_ce3_merged_native_first_complete_local_CPU_v2_once.py';ast.parse(text)
 with reader.open('x',encoding='utf8') as f:f.write(text)
 with (R/'CE3_PRIOR900S_NATIVE_COMPLETE_FIRST_PENDING_NEW_MISSING_READER_V2_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prior_collection=dict(path=str(prior),SHA=H(prior)),prior_normal_bounded_pending_not_failure=True,complete_two_native_PT_reused_no_remote_hash_or_download=True,new_collector=dict(path=str(new),SHA=H(new)),new_reader=dict(path=str(reader),SHA=H(reader)),native_GPU_complete_remote_CPU_still_running_at_prior_snapshot=True,no_Task_native_GO_or_account_mutation=True,old_CPU_reader_prepared_not_executed=True),f,indent=2)
 print(json.dumps(dict(missing_reader_V2_prepared=True,prior_native_models=2,no_GPU_replay=True)))

if __name__=='__main__':main()
