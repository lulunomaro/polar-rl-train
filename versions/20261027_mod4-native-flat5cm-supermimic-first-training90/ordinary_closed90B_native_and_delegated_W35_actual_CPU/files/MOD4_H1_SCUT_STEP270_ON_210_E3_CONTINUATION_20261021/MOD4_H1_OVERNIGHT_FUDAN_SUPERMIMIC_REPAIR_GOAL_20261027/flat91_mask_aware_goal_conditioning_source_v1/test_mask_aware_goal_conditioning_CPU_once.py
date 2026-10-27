from pathlib import Path
import ast, hashlib, importlib.util, json, sys, time
import torch

F=Path(__file__).resolve().parent
T=F.parents[1]
N=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027'
old=N/'payload/source/supermimic_wheel_leg_v3/networks.py'
new=F/'supermimic_wheel_leg_v3/networks.py'
sys.path[:0]=[str(F),str(N/'payload/source')]
from flat91_mask_aware_goal_conditioning_v1 import masked_goal_conditioning, validate_goal_source

def main():
    if (F/'SOURCE_CPU_STARTED.json').exists():raise RuntimeError('one source-purpose fixture only')
    (F/'SOURCE_CPU_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),no_saved_model_load=True)),encoding='utf8')
    torch.set_num_threads(2)
    results=[]
    a=ast.parse(old.read_text('utf8'));b=ast.parse(new.read_text('utf8'))
    def unchanged(tree):
        out=[]
        for node in tree.body:
            if isinstance(node,ast.ImportFrom) and node.module=='flat91_mask_aware_goal_conditioning_v1':continue
            if isinstance(node,ast.ClassDef) and node.name in ('Policy','Critic'):
                node.body=[x for x in node.body if not isinstance(x,ast.FunctionDef) or x.name!='forward']
            out.append(ast.dump(node,include_attributes=False))
        return out
    assert unchanged(a)==unchanged(b)
    results.append('all original AST except exact Policy/Critic forward and one import retained')
    spec=importlib.util.spec_from_file_location('supermimic_wheel_leg_v3.networks_flat91_source_fixture',new)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    raw=torch.zeros(2,10,146);raw[...,:13]=.2;raw[...,73:86]=1;raw=raw.reshape(2,1460)
    assert validate_goal_source(raw)
    normalized=torch.full_like(raw,100.,requires_grad=True)
    out=masked_goal_conditioning(normalized,raw).reshape(2,10,146)
    assert torch.equal(out[...,73:],raw.reshape(2,10,146)[...,73:])
    assert torch.equal(out[...,13:73],torch.zeros_like(out[...,13:73]))
    out.sum().backward()
    gradient=normalized.grad.reshape(2,10,146)
    assert (gradient[...,:13]==1).all() and (gradient[...,13:]==0).all()
    results.append('unknown normalized values stay zero; masks literal; known-value gradient retained')
    wrong=raw.clone();wrong.reshape(2,10,146)[0,0,73]=.5
    try:validate_goal_source(wrong)
    except ValueError:pass
    else:raise AssertionError('untyped mask accepted')
    results.append('non-binary mask rejected at admission without per-step GPU synchronization')
    original=__import__('supermimic_wheel_leg_v3.networks',fromlist=['Policy','Critic'])
    pi=mod.Policy(86,1460,hist=10,z_dim=4,num_joints=6,hidden=(8,))
    critic=mod.Critic(1625,hidden=(8,))
    oldpi=original.Policy(86,1460,hist=10,z_dim=4,num_joints=6,hidden=(8,))
    oldcritic=original.Critic(1625,hidden=(8,))
    for src,dst in [(oldpi,pi),(oldcritic,critic)]:
        dst.load_state_dict(src.state_dict(),strict=True)
        assert set(src.state_dict())==set(dst.state_dict())
        assert all(torch.equal(x,dst.state_dict()[k]) for k,x in src.state_dict().items())
    results.append('same architecture and literal state dict including all original normalizers')
    pi.goal_norm.mean.fill_(1);pi.goal_norm.var.zero_();pi.goal_norm.count.fill_(200014848)
    critic.norm.mean.fill_(1);critic.norm.var.zero_();critic.norm.count.fill_(200014848)
    pi_before={k:v.clone() for k,v in pi.state_dict().items()}
    critic_before={k:v.clone() for k,v in critic.state_dict().items()}
    obs=torch.zeros(2,10,86)
    action=pi(obs,raw);value=critic(torch.cat((torch.zeros(2,165),raw),-1))
    assert torch.isfinite(action).all() and torch.isfinite(value).all()
    for module,before in [(pi,pi_before),(critic,critic_before)]:
        assert all(torch.equal(v,module.state_dict()[k]) for k,v in before.items())
    results.append('source fixture forward leaves parameters/norms untouched at frozen-count boundary')
    action.square().sum().backward()
    assert all(x.grad is not None and torch.isfinite(x.grad).all() for x in pi.parameters())
    results.append('synthetic-policy BPTT gradients finite; no saved actor/world model/physics used')
    record=dict(epoch=time.time(),passed=True,checks=results,
        original_networks_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),
        selected_networks_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),
        no_saved_model_load_or_GPU_SDK_physics_remote=True,
        source_only_not_installed_or_trained=True,
        preserved_normalizers_and_optimizers_require_actual_source_admission=True,
        no_actual_learning_gain_or_unique_rootcause_claim=True)
    (F/'SOURCE_CPU_ACTUAL.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    print(json.dumps(dict(passed=True,checks=len(results),source_only=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        (F/('SOURCE_CPU_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc())),encoding='utf8')
        raise
