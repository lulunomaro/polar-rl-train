"""Schema/complete payload fixture only; real CUDA restoration is separate."""
from pathlib import Path
import sys,copy,tempfile,json,hashlib,torch
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D));sys.path.insert(1,str(D.parent/'MOD4_D5_FULL_CONTRACT_20261008/isaac/mod4'))
from gas_damping_factor import GasDamping,PROFILE
from gas_damping_checkpoint import validate_saved_damping
from spring_pressure_checkpoint import exact
def main():
    assert not torch.cuda.is_initialized();checks=[]
    gas=GasDamping(10,'cpu',20261002);gas.reset(torch.arange(10));saved=gas.state_dict()
    assert validate_saved_damping(saved,10,'cpu');checks.append('full_factor_episode_two_private_RNG_schema')
    clone=GasDamping(10,'cpu',20261002);clone.load_state_dict(saved)
    assert exact(clone.state_dict(),saved);checks.append('CPU_component_roundtrip_exact_not_CUDA_proof')
    actor=torch.nn.Linear(35,6);critic=torch.nn.Linear(38,1);opt=torch.optim.Adam(list(actor.parameters())+list(critic.parameters()))
    loss=actor(torch.ones(2,35)).square().sum()+critic(torch.ones(2,38)).square().sum();loss.backward();opt.step()
    base=dict(actor_state_dict=actor.state_dict(),critic_state_dict=critic.state_dict(),optimizer_state_dict=opt.state_dict(),
        distribution_std=torch.tensor([.03]*6),sensor_DR_state={'fixture':'complete original D1-D5 is verified by own real source'},
        global_rng=torch.get_rng_state(),gas_damping_state=saved,gas_damping_recipe={'profile':PROFILE})
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'full.pt';torch.save(base,p);loaded=torch.load(p,weights_only=False)
    assert exact(base,loaded);checks.append('actor_critic_optimizer_std_global_and_gas_complete_payload')
    ids=torch.tensor([1,4,7]);gas.reset(ids);clone.reset(ids);assert exact(gas.state_dict(),clone.state_dict());checks.append('next_selected_private_draw_exact')
    cpu=torch.get_rng_state();clone.reset(ids);assert torch.equal(cpu,torch.get_rng_state());checks.append('global_RNG_unchanged_by_new_group')
    for name,change in [('wrong_parameter',lambda s:s.update(physical_parameter='D5 stiffness')),('count_mismatch',lambda s:s.update(n=11)),
        ('factor_nan',lambda s:s['factor'].__setitem__((0,0),float('nan'))),('missing_RNG',lambda s:s.update(rng=[s['rng'][0]])),
        ('CUDA_CPU_codec_mismatch',lambda s:s.update(rng_device_type='cuda'))]:
        bad=copy.deepcopy(saved);change(bad)
        try:validate_saved_damping(bad,10,'cpu')
        except (AssertionError,ValueError):checks.append(name+'_rejected')
        else:raise AssertionError(name)
    assert len(checks)==10 and not torch.cuda.is_initialized()
    out=dict(passed=True,count=len(checks),checks=checks,Torch=torch.__version__,CPU_only=True,CUDA_initialized=False,
        real_PPO_resume_contract_pending=True,no_GPU_PPO_or_canonical_write=True)
    print(json.dumps(out))
if __name__=='__main__':main()
