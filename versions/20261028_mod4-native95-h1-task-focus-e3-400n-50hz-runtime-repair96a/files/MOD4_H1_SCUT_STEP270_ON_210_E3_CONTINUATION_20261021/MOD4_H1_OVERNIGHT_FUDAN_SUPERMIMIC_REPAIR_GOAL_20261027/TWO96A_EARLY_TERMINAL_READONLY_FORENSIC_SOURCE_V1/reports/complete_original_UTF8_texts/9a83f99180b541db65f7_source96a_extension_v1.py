"""Exact actual same-source namespace/asset extension. No model access."""
from pathlib import Path
import hashlib,json
def require(v,m):
 if not v:raise ValueError(m)
def validate_value(x,s):
 require(x.get('passed') is True and x.get('kind')=='MOD4_96A_SAME_SOURCE_NAMESPACE_AND_EXACT_ASSET_ROUTE_EXTENSION_V1','actual source-only extension')
 require(x.get('key')==s['key'] and x.get('new_job')==s['job_root'] and x.get('source_SHA')==s['source_SHA'] and x.get('worker_SHA')==s['worker_SHA'],'new target same model/worker')
 require(x.get('base_actual_fullstate_CPU_SHA')==s['source_CPU_SHA'] and x.get('base_actual_waited_proof_SHA')==s['CPU_waited_proof_SHA'],'original actual wholeCPU and waited pins')
 require(x.get('base_actual_fullstate_CPU_path')==s['CPU_path'] and x.get('base_actual_waited_proof_path')==s['CPU_proof_path'],'original CPU paths not a new decode claim')
 require(x.get('no_new_model_decode_or_Torch_SDK_GPU_import') is True and x.get('original95_failed_resource_only_not_model_source') is True and x.get('actual_GPU_fullrestore_native_and_new_policy_still_pending') is True,'scope and original failure preserved')
 require(x.get('payload_manifest_SHA')==s['payload_manifest_SHA'],'new exact input manifest')
 if s['key']=='h1':require(x.get('source_payload_bytes_unchanged') is True,'native source unchanged')
 else:require(x.get('sole_new_relative')=='runtime/assets/import_contract.json' and x.get('added_source_contract_SHA')==x.get('existing_adjacent_mod4_contract_SHA')=='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49','one exact missing actual USD-parent dependency')
 return True
def load(s):
 p=Path(s['source_namespace_extension_path']);require(p==Path(s['job_root'])/'SAME_SOURCE_96A_NAMESPACE_ASSET_EXTENSION_ACTUAL.json','exact source extension path')
 raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()==s['source_namespace_extension_SHA'],'actual source extension bytes pin')
 x=json.loads(raw);validate_value(x,s);return x
