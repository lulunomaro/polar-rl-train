"""Keep real601 fullsave; repair only cache tensor transfer, then one missing own0."""
from pathlib import Path
import json,ast,time,hashlib,sys,copy,os
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
import torch
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def one(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def save(name,s):
 ast.parse(s);p=D/name;assert not p.exists();p.write_text(s,encoding='utf8');return dict(path=str(p),sha256=sha(p))
def main():
 evidence=json.loads(sorted((D/'reports').glob('S4_VALID_FIRST_ZERO_FULLSAVE_AND_FAILED_CACHE_ALL_ACTUAL_*.json'))[-1].read_bytes())
 rows={v['relative']:v for v in evidence['files']};prefix='own_first_fullsave0_healthschema/attempt/'
 done=json.loads(Path(rows[prefix+'S4_COMPLETE_ACTUAL.json']['local_path']).read_bytes());assert done['passed'] and done['controls']==0
 source=rows[prefix+'S4_OWN_INTEGRATION_FULLSAVE.pt'];assert source['sha256']==done['own_checkpoint_SHA']=='601455ca68fbabe8a89b9165ce83007fe6157333b1c6f770520b6890a061f19d'
 ck=torch.load(source['local_path'],map_location='cpu',weights_only=False)
 assert all(k in ck for k in ('sensor_DR_state','chassis_PD_state','E1_terrain_state','E1_retained_flat_command_state','S4_shared_control_state'))
 assert not ck['optimizer_state_dict']['state'] and ck['S4_shared_control_state']['completed_controls']==0
 helper=(D/'s4_original_fullstate_migration_v1.py').read_text()
 old="self.cache=state['cache'].to(device).clone();self.completed_controls=state['completed_controls']"
 new="""from tensordict import TensorDict
        raw=state['cache']
        assert set(raw.keys())>={'policy','critic'} and set(raw.keys())<={'policy','critic','s4_training_supported_domain'}
        assert all(torch.is_tensor(v) and v.shape[0]==len(self.previous) for v in raw.values())
        # A freshly built container with each actual tensor moved explicitly;
        # never trust serialized container metadata or a cached .to() result.
        self.cache=TensorDict({k:v.detach().to(device=device).clone() for k,v in raw.items()},batch_size=[len(self.previous)],device=device)
        assert all(v.device==device for v in self.cache.values())
        self.completed_controls=state['completed_controls']"""
 helper=one(helper,old,new);generated=[save('s4_original_fullstate_migration_v2.py',helper)]
 from s4_original_fullstate_migration_v2 import SharedControlState
 # Real serialized GPU-origin state, map_location CPU; no CUDA initialization.
 state=ck['S4_shared_control_state'];s=SharedControlState(state['cache']);s.restore(state)
 assert all(v.device.type=='cpu' for v in s.cache.values()) and torch.equal(s.previous,state['previous'])
 assert all(torch.equal(v,state['cache'][k]) for k,v in s.cache.items())
 class RejectContainerTo:
  def __init__(self,x):self.x=x
  def keys(self):return self.x.keys()
  def values(self):return self.x.values()
  def items(self):return self.x.items()
  def to(self,*a,**k):raise AssertionError('Container to() must not be trusted')
 mutated=copy.deepcopy(state);mutated['cache']=RejectContainerTo(state['cache']);s.restore(mutated)
 assert torch.equal(s.previous,state['previous']) and not torch.cuda.is_initialized()
 worker=(D/'s4_linux20k_missing_zero_fullsave_worker_v3.py').read_text()
 worker=worker.replace("('own_first_fullsave0_healthschema','own_fullrestore0_healthschema')","('own_fullrestore0_cacheABI_v4',)").replace("own=manifest['phase']=='own_fullrestore0_healthschema'","own=True  # Only genuinely missing own restore from valid real601")
 worker=worker.replace('from s4_original_fullstate_migration_v1 import','from s4_original_fullstate_migration_v2 import')
 generated.append(save('s4_linux20k_direct_own_restore0_worker_v4.py',worker))
 parent=(D/'s4_missing_zero_fullsave_parent_v3.py').read_text()
 parent=one(parent,"assert phase in ('own_first_fullsave0_healthschema','own_fullrestore0_healthschema')","assert phase=='own_fullrestore0_cacheABI_v4'")
 parent=parent.replace('s4_linux20k_missing_zero_fullsave_worker_v3.py','s4_linux20k_direct_own_restore0_worker_v4.py')
 parent=one(parent,"first=stage(config,'own_first_fullsave0_healthschema',Path(config['refs'][1]['local_path']))\n        second=stage(config,'own_fullrestore0_healthschema',Path(first['checkpoint']))","assert config['valid_prior_own_zero_source_SHA']=='601455ca68fbabe8a89b9165ce83007fe6157333b1c6f770520b6890a061f19d'\n        second=stage(config,'own_fullrestore0_cacheABI_v4',Path(config['valid_prior_own_zero_source_path']))")
 parent=one(parent,'stages=[first,second]','stages=[second]')
 parent=one(parent,'zero_control_fullsave_and_own_fullrestore_sourcebound_complete=True','own_fullrestore0_from_valid601_complete=True,prior_real_first_zero_fullsave_source_SHA=config[\'valid_prior_own_zero_source_SHA\']')
 generated.append(save('s4_missing_direct_own_restore0_parent_v4.py',parent))
 material=(D/'materialize_s4_zero_fullsave_target_CPU_v3.py').read_text().replace('s4_missing_zero_fullsave_parent_v3','s4_missing_direct_own_restore0_parent_v4')
 material=one(material,"result=dict(epoch=time.time(),passed=True", "assert sha(ctx['valid_prior_own_zero_source_path'])==ctx['valid_prior_own_zero_source_SHA']\n        prior=torch.load(ctx['valid_prior_own_zero_source_path'],map_location='cpu',weights_only=False)\n        assert all(k in prior for k in ('sensor_DR_state','chassis_PD_state','E1_terrain_state','S4_shared_control_state')) and not prior['optimizer_state_dict']['state']\n        result=dict(valid_prior_own_zero_source_path=ctx['valid_prior_own_zero_source_path'],valid_prior_own_zero_source_SHA=ctx['valid_prior_own_zero_source_SHA'],epoch=time.time(),passed=True")
 generated.append(save('materialize_s4_direct_own_restore0_target_CPU_v4.py',material))
 publish=(D/'publish_s4_zero_fullsave_target_CPU_once_v3.py').read_text()
 publish=publish.replace('MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_HEALTH_V3_20261015','MOD4_S4_E0_WAVE35_DIRECT_OWN_RESTORE_CACHE_V4_20261015').replace('MOD4_S4_E0_WAVE35_LINUX_ZERO_FULLSAVE_UPLOAD_V3_20261015','MOD4_S4_E0_WAVE35_DIRECT_OWN_RESTORE_UPLOAD_V4_20261015')
 publish=publish.replace('s4_linux20k_missing_zero_fullsave_worker_v3.py','s4_linux20k_direct_own_restore0_worker_v4.py').replace('s4_missing_zero_fullsave_parent_v3.py','s4_missing_direct_own_restore0_parent_v4.py').replace('materialize_s4_zero_fullsave_target_CPU_v3.py','materialize_s4_direct_own_restore0_target_CPU_v4.py').replace('s4_original_fullstate_migration_v1.py','s4_original_fullstate_migration_v2.py')
 publish=publish.replace('zero_fullsave_health_payload_v3','direct_own_cache_payload_v4').replace('S4_ZERO_FULLSAVE_HEALTH_V3','S4_DIRECT_OWN_CACHE_V4')
 publish=one(publish,"actual_logger_source_SHA='d9822d8317724507a7c817e85399db0db9e56a4eae959435138e75cf92e44b8d')", "actual_logger_source_SHA='d9822d8317724507a7c817e85399db0db9e56a4eae959435138e75cf92e44b8d',valid_prior_own_zero_source_path="+repr(source['path'])+",valid_prior_own_zero_source_SHA="+repr(source['sha256'])+")")
 generated.append(save('publish_s4_direct_own_restore0_target_CPU_once_v4.py',publish))
 dispatch=(D/'dispatch_s4_missing_zero_fullsave_fixed_two_once_v3.py').read_text().replace('S4_ZERO_FULLSAVE_HEALTH_V3','S4_DIRECT_OWN_CACHE_V4').replace('s4_missing_zero_fullsave_parent_v3','s4_missing_direct_own_restore0_parent_v4')
 dispatch=one(dispatch,"['own_first_fullsave0_healthschema','own_fullrestore0_healthschema']","['own_fullrestore0_cacheABI_v4']")
 generated.append(save('dispatch_s4_missing_direct_own_restore0_once_v4.py',dispatch))
 report=dict(epoch=time.time(),passed_CPU=True,valid_real_first_zero_fullsave_source=source,original_first_zero_scope_passed=True,
  original_V3_parent_failed_second_cache_restore_preserved=True,original_error_actual_CPU_and_CUDA_tensor_mismatch=True,
  serialized_container_device_metadata_is_not_actual_tensor_device_proof=True,unique_stale_label_cause_not_proven=True,
  actual_source_cache_keys=list(state['cache'].keys()),fieldwise_actual_tensor_and_fresh_container_CPU_restore_exact=True,
  refuses_reliance_on_container_to_or_its_cached_result=True,source_whole_DR_and_untrained_gate_critic_optimizer_retained=True,
  new_GPU_scope_only_missing_own_restore0=True,no_native120_or_first_fullsave0_replay=True,CUDA_initialized=False,
  new_sources=generated,original_parent_child_absent_two_locks_free=evidence['own_parent_child_absent_two_locks_free'])
 p=D/'reports/S4_REAL601_AND_FIELDWISE_CACHE_CPU_REPAIR_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=True,report=str(p),source_SHA=source['sha256'],only_new_own_restore0=True)))
if __name__=='__main__':main()
