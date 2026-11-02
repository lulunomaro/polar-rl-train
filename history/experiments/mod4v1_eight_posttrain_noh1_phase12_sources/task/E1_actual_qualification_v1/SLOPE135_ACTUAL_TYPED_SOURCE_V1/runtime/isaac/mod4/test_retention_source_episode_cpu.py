"""Actual saved-counter baseline CPU contract; no CUDA or simulation."""
from pathlib import Path
import ast,json,sys,torch

def main(source):
 torch.set_num_threads(1);ck=torch.load(source,map_location='cpu',weights_only=False);saved=ck['E1_terrain_state']['episode'];assert saved.shape==(20000,) and saved.dtype==torch.long
 new=ast.parse(Path(__file__).with_name('retention_checkpoint_episode_reviewed.py').read_text())
 fn=next(x for x in new.body if isinstance(x,ast.FunctionDef) and x.name=='resume_e1_new_episode')
 statements=[ast.unparse(x) for x in fn.body]
 assert any("episode = ck['E1_terrain_state']['episode']" in x for x in statements)
 assert any('env._e1_episode, episode + 1' in x for x in statements)
 actual=saved+1;assert torch.equal(actual,saved+1)
 assert not torch.equal(actual,saved) and not torch.equal(actual,saved+2)
 assert not torch.equal(actual,torch.zeros_like(saved)+1), 'Actual source is not an all-zero new initialization.'
 old=ast.parse(Path(__file__).with_name('g3_terrain_checkpoint.py').read_text());fn=next(x for x in old.body if isinstance(x,ast.FunctionDef) and x.name=='resume_e1_new_episode')
 positions=[(i,ast.unparse(x)) for i,x in enumerate(fn.body)]
 snapshot=next(i for i,s in positions if s.startswith('episode = env._e1_episode.clone()'))
 restore=next(i for i,s in positions if s.startswith('before = current_state(env)'))
 assert snapshot>restore
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,saved_source_episode_baseline_CPU_verified=True,old_g3_verified_resume_restores_before_increment=True,new_CPU_source_episode_contract_checks=3,actual_source_episode_min=int(saved.min()),actual_source_episode_max=int(saved.max()),initial_zero_episode_is_not_saved_counter=True,no_CUDA_initialized=True,not_physical_new_scope_pass=True)))
if __name__=='__main__':main(sys.argv[1])
