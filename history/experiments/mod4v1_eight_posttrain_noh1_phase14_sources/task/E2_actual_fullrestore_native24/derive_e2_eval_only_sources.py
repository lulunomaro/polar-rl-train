"""Prepare E2-specific bounded eval-only scaffold; does not execute or read E2 PT."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
pairs=[('evaluate_e0_a92_native24_no_update_v1.py','evaluate_e2_b3_native24_no_update_v1.py'),('supervise_e0_a92_no_update_v1.py','supervise_e2_b3_no_update_v1.py'),('collect_a92_no_update_v1.py','collect_b3_no_update_v1.py')]
for old,new in pairs:
 text=(ROOT/'E0_actual_fullrestore_native24'/old).read_text(encoding='utf-8').replace('E0','E2').replace('e0','e2').replace('A92','B3').replace('a92','b3')
 text=text.replace('MOD4_E2_PPO50_GAS400_2610v89d','MOD4_E2_PPO50_GAS400_2610v93').replace('final_valid_update82.pt','final_valid_update92.pt')
 text=text.replace('a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a','b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1')
 # The textual short-name substitution above also changed the initial SHA prefix.
 text=text.replace('b3c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a','b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1')
 text=text.replace('14031973','14615089').replace('31984','42822').replace('641200','859300').replace('.00038443359375000017','.00022500000000000002')
 if old.startswith('evaluate_'):
  anchor="    storage=job/'kit_isolation'";assert anchor in text
  text=text.replace(anchor,"    os.environ.update(OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')\n"+anchor)
  text=text.replace("sys.path[:0]=[str(mod),str(job/'runtime')]","sys.path[:0]=[str(mod),str(job/'runtime'),str(job/'lib')]")
  text=text.replace("'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json'}","'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E2_COMMAND_RESUME_STARTUP_VERIFIED.json'}")
  anchor="            for name in required:assert json.loads(receipts[name].read_bytes())['source_sha256']==SHA";assert anchor in text
  text=text.replace(anchor,"            for name in required:\n                receipt=json.loads(receipts[name].read_bytes());assert receipt.get('source_sha256',receipt.get('source_SHA'))==SHA\n            command_proof=json.loads(receipts['E2_COMMAND_RESUME_STARTUP_VERIFIED.json'].read_bytes());assert command_proof['source_has_E2_command_state']\n            command=source['E2_moving4_command_state'];assert command['kind']=='E2_WORLD_MOVING_SIGNED4' and command['moving_yaw_cap']==4.\n            assert len(command['tensors'])==9 and all(v.shape[0]==20000 for v in command['tensors'].values())\n            term=env.command_manager.get_term('twist');assert type(term).__module__=='e2_directional_spin_runtime_v1' and term._dt==.02")
  text=text.replace('original_six_helper_receipts','original_seven_helper_receipts').replace("one_original_fresh_reset=guard.reset_calls,","one_original_fresh_reset=guard.reset_calls,E2_world_signed4_nine_tensor_private_mode_RNG_restored=True,")
 ast.parse(text)
 with (HERE/new).open('x',encoding='utf-8') as f:f.write(text)
print(json.dumps({'E2_eval_only_sources':[new for old,new in pairs],'E2_PT_SDK_started':False,'gate':'Fresh80 actualPASS and clean exit REQUIRED before any selected source read'},indent=2))
