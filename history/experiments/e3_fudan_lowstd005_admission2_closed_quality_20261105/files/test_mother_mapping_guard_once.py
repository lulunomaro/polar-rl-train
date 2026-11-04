"""One small synthetic regression: native W1's exact-dict/OrderedDict category error, no PT or SDK."""
from pathlib import Path
from collections import OrderedDict
import importlib.util,json,torch
D=Path(__file__).resolve().parent;out=D/'FDN_W2_MAPPING_GUARD_CPU_RESULT.json';assert not out.exists();torch.set_num_threads(1)
def load(v):
 p=D/('source_fudan_native_worker_v'+str(v))/'worker_fudan_sequence_ppo_native_v1.py';spec=importlib.util.spec_from_file_location('worker_guard_'+str(v),p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def fixture(mod):
 m=mod.MotherCache.__new__(mod.MotherCache);m.torch=torch;m.root=dict(actor_state_dict=OrderedDict(a=torch.arange(6).reshape(2,3).float()),critic_state_dict=OrderedDict(b=torch.ones(2)),iter=43090,scalar='unchanged');m.frozen=m._freeze(m.root);return m
old=fixture(load(1));caught=None
try:old.assert_frozen()
except RuntimeError as e:caught=str(e)
assert caught and 'Boolean value of Tensor'in caught,caught
new=fixture(load(2));new.assert_frozen();new.root['actor_state_dict']['a'].add_(1);mutation=None
try:new.assert_frozen()
except RuntimeError as e:mutation=str(e)
assert mutation=='Mother tensor changed',mutation
new=fixture(load(2));new.root['actor_state_dict']['a']=new.root['actor_state_dict']['a'].clone();replacement=None
try:new.assert_frozen()
except RuntimeError as e:replacement=str(e)
assert replacement=='Mother tensor changed',replacement
r=dict(passed=True,old_exact_dict_guard_synthetic_reproduced_error=caught,new_Mapping_OrderedDict_nested_tensor_guard_passed=True,in_place_tensor_version_mutation_detected=True,tensor_replacement_detected=True,Torch=str(torch.__version__),actual_models_SDK_GPU_or_native_policy_steps=0,policy_optimizer_steps=0,no_previous_core_test_rerun=True);out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
