"""Metadata-only exact NEW savedmodel binding. Never reads PT or budget."""
from pathlib import Path
import json,math
P=json.loads((Path(__file__).resolve().parent/'SOURCE_PRODUCER_METADATA.json').read_bytes())
SHA=P['SHA'];BYTES=P['bytes'];ITER=P['saved_iteration'];ADAM=P['Adam_min'];UPDATES=P['actual_new_PPO_updates'];LR=None
KIND='MOD4V1_W35_POSTADAPT_MOTION_WIRING_TRACE200_V1'
assert P['source_SHA']=='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b' and UPDATES>0 and ITER==32481+UPDATES and ADAM==P['Adam_max']==651260+20*UPDATES and P['full_core_STD_optimizer_and_targetDR_saved'] and P['same_RM70_course_assignment_command_fullstate_restored']
def validate_task(t,admitted=False):
 assert t['kind']==KIND and t['model_SHA']==SHA and t['model_bytes']==BYTES and t['model_iteration']==ITER and t['Adam17']==ADAM and t['model_new_PPO_updates']==UPDATES and t['model_path']==P['path'] and t['actual_saved_LR'] is None
 assert t['num_envs']==20000 and t['controls_max']==200 and t['worker_seconds']==900 and t['parent_seconds']==1200 and t['no_new_learning_or_GO']
 assert t['asset_USD_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3' and t['asset_contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
 if admitted:assert t['actual_current_authority_private_shared_resources_admitted'] and t['actual_parent_privateEX_finiteSH']
 return True
