"""New V4 document snapshot QA only; no controller/model/raw, old QA or tool invocation."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent
O=R/'reports/STARTUP_DEPLOY_PROGRESS_20261104_V4_VALIDATION.json'
assert not O.exists(), 'This document snapshot validation has already been consumed'
docs=[R/'reports/STARTUP_DEPLOY_PROGRESS_20261104_V4.md',R/'CONTINUATION_V5_CLOSED_FIRST_LINK_V16.md']
records=[];links=[]
for p in docs:
    raw=p.read_bytes();s=raw.decode('utf-8')
    records.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    for m in re.finditer(r'\]\(<([^>]+)>\)',s):
        dest=m.group(1)
        assert dest.startswith('F:/RMPOLAR-RL/'),dest
        target=Path(dest.split('#',1)[0])
        assert target.is_file(),str(target)
        links.append(dict(document=str(p),destination=dest,exists=True))
def get(rel):return json.loads((R/rel).read_bytes())
a=get('MOD4_DEPLOYMENT_FIRST_LINK_V16/RESULT.json')
assert a['link_calls']==1 and a['returncode']==0 and a['output_present'] is True
assert a['output_bytes']==a['image']['bytes']==629048 and a['diagnostic_lines']==[]
assert a['image']['SHA']=='a70772a2c56bf38c144817b86a27d2ca01d32aa288c17bdcb9b592987ff4f601'
assert a['input_current_SHA_matched165'] is a['inputs_poststat_unchanged'] is True
assert a['latest_MOD4_C3_startup_integration'] is a['full_hardware_firmware_qualified'] is False
assert a['image']['entry']==0x080003dd and a['image']['first_flash_vector_words']['initial_SP']==0x20010330
b=get('results/startup_front065_lift_pose_v5_nominal1/result.json')
assert b['controls']==188 and b['physics_steps']==3760 and b['complete'] is False
assert b['startup_stand_original_v1_gate'] is False and b['controller_phase']=='INHIBIT'
assert b['controller_fault_reason']=='limited startup pitch/roll envelope exceeded'
assert b['end_stable_s']==0 and abs(b['body_height_gain_m']-0.06818300455)<1e-10
q=dict(status='PASS_NEW_V4_REPORT_AND_HANDOFF_SNAPSHOT_LINKS_AND_TWO_SMALL_RESULT_BOUNDARIES',
       document_snapshots=records,local_document_links=len(links),all_local_links_exist=True,links=links,
       small_result_files_read=2,new_image_object_library_or_trace_payload_reads=0,
       controller_model_FK_PHY_oldQA_native_Git_calls=0,
       metadata_asserts_not_hardware_or_standup_qualification=True,
       future_document_edits_require_separate_snapshot_not_reexecuting_this_once=True)
with O.open('x',encoding='utf-8',newline='\n') as f:json.dump(q,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:v for k,v in q.items() if k!='links'},indent=2))
