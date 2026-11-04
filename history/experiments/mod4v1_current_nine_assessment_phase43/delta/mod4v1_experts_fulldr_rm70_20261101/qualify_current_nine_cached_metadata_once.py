"""Correct local collector's E1 start-marker assumption using existing original evidence.
No new physical evaluation, marker fabrication, producer mutation, SSH, model/raw/SDK reads.
"""
from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent;A=T.parent/'mod4v1_current_nine_assessment_20261104';p=A/'reports/CLOSED_RESULT.json';raw=p.read_bytes();v=json.loads(raw);out=A/'reports/QUALIFIED_CLOSED_RESULT.json';err=A/'reports/COLLECTOR_START_MARKER_ERRATUM.json';assert not out.exists()and not err.exists();outer=v['outer_actual_wait'];end=v['parent_exit'];g=v['parent_group_final'];assert outer['actual_parent_p_wait_returned']and outer['returncode']==0 and not outer['errors'];assert end['all_own_children_waited']and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released']and not end['errors']and v['parent_error']is None;assert g['all_nine_actual_execution_complete']and g['nine_ready_before_start'];original={r['role']:r for r in g['rows']};changes=[];E1={'CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'}
for z in v['rows']:
 role=z['role'];f=z['final'];r=original[role];task=z['task'];pre=z['pre_close'];wait=z['wait'];common=v['common_start'];assert z['ready']and f['passed_execution']and z['error']is None and pre and r['passed_execution']and r['actual_waited']and r['returncode']==0 and wait['actual_waited']and wait['returncode']==0;assert f==r['data']and f['group_id']==v['group_id']and f['GPU_UUID']==v['GPU_UUID'];assert f['controls']==task['controls']and f['optimizer_updates']==0;sc=f['source_cache'];assert sc['source_SHA']==z['selected_model_SHA']and sc['physical_byte_opens']==sc['decodes']==sc.get('SHA_calls',sc.get('SHA_calculations'))==1;assert f.get('physics',f.get('physics_callbacks'))==f['controls']*8 and f.get('feedback',f.get('feedback_samples'))==f['controls']*2
 if role in E1:
  bar=f['group_barrier']['barrier_start'];assert bar==common and bar['all_members_ready']and len(set(bar['members']))==9 and role in bar['members'];assert f['actor_calls']==f['controls']and f['wall_start_epoch']>=common['epoch']and f['wall_end_epoch']>=f['wall_start_epoch'];assert f['env_close_returned']and pre['env_close_returned']and pre['stage']=='COMPLETE'and pre['App_close_will_be_called'];evidence='Original group_barrier + actual actor_calls/physics/feedback + wall_start/end + env/App PRE_CLOSE + inner/outer wait; this worker does not publish WORKER_EVAL_STARTED'
 else:
  assert z['started']and f['first_eval_epoch']>=common['epoch']and f['last_eval_epoch']>=f['first_eval_epoch'];evidence='WORKER_EVAL_STARTED and actual final control counters/timestamps + PRE_CLOSE + inner/outer wait'
 before=z['qualified_execution'];z['collector_V1_qualified_execution']=before;z['qualified_execution']=True;z['actual_start_evidence']=evidence
 if not before:changes.append(dict(role=role,original_started_marker_present=z['started'],actual_actor_calls=f.get('actor_calls'),controls=f['controls'],reason=evidence))
assert len(changes)==4 and{r['role']for r in changes}==E1
v.update(kind='CURRENT_NINE_ASSESSMENT_CLOSED_CORRECT_ORIGINAL_START_SEMANTICS_V2',qualified_execution_count=9,all_nine_qualified=True,collector_erratum=dict(original_report=str(p),original_SHA256=hashlib.sha256(raw).hexdigest(),original_unchanged=True,changes=changes,physical_reruns=0,original_producer_or_markers_modified=False))
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
with err.open('x',encoding='utf8')as f:json.dump(v['collector_erratum'],f,indent=2)
print(json.dumps(dict(qualified_report=str(out),all_nine_qualified=True,physical_reruns=0,changes=changes),indent=2))
