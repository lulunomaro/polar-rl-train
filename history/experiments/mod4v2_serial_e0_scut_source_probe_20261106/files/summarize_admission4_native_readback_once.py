"""Analyze only completed A4 metadata; do not query models or execute physics."""
from pathlib import Path
import json,math
D=Path(__file__).resolve().parent;p=D/'ADMISSION4_NATIVE_LIMIT_FAILURE_SUMMARY.json';assert not p.exists();pointer=json.loads((D/'NINE_ADMISSION4_CLOSED_RESULT_PATH.json').read_bytes());c=json.loads(Path(pointer['path']).read_bytes());m=c['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert c['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and outer['original_owner_reaped']is True
case=c['cases']['H1_normal'];rb=case['V2_NATIVE_LIMIT_READBACK.json'];assert rb['native_tensor_shape']==[20000,30,2]and rb['source_weights_opens']==rb['source_decodes']==0 and case['V2_NATIVE_INITIALIZED.json']is None and case['V2_LEARNER_LOADED.json']is None
rows=[];missing=[]
for r in rb['rows']:
 x=dict(name=r['name'],expected_SI=r['expected_SI'],native_first4=[a['first_four_native']for a in r.get('endpoints',[])],native_ranges=[[a['native_min'],a['native_max']]for a in r.get('endpoints',[])],classification=[a['classification']for a in r.get('endpoints',[])])
 for a in r.get('endpoints',[]):
  want=a['raw_contract_endpoint'];samples=a['first_four_native']
  if want is not None and any(not isinstance(v,(int,float))or abs(v-want)>1e-6 for v in samples):missing.append(dict(name=r['name'],endpoint=a['endpoint'],expected_SI=want,native_first4=samples,native_min=a['native_min'],native_max=a['native_max']))
 rows.append(x)
v=dict(kind='MOD4V2_ADMISSION4_ACTUAL_NATIVE_LIMIT_FAILURE_NOT_SKILL_SCORE',root=c['root'],closed_path=pointer['path'],native_readback_epoch=rb['epoch'],native_api=rb['native_view_type']+'.get_dof_limits',num_envs=20000,target_joint_count=rb['target_joint_count'],missing_finite_mechanical_endpoints=missing,missing_finite_mechanical_endpoint_count=len(missing),native_rows=rows,original_owner_exit=end,outer_actual_wait=outer,source_weights_read_or_decode=0,new_PPO_updates=0,other_eight_GO=any(v.get('GO_PRODUCTION.json')is not None for k,v in c['cases'].items()if k!='H1_normal'),no_threshold_or_asset_changes=True,skill_score=None,goal_complete=False,model_raw_GPU_SDK_C_or_foreign_operations=0)
p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf8');print(json.dumps(dict(path=str(p),missing_count=len(missing),missing=missing,other_eight_GO=v['other_eight_GO'],source_weights_reads=0,new_PPO_updates=0),indent=2))
