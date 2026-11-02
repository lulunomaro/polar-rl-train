from pathlib import Path
import sys,json,datetime,time,ast
D=Path(__file__).resolve().parent;R=D.parent;sys.path.insert(0,str(D/'parent_source'));from build_e2_e3_original_role_spec_v2 import build_role_spec
out=D/'parent_source/E2_E3_VALIDATED_ROLE_SPECS_V2.json';assert not out.exists();stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());rows=[]
for idx,role in((2,'E2'),(3,'E3')):
 run='MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR'+str(idx)+'_GENERIC_V2_'+stamp;root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;spec=build_role_spec(role,task_root=R,job_root=root+'/roles/'+role,run_id=run);spec['future_group_root_not_created']=root;rows.append(spec)
v={'kind':'LOCAL_SOURCE_ROLE_SPECS_FROM_ACTUAL_METADATA_NOT_PARENT_OR_READY','rows':rows,'source_models_stat_hash_decode':0,'SSH_SDK_GPU_GO_C_or_remote_root_creation':0};out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps({'roles':[r['role']for r in rows],'validated_full20k_historical_source':[r['source_pin']for r in rows],'PTOpen_SDK_GO_C':0,'remote_roots_created':False},indent=2))
