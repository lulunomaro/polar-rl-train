"""Onlyprepareunconsumedpair2/3 stagers; DOESNOTdispatch/GO/SDK/modelread. Reusefull20koriginalproofschemas."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;base=(D/'stage_dispatch_pair1_v4_e0_curb878_once.py').read_text(encoding='utf-8')
for idx,role,curb,proofrel in((2,'E2','CURB_INDEPENDENT113','reports/E2_b3_no_update_final_20261102_024838/COLLECTION.json'),(3,'E3','SLOPE135','reports/E3_1cd_no_update_final_20261102_031620/COLLECTION.json')):
 lower=role.lower();s=base.replace('PAIR1_V4','PAIR'+str(idx)+'_V1').replace('PAIR1_V4_','PAIR'+str(idx)+'_V1_').replace('PAIR1_ORIGINAL','PAIR'+str(idx)+'_ORIGINAL').replace('PAIR1','PAIR'+str(idx));s=s.replace('CURB_PROTECTED878',curb).replace('curb878','curb113'if idx==2 else'slope135').replace('E0',role).replace('e0',lower);s=s.replace('source_'+lower+'_e2_e3','source_e0_e2_e3').replace("source_family='"+lower+"_e2_e3'","source_family='e0_e2_e3'").replace("=='"+lower+"_e2_e3'","=='e0_e2_e3'")
 start=s.index("proof=R/'"+role+"_actual_fullrestore_native24/");end=s.index(";(out/'evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json')",start)
 replacement="proof=R/"+repr(proofrel)+";collection=json.loads(proof.read_bytes());n=collection['files']['FINAL.json']['rows'][0]['data'];assert collection['files']['FINAL.json']['passed']and collection['files']['PARENT_EXIT_SCOPE.json']['all_own_children_waited']and n['passed']and n['source_SHA']==pins["+repr(role)+"]['source_SHA']and n['num_envs']==20000 and n['controls']==24 and n['core_actor_critic_STD17Adam_before_after_exact'];g=n['new_nominal_guard'];assert g['usd_sha256']==USD and g['contract_sha256']==CONTRACT;v={'source_SHA':n['source_SHA'],'asset_SHA':g['usd_sha256'],'contract_SHA':g['contract_sha256']}"
 s=s[:start]+replacement+s[end:];s=s.replace("R/'staged_sources/"+role+"_MOD4V1_SOURCE_FINAL'/n","Path(descriptor['exact_sealed_overlay'])/n")
 # Pair2/3 constructor musthash ownrolefiles, notthefirstE0entry.
 s=s.replace("h('worker_posttrain_"+lower+"_v1.py')","h('worker_posttrain_'+e['role'].lower()+'_v1.py')").replace("h('"+role+"_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json')","h(e['role']+'_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json')")
 # Exactlivepayload ofthefirst role keepsunified e0_e2_e3 family.
 for name in('posttrain_fullstate_common_v1.py','construct_source_task_go_v1.py'):assert name in s
 ast.parse(s);p=D/('stage_dispatch_pair'+str(idx)+'_v1_'+lower+'_'+('curb113'if idx==2 else'slope135')+'_once.py');assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n');print(p)
