"""Evaluation mode is lease configuration, never policy feedback or task truth."""
def build_frozen_ABC(vec,path,device):
 from retention_native_witness_v8 import CONTEXT
 mode=CONTEXT['router_mode'];assert mode in ('single_eval','rule_eval','gate_eval')
 if mode=='single_eval':
  from s5_retention_single_adapter_v1 import build_retention_single
  return build_retention_single(vec,path,device)
 from s4_retention_pair_adapter_v1 import build_native_rule_pair
 return build_native_rule_pair(vec,path,device)
