# Export the RL plant for the browser viewer as: model.json (tree + joints + equality + poses)
# and parts.bin (one interleaved pos+normal triangle soup per geom).  No MuJoCo load: the XML
# is parsed directly and the poses come from the validated analytic closed chain (leg2d), so
# this runs next to a training job without fighting for memory.
import json, os, sys, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:/claude2/fangzhen/scripts')
import numpy as np, trimesh
from fast_simplification import simplify
from leg2d import Kite2D, CAD

def _budgets():
    g = [a for a in sys.argv if a.startswith('--budget')]
    if g:
        v = g[0].split('=')[-1].split(',')
        return (float(v[0]), float(v[1]) if len(v) > 1 else float(v[0]) * 0.5)
    return (6000.0, 3000.0)
BASE_BUDGET, BODY_BUDGET = _budgets()
ROOT = r'D:/claude2/fangzhen'
XMLP = os.path.join(ROOT, 'robot/out_cc_linkfix/rm_vehicle_cc.xml')
MESHDIR = os.path.join(ROOT, 'robot/out_cc/meshes')
OUT = os.path.join(ROOT, 'docs/viz')
os.makedirs(OUT, exist_ok=True)
Q = chr(34)

def v3(s):
    return [float(x) for x in str(s).split()]

root = ET.parse(XMLP).getroot()
assets = {m.get('name'): {'file': m.get('file'), 'scale': v3(m.get('scale') or '1 1 1')}
          for m in root.find('asset').findall('mesh')}
dflt = root.find('default')
def chain(node, acc):
    out = dict(acc)
    for dd in node.findall('default'):
        cls = dd.get('class') or ''
        for j in dd.findall('joint'):
            out['j_' + cls] = dict(j.attrib)
        for g in dd.findall('geom'):
            out['g_' + cls] = dict(g.attrib)
        out = chain(dd, out)
    return out
DEF = chain(dflt, {}) if dflt is not None else {}
PARTS = []            # interleaved float32: x y z nx ny nz
ALLP = []
def add_soup(name, budget, body_i, g, kind, extra):
    a = assets[name]
    tm = trimesh.load(os.path.join(MESHDIR, a['file']), process=False, force='mesh')
    v = np.ascontiguousarray(tm.vertices, dtype=np.float64)
    f = np.ascontiguousarray(tm.faces, dtype=np.int32)
    if len(f) > budget:
        try:
            v, f = simplify(v, f, target_count=budget, agg=8.0)
            v = np.asarray(v, dtype=np.float64); f = np.asarray(f, dtype=np.int64)
            keep = np.unique(f)
            remap = np.full(len(v), -1, dtype=np.int64)
            remap[keep] = np.arange(len(keep))
            v = v[keep]; f = remap[f]
        except Exception as ex:
            print('  decimate failed', name, type(ex).__name__)
    sc = np.asarray(a['scale'], dtype=np.float64)
    # THE FIX: the STL is millimetres and the MJCF carries scale="0.001 ...".  MuJoCo
    # applies it, this exporter used to compute `sc` and then never use it, so the
    # browser got a 1000x-scaled soup (camera inside the geometry, every joint
    # rotation flinging parts hundreds of metres -> looked like detached links).
    # Apply it here and record it, so model.json's mesh_scale is always identity.
    if np.any(sc != 1.0):
        v = v * sc
    tri = v[f]                              # (ntri, 3, 3) triangle soup
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1
    n = n / ln
    pts = tri.reshape(-1, 3) * np.repeat(n, 3, axis=0) * 0 + tri.reshape(-1, 3)
    nrm = np.repeat(n, 3, axis=0)
    start = len(PARTS) // 6
    count = len(pts)
    PARTS.extend(np.concatenate([pts, nrm], axis=1).reshape(-1).astype(np.float32).tolist())
    info = {'body': body_i, 'kind': 'mesh', 'name': g.get('name') or (name),
            'pos': v3(g.get('pos') or '0 0 0'), 'quat': v3(g.get('quat') or '1 0 0 0'),
            'rgba': v3(g.get('rgba') or '0.6 0.6 0.6 1'), 'group': int(g.get('group') or 0),
            'contype': int(g.get('contype') or 0), 'conaffinity': int(g.get('conaffinity') or 0),
            'condim': int(g.get('condim') or 0), 'file': a['file'],
            'start': start, 'count': count,
            'mesh_scale': [1.0, 1.0, 1.0],          # already applied to the soup
            'baked_scale': [float(x) for x in sc]}
    info.update(extra or {})
    return info

def soup_from_trimesh(tm, body_i, g, kind_label, extra_pos=None, extra_rot=None):
    v = np.ascontiguousarray(tm.vertices, dtype=np.float64)
    f = np.ascontiguousarray(tm.faces, dtype=np.int64)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1
    n = n / ln
    pts = tri.reshape(-1, 3)
    nrm = np.repeat(n, 3, axis=0)
    start = len(PARTS) // 6
    PARTS.extend(np.concatenate([pts, nrm], axis=1).reshape(-1).astype(np.float32).tolist())
    info = {'body': body_i, 'kind': kind_label, 'name': g.get('name') or kind_label,
            'pos': [0.0, 0.0, 0.0], 'quat': [1.0, 0.0, 0.0, 0.0],
            'rgba': v3(g.get('rgba') or '0.6 0.6 0.6 1'),
            'group': int(g.get('group') or 0),
            'contype': int(g.get('contype') or 0),
            'conaffinity': int(g.get('conaffinity') or 0),
            'condim': int(g.get('condim') or 0),
            'start': start, 'count': len(pts)}
    return info

def qmul(a, b):
    return [a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
            a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
            a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
            a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]]
def qrot(q, v):
    qv = [q[1], q[2], q[3]]
    t = [qv[1]*v[2]-qv[2]*v[1]+q[0]*v[0], qv[2]*v[0]-qv[0]*v[2]+q[0]*v[1],
         qv[0]*v[1]-qv[1]*v[0]+q[0]*v[2]]
    t = [2*t[0], 2*t[1], 2*t[2]]
    return [v[0]+t[1]*qv[2]-t[2]*qv[1]+q[0]*t[0],
            v[1]+t[2]*qv[0]-t[0]*qv[2]+q[0]*t[1],
            v[2]+t[0]*qv[1]-t[1]*qv[0]+q[0]*t[2]]
def prim_info(kind, g, gd, body_i):
    import trimesh as T3
    from OCP.gp import gp_Vec
    sz = v3(g.get('size') or gd.get('size') or '0.02')
    ft = g.get('fromto') or gd.get('fromto')
    pos = v3(g.get('pos') or gd.get('pos') or '0 0 0')
    quat = v3(g.get('quat') or gd.get('quat') or '1 0 0 0')
    tm = None
    if kind == 'capsule':
        if ft:
            p = v3(ft); a1 = np.array(p[:3]); b1 = np.array(p[3:])
            tm = T3.creation.capsule(radius=sz[0], height=float(np.linalg.norm(b1 - a1)), count=(14, 14))
            mid = (a1 + b1) / 2.0
            d = b1 - a1; L = np.linalg.norm(d) or 1e-9
            import math
            ax = np.cross([0, 0, 1.0], d / L)
            ang = math.acos(max(-1.0, min(1.0, d[2] / L)))
            if np.linalg.norm(ax) < 1e-9:
                rotq = [1.0, 0, 0, 0] if ang < 1e-6 else [0, 0, 0, 1]
                if ang > 1:
                    tm.apply_transform(np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]], dtype=float))
            else:
                ax = ax / np.linalg.norm(ax)
                s2, c2 = math.sin(ang/2), math.cos(ang/2)
                rotq = [c2, ax[0]*s2, ax[1]*s2, ax[2]*s2]
            def xf2(v):
                return [v[i] + rotq[0]*rotq[1]*0 for i in range(3)]
            tm.apply_transform(q_to_mat(rotq, mid))
            return soup_from_trimesh(tm, body_i, g, 'capsule')
        tm = T3.creation.capsule(radius=sz[0], height=2*(sz[1] if len(sz) > 1 else 0.02), count=(14, 14))
    elif kind == 'cylinder':
        tm = T3.creation.cylinder(radius=sz[0], height=2*(sz[1] if len(sz) > 1 else 0.02), sections=20)
    elif kind == 'box':
        tm = T3.creation.box(extents=[2*sz[0], 2*sz[1], 2*sz[2]])
    elif kind == 'sphere':
        tm = T3.creation.icosphere(subdivisions=2, radius=sz[0])
    else:
        return None
    tm.apply_transform(q_to_mat(quat, pos))
    return soup_from_trimesh(tm, body_i, g, kind)
def q_to_mat(q, t):
    w, x, y, z = q
    n = np.sqrt(w*w+x*x+y*y+z*z) or 1.0
    w, x, y, z = w/n, x/n, y/n, z/n
    return np.array([
      [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w), t[0]],
      [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w), t[1]],
      [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y), t[2]],
      [0, 0, 0, 1]], dtype=float)

bodies, joint_order = [], []
def walk(b, parent):
    i = len(bodies)
    j = b.find('joint')
    jinfo = None
    if j is not None:
        da = {}
        for c in (j.get('class') or '').split():
            da.update(DEF.get('j_' + c, {}))
        def gv(k, d='0'):
            return j.get(k) or da.get(k) or d
        jinfo = {'name': j.get('name'), 'tname': gv('type', 'hinge'), 'pos': v3(gv('pos')),
                 'axis': v3(gv('axis', '0 0 1')), 'range': v3(gv('range')),
                 'limited': bool(j.get('range') or da.get('range')),
                 'armature': float(gv('armature')), 'damping': float(gv('damping')),
                 'frictionloss': float(gv('frictionloss')), 'stiffness': float(gv('stiffness')),
                 'springref': float(gv('springref')), 'ref': float(gv('ref'))}
        joint_order.append(jinfo['name'])
    inert = b.find('inertial')
    geoms = []
    for g in b.findall('geom'):
        gd = {}
        for c in (g.get('class') or '').split():
            gd.update(DEF.get('g_' + c, {}))
        kind = g.get('type') or gd.get('type') or 'sphere'
        base = {'name': g.get('name') or '', 'pos': v3(g.get('pos') or gd.get('pos') or '0 0 0'),
                'quat': v3(g.get('quat') or gd.get('quat') or '1 0 0 0'),
                'rgba': v3(g.get('rgba') or gd.get('rgba') or '0.6 0.6 0.6 1'),
                'group': int(g.get('group') or gd.get('group') or 0),
                'contype': int(g.get('contype') or gd.get('contype') or 0),
                'conaffinity': int(g.get('conaffinity') or gd.get('conaffinity') or 0),
                'condim': int(g.get('condim') or gd.get('condim') or 3)}
        if kind == 'mesh':
            # budget is in FACES.  Each group here is ~20 merged CAD parts capped at
            # 150k faces by build_cc.py, so 1500 faces shredded them.  Configurable:
            #   python export_viz_model.py --budget 6000,3000
            budget = BASE_BUDGET if b.get('name') == 'base_link' else BODY_BUDGET
            geoms.append(add_soup(g.get('mesh'), budget, i, g, 'mesh', {}))
        else:
            it = prim_info(kind, g, gd, i)
            if it is not None:
                geoms.append(it)
    for gg in geoms:
        ALLP.append(gg)
    bodies.append({'id': i, 'name': b.get('name'), 'parent': parent,
                   'pos': v3(b.get('pos') or '0 0 0'), 'quat': v3(b.get('quat') or '1 0 0 0'),
                   'mass': float(inert.get('mass')) if inert is not None else 0.0,
                   'com': v3(inert.get('pos')) if inert is not None else [0.0, 0.0, 0.0],
                   'joint': jinfo, 'ngeom': len(geoms)})
    for c in b.findall('body'):
        walk(c, i)
for b in root.find('worldbody').findall('body'):
    walk(b, -1)

acts = [{'name': a.get('name'), 'joint': a.get('joint'), 'forcerange': v3(a.get('forcerange') or '0 0')}
        for a in root.find('actuator').findall('motor')]
eqs = [{'body1': e.get('body1'), 'body2': e.get('body2'), 'anchor': v3(e.get('anchor') or '0 0 0')}
       for e in root.find('equality').findall('connect')]
tendons = [{'name': t.get('name'), 'range': v3(t.get('range') or '0 0'),
            'coefs': [[jj.get('joint'), float(jj.get('coef'))] for jj in t.findall('joint')]}
           for t in root.find('tendon').findall('fixed')]
BID = {b['name']: b['id'] for b in bodies}
for e in eqs:
    e['b1'] = BID[e['body1']]; e['b2'] = BID[e['body2']]

L = Kite2D(CAD, 'ours')
HINGES = ('rear1', 'front1', 'rear2', 'front2', 'front3', 'front4', 'spring1')
def pose(tL, cL, tR, cR, label, pitch=0.0):
    sL, sR = L.qpos_full(tL, cL), L.qpos_full(tR, cR)
    if sL is None or sR is None:
        return None
    q = {'__root__': [0, 0, 0.073, np.cos(np.radians(pitch) / 2), 0, np.sin(np.radians(pitch) / 2), 0]}
    for side, s in (('left', sL), ('right', sR)):
        for k in HINGES:
            q[side + '_' + k + '_joint'] = -s[k]
        q[side + '_spring2_joint'] = s['spring2'] / 1000.0
        q[side + '_wheel_joint'] = 0.0
    return {'label': label, 'q': q, 'thigh_L': tL, 'crank_L': cL,
            'knee_L': -sL['rear2'], 'delta_L': tL - cL,
            'ext_L': float(sL['pts']['ext']) / 1000.0,
            'spring_L': float(sL['pts']['spring'])}
def scan(target, hi=True):
    best = None
    for c in np.arange(-2.5, 2.51, 0.005):
        k = -L.qpos_full(0.0, c)['rear2'] if L.qpos_full(0.0, c) else None
        if k is None:
            continue
        if best is None or abs(k - target) < abs(best[1] - target):
            best = (c, k)
    return best
kmax = max((-L.qpos_full(0.0, c)['rear2']) for c in np.arange(-2.5, 2.51, 0.01) if L.qpos_full(0.0, c))
kmin = min((-L.qpos_full(0.0, c)['rear2']) for c in np.arange(-2.5, 2.51, 0.01) if L.qpos_full(0.0, c))
cmax = scan(kmax)[0]; cmin = scan(kmin)[0]
raw = [pose(0, 0, 0, 0, 'CAD 装配位 qpos=0（训练与部署的初始位）'),
       pose(0.097, 0.222, 0.117, 0.230, '站起 stance（v16/v17a 实测髋角，部署 keyframe）'),
       pose(0.30, 0.55, 0.32, 0.57, '下蹲 crouch'),
       pose(0.0, cmax, 0.0, cmax, '膝到上端 %.2f rad（平行四边形摊平前）' % kmax),
       pose(0.0, cmin, 0.0, cmin, '膝到下端 %.2f rad（筝形折叠前）' % kmin),
       pose(0.097, 1.30, 0.117, 1.32, '曲柄单独多转（膝被闭链解出）')]
poses = [p for p in raw if p]
sweep = [p for p in (pose(0.097, -1.2 + 0.3 * i, 0.097, -1.2 + 0.3 * i,
                          'sweep crank %+0.2f' % (-1.2 + 0.3 * i)) for i in range(9)) if p]
model = {'file': os.path.basename(XMLP), 'plant_dir': 'robot/out_cc_linkfix',
         'desc': 'v17a 正在训练的闭链模型（相似连杆：筝形 + 平行四边形 + 气弹簧）',
         'bodies': bodies, 'parts': ALLP, 'joint_order': joint_order, 'actuators': acts,
         'equality': eqs, 'tendons': tendons, 'poses': poses, 'sweep': sweep,
         'CAD': {k: list(map(float, CAD[k])) for k in CAD},
         'lengths': {'r_crank': L.r_c, 'thigh': L.a, 'shank': L.b, 'L2': L.L2, 'L3': L.L3,
                     'R3': L.R3, 'L4': L.L4, 'Rq': L.Rq, 'spring0': L.Lspr0,
                     'knee_max': float(kmax), 'knee_min': float(kmin)},
         'total_mass': float(sum(b['mass'] for b in bodies)),
         'part_count': len([1 for b in bodies for _ in range(b['ngeom'])])}
json.dump(model, open(os.path.join(OUT, 'model.json'), 'w', encoding='utf-8'))
open(os.path.join(OUT, 'parts.bin'), 'wb').write(np.asarray(PARTS, dtype=np.float32).tobytes())
print('bodies', len(bodies), 'joints', len(joint_order), 'soup floats', len(PARTS),
      'tris', len(PARTS) // 18)
print('model.json', os.path.getsize(os.path.join(OUT, 'model.json')),
      'parts.bin', os.path.getsize(os.path.join(OUT, 'parts.bin')))
for p in poses:
    print('   %-46s knee %+0.3f ext %.3f m delta %+0.2f' % (p['label'][:46], p['knee_L'], p['ext_L'], p['delta_L']))
