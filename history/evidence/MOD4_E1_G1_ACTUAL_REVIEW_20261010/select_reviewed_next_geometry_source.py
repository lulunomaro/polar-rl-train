"""CPU selection from actual full-wave and existing inherited-skill evidence, not max iteration."""
from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
p=R/'SELECTED_E1_NEXT_GEOMETRY_BEHAVIOR_SOURCE.json';assert not p.exists()
oldpath=W/'MOD4_E1_RETENTION_REPAIR_20261009/reports/SELECTED_E1_REPAIR_SOURCE.json';old=json.loads(oldpath.read_bytes())
reviews=sorted(R.glob('PROXY_ROUTE_REVIEW_*.json'));reviews=[q for q in reviews if 'ERROR' not in q.name];q=reviews[-1];v=json.loads(q.read_bytes());a=v['review']['anchor32053']
assert a['checkpoint_sha256']==old['source']['sha256'] and old['actual_behavior_review_complete'] and old['source310_snapshot57_finite96']
groups=a['review']['groups'];assert groups['forward']['complete_envs']==groups['forward']['environments']==27 and groups['reverse']['complete_envs']==groups['reverse']['environments']==27
assert a['review']['base_review']['ordinary']==0
ret=json.loads((R/'REVIEW_1791563987.json').read_bytes());assert ret['review_complete']
assert ret['summary']['retention']['world']['rollback32053']['passed']==63 and ret['summary']['retention']['world']['candidate']['passed']==19
v=dict(epoch=time.time(),trial_id='E1-G1-REVIEWED-NEXT-GEOMETRY-SOURCE-SELECT-02',source=old['source'],behavior_review_complete=True,source_count=310,snapshot_count=57,finite_tensors=96,own_PID_bound_receipt=old['own_PID_bound_receipt'],unique_completed_segment=old['unique_completed_segment'],complete_same_G1_route_case=dict(job_id=a['job_id'],review_path=str(q.resolve()),review_sha256=H(q.read_bytes()),groups=groups,ordinary=0),paired_inherited_cases={k:'clk2500-closure-episode-d3-115-e1-retention32053-'+k for k in ('flat','spin','world')},existing_rollback_receipt=dict(path=str(oldpath.resolve()),sha256=H(oldpath.read_bytes())),selection_reason='Actual complete10mm whole-wave passage plus already complete balanced old-skill evidence; new32098 persistent world/positive-straight regression.',candidate32098_not_selected=True,candidate_fullroute_pair_may_still_be_pending=True,old_negative4pi5of8_and_world63of64_residuals_retained=True,not_allDR_RM_or_E1_graduation=True,previous_terrain_state_is_G0_explicit_new_next_geometry_required=True,no_new_PPO_launch_or_canonical_transaction=True,new_budget_seconds=0)
p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(selected_source=v['source'],actual_full10mm_route=True,next_geometry_authority_not_yet_deployed=True)))
