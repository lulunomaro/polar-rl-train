from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1]/'E0_PPO50_gas400_single72_V5_89D_controller_source_candidate_v1'
def main():
 p=HERE/'flat90_detached_launcher_v1.py';assert not p.exists()
 old=(BASE/'E0_single72_detached_launcher_v1.py').read_text('utf8')
 new=old.replace('E0_single72_bound_cfg_v1','flat90_bound_cfg_v1').replace('E0_single72_protocol_v1','flat90_protocol_v1').replace('load_E0_preinstalled_CPU','load_actual_flat_preinstalled_CPU')
 new=new.replace("Path(JOB)/'GO_PRODUCTION.json'","Path(JOB)/'job0/GO_PRODUCTION.json'").replace("Path(JOB)/'adaptation'","Path(JOB)/'job0/production'")
 new=new.replace('E0_LAUNCH','FLAT90_LAUNCH').replace('E0_SINGLE_OWNER_NODE','FLAT90_SINGLE_OWNER_NODE').replace('one_owner_one_real_E0_node','one_owner_one_real_h1_flat90_node').replace('actual_GO_worker_CUDA_PPO_outcome','actual_GO_worker_CUDA_native_outcome')
 p.write_text(new,encoding='utf8');ast.parse(new)
 for name in ('own','start'):
  find=lambda s:next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name)
  assert ast.dump(find(old),include_attributes=False)==ast.dump(find(new),include_attributes=False)
 print(json.dumps(dict(launcher_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_token_memory_stdin_and_exact_identity_start_functions_AST_exact=True)))
if __name__=='__main__':main()
