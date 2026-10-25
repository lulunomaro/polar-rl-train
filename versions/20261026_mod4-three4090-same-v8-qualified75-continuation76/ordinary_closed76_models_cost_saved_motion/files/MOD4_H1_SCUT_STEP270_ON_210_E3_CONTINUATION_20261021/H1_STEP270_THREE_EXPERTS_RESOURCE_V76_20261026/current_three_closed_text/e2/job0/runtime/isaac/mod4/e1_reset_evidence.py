"""Bridge independently requested CAD reset q to unchanged D1-D7 restore audit.

Bookkeeping only: never write articulation state or draw a random stream.
"""
import torch

def bind_expected_reset_q(env, ids):
    expected=env._rough_probe_expected_q
    selected=torch.arange(env.num_envs,device=env.device) if ids is None else torch.as_tensor(ids,device=env.device,dtype=torch.long)
    if not len(selected):return
    actual=env.scene['robot'].data.joint_pos
    assert expected.shape==actual.shape==(env.num_envs,30)
    assert torch.isfinite(expected[selected]).all() and torch.equal(actual[selected],expected[selected]),'Real full30q reset differs from independently requested CAD bank q'
    if not hasattr(env,'_rescue_reset_q'):env._rescue_reset_q=expected.clone()
    else:env._rescue_reset_q[selected]=expected[selected]
    assert torch.equal(env._rescue_reset_q[selected],expected[selected])
