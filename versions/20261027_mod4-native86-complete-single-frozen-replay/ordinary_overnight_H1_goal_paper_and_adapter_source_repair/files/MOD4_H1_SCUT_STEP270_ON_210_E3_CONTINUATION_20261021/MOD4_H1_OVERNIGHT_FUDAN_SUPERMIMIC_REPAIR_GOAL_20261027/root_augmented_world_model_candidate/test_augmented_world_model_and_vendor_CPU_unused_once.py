"""New bounded CPU fixture for new code, never reads native86 checkpoints."""
from pathlib import Path
import hashlib, json, sys, traceback, types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REPORT=ROOT/'reports/AUGMENTED_WHEEL_LEG_WORLD_MODEL_AND_VENDOR_CPU_ACTUAL.json'
assert not REPORT.exists(), 'new fixture once'
intent={'scope':'new source-only synthetic WM/replay/learner test; no saved model/actor/physics/SDK/GPU/SSH','device':'cpu','candidate':str(HERE/'v2')}
(ROOT/'reports/AUGMENTED_WHEEL_LEG_WORLD_MODEL_CPU_INTENT_ACTUAL.json').write_text(json.dumps(intent,indent=2),'utf8')
sys.path.insert(0,str(HERE/'v2'))
checks=[]
try:
    import torch
    from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel, WheelLegStateLayout, require_architecture_source_migration, learner_error_floor
    from supermimic_wheel_leg_v3.geometry import flatten_state, unflatten_state
    from supermimic_wheel_leg_v3.learner import SuperMimicLearner
    from supermimic_wheel_leg_v3.replay import ReplayBuffer
    torch.set_num_threads(2)
    def check(name, value):
        assert bool(value),name
        checks.append(name)
    def rejects(name, fn):
        try: fn()
        except ValueError: checks.append(name); return
        raise AssertionError(name)
    layout=WheelLegStateLayout()
    n=3
    p=torch.zeros(n,3);p[:,2]=.3377423
    R=torch.eye(3).expand(n,3,3).clone()
    state=(p,R,torch.zeros(n,3),torch.zeros(n,3),torch.zeros(n,30),torch.zeros(n,30),torch.zeros(n,54))
    packed=layout.pack(state)
    check('physical30 plus aux54 is explicit packed127, seven parts',packed.shape==(n,127) and len(unflatten_state(packed))==7)
    check('two packing implementations agree',torch.equal(packed,flatten_state(state)))
    check('state roundtrip',all(torch.allclose(x,y,atol=1e-6) for x,y in zip(state,layout.unpack(packed))))
    rejects('legacy73 rejected instead of fictitious joint inference',lambda:unflatten_state(packed[:,:73]))
    rejects('legacy checkpoint semantic contract rejected',lambda:require_architecture_source_migration({'schema':'native86_xi49'},{'schema':'wheel_leg_v3_static_dynamic'}))
    require_architecture_source_migration({'schema':'v3'},{'schema':'v3'})
    checks.append('equal explicit semantic contracts accepted')
    wm=AugmentedWheelLegWorldModel(context_dim=4,hidden=(32,32))
    action=torch.zeros(n,6);xi=torch.zeros(n,4);xi0=xi.clone()
    oldinputs=wm.inputs(state,action,xi)
    shifted=(p+torch.tensor([.2,0.,0.]),*state[1:])
    check('terrain-relative state removes old XY alias',not torch.equal(oldinputs,wm.inputs(shifted,action,xi)))
    changed=(*state[:6],state[6]+.1)
    check('dynamic auxiliary enters model input',not torch.equal(oldinputs,wm.inputs(changed,action,xi)))
    with torch.no_grad(): wm.net[-1].bias[-54:]=.1
    nxt=wm.step(state,action,xi)
    check('aux state evolves rather than frozen xi',torch.all(nxt[6]>state[6]))
    check('static xi not modified by step',torch.equal(xi,xi0))
    check('WM output and error label include dynamic54',wm.targets(state,nxt).shape==(n,126) and wm.state_error(nxt,state).shape==(n,126))
    check('original physical increments preserved independently of aux',torch.allclose(nxt[0],state[0]) and torch.allclose(nxt[4],state[4]))
    check('7-part trajectory stack',layout.stack([state,nxt],1)[6].shape==(n,2,54))
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(20261027)
        with torch.no_grad():
            for parameter in wm.parameters():
                if parameter.ndim>1: parameter.normal_(0,.02)
        a=action.clone().requires_grad_()
        pred=wm.step(state,a,xi)
        grad=torch.autograd.grad(pred[6].square().sum()+pred[0].square().sum(),a)[0]
        check('new source has finite nonzero action Jacobian into body and aux',torch.isfinite(grad).all() and grad.abs().max()>0)
    dummy=types.SimpleNamespace(wm=wm,cfg=types.SimpleNamespace(wm_window=2),mdp=types.SimpleNamespace(normalize_context=lambda x:x),err_floor=learner_error_floor(layout))
    states=torch.stack((packed,layout.pack(nxt)),1)
    actions=torch.zeros(n,2,6)
    contexts=xi[:,None].expand(n,2,4).clone()
    predicted=SuperMimicLearner._wm_rollout(dummy,states,actions,contexts)
    check('actual new learner autoregressive fit carries seventh dynamic state',len(predicted)==7 and predicted[6].shape==(n,2,54))
    loss,last=SuperMimicLearner._wm_err(dummy,predicted,states,torch.ones(n,2))
    check('actual learner full state loss finite',torch.isfinite(loss) and torch.isfinite(last).all())
    replay=ReplayBuffer(8,n,'cpu',num_joints=30,context_dim=4,action_dim=6,state_dim=127)
    for i in range(4):
        replay.add(dict(s=packed,s1=layout.pack(nxt),a=action,a_prev=action,xi=xi,r=torch.zeros(n),f=torch.full((n,),i,dtype=torch.long),ep_step=torch.full((n,),i,dtype=torch.int32),done=torch.zeros(n,dtype=torch.bool)))
    window=replay.sample_windows(4,2)
    start,history=replay.sample_starts(4,3)
    check('actual replay preserves127 state and4 fixture static context',window['s'].shape==(4,2,127) and window['xi'].shape==(4,2,4) and history['s'].shape==(4,3,127))
    check('actual replay histories keep true physical30/aux54 layout',len(unflatten_state(start['s']))==7)
    source_index=[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((HERE/'v2/supermimic_wheel_leg_v3').iterdir()) if p.is_file()]
    result={'schema':'source_only_augmented_WM_CPU_fixture_v1','passed':True,'checks':checks,'count':len(checks),'intent':intent,'static_context4':'synthetic fixture width only; actual DR schema/getters require separate verified contract','not_actual_native86_parameters':True,'not_actor_forward':True,'no_skill_or_actual_SDK_admission':True,'runtime_bridge_and_MDP_still_pending':True,'source_index':source_index}
except BaseException:
    result={'passed':False,'checks_before_failure':checks,'intent':intent,'error':traceback.format_exc(),'all_partial_source_preserved':True}
    REPORT.write_text(json.dumps(result,indent=2),'utf8')
    raise
REPORT.write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps({'passed':True,'count':len(checks),'report':str(REPORT)}))

