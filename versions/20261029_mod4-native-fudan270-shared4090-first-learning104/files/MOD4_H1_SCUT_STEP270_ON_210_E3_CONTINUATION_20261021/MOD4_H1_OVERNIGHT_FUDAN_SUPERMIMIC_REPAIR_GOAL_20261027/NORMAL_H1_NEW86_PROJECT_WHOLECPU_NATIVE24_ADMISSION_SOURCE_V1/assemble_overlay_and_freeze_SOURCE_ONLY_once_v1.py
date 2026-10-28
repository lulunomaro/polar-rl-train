"""Local source/AST/metadata assembly only: no model, USD/NPZ, SDK or network."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
BASE=L/'NORMAL_H1_PPO86B_400N50_NEW86_RUNTIME_SOURCE_V1';RT='job0/runtime/isaac/mod4/'
def H(x):return hashlib.sha256(x).hexdigest()
def main():
 out=B/'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V1.json';assert not out.exists()
 mf=BASE/'NORMAL_H1_PPO40050_COMPLETE_INPUT_MANIFEST_V1.json';raw=mf.read_bytes();assert H(raw)=='019353f9d6fe37a9633ff3ee471c447edfd6e1a28653c52f521b5ff9286d920b';m=json.loads(raw);assert len(m['files'])==451;rows={r['relative']:dict(r) for r in m['files']}
 overlays=[];inverse_proofs=[]
 def edit(name,changes):
  rel=RT+name;old=(BASE/'candidate_payload'/rel).read_bytes();assert H(old)==rows[rel]['SHA'];sep=b'\r\n' if b'\r\n' in old else b'\n';new=old;ops=[]
  for a,b in changes:
   a=a.encode().replace(b'\n',sep);b=b.encode().replace(b'\n',sep);assert new.count(a)==1,(name,a,new.count(a));new=new.replace(a,b);ops.append((a,b))
  back=new
  for a,b in reversed(ops):assert back.count(b)==1;back=back.replace(b,a)
  assert back==old;ast.parse(new)
  qualified=(L/'W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4'/name).read_bytes();assert ast.dump(ast.parse(new),include_attributes=False)==ast.dump(ast.parse(qualified),include_attributes=False)
  p=B/'input_overlays'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(new);rows[rel]=dict(relative=rel,local_path=str(p),bytes=len(new),SHA=H(new),index_kind='new exact source-only clock extension; original451 frozen unchanged')
  overlays.append(dict(relative=rel,old_SHA=H(old),new_SHA=H(new),proven_same_AST_as_existing_qualified50Hz_adapter=True,existing_qualified_source_SHA=H(qualified)))
  inverse_proofs.append(dict(relative=rel,exact_inverse_bytes=True,changes=[dict(old=a.decode(),new=b.decode()) for a,b in ops]))
 edit('physics_clock.py',[
  ('Reviewed integer-microsecond clock; 100 Hz control and fixed 5 ms bins.','Reviewed integer-microsecond clock; 50 Hz policy control and fixed 5 ms bins.'),
  ('control_s=.01','control_s=.02'),('abs(control_s-.01)','abs(control_s-.02)'),('decimation=10000//us','decimation=20000//us'),('decimation*us!=10000','decimation*us!=20000'),('policy_hz=100.','policy_hz=50.')])
 edit('feedback_delay_runtime.py',[
  ('tick = env.common_step_counter',"tick = getattr(env, '_feedback_100hz_tick', env.common_step_counter)"),
  ('        super().__init__(**kwargs)\n        assert sum(self.observation_manager.group_obs_dim[\'policy\']) == 35',"        self._feedback_100hz_tick = 0\n        super().__init__(**kwargs)\n        self._install_feedback_100hz_sampling()\n        assert sum(self.observation_manager.group_obs_dim['policy']) == 35"),
  ('    def clean_policy(self):',"    def _install_feedback_100hz_sampling(self):\n        assert self.physics_dt == .0025 and self.step_dt == .02\n        previous = self.scene.update\n        def update(dt):\n            previous(dt)\n            tick = int(self._sim_step_counter)\n            if tick % 4 == 0:\n                self._feedback_100hz_tick = tick // 4\n                for name in WIDTHS:\n                    names = self.observation_manager.active_terms['policy']\n                    term = self.observation_manager._group_obs_term_cfgs['policy'][names.index(name)]\n                    term.func(self, **term.params)\n        self.scene.update = update\n\n    def clean_policy(self):"),
  ('tick = int(self.common_step_counter)',"tick = int(getattr(self, '_feedback_100hz_tick', self.common_step_counter))")])
 rel='job0/runtime/reports/SOURCE_FREEZE.json';p=BASE/'candidate_payload'/rel;old=p.read_bytes();freeze=json.loads(old);changes={}
 for r in overlays:
  key=r['relative'].removeprefix('job0/runtime/');assert freeze['sha256'][key]==r['old_SHA'];changes[('sha256',key)]=(r['old_SHA'],r['new_SHA'])
 source=L/'native88C_selected_runtime_integration_source_v1/gas400_source_patcher_v1.py';spec=importlib.util.spec_from_file_location('source_json_scalar_edit_only',source);patcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(patcher);new=patcher.replace_json_scalars(old,changes);p=B/'input_overlays'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(new);rows[rel]=dict(relative=rel,local_path=str(p),bytes=len(new),SHA=H(new),index_kind='only derived source hash entries')
 overlays.append(dict(relative=rel,old_SHA=H(old),new_SHA=H(new),only_two_source_SHA_fields_changed=True))
 for name in ('target_normal_H1_whole_source_SDK_CPU_once_v1.py','target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py'):
  p=B/name;b=p.read_bytes();ast.parse(b);assert name not in rows;rows[name]=dict(relative=name,local_path=str(p),bytes=len(b),SHA=H(b),index_kind='new admission source, never executed as target')
 old=json.loads((T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 result=dict(kind='normal_H1_PPO40050_NEW86_wholeCPU_and_frozen_native24_SOURCE_v1',files=list(rows.values()),base_frozen_451_manifest_SHA=H(raw),base_frozen_worker_SHA=m['worker_SHA'],source_only_clock_overlay=overlays,typed_source_SHA='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4',source_Adam=832460,source_iteration=41448,constructor_LR=.00038443359375000017,expected_RSL_sources=old['expected_actual_RSL_sources'],expected_SDK_math_SHA=old['expected_actual_SDK_math_SHA'],no_learning_GO_or_optimizer=True,all_targetCPU_CUDA_native24_actual_evidence_pending=True)
 target=B/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json';target.write_text(json.dumps(result,indent=2)+'\n')
 ast_checks=[]
 for p in sorted(B.glob('*.py')):
  b=p.read_bytes();tree=ast.parse(b)
  for n in tree.body:
   if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) and any(isinstance(x,ast.Name) and x.id=='AUTH' for x in n.targets):ast.parse(n.value.value)
  ast_checks.append(dict(path=str(p),bytes=len(b),SHA=H(b),parsed=True))
 # Pure integer clock module only; no Torch/model/SDK import or fake physics.
 namespace={};exec(compile((B/'input_overlays'/RT/'physics_clock.py').read_bytes(),'actual_clock_source_only','exec'),namespace);clock=namespace['validate_clock'](.0025,.02);assert clock['decimation']==8 and clock['policy_hz']==50 and clock['contact_bin_us']==5000
 src=json.loads((L/'NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1/reports/NORMAL_H1_TYPED40050_ORIGINAL_FULLSTATE_CPU_ACTUAL_V1.json').read_bytes());assert src['passed'] and src['new_source']['SHA']==result['typed_source_SHA']
 proof=dict(epoch=time.time(),source_only=True,all_source_and_AUTH_AST_passed=True,source_AST=ast_checks,exact_inverse_overlay_proofs=inverse_proofs,clock_function_source_only=clock,no_physics_or_feedback_sample_execution_claim=True,only_original_metadata_and_small_sources_read=True,PT_USD_NPZ_raw_model_reads_this_scope=0,no_SSH_credentials_GPU_or_ledger=True,original451_and_worker_unchanged=True,pending_actual={'target_CPU':True,'CUDA_fullrestore':True,'native24_controls_192physics_48feedback':True,'skill_qualification':True})
 (B/'SOURCE_AST_AND_EXACT_CLOCK_EXTENSION_ONLY_ACTUAL.json').write_text(json.dumps(proof,indent=2)+'\n')
 clone=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json';sdk=L/'NEW86_CLONED_RUNTIME_CUDA_SMALL_SCENE_SOURCE_V2_PROJECT_ENV/reports/NEW86_CLONED_CUDA_SMALL_SCENE_ORIGINAL_RETURNED_ACTUAL.json'
 executable={p.name:H(p.read_bytes()) for p in B.glob('*.py') if p.name!='assemble_overlay_and_freeze_SOURCE_ONLY_once_v1.py'}
 index=dict(status='FROZEN_UNUSED_SOURCE_ONLY_NEW86_NORMAL_H1_ADMISSION',epoch=time.time(),entry_filename='upload_and_admit_NEW86_normal_H1_wholeCPU_native24_secure_stdin_UNUSED_once_v1.py',entry_SHA=executable['upload_and_admit_NEW86_normal_H1_wholeCPU_native24_secure_stdin_UNUSED_once_v1.py'],manifest_SHA=H(target.read_bytes()),input_file_count=len(rows),base451_manifest_SHA=H(raw),executable_source_SHAs=executable,clone_receipt_SHA=H(clone.read_bytes()),actual_clone_CUDA_SDK_receipt_SHA=H(sdk.read_bytes()),phase_wait_seconds=dict(CPU=120,GPU=900,own_timeout_cleanup=30),maximum_control_seconds_after_stdin=1500,known72_binding_optional_only_if_CNone_else_actual_owner_GO_required=True,not_a_training_writer_or_skill_or_WM_data=True,source_AST_only_proof=proof,Git='root ordinary pending; no trial/tag/remote attempted')
 out.write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(dict(index=str(out),index_SHA=H(out.read_bytes()),entry_SHA=index['entry_SHA'],manifest_SHA=index['manifest_SHA'],files=len(rows),source_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  import traceback
  p=B/('SOURCE_ASSEMBLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_model_GPU_or_network=True),indent=2));raise
