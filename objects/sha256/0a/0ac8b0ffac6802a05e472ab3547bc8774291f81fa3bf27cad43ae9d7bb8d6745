# Rewrite an exported policy so that its ACTION vector is in the deployment contract order.
#
# WHY THIS EXISTS (2026-09-06).  Inside mjlab the observation and the action of the same
# joint do NOT share a slot order: the observation term uses SceneEntityCfg(preserve_order=
# True) -> the order listed in rmvehicle.names (front1_L, rear1_L, front1_R, rear1_R), while
# an action term uses BaseActionCfg.preserve_order = False (envs/mdp/actions/actions.py:35)
# -> the joints come back in MODEL DEFINITION order (rear1_L, front1_L, rear1_R, front1_R).
# wheelbipe_ros2_sim2sim's controller has ONE joints list and uses it for both (state_rl.cpp
# builds obs[10:14] from robot_state.joints and applies desired_pos_[i] to the same list), so
# every deployment - this harness included until today - fed action[0] to front1 while the
# policy meant rear1.  The two hip motors were swapped, which is why v14/v15/v16 looked
# perfect in mjlab and toppled instantly in native MuJoCo / ROS2 / sim2real.
#
# The permutation is applied to the LAST linear layer only (rows of W and entries of b), so
# it is exact and lossless: the network, the observation normalizer and the obs order are
# untouched.  After this, action[i] <-> joints[i] in the contract order everywhere.
import sys, os, argparse
import numpy as np, onnx
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ap = argparse.ArgumentParser()
ap.add_argument('--onnx', required=True)
ap.add_argument('--perm', required=True, help='comma list: new slot i takes old slot perm[i]')
ap.add_argument('--order', help='human label of the resulting action order (goes into metadata)')
ap.add_argument('--out', default=None)
a = ap.parse_args()

perm = [int(x) for x in a.perm.split(',') if x.strip() != '']
model = onnx.load(a.onnx)
g = model.graph
final = [n for n in g.node if 'actions' in list(n.output)]
assert len(final) == 1, 'cannot find the node that writes the action vector'
node = final[0]
inits = {i.name: i for i in g.initializer}
changed = []
for name in node.input:
    if name not in inits:
        continue
    arr = onnx.numpy_helper.to_array(inits[name])
    if arr.ndim == 2 and arr.shape[0] == len(perm):
        arr = arr[perm, :]; changed.append((name, 'rows'))
    elif arr.ndim == 1 and arr.shape[0] == len(perm):
        arr = arr[perm]; changed.append((name, 'entries'))
    else:
        continue
    new = onnx.numpy_helper.from_array(arr, name=name)
    for k in range(len(g.initializer)):
        if g.initializer[k].name == name:
            g.initializer[k].CopyFrom(new)
assert changed, 'no final-layer initializer matched the action width %d' % len(perm)
print('permuted', changed, 'with perm', perm)

meta = {e.key: e for e in model.metadata_props}
def put(key, value):
    if key in meta: meta[key].value = value
    else:
        e = onnx.StringStringEntryProto(); e.key = key; e.value = value
        model.metadata_props.append(e); meta[key] = e
put('action_order', a.order or ('permuted by ' + ','.join(map(str, perm))))
put('action_order_source', 'scripts/onnx_action_order.py')
out = a.out or a.onnx
onnx.save(model, out)
print('wrote', out)
