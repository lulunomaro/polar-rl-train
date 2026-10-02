# The action-slot order of an exported policy, and how to make it agree with the contract.
#
# mjlab resolves an ACTION term with BaseActionCfg.preserve_order = False, i.e. the matched
# joints come back in MODEL DEFINITION order, while an OBSERVATION term is configured with
# SceneEntityCfg(preserve_order=True), i.e. the order listed in rmvehicle.names.  For the
# closed-chain plant the MJCF defines left_rear1 before left_front1, so the raw 6-D policy
# action is [rear1_L, front1_L, rear1_R, front1_R, wheel_L, wheel_R] while obs[10:14] is
# [front1_L, rear1_L, front1_R, rear1_R].
#
# wheelbipe_ros2_sim2sim (and this project MJCF exporter) have ONE joints list and use it for
# both the observation and the command, so the exported ONNX is permuted at export time to
# speak the contract order.  The permutation touches only the last linear layer.
import re
import numpy as np


def resolve(patterns, universe):
    out = []
    for pat in patterns:
        for n in universe:
            if re.match(pat, n) and n not in out:
                out.append(n)
    return out


def permutation(model_joint_names, leg_patterns, wheel_patterns):
# perm[i] = the raw action slot that has to move into contract slot i.
#
# mjlab keeps one action TERM per group (leg_joint_pos, wheel_joint_vel) and concatenates
# them in cfg order, so each group is resolved on its own against the model joint order.
# Resolving legs and wheels together would interleave them (the MJCF defines left_wheel
# between left_rear1 and left_front1) and give a wrong permutation.
    legs_contract = resolve(leg_patterns, model_joint_names)
    wheels_contract = resolve(wheel_patterns, model_joint_names)
    contract = list(legs_contract) + list(wheels_contract)
    legs_natural = [n for n in model_joint_names if n in set(legs_contract)]
    wheels_natural = [n for n in model_joint_names if n in set(wheels_contract)]
    natural = legs_natural + wheels_natural
    assert sorted(natural) == sorted(contract), (natural, contract)
    return [natural.index(j) for j in contract], contract

def permute_onnx(model, perm):
    "Reorder the output rows of the node that writes the action vector. In-place."
    g = model.graph
    final = [n for n in g.node if 'actions' in list(n.output)]
    if len(final) != 1:
        raise RuntimeError('cannot find the node that writes the action vector')
    node = final[0]
    import onnx
    inits = {i.name: i for i in g.initializer}
    changed = []
    for name in node.input:
        if name not in inits:
            continue
        arr = onnx.numpy_helper.to_array(inits[name])
        if arr.ndim == 2 and arr.shape[0] == len(perm):
            arr = arr[perm, :]; changed.append(name)
        elif arr.ndim == 1 and arr.shape[0] == len(perm):
            arr = arr[perm]; changed.append(name)
    if not changed:
        raise RuntimeError('no final-layer initializer matched action width %d' % len(perm))
    for name in changed:
        arr = onnx.numpy_helper.to_array(inits[name])
        new = onnx.numpy_helper.from_array(arr[perm, ...] if arr.ndim == 2 else arr[perm], name=name)
        for k in range(len(g.initializer)):
            if g.initializer[k].name == name:
                g.initializer[k].CopyFrom(new)
    return changed
