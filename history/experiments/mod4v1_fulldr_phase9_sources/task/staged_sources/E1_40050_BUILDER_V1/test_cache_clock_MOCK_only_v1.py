"""Pure MOCK cache/clock proof. Synthetic .txt buffers, fake decoder, NO Torch/PT/SDK."""
from pathlib import Path
import importlib.util,hashlib,json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent

def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
 fixture=module('explicit_fake_complete_dict_fixture',B/'test_four_leaf_migration_MOCK_v1.py').fixture;rows=[]
 for name,role in [('CURB141','E1_CURB'),('SLOPE135','E1_SLOPE')]:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');rt=root/'runtime/isaac/mod4'
  module('e1_four_leaf_migration_v1',rt/'e1_four_leaf_migration_v1.py');cacheModule=module('e1_pinned_source_MOCK_'+name,rt/'e1_pinned_source_v1.py')
  class FakeTorch:
   def __init__(self):self.decodes=0;self.ownloads=0
   def load(self,path,*a,**kw):
    if hasattr(path,'read'):
     assert kw==dict(map_location='cpu',weights_only=False);self.decodes+=1;return fixture(role)
    self.ownloads+=1;return dict(MOCK_OWN_ROUNDTRIP=True)
  torch=FakeTorch();raw=('EXPLICIT_MOCK_NOT_PT_NOT_WEIGHTS_'+name).encode();path=B/('MOCK_CACHE_INPUT_'+name+'.txt')
  with path.open('xb') as f:f.write(raw)
  cache=cacheModule.PinnedSourceE1(torch,path,hashlib.sha256(raw).hexdigest(),len(raw),role=role);assert torch.decodes==1
  with cacheModule.selected_source(cache):
   with cacheModule.runner_source_load_scope():state=torch.load(path,map_location='cpu',weights_only=False)
   assert state['physical_action_delay_state']['control_us']==20000 and state['feedback_delay_recipe']['control_period_us']==10000
   sites=['sensor','feedback','action','spring','gas','chassis_PD','E1terrain_retention']+(['CURBdirection'] if role=='E1_CURB' else [])
   for helper in sites:
    state=cacheModule.cached_load(path,map_location='cpu',weights_only=False,purpose='MOCK_LOGICAL_HELPER_'+helper);assert state['UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP'].name=='MOCK_VARIANT_SPECIFIC_EXTRA'
    assert cacheModule.cached_H(path,purpose='MOCK_LOGICAL_HASH_'+helper)==hashlib.sha256(raw).hexdigest()
   own=cacheModule.cached_load(B/'MOCK_OWN_ARTIFACT_NOT_A_PT.txt',purpose='MOCK_REAL_FALLTHROUGH');assert own['MOCK_OWN_ROUNDTRIP'] and torch.ownloads==1
  r=cache.receipt();assert r['selected_source_physical_byte_reads']==r['selected_source_SHA_calculations']==r['selected_source_decodes']==1
  clock=module('source_clock_MOCK_'+name,rt/'physics_clock.py');actual=clock.validate_clock(.0025);assert actual['policy_hz']==50 and actual['decimation']==8 and actual['contact_bin_samples']==2
  ticks=feedback=bins=0
  for control in range(24):
   for j in range(actual['decimation']):
    ticks+=1;feedback+=int(ticks%4==0);bins+=sum(int(end) for dt,end in clock.fragments(ticks,2500))
  assert ticks==192 and feedback==48 and bins==96
  rows.append(dict(canonical=name,passed=True,MOCK_synthetic_plaintext_input=True,fake_CPU_decoder_not_real_checkpoint=True,real_PT_reads_stats_hashes_decodes=0,cache_receipt=r,clock_source_validation=actual,symbolic_controls=24,symbolic_physics=192,symbolic_feedback=48,symbolic_contact5ms_bins=96,real_SDK_or_GPU_pass=False))
 report=dict(kind='E1_CACHE_AND_50_100_CLOCK_MOCK_ONLY_NOT_ACTUAL_GPU',passed=True,rows=rows,Torch_imports=0,real_PT_SDK_SSH_GPU_budget_operations=0)
 with (B/'CACHE_CLOCK_MOCK_PROOF_V1.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(MOCK_ONLY=True,roles=len(rows),cache_readhashfakedecode_each=1,symbolic_clock=[24,192,48],real_PT_SDK_operations=0,report=str(B/'CACHE_CLOCK_MOCK_PROOF_V1.json')),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('CACHE_CLOCK_MOCK_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),MOCK_ONLY=True,real_PT_SDK_operations=0),f,indent=2)
  raise
