"""One local source integration; no policy/binary reads or target API imports."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent
E2=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4'
E3=L/'E3_97_SOURCE210_ENTRY_RECEIPT_CLI_CLOSURE_REPAIR_SOURCE_20261029_V4'
def put(p,s):p.write_text(s,encoding='utf8',newline='\n')
def change(s,a,b):assert a in s,a;return s.replace(a,b)
p=B/'e0_long_command_domain_telemetry_v1.py';s=p.read_text(encoding='utf8')
s=change(s,'class E0Book:', 'from e0_observed_command_instances_v1 import CommandInstances\n\nclass E0Book:')
s=change(s,'        self.phase_count=t.zeros((2,9,2,n),device=device,dtype=t.long)','        self.phase_count=t.zeros((2,9,2,n),device=device,dtype=t.long)\n        self.phase_error=t.zeros((2,3,9,2,n),device=device)')
s=change(s,'            self.phase_count[phase,bins,key[ids]-6,ids]+=1','            self.phase_count[phase,bins,key[ids]-6,ids]+=1\n            for j,error in enumerate(after[\'errors\']):self.phase_error[phase,j,bins,key[ids]-6,ids]+=error[ids]')
s=change(s,'self.episode=t.zeros(e.num_envs,device=e.device,dtype=t.long);self.command_uid=self.episode.clone()','self.episode=t.zeros(e.num_envs,device=e.device,dtype=t.long);self.command_uid=self.episode.clone()\n        self.instances=CommandInstances(t,e.num_envs,e.device);self.in_reset=t.zeros(e.num_envs,device=e.device,dtype=t.bool)')
s=change(s,"        def reset(this,ids):\n            result=panel.old_reset(ids);selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.episode[selected]+=1", "        def reset(this,ids):\n            selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.instances.close(selected,'reset');panel.episode[selected]+=1;panel.in_reset[selected]=True\n            try:result=panel.old_reset(ids)\n            finally:panel.in_reset[selected]=False")
s=change(s,"        def resample(this,ids):\n            result=panel.old_resample(ids);panel.command_uid[ids]+=1", "        def resample(this,ids):\n            ids=t.as_tensor(ids,device=e.device,dtype=t.long);panel.instances.close(ids,'resample')\n            result=panel.old_resample(ids);panel.command_uid[ids]+=1\n            ctx=panel.instance_context();panel.instances.open(ids,ctx,True)")
s=change(s,'    def begin(self,index,obs):','    def instance_context(self):\n        term=self.cmd;t=self.t\n        return dict(key=classify(t,term.is_standing_env,term.is_pure_spin,term.is_moving_spin,term.is_transition_spin,term.command,term.signed_yaw),episode=self.episode,command_uid=self.command_uid,command=term.command,direction=term.world_direction,signed_yaw=term.signed_yaw)\n\n    def begin(self,index,obs):\n        self.instances.control=index+1')
s=change(s,"        self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names])", "        self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names]);self.instances.observe(c,after)")
s=change(s,'        self.uninstall();self.book.export', '        self.uninstall();instances=self.instances.finish(self.out);self.book.export')
s=change(s,"source_model_SHA=self.task['source_SHA'],original_kind=", "command_instances=instances,transition_phase_error_sums=self.book.phase_error.sum(-1).cpu().tolist(),transition_phase_error_denominators=self.book.phase_count.sum(-1).cpu().tolist(),\n            source_model_SHA=self.task['source_SHA'],original_kind=")
s=s.replace('transition_full12s_same_command_graduation_not_claimed=True','transition_full12s_same_command_graduation_not_claimed=True,observed_complete_command_lifetimes_reported_separately=True')
put(p,s)
# Exact E0 fixture calls selected constructor and real original physics queue on fresh CPU.
s=(E2/'selected_telemetry_constructor_API_fixture_v1.py').read_text(encoding='utf8')
s=change(s,"assert role in ('E2','E3')","assert role=='E0'")
s=s.replace("n=10 if role=='E2' else 13","n=10").replace("role=='E2'","role=='E0'").replace("role=='E3'","False")
start=s.index(" if role=='E0':load");end=s.index(" assert not hasattr(e,'_mod4_ground_z')",start)
s=s[:start]+" load('e0_original_profile_catalog_v1',J/'e0_original_profile_catalog_v1.py');load('e0_observed_command_instances_v1',J/'e0_observed_command_instances_v1.py');tele=load('_selected_actual_E0_telemetry_fixture',J/'e0_long_command_domain_telemetry_v1.py');cls=tele.E0Panel\n"+s[end:]
s=s.replace('_selected_profile_actual_domain','_selected_profile_actual_domain').replace('E2_selected','E0_selected')
# Prove absence of E2 capture API rather than silently supplying synthetic extras.
s=change(s," assert not hasattr(e,'_mod4_ground_z');rng=", " del e._own_native_capture;del e.e3_capture;del e.e3_stepping;del e.e3_shapes;del e._mod4_mode_bit;del e.recovery_original_soft\n assert not hasattr(e,'_mod4_ground_z') and not hasattr(e,'_own_native_capture');rng=")
put(B/'selected_telemetry_constructor_API_fixture_v1.py',s)
# Shared AST architecture, with true E0 filename/hash/CLI/module mapping.
s=(E3/'e3_declared_entry_receipt_cli_contract_v1.py').read_text(encoding='utf8')
replace={
'runtime/isaac/mod4/train_E3_fullstate_v1.py':'runtime/isaac/mod4/train_chassis_pd_resume_ppo.py',
'9799d3485f23f3947d28d64160e3ec68323eafe56b1e822f531ee36fd8441260':'f7ab426fe81444b1c5d0bae7db8173e1309dbbe4fec9eea16006cb7404aad135',
'evaluate_E3_adapted97_source210_frozen600_once_v1.py':'evaluate_E0_adapted82_new86_frozen1000_once_v1.py',
'detached_E3_source210_frozen_recipe_supervisor_once_v1.py':'detached_E0_new86_frozen_profile_supervisor_once_v1.py',
'E3_source210_actual_receipts_readonly_CODE_v4.py':'E0_frozen_actual_receipts_readonly_CODE_v1.py',
'E3_source210_target_source_SDK_metadata_admission_v1.py':'E0_new86_target_source_SDK_metadata_admission_v1.py',
'ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json':'ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json',
'.0002562890625000001':'.00038443359375000017',
'original E3':'original E0','original_E3':'original_E0','E3_PUBLIC_RECOVERY':'E0_DIRECTIONAL_SPIN_V1',
}
for a,b in replace.items():s=s.replace(a,b)
s=s.replace(";modules['directional_spin_runtime']='runtime/isaac/mod4/h1_external_operator_command_v1.py'",'')
put(B/'e0_declared_entry_receipt_cli_contract_v1.py',s)
p=B/'E0_new86_target_source_SDK_metadata_admission_v1.py';s=p.read_text(encoding='utf8')
s=change(s," constructor_proof=run_selected_constructor_fixture(J,'E0',torch)"," constructor_proof=run_selected_constructor_fixture(J,'E0',torch)\n from e0_declared_entry_receipt_cli_contract_v1 import validate_installed_entry_contract\n entry_proof=validate_installed_entry_contract(J,m,Path(modules['isaaclab']).parent/'app/app_launcher.py')")
s=change(s,'selected_constructor_fresh_CPU_API_fixture=constructor_proof,','selected_constructor_fresh_CPU_API_fixture=constructor_proof,declared_entry_CLI_hook_receipt_dependency_closure=entry_proof,')
put(p,s)
# Keep future receipts and Task explicit about the distinct20s original20k diagnostic.
p=B/'remote_E0_new86_long_command_install_and_detach_v1.py';s=p.read_text(encoding='utf8')
s=change(s,'full_WM_tap_included=False)',"full_WM_tap_included=False,population_contract='original20k_D1_D7_fullrestore_no_projection',initial_command_instance_start_unknown=True,requested_simulated_seconds=20,original_episode_seconds=20,complete_command_exposure_may_be_missing=True)")
put(p,s)
print(json.dumps(dict(passed_text_integration_only=True,no_model_reads=True)))
