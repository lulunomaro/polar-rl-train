"""Prepare new point-in-time archive source; no Git/native/CPU replay."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;source=R/'archive_phase40_b4_cpu_good_stage_delta.py';dest=R/'archive_phase41_sensor_pass_case_bound_delta.py';report=R/'reports/PHASE41_ARCHIVE_SOURCE_PREPARATION_V1.json';assert not dest.exists()and not report.exists();raw=source.read_bytes();text=raw.decode().replace('\r\n','\n')
def change(old,new):
 global text
 assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new)
change("REL=Path('history/experiments/mod4v1_supermimic_bptt_phase40_delta')","REL=Path('history/experiments/mod4v1_supermimic_bptt_phase41_delta')")
change("G('rev-parse','HEAD')=='2c81b89322a393926ba8779b7c4bcbf0de2ede86'","G('rev-parse','HEAD')=='e33c2fd93335ef47ef6682dfc148b3e27fd46717'")
guard="""b4cpu2=json.loads((R/'reports/PHASE1_B4_ACTUAL_REAL_SENSOR_CPU_V2.json').read_bytes());q=b4cpu2['receipt'];f=q['fixture_result'];assert b4cpu2['returncode']==0 and q['status']==f['status']=='PASS'and q['source_files_verified']==41 and q['all_uploaded_source_bytes_unchanged']and q['global_Python_and_Torch_CPU_RNG_unchanged']and f['N']==80 and f['checks']['main64']['controls']==64 and f['checks']['main64']['normal_channel_records']==640 and not q['native_install_or_binding_preflight_executed']
good_failure=json.loads((R/'reports/GOOD_HOLDOUT_D6_SEED20260929_CLOSED_FAILURE_FACTS_V1.json').read_bytes());e=good_failure['parent_exit'];w=good_failure['actual_outer_wait'];assert not good_failure['passed_closed_execution']and e['all_own_children_waited']and e['errors']==[]and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released']and w['actual_parent_p_wait_returned']and w['returncode']==1 and w['controller_errors']==[]and len(e['child_waits'])==2 and all(x['actual_waited']and x['returncode']==0 for x in e['child_waits'])
assert len(good_failure['original_errors'])==2 and all('JSON metadata exceeds bounded source contract'in x['error']for x in good_failure['original_errors'].values());assert all(x['unqualified_group_embedded_counts']==dict(controls=750,physics=6000,feedback=1500,actor_calls=750)for x in good_failure['unqualified_group_embedded_rows'])and not good_failure['producer_source_grade']['passed_closed_reference_source_grade']
sizes=json.loads((R/'reports/GOOD_HOLDOUT_D6_CASE_FINAL_SIZE_DIAGNOSIS_V1.json').read_bytes());assert sizes['returncode']==0;sr=sizes['receipt']['roles'];assert[(x['role'],x['bytes'],x['SHA256'])for x in sr]==[('CURB_PROTECTED878',802787,'20e07a25e41b00849e271a009d9e9859ee24751ff2571bd37c52b4a50d885ea7'),('SLOPE135',509289,'4249ebaff07dd8a0d8b2ab45df806d96172b2c4960f7288789c48fe6bea766cc')];assert all(x['physical_file_opens']==x['whole_raw_hashes']==x['JSON_decodes']==1 and x['input_canonical_unchanged']and x['compact_object_bytes']>262144 and not x['original_failed_results_regraded']for x in sr)
assert(R/'CURRENT_PROGRESS_v55_B4_REAL_CPU_PASS_GOOD_NATIVE750_CLOSED_FINAL_BOUND_FAILURE.md').is_file()
"""
change('known={}\n',guard+'known={}\n')
extra="""for x in json.loads((REPO/'history/experiments/mod4v1_supermimic_bptt_phase40_delta/SOURCE_INDEX.json').read_bytes())['rows']:
 if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or'e33c2fd93335ef47ef6682dfc148b3e27fd46717'}
"""
change('D.mkdir(parents=True);rows=[];files=[];refs=0',extra+'D.mkdir(parents=True);rows=[];files=[];refs=0')
change("'unchanged_reference_existing_phase18_through39'","'unchanged_reference_existing_phase18_through40'")
change("prior_phase39_commit='2c81b89322a393926ba8779b7c4bcbf0de2ede86'","prior_phase40_commit='e33c2fd93335ef47ef6682dfc148b3e27fd46717'")
node=next(n for n in ast.walk(ast.parse(text))if isinstance(n,ast.keyword)and n.arg=='not_captured_yet');old=ast.literal_eval(node.value);new='This point-in-time delta includes the separate actual B4 real-Sensor CPU V2 PASS while retaining V1 failure, the first actual seed29 C878/S135 750-control loops and original failed close/grade, exact whole-case JSON byte-size diagnosis, typed producer/consumer and final-size audit SOURCE as captured. Later source seals, independent reviews, finite case-contract fixes, NEW typed native execution or qualified holdouts and handoffs append later; no model/raw/CPU/SDK/record replay for Git.';change(old,new)
note='''# Phase41 — real sensor CPU success and honest native holdout close failure

The quality-first ordered goal stays active at Stage1. H1/mothers/Registryv12 and original physics/full DR/speeds/skill acceptance, original canonical writer, private/finite EX/SH, reserve and all native deadlines are unchanged. No new BPTT, Gate1 or Stage2 admission, whole-skill pass rate or promotion is claimed.

The old B4 CPU V1 untapped-baseline dtype error remains an immutable failure. A separate V2 changes exactly two synthetic dtype leaves, with full reverse-byte proof; original Sensor/Delay maths, B4/codec, random streams and all seven scenarios remain. Actual TorchCPU V2 passed N80/64 controls/640 original MID-END samples with 41 source identities, original callback identities/private-state/output parity and unchanged Python/TorchCPU RNG. This does not prove actual SDK clock/reset/physical readback or native actor equivalence.

D6 full metadata preflight/static materialization was followed by a NEW exact controller and original parent, after a real readonly free-resource observation and original fresh gates. C878 and S135 each actually recorded 750 controls/6000 physics/1500 feedback/750 mean-actor calls and zero optimizer updates. Both own children returned0 and were actually waited; both EX released, canonical writes0 and no foreign scope touched. The original producer source grade FAILED and outer actual Popen.wait returned1. Those facts are separate and are not promoted by worker RC0 or early FINAL passed_execution.

Both original close paths failed while reading the full case FINAL using a generic262144-byte source-metadata helper before its required original App intent. App close still ran, so zero process return and failed semantic qualification coexist. The original worker errors, absent valid intent, false producer grade, collector bound errors and null bounded-reader counts remain. No after-the-fact intent/grade is written. Group-embedded case counts are explicitly a different provenance, not raw original case-byte proof.

A NEW functional byte/schema diagnosis opened each own original case FINAL once, hashed and decoded once, and did not write it. Exact original sizes are802787 and509289; even compact forms396677 and270439 exceed262144. The largest route_scope values and complete DR/metrics/cache fields are preserved. No metadata, physics, skill threshold or close evidence contract has been changed. A bounded SOURCE audit identifies specific case-read/collector selectors before any new finite contract or native purpose; the old failed run is not retried or regraded for Git.

Typed producer/consumer SOURCE remains unsealed or as captured, with explicit separate clock domains, full80 flags/K IDs/queue, bounded sensor witnesses and UNKNOWN DOF/readback. SOURCE claims, finite data consistency, actual process close, Gate1 and quality remain separate. Late final seals, reviews, new contract tests/actual typed capture and qualified independent holdouts require the next append. Models are skipped before stat/read and raw/binary files are metadata references only; all new/old failure evidence is retained.
'''
tree=ast.parse(text);n=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='note'for t in n.targets));lines=text.splitlines(keepends=True);lines[n.lineno-1:n.end_lineno]=['note='+repr(note)+'\n'];text=''.join(lines)
change('mod4v1-supermimic-phase1-b4-cpu-good-static-stage-phase40','mod4v1-supermimic-phase1-b4-sensor-pass-case-final-bound-phase41')
change('Record good static stage and real sensor CPU evidence','Record real sensor CPU pass and native case close-bound failure')
change("'--validation','quality-first;","'--validation','actual-real-Sensor-B4-CPU-V2-pass;old-baseline-dtype-failure-retained;native-two-role750-controls-unqualified-close;generic-case-metadata-cap-root-cause;whole-case-byte-schema-functional-one-read;no-intent-backfill;quality-first;")
ast.parse(text)
with dest.open('x',encoding='utf8',newline='\n')as f:f.write(text)
v=dict(kind='PHASE41_ARCHIVE_SOURCE_PREPARED_NOT_EXECUTED',epoch=time.time(),base_source=source.name,base_SHA256=hashlib.sha256(raw).hexdigest(),new_source=dest.name,bytes=len(text.encode()),SHA256=hashlib.sha256(text.encode()).hexdigest(),required_feature_head='e33c2fd93335ef47ef6682dfc148b3e27fd46717',actual_Git_record_push_native_or_model_operations=0)
with report.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
