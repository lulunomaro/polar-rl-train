# Gate the action-slot order across the whole pipeline (plant model -> training config ->
# exported ONNX -> deployment YAML -> CPU harness).  This is the check that was missing when
# the two hip motors were silently swapped in every deployment (docs/HOWTO.md sec.38).
import sys, os, json, glob, argparse
from pathlib import Path
import numpy as np, mujoco, onnx, yaml
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, os.path.join(ROOT, 'train', 'rmvehicle', 'src'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from rmvehicle import action_order as AO
from rmvehicle.names import CC, RM2025_LATER
FAIL = []
def ok(cond, msg):
    print(('   OK   ' if cond else '   FAIL ') + msg)
    if not cond: FAIL.append(msg)

ap = argparse.ArgumentParser()
ap.add_argument('--model', choices=('cc', 'later'), default='cc')
ap.add_argument('--contract', default=os.path.join(ROOT, 'train/deploy/contract.json'))
ap.add_argument('--plant', default='')
ARGS = ap.parse_args()
NAMES = RM2025_LATER if ARGS.model == 'later' else CC
PLANT = ARGS.plant or (os.path.join(ROOT, 'incoming/rm2025_mod4/robot_hifi.xml')
                       if ARGS.model == 'later'
                       else os.path.join(ROOT, 'robot/out_cc/rm_vehicle_cc.xml'))
m = mujoco.MjModel.from_xml_path(PLANT)
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
perm, contract = AO.permutation(names, NAMES.leg_joints, NAMES.wheel_joints)
# mjlab resolves one action term per group and concatenates them, so the raw order is the
# legs in model order followed by the wheels in model order - NOT the two interleaved.
natural = ([n for n in names if n in set(contract[:4])]
           + [n for n in names if n in set(contract[4:])])
print('1. plant model joint order  :', [n for n in names if n != 'floating_base'][:6], '...')
print('   raw mjlab action order   :', natural)
print('   contract (obs) order     :', contract)
print('   export permutation       :', perm)

C = json.load(open(ARGS.contract, encoding='utf-8'))
ok(C.get('plant_kind') == 'similar_linkage_closed_chain',
   'deployment contract is explicitly closed-chain')
ok(C.get('model_key') == NAMES.key,
   'deployment contract model_key == %r (got %r)' % (NAMES.key, C.get('model_key')))
ok(C.get('policy_coordinate_space') == 'actuator_output_joint',
   'policy speaks actuator output-joint coordinates')
ok(C.get('policy_controls_passive_knee') is False,
   'passive knee is absent from the policy action contract')
ok(not any('knee' in n for n in C.get('action_slot_order_exported', [])),
   'no passive knee name appears in exported action slots')
roles = C.get('leg_drive_roles', {})
if ARGS.model == 'later':
    ok(roles.get('left_crank') == 'left_crank_drive' and
       roles.get('left_hip') == 'left_thigh_drive',
       'crank/hip are documented as crank/thigh drives')
else:
    ok(roles.get('left_front1_joint') == 'left_crank_drive' and
       roles.get('left_rear1_joint') == 'left_thigh_drive',
       'front1/rear1 are documented as crank/thigh drives')
if 'action_slot_order_raw' in C:
    ok(C['action_slot_order_raw'] == natural, 'contract.action_slot_order_raw matches the model')
    ok(C['action_slot_order_exported'] == contract, 'contract.action_slot_order_exported matches the patterns')
    ok(list(C['export_action_permutation']) == perm, 'contract.export_action_permutation matches')
else:
    ok(False, 'contract.json carries the action order at all (regenerate with write_deploy_contract.py)')

for o in sorted(glob.glob(os.path.join(ROOT, 'train/deploy/*.onnx'))):
    md = {e.key: e.value for e in onnx.load(o).metadata_props}
    if 'action_width' not in md and 'joint_action_scale' not in md:
        continue
    ao = [x.strip() for x in (md.get('action_order') or '').split(',') if x.strip()]
    tag = os.path.basename(o)
    if not ao:
        print('   WARN %s has no action_order metadata (exported before the fix)' % tag); continue
    ok(ao == contract, '%s action_order == contract order' % tag)
    perm_md = [int(x) for x in (md.get('action_order_permutation') or '').split(',') if x != '']
    ok(perm_md == perm, '%s records the permutation %s' % (tag, perm))

YAMLS = glob.glob(os.path.join(ROOT, 'sim2sim_cc/*/config/*.yaml')) + \
        glob.glob(os.path.join(ROOT, 'sim2sim/*/config/*.yaml'))
for y in sorted(YAMLS):
    try:
        doc = yaml.safe_load(open(y, encoding='utf-8'))
    except Exception as ex:
        print('   WARN cannot parse %s (%s)' % (y, ex)); continue
    prm = doc.get('/**', {}).get('template_ros2_controller', {}).get('ros__parameters', {})
    joints = list(prm.get('joints') or [])
    if not joints: continue
    scale = list(prm.get('joint_action_scale') or [])
    ok(joints[:4] == contract[:4] and joints[4:6] == contract[4:6],
       '%s joints list is in the contract action order %s' % (os.path.basename(y), joints[:6]))
    if scale:
        ok(len(scale) >= 6, '%s joint_action_scale covers 6 slots' % os.path.basename(y))
print()
print('RESULT:', 'ALL CHECKS PASS' if not FAIL else '%d CHECK(S) FAILED' % len(FAIL))
for f in FAIL: print('   - ' + f)
sys.exit(1 if FAIL else 0)
