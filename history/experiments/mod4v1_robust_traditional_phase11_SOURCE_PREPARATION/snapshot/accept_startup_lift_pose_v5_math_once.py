"""Parent new saved-evidence acceptance, no controller import or old test execution."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;V=R/'STARTUP_STAND_V5';O=V/'PARENT_MATH_PROOF_ACCEPTANCE.json'
def get(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists()
p=get(V/'preflight001/RESULT.json');rc=get(V/'preflight001/RECEIPT.json');done=get(V/'preflight001/COMPLETION_RECEIPT.json')
assert p['status']=='PASS_NEW_V5_TIMING_ONLY_FEATURE_SYNTHETIC_NOT_STANDUP'
assert p['counts']==rc['counts']==done['counts'];c=p['counts']
assert (c['enabled_external_new_and_V4_oracle'],c['disabled_external_new_and_V4_oracle'],c['typed_contexts'],c['checks'])==(57,40,16,455)
assert c['geometry_calls']==c['model_FK_PHY_DARE_DR_oldQA_native_Git_agents']==p['model_FK_PHY_DARE_DR_oldQA_native_Git_agents']==0
assert len(p['typed'])==16 and all(x['passed'] is True for x in p['typed'])
assert p['branch_fired_LIFT_commands']==rc['new_proof_actual_branch_fired']==8
assert p['source_after_equal'] is rc['all_source_before_after_equal'] is True
assert p['same_input_leg_reference_and_FF_unchanged'] is p['non_LIFT_original_V4_delegate'] is p['inactive_20pairs_exact'] is True
assert p['V7_entry_not_imported_or_executed'] is p['old551_not_replayed'] is True
assert sha(V/'preflight001/RESULT.json')==rc['result_SHA']=='e18bbb0f8296c3de8cbb45d961689738fa3e342560e7f551e036273c847fc647'
assert sha(V/'controller.py')==rc['core_SHA']=='209c0385d1501021b05822f0222228ae78b012570f73fb526a435e8c02b2045a'
assert sha(R/'run_startup_stand_case_v7.py')==rc['entry_SHA']=='b96f10a45b79527e63a5afdc126579b480ce87931aeb8de57d2805e0a8b48367'
assert sha(V/'preflight001/REPORT.md')==rc['report_SHA']
records={}
for x in p['source_before']+done['artifacts']:
    f=Path(x['path']).resolve();assert f.is_relative_to(R) and f.stat().st_size==x['bytes'] and sha(f)==x['SHA'],str(f)
    key=str(f).casefold();rec=dict(path=str(f),bytes=x['bytes'],SHA=x['SHA'])
    if key in records:assert records[key]==rec
    records[key]=rec
for f in [Path(__file__).resolve(),V/'preflight001/COMPLETION_RECEIPT.json',V/'derive_sources.py',V/'GENERATION_FAILURE_SOURCE_001.py',V/'GENERATION_FAILURE_001.txt',V/'GENERATION_FAILURE_RECEIPT_001.json',V/'preflight001/STDERR_001.txt',V/'preflight001/PREPARATION_NOTE_001.md']:
    assert f.is_file() and f.stat().st_size<2*1024*1024
    records[str(f.resolve()).casefold()]=dict(path=str(f.resolve()),bytes=f.stat().st_size,SHA=sha(f))
a=dict(approved_synthetic_only=True,physical_skill_qualified=False,counts=dict(enabled_including_oracles=57,disabled_including_oracles=40,typed_cases=16,checks=455),
    new_feature_branch_fired_in_synthetic=True,synthetic_branch_commands=8,proof_failures=0,core_SHA=rc['core_SHA'],entry_SHA=rc['entry_SHA'],proof_SHA=rc['result_SHA'],
    actual_parent_read_core209_entry111_proof329_report10_receipt26=True,completion_metadata_long_line_truncated_but_artifact_records_parsed_and_checked=True,
    generator_error_and_original_stderr_warning_preserved=True,warning_did_not_change_sources_or_reexecute_proof=True,
    synthetic_fixture_K_is_NOT_actual_nominal_K_or_skill_proof=True,first_physical_case_requires_independent_review_and_separate_parent_approval=True,
    source_artifacts=sorted(records.values(),key=lambda x:x['path'].casefold()),new_controller_model_FK_PHY_oldQA_ARM_Git_calls=0,PH11pending=True)
with O.open('x',encoding='utf-8',newline='\n')as f:json.dump(a,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:v for k,v in a.items()if k!='source_artifacts'},indent=2))
