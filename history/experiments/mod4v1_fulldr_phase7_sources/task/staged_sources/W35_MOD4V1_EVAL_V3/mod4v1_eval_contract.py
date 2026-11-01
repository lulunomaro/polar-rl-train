"""New MOD4v1/W35 EVAL_ONLY identity, no GO or authority writer."""
from pathlib import Path
SHA='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b'
BYTES=17619333;ITER=32481;ADAM=651260;LR=.0002562890625000001;UPDATES=77
KIND='MOD4V1_W35_LATEST32481_FULLDR_SAMEUID_EVAL_V1'
def validate_task(t,admitted=False):
 assert t['kind']==KIND and t['model_SHA']==SHA and t['model_bytes']==BYTES and t['model_iteration']==ITER and t['Adam17']==ADAM and t['actual_saved_LR']==LR
 assert t['num_envs']==20000 and t['controls_max']==1600 and t['worker_seconds']==3600 and t['parent_seconds']==3780 and t['no_new_learning_or_GO']
 assert t['asset_USD_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3' and t['asset_contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
 if admitted:assert t['actual_current_authority_private_shared_resources_admitted'] and t['original_eval_parent_holds_private_and_validation_EX']
 return True
