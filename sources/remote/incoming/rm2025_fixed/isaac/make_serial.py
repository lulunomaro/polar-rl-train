
# PhysX cannot carry this chassis' closed loops (the delivered acceptance run proves it:
# left_proximal_closure separated by 0.283 m even with 32 solver iterations), so for Isaac
# training we build the serial surrogate of the SAME model:
#   chassis -> thigh(hip motor) -> shin(knee motor) -> wheel(wheel motor)   per side
# Everything geometrically load-bearing stays: chassis/thigh/shin/wheel bodies, their masses,
# inertias, visual meshes and collision primitives.  Dropped: crank, rocker, distal, coupler,
# gas-spring branch, the two chain-drive input proxies, the 6 <connect> closures and the
# (crank-hip) tendon.  The crank motor becomes the knee motor, so the action vector stays
# 6-wide (hip, knee, wheel per side) and the effort limits are unchanged.
import copy, io, os, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'scene_training.xml')
OUT = os.path.abspath(os.path.join(HERE, '..', 'robot_serial.xml'))
SCENE = os.path.abspath(os.path.join(HERE, '..', 'scene_serial.xml'))
DROP_FROM_CHASSIS = ('input', 'drive_hip', 'drive_input')
DROP_FROM_THIGH = ('rocker', 'gas_inner')
tree = ET.parse(SRC)
root = tree.getroot()
for tag in ('equality', 'tendon', 'sensor', 'contact', 'keyframe'):
    for el in list(root.findall(tag)):
        root.remove(el)
        print('dropped <%s>' % tag)
wb = root.find('worldbody')
chassis = wb.find('body')
# The USD is a robot asset, not a complete scene.  Remove the source scene's top-level
# floor/lights/cameras; Isaac Lab supplies one terrain per training scene.  Keeping the MJCF
# floor here used to clone a translated collision plane with every robot.
for tag in ('geom', 'light', 'camera'):
    for el in list(wb.findall(tag)):
        wb.remove(el)
        print('dropped worldbody <%s> %s' % (tag, el.get('name', '')))
removed = []
def drop(parent, names):
    for ch in list(parent.findall('body')):
        nm = ch.get('name') or ''
        if any(nm.endswith(s) for s in names):
            parent.remove(ch)
            removed.append(nm)
        else:
            drop(ch, ())
drop(chassis, DROP_FROM_CHASSIS)
for b in list(chassis.findall('body')):
    drop(b, DROP_FROM_THIGH)
print('dropped bodies:', removed)
act = root.find('actuator')
hip = None
for a in list(act):
    jn = a.get('joint') or ''
    if jn.endswith('_crank'):
        act.remove(a)
        removed.append('actuator ' + a.get('name'))
    if jn.endswith('_hip'):
        hip = a
for side in ('left', 'right'):
    m = copy.deepcopy(hip)
    m.set('name', side + '_knee_motor')
    m.set('joint', side + '_knee')
    act.append(m)
# the knee is now an actuated joint: give it the same motor-side joint properties as the hip
def joints(el, out):
    for j in el.findall('joint'):
        out.append(j)
    for b in el.findall('body'):
        joints(b, out)
J = []
joints(wb, J)
byname = {j.get('name'): j for j in J}
for side in ('left', 'right'):
    h = byname[side + '_hip']
    k = byname[side + '_knee']
    for attr in ('armature', 'damping', 'frictionloss'):
        if h.get(attr) is not None:
            k.set(attr, h.get(attr))
tree.write(OUT, encoding='utf-8', xml_declaration=True)
print('wrote', OUT)
print('remaining joints:', sorted(byname.keys()))
# a scene with a floor + the neutral keyframe, for MuJoCo-side sanity checks
names = [j.get('name') for j in J]
q = ['0', '0', '0.298937', '1', '0', '0', '0'] + ['0'] * len(names)
sc = ('<mujoco model="rm2025 serial surrogate on flat floor">\n'
      '  <include file="robot_serial.xml"/>\n'
      '  <visual><global offwidth="1280" offheight="768"/>\n'
      '    <headlight ambient="0.42 0.42 0.44" diffuse="0.55 0.55 0.55"/></visual>\n'
      '  <asset><texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" rgb2="0.25 0.28 0.33" width="256" height="256"/></asset>\n'
      '  <worldbody>\n'
      '    <geom name="floor" type="plane" size="20 20 0.05" contype="1" conaffinity="255" friction="1.6 0.01 0.001"/>\n'
      '    <light pos="3 -3 5" dir="-0.2 0.2 -1" diffuse="0.9 0.9 0.9"/>\n'
      '  </worldbody>\n'
      '  <keyframe><key name="neutral" qpos="' + ' '.join(q) + '" ctrl="' + ' '.join(['0'] * 6) + '"/></keyframe>\n'
      '</mujoco>\n')
io.open(SCENE, 'w', encoding='utf-8', newline=chr(10)).write(sc)
print('wrote', SCENE, 'qpos width', len(q))
