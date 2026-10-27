"""New source-only derivation. Original failed reader and its outputs stay intact."""
from pathlib import Path
import ast, hashlib, json, difflib, time
N=Path(__file__).resolve().parent; T=N.parent; R=N/'reports'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
D=L/'native88C_exact_reset_bank_lifecycle_source_v1'
H=L/'native88C_initial_reader_name_dependency_repair_source_v1'
O=L/'native88C_fullstate_qualification_reader_repair_v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists(),'unused new source namespace only'
 index=json.loads((H/'INDEX_SHA256_ACTUAL.json').read_bytes())
 for row in index['files']:
  p=H/row['relative'];assert p.stat().st_size==row['bytes'] and sha(p)==row['SHA']
 candidates=[H/r['relative'] for r in index['files'] if r['SHA']=='da0c81ae801c768578f199f280d86c73c2fd69a86ed16c56d31b7560d991a63f']
 assert len(candidates)==1
 old=D/'review_native88_finals_initial_CPU_unused_once.py'
 assert sha(old)=='a97587c3ee6ff7015949d06aa429851026f8d3837ab65bda56f69a048906bbb9'
 raw=old.read_bytes(); s=raw.decode('utf8')
 def patch(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
 patch("sys.path.insert(0,str(Path(__file__).resolve().parent))", "sys.path[:0]=[str(Path(__file__).resolve().parent),str(Path(__file__).resolve().parents[1]/'native88C_exact_reset_bank_lifecycle_source_v1')]")
 patch("from native88_event_curve_summary_v1 import read_curve", "from native88_event_curve_summary_v1 import read_curve\nimport native88_initial_CPU_reader_primitives_v1 as repaired_primitives\nrequire(Path(repaired_primitives.__file__).resolve()==Path(__file__).resolve().parent/'native88_initial_CPU_reader_primitives_v1.py','exact new primitives import path')\nrequire(hashlib.sha256(Path(repaired_primitives.__file__).read_bytes()).hexdigest()=='da0c81ae801c768578f199f280d86c73c2fd69a86ed16c56d31b7560d991a63f','exact dependency-only source repair')")
 # Only saved reviewer outputs are renamed; actual production metadata paths stay exact.
 s=s.replace("put(R,'NATIVE88_", "put(R,'NATIVE88C_READER_REPAIRED_")
 s=s.replace("R/'NATIVE88_EVENT_CURVE_TEXT_SUMMARY_ACTUAL.txt'", "R/'NATIVE88C_READER_REPAIRED_EVENT_CURVE_TEXT_SUMMARY_ACTUAL.txt'")
 marker=" intent=dict(epoch=time.time(),purpose='native88 changed-plant own-step FINAL initial CPU + frozen normal86 witness qualification',run_id=q['run_id'],"
 preflight=""" prior_path=R/'NATIVE88_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
 prior=read(prior_path);records=prior['initial_model_load_records']
 require(prior['passed'] is False and set(prior['errors'])==set(KEYS),'preserve exact original failed two-role reader')
 require(all(\"NameError: name 'H' is not defined\" in prior['errors'][k] for k in KEYS),'only exact source dependency failure admitted')
 require(len(records)==1 and records[0]['completed'] is True and records[0]['producer_SHA']==BOOTSTRAP_SHA,'only old shared witness loaded; no NEW FINAL initial load was attempted')
 require(receipt['all_active_node_collection_passed'] is True and not receipt['collection_errors'],'actual complete case-safe collection required')
 # Actual source/metadata preflight before any required witness reread or NEW model load.
 for key in KEYS:
  spec=q['specs'][key];pins=PinnedSource(prepared['payloads'][key],spec)
  protocol=load_pinned_module('native88_repaired_preflight_'+key,'native88_protocol_v1.py',pins)
  envelope=cpu['results'][key]['ready_envelope']
  require(envelope['value'].get('exact_gas400_reset_bank_source_CPU_passed') is True,'actual installed source CPU reset proof')
  require(protocol.native88_valid_ready(dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec),'original actual ready guard unchanged')
 put(R,'NATIVE88C_READER_REPAIRED_SOURCE_METADATA_PREFLIGHT_ACTUAL.json',dict(passed=True,old_failed_reader_report=str(prior_path),old_report_SHA=H(prior_path),old_load_records=records,NEW_FINAL_initial_loads_before_this_entry=0,shared_witness_prior_loads=1,additional_shared_witness_read_required_for_literal_frozen_comparison=True,not_a_replay_of_old_once=True))
 intent=dict(epoch=time.time(),purpose='complete actual88C formal qualification after pure-source H/read dependency repair; first2NEW FINAL loads plus1necessary shared witness reread',run_id=q['run_id'],"""
 patch(marker,preflight)
 patch("  each_new_FINAL_initial_load_maximum=1,shared_qualified_normal86_witness_initial_load_maximum=1,normal86_producer_SHA=BOOTSTRAP_SHA,", "  each_new_FINAL_initial_load_maximum=1,shared_witness_reads_in_this_new_purpose=1,prior_shared_witness_loads=1,necessary_witness_reread_reason='old reader process exited before both NEW FINAL loads; literal frozen comparison requires the shared witness in this process',normal86_producer_SHA=BOOTSTRAP_SHA,")
 ast.parse(s)
 O.mkdir()
 primitive=O/'native88_initial_CPU_reader_primitives_v1.py';primitive.write_bytes(candidates[0].read_bytes())
 entry=O/'qualify_native88C_formal_fullstate_after_reader_name_fix_once.py';entry.write_text(s,encoding='utf8')
 (O/'SOURCE_DERIVATION.diff').write_text(''.join(difflib.unified_diff(raw.decode('utf8').splitlines(True),s.splitlines(True),fromfile=str(old),tofile=str(entry))),encoding='utf8')
 report=dict(epoch=time.time(),scope='pure source reader dependency repair and new output namespace; original all numeric/model/physical/admission checks retained',old_reader=str(old),old_reader_SHA=sha(old),helper_index_SHA=sha(H/'INDEX_SHA256_ACTUAL.json'),new_primitive_SHA=sha(primitive),new_entry=str(entry),new_entry_SHA=sha(entry),no_model_GPU_raw_SSH_or_account_action_in_derivation=True,old_errors_outputs_and_once_unchanged=True,actual_NEW_FINAL_loads_still_zero=True,shared_witness_will_be_read_once_more_for_necessary_literal_comparison=True)
 (O/'SOURCE_DERIVATION_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 (O/'INDEX_SHA256_ACTUAL.json').write_text(json.dumps(dict(files=[dict(relative=p.relative_to(O).as_posix(),bytes=p.stat().st_size,SHA=sha(p)) for p in sorted(O.iterdir())]),indent=2),encoding='utf8')
 print(json.dumps(report))
if __name__=='__main__':main()
