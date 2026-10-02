
# Build a PhysX-friendly SERIAL surrogate of the closed-chain plant:
#   base -> rear1 (thigh, motor) -> rear2 (knee, motor) -> wheel (motor)   per side
# The closed chain (front*/spring* links + equality + tendon) is removed because PhysX
# articulations cannot carry the loop; the knee angle comes from the analytic closed chain
# (docs/viz/model.json poses), so the surrogate reproduces the same leg extension.
import copy, os, xml.etree.ElementTree as ET
ROOT = r'D:/claude2/fangzhen'
SRC = os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'rm_vehicle_cc.xml')
OUT = os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'rm_vehicle_serial.xml')
DROP = ('front', 'spring')
tree = ET.parse(SRC)
root = tree.getroot()
for tag in ('equality', 'tendon', 'contact', 'keyframe', 'sensor'):
    for el in list(root.findall(tag)):
        root.remove(el)
        print('removed <%s>' % tag)
def prune(body):
    for ch in list(body.findall('body')):
        if any(k in (ch.get('name') or '') for k in DROP):
            body.remove(ch)
            print('removed body', ch.get('name'))
        else:
            prune(ch)
wb = root.find('worldbody')
for b in list(wb.findall('body')):
    prune(b)
act = root.find('actuator')
keep = set()
def collect(el):
    for j in el.findall('joint'):
        keep.add(j.get('name'))
    for b in el.findall('body'):
        collect(b)
collect(wb)
for a in list(act):
    jn = a.get('joint')
    if jn and jn not in keep:
        act.remove(a)
        print('removed actuator', a.get('name'), '-> orphan joint', jn)
tmpl = None
for m in act.findall('motor'):
    if m.get('joint') == 'left_rear1_joint':
        tmpl = m
for side in ('left', 'right'):
    nm = side + '_rear2'
    el = copy.deepcopy(tmpl)
    el.set('name', nm + '_ctrl')
    el.set('joint', nm + '_joint')
    el.set('ctrlrange', '-40 40')
    el.set('forcerange', '-40 40')
    act.append(el)
    print('added knee actuator', el.get('name'))
# the surrogate knee is now actuated: give it the motor joint properties (armature/friction)
def find_joints(el):
    for j in el.findall('joint'):
        yield j
    for b in el.findall('body'):
        for j in find_joints(b):
            yield j
for j in find_joints(wb):
    if j.get('name', '').endswith('rear2_joint'):
        j.set('armature', '0.0158')
        j.set('damping', '0.0')
        j.set('frictionloss', '1.5')
tree.write(OUT, encoding='utf-8', xml_declaration=True)
print('wrote', OUT)
# scene with a floor for MuJoCo checking
sc = ET.Element('mujoco', {'model': 'rm_vehicle_serial scene'})
inc = ET.SubElement(sc, 'include', {'file': os.path.basename(OUT)})
wbx = ET.SubElement(sc, 'worldbody')
ET.SubElement(wbx, 'geom', {'name': 'floor', 'type': 'plane', 'size': '10 10 0.05',
                            'contype': '1', 'conaffinity': '255', 'friction': '1.6 0.01 0.001'})
kf = ET.SubElement(sc, 'keyframe')
q = ['0', '0', '0.0531', '1', '0', '0', '0']
names = [j.get('name') for j in find_joints(wb)]
vals = {'left_rear1_joint': -0.097, 'left_rear2_joint': -0.0865, 'right_rear1_joint': -0.117,
        'right_rear2_joint': -0.0784, 'left_wheel_joint': 0.0, 'right_wheel_joint': 0.0}
for n in names:
    q.append('%+.6f' % vals.get(n, 0.0))
ET.SubElement(kf, 'key', {'name': 'stand', 'qpos': ' '.join(q)})
ET.ElementTree(sc).write(os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'scene_serial.xml'), encoding='utf-8', xml_declaration=True)
print('wrote scene_serial.xml with %d qpos entries' % len(q))
