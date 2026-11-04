"""New admission002: add missing data dependency; immutable old001 stays HOLD. No robot imports/tests."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;V=R/'STARTUP_STAND_V4';OLD=V/'front_admission001';D=V/'front_admission002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(p):return json.loads(p.read_bytes())
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
assert not D.exists()
assert sha(OLD/'CONFIG.json')=='5073d59802a8fd37785cf1481624a28be3acea7c302d4ebc5a71fc2edfd0195d'
assert sha(OLD/'PROTOCOL.json')=='e753e7fcc7c28376f7e9a487c3cf5f1749720d0a4a60f79ef02cc2adbfdc747a'
assert sha(OLD/'SOURCE_PREEXEC.json')=='2f35d373ba2326880ef0a11342d7281749dbeee347a93b841ea73e3b5b6b2269'
assert sha(OLD/'FINAL_ENTRY_REVIEW_001.json')=='1cf80b270b35743d830bb7f34658eb7b1d5b12a1e76b24934b89dd56693f32af'
hold=get(OLD/'FINAL_ENTRY_REVIEW_001.json');assert hold['ready_one_front_nominal'] is False and len(hold['issues'])==1
cfg=get(OLD/'CONFIG.json');assert not (R/'results'/cfg['case_id']).exists() and not (R/'batches'/cfg['case_id']).exists()
index=get(OLD/'SOURCE_PREEXEC.json');assert len(index['files'])==54
support=R/'TALL_ROUGH_BANK_V1/gain_delta20.json';pin=hold['missing_support_input']
assert str(support)==pin['path'] and support.stat().st_size==pin['bytes']==29484
assert sha(support)==pin['SHA']=='f97040665db51c4bc1686187f14aa46579d8d6f6eabff6ef2ee69dea5328d099'
assert all(Path(x['path']).resolve()!=support.resolve() for x in index['files'])
old_launcher=R/'launch_startup_world_support_v4.py';launcher=R/'launch_startup_world_support_v4_v2.py'
assert not launcher.exists()
old_bytes=old_launcher.read_bytes();old_text=old_bytes.decode('utf-8')
assert old_text.count('STARTUP_STAND_V4/front_admission001')==1
new_text=old_text.replace('STARTUP_STAND_V4/front_admission001','STARTUP_STAND_V4/front_admission002')
assert new_text.replace('STARTUP_STAND_V4/front_admission002','STARTUP_STAND_V4/front_admission001').encode('utf-8')==old_bytes
with launcher.open('xb') as f:f.write(new_text.encode('utf-8'))
# Inherit exactly54 locked records, not a second deep source/proof/model review.
extra=[support,Path(__file__).resolve(),launcher]
records=index['files']+[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p)) for p in extra]
assert len(records)==57 and len({x['path'] for x in records})==57
D.mkdir(exist_ok=False)
with (D/'CONFIG.json').open('xb') as f:f.write((OLD/'CONFIG.json').read_bytes())
protocol=get(OLD/'PROTOCOL.json');protocol.update(admission_revision=2,metadata_only_dependency_lock_repair=True,
    previous_admission=str(OLD),previous_review_SHA=sha(OLD/'FINAL_ENTRY_REVIEW_001.json'),
    support_dependency_pin=pin,core_entry_proof_and_old54_records_unchanged=True,
    same_case_id_unconsumed_no_prior_physics=True)
index=dict(index);index.update(files=records,inherited54_exact_record_identity=True,
    added_support_dependency_from_independent_saved_synthetic_binding=pin,
    launcher_rehashes_all57_before_first_new_case=True)
dump(D/'SOURCE_PREEXEC.json',index);dump(D/'PROTOCOL.json',protocol)
rc=get(OLD/'PREPARATION_RECEIPT.json')
rc.update(status='PREPARED_V4_ADMISSION002_DATA_DEPENDENCY_LOCK_NOT_EXECUTED',
    config_SHA=sha(D/'CONFIG.json'),protocol_SHA=sha(D/'PROTOCOL.json'),source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),
    files_pinned=57,old54_records_unchanged=True,old_negative_review_preserved=True,
    support_dependency_actual_matches_first_saved_synthetic=True,launcher_SHA=sha(launcher),
    previous_admission_config_byte_exact=sha(D/'CONFIG.json')==sha(OLD/'CONFIG.json'),
    old_launcher_byte_inverse_exact=True,actual_model_FK_PHY_oldQA_extra_proof_Git_calls=0)
dump(D/'PREPARATION_RECEIPT.json',rc)
dump(D/'METADATA_REPAIR_DERIVATION.json',dict(old_launcher_SHA=sha(old_launcher),new_launcher_SHA=sha(launcher),
    only_launcher_change='literal admission directory001->002; exact byte inverse',
    old_preparer_and_old_admission_untouched=True,inherited54_records=index['files'][:54]==get(OLD/'SOURCE_PREEXEC.json')['files'],
    new_dependency=pin,new_script_records=records[-2:],negative_review_SHA=sha(OLD/'FINAL_ENTRY_REVIEW_001.json'),
    source_reference_read_mode='inherited records only; new support payload29484B+new scripts; no old proof or physics replay',
    config_equal=True,case_id_not_previously_consumed=True))
print(json.dumps(rc,indent=2))
