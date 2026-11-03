"""Derive NEW B admission from saved A outer code, not controller/PHY replay."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V3/front_B_derivation001';D.mkdir(exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def replace(text,old,new):
    assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)
source=R/'prepare_startup_tracking_front_v3a.py';raw=source.read_bytes();text=raw.decode('utf-8')
text=replace(text,'B is not admitted by this preparer, including if its synthetic proof is green.','B requires actual failed A sensor eligibility; physics still needs separate review/approval.')
text=replace(text,"STARTUP_STAND_V3/front_A_admission001","STARTUP_STAND_V3/front_B_admission001")
text=replace(text,"case_id='startup_front065_tracking_v3a_nominal1',kind='NEW_STARTUP_TRACKING_QUIET_FRONT_NOMINAL_V3A',controller=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False)","case_id='startup_front065_tracking_v3b_nominal1',kind='NEW_STARTUP_ELIGIBLE_ALIGNMENT_FRONT_NOMINAL_V3B',controller=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=True)")
anchor="old=json.loads((R/'STARTUP_STAND_V1/front_admission001/CONFIG.json').read_bytes());cfg=dict(old)"
guard="""Aresult=R/'results/startup_front065_tracking_v3a_nominal1/result.json';Aanalysis=R/'STARTUP_STAND_V3/front_A_saved_analysis001/RESULT.json'
ar=json.loads(Aresult.read_bytes());az=json.loads(Aanalysis.read_bytes())
assert ar['config']['case_id']==az['case_id']=='startup_front065_tracking_v3a_nominal1'
assert ar['startup_stand_original_v1_gate']is False and ar['stop']=='controller_fault'and ar['controller_fault_reason']=='startup timeout6s'
assert az['future_B_condition_available_but_NOT_launch_permission']is True and az['actual_A_sensor_alignment_eligible_count']>0
assert ar['trace_artifact']==az['source_trace_producer']and az['actual_control_stream_open_count']==1 and az['actual_physics_stream_or_old_raw_open_count']==0
"""
text=replace(text,anchor,guard+anchor)
text=replace(text,"roots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()];records=[]","paths.update([Aresult,Aanalysis,R/'STARTUP_STAND_V3/front_A_admission001/CONFIG.json',R/'STARTUP_STAND_V3/front_A_admission001/PROTOCOL.json'])\nroots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()];records=[]")
text=replace(text,"kind='STARTUP_V3A_TRACKING_QUIET_FRONT065_ONE_NOMINAL_TRAIN'","kind='STARTUP_V3B_ELIGIBLE_POSE_ALIGNMENT_FRONT065_ONE_NOMINAL_TRAIN'")
text=replace(text,"no_automatic_DR_back_side_B_or_retry=True,profile_B_not_admitted=True,","no_automatic_DR_back_side_or_retry=True,profile_B_not_admitted=False,A_saved_evidence_required=True,A_sensor_eligible_count=az['actual_A_sensor_alignment_eligible_count'],A_first_sensor_eligible_s=az['actual_A_first_sensor_alignment_eligible_s'],")
text=replace(text,"B_future_eligibility='Only later separate approval if actual A saved sensor eligibility occurred and A original pass is false; no B if A already passes.',","B_offline_admission_only_no_truth_control='Actual A originalgateFalse+sensor eligibility already observed; this does not add ground-truth inputs to runtime controller.',")
text=replace(text,"A_is_training_not_holdout_or_reliability_certificate=True","B_is_training_not_holdout_or_reliability_certificate=True")
text=replace(text,"status='PREPARED_V3A_NEW_NOMINAL_NOT_EXECUTED'","status='PREPARED_V3B_AFTER_REAL_A_SENSOR_ELIGIBILITY_NOT_EXECUTED'")
new=R/'prepare_startup_tracking_front_v3b.py';assert not new.exists();new.write_bytes(text.encode('utf-8'))
ls=R/'launch_startup_tracking_front_v3a.py';lb=ls.read_bytes();lt=lb.decode('utf-8').replace('V3A','V3B').replace('front_A_admission001','front_B_admission001').replace('tracking_v3a_nominal1','tracking_v3b_nominal1').replace('alignment_wheel_enable=False','alignment_wheel_enable=True')
lt=replace(lt,"protocol['profile_B_not_admitted']is True","protocol['profile_B_not_admitted']is False and protocol['A_saved_evidence_required']is True")
lt=replace(lt,"    return launch(R,cfg['case_id']", "    az=json.loads((R/'STARTUP_STAND_V3/front_A_saved_analysis001/RESULT.json').read_bytes())\n    ar=json.loads((R/'results/startup_front065_tracking_v3a_nominal1/result.json').read_bytes())\n    assert az['future_B_condition_available_but_NOT_launch_permission']is True and az['actual_A_sensor_alignment_eligible_count']>0 and ar['startup_stand_original_v1_gate']is False\n    assert ar['trace_artifact']==az['source_trace_producer']\n    return launch(R,cfg['case_id']")
lt=lt.replace('no_automatic_DR_back_side_B_or_retry=True','no_automatic_DR_back_side_or_retry=True').replace('V3B tracking/quiet nominal case','V3B eligible pose-alignment nominal case')
ln=R/'launch_startup_tracking_front_v3b.py';assert not ln.exists();ln.write_bytes(lt.encode('utf-8'))
with (D/'DERIVATION.json').open('x',encoding='utf-8')as f:json.dump(dict(status='NEW_B_OUTER_CODE_DERIVED_NOT_IMPORTED_OR_EXECUTED',old_prepare_SHA=sha(raw),new_prepare_SHA=sha(new.read_bytes()),old_launcher_SHA=sha(lb),new_launcher_SHA=sha(ln.read_bytes()),changes='B freshID/alignmentTrue, real-A saved conditional guard+pins, B protocol fields; controller/entry/physics not changed',model_QA_FK_PHY_or_oldcase_replay=0),f,indent=2)
print('B_ADMISSION_CODE_DERIVED_ONLY_NO_PREPARER_OR_PHYSICS_EXECUTED')
