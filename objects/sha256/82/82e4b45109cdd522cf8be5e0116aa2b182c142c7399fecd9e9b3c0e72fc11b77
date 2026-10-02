# Render the RL plant (the exact MJCF/triangles the browser viewer uses) to PNG, offline.
# Same FK + same camera math as docs/viz/model_viewer.html, so a pixel here is a pixel there.
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = r'D:/claude2/fangzhen'
VIZ = os.path.join(ROOT, 'docs', 'viz')
M = json.load(open(os.path.join(VIZ, 'model.json'), encoding='utf-8'))
SOUP = np.fromfile(os.path.join(VIZ, 'parts.bin'), dtype='<f4').reshape(-1, 6)

def T(x, y, z):
    o = np.eye(4); o[0, 3] = x; o[1, 3] = y; o[2, 3] = z; return o

def RQ(w, x, y, z):
    n = math.sqrt(w*w + x*x + y*y + z*z) or 1.0
    w, x, y, z = w/n, x/n, y/n, z/n
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z-y*w), 0.0],
                     [2*(x*y-z*w), 1-2*(x*x+z*z), 2*(y*z+x*w), 0.0],
                     [2*(x*z+y*w), 2*(y*z-x*w), 1-2*(x*x+y*y), 0.0],
                     [0.0, 0.0, 0.0, 1.0]])

def axrot(axis, a):
    ax = np.asarray(axis, float); L = np.linalg.norm(ax) or 1.0; ax = ax/L
    s = math.sin(a/2.0)
    return RQ(math.cos(a/2.0), ax[0]*s, ax[1]*s, ax[2]*s)

def bodyframe(b, q):
    Mm = T(*[float(v) for v in b['pos']])
    if b.get('quat'):
        Mm = Mm @ RQ(*[float(v) for v in b['quat']])
    j = b.get('joint')
    if not j:
        return Mm
    val = float(q.get(j['name'], 0.0)); jp = [float(v) for v in j['pos']]
    if j['tname'] == 'hinge':
        return Mm @ T(*jp) @ axrot(j['axis'], val) @ T(-jp[0], -jp[1], -jp[2])
    if j['tname'] == 'slide':
        ax = np.asarray(j['axis'], float); L = np.linalg.norm(ax) or 1.0
        return Mm @ T(*(ax/L*val))
    return Mm

def fk(q):
    W = []
    for b in M['bodies']:
        if b['parent'] < 0:
            r = [float(v) for v in (q.get('__root__') or [0, 0, 0.073, 1, 0, 0, 0])]
            W.append(T(r[0], r[1], r[2]) @ RQ(r[3], r[4], r[5], r[6]))
        else:
            W.append(W[b['parent']] @ bodyframe(b, q))
    return W

def cam_mats(az, el, dist, target, Wpx, Hpx, fov=0.62, near=0.02, far=30.0):
    a = math.radians(az); e = math.radians(el); t = np.asarray(target, float)
    eye = t + dist*np.array([math.cos(e)*math.cos(a), math.cos(e)*math.sin(a), math.sin(e)])
    z = eye - t; z /= np.linalg.norm(z)
    up = np.array([0.0, 0.0, 1.0])
    x = np.cross(up, z); x /= (np.linalg.norm(x) or 1e-9)
    y = np.cross(z, x)
    Vm = np.eye(4); Vm[0, :3] = x; Vm[1, :3] = y; Vm[2, :3] = z
    Vm[0, 3] = -x @ eye; Vm[1, 3] = -y @ eye; Vm[2, 3] = -z @ eye
    tt = 1.0/math.tan(fov/2.0); asp = Wpx/float(Hpx)
    Pm = np.zeros((4, 4)); Pm[0, 0] = tt/asp; Pm[1, 1] = tt; Pm[2, 2] = -2*near*far/(far-near); Pm[3, 2] = -1.0
    return eye, Vm, Pm

L1 = np.array([0.4, 0.3, 0.9]); L1 = L1/np.linalg.norm(L1)
L2 = np.array([-0.5, 0.2, 0.35]); L2 = L2/np.linalg.norm(L2)
NTOT = int(SOUP.shape[0])

def part_filter(visual):
    out = []
    for i, p in enumerate(M['parts']):
        if (p['kind'] == 'mesh') == visual:
            out.append((i, p))
    return out

def scene(q, visual, mats):
    """build world-space triangle soup for either the CAD meshes or the RL collision primitives"""
    sel = [pr for pr in part_filter(visual)
           if ONLY is None or M['bodies'][pr[1]['body']]['name'] in ONLY]
    vi = []; ti = []
    for i, p in sel:
        a = p['start']; n = p['count'] - (p['count'] % 3)
        vi.append(np.arange(a, a + n))
        ti.append(np.full(n // 3, i, np.int32))
    vv = np.concatenate(vi); tt = np.concatenate(ti)
    W = fk(q)
    rot = np.zeros((len(sel) + 1, 3, 3), np.float32); trn = np.zeros((len(sel) + 1, 3), np.float32)
    col = np.zeros((len(sel) + 1, 3), np.float32); slot = {}
    for slot_i, (i, p) in enumerate(sel):
        slot[i] = slot_i + 1
        Mm = W[p['body']]
        col[slot_i + 1] = np.asarray(p['rgba'][:3], np.float32)
        rot[slot_i + 1] = Mm[:3, :3].astype(np.float32); trn[slot_i + 1] = Mm[:3, 3].astype(np.float32)
    mi = np.array([slot[t] for t in tt], np.int32)          # per-triangle part slot
    v0 = SOUP[vv[0::3], :3]; v1 = SOUP[vv[1::3], :3]; v2 = SOUP[vv[2::3], :3]
    def xf3(a):
        return np.einsum('kij,kj->ki', rot[mi], a.astype(np.float32)) + trn[mi]
    p0 = xf3(v0); p1 = xf3(v1); p2 = xf3(v2)
    n = np.cross(p1 - p0, p2 - p0)
    area = 0.5*np.linalg.norm(n, axis=1)
    ln = np.maximum(area*2.0, 1e-12)
    return dict(p0=p0, p1=p1, p2=p2, n=n/ln[:, None], area=area, mi=mi, col=col)

def sample_sc(sc, eye, budget):
    ar = sc['area']
    npart = sc['col'].shape[0] - 1
    pa = np.bincount(sc['mi'], weights=ar, minlength=npart + 1)[1:]
    floor = pa.sum() / (3.0 * max(npart, 1))
    boost = np.maximum(pa, floor) / np.maximum(pa, 1e-12)
    wt = ar * boost[np.clip(sc['mi'] - 1, 0, npart - 1)]
    n = int(budget)
    cum = np.cumsum(wt); cum = cum/cum[-1]
    idx = np.searchsorted(cum, np.random.rand(n)).clip(0, len(sc['area'])-1)
    r1 = np.random.rand(n); r2 = np.random.rand(n)
    flip = r1 + r2 > 1.0; r1[flip] = 1 - r2[flip]; r2[flip] = 1 - r1[flip]
    p0 = sc['p0'][idx]; p1 = sc['p1'][idx]; p2 = sc['p2'][idx]
    P = p0 + r1[:, None]*(p1-p0) + r2[:, None]*(p2-p0)
    N = sc['n'][idx]
    face = np.einsum('ij,ij->i', N, eye[None, :] - P) > 0
    d = np.maximum(N@L1, 0)*0.95 + np.maximum(N@L2, 0)*0.30 + 0.42
    C = np.clip(sc['col'][sc['mi'][idx]]*d[:, None], 0, 1)
    return P[face], C[face]

def grid_splats(eye, nseg=41, nper=260):
    pts = []
    for i in range(nseg):
        u = -1.0 + i*(2.0/(nseg-1))
        s = np.linspace(-0.95, 0.95, nper).astype(np.float32)
        a = np.zeros((nper, 3), np.float32); a[:, 0] = u; a[:, 2] = 0.0; a[:, 1] = s; pts.append(a)
        b = np.zeros((nper, 3), np.float32); b[:, 1] = u; b[:, 2] = 0.0; b[:, 0] = s; pts.append(b)
    G = np.concatenate(pts)
    d = eye[None, :] - G; dl = np.maximum(np.linalg.norm(d, axis=1), 1e-6)
    C = np.full((len(G), 3), 0.115, np.float32) + (0.06*(d/dl[:, None])**2).astype(np.float32)
    return G, np.clip(C, 0, 1)
def splat(img, P, C, eye, Vm, Pm, Wpx, Hpx):
    ones = np.ones((len(P), 1), np.float32)
    vv = np.hstack([P, ones]) @ Vm.T.astype(np.float32)
    cl = vv @ Pm.T.astype(np.float32)
    w = cl[:, 3]
    xi = ((cl[:, 0]/np.where(w > 0, w, 1))*0.5 + 0.5)*Wpx
    yi = (1 - ((cl[:, 1]/np.where(w > 0, w, 1))*0.5 + 0.5))*Hpx
    xi = xi.astype(np.int32); yi = yi.astype(np.int32)
    keep = (w > 1e-4) & (xi >= 0) & (xi < Wpx) & (yi >= 0) & (yi < Hpx)
    zi = vv[:, 2][keep]; xi = xi[keep]; yi = yi[keep]; cc = (C[keep]*255).astype(np.uint8)
    offs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    xs = np.empty(len(xi)*len(offs), np.int32); ys = np.empty_like(xs); zs = np.empty(len(xi)*len(offs), np.float32)
    cs = np.repeat(cc, len(offs), axis=0)
    for k, (dx, dy) in enumerate(offs):
        sl = slice(k, None, len(offs))
        xs[sl] = xi + dx; ys[sl] = yi + dy; zs[sl] = zi
    okx = (xs >= 0) & (xs < Wpx); oky = (ys >= 0) & (ys < Hpx); ok = okx & oky
    o = np.argsort(zs[ok])
    flat = ((ys[ok] + 0)*Wpx + xs[ok])[o]
    flat = flat[flat < Wpx*Hpx]
    col = cs[ok][o]
    img.reshape(-1, 3)[flat] = col
    mask = np.zeros(Wpx*Hpx, bool); mask[flat] = True
    return mask.reshape(Hpx, Wpx)

def bg(Wpx, Hpx):
    g = np.linspace(0.055, 0.13, Hpx, dtype=np.float32)[:, None]
    img = np.zeros((Hpx, Wpx, 3), np.float32)
    img[:, :, 0] = (g*0.7)[:, :, None][:, :, 0]*0 + 0.045 + g*0.2
    img[:, :, 1] = 0.06 + g*0.28
    img[:, :, 2] = 0.09 + g*0.42
    return (np.clip(img, 0, 1)*255).astype(np.uint8)

P0 = M['poses'][0]; P1 = M['poses'][1]
SC = {False: {}, True: {}}
def sc_for(visual, pose):
    key = (visual, pose['label'][:2], str(sorted(ONLY)) if ONLY else '')
    if key not in SC[visual]:
        SC[visual][key] = scene(pose['q'], visual, None)
    return SC[visual][key]

MAIN = (-32, 15, 1.15, (-0.03, -0.02, 0.19))
SIDE = (-90, 8, 1.15, (-0.05, -0.10, 0.19))
LEGC = (-90, 9, 0.66, (-0.085, -0.235, 0.185))
ONLY = None
LEGSET = set(['base_link', 'left_rear1', 'left_rear2', 'left_wheel', 'left_spring1',
             'left_spring2', 'left_front1', 'left_front2', 'left_front3', 'left_front4'])

def panel(pose, visual=True, cam=MAIN, Wpx=740, Hpx=560, extra=None, budget=3500000):
    eye, Vm, Pm = cam_mats(*cam, Wpx, Hpx)
    img = bg(Wpx, Hpx)
    gpos, gcol = grid_splats(eye)
    splat(img, gpos, gcol, eye, Vm, Pm, Wpx, Hpx)
    s = sc_for(visual, pose)
    P, C = sample_sc(s, eye, budget)
    mask = splat(img, P, C, eye, Vm, Pm, Wpx, Hpx)
    if extra is not None:
        s2 = sc_for(visual, extra)
        P2, C2 = sample_sc(s2, eye, budget)
        P2 = P2 + np.array([0.0, 0.0, 0.004], np.float32)
        m2 = splat(bg(Wpx, Hpx).copy(), P2, C2*0.0 + C2, eye, Vm, Pm, Wpx, Hpx)
        im2 = bg(Wpx, Hpx)
        splat(im2, P2, np.clip(C2*0.75 + np.array([0.45, 0.05, 0.55], np.float32), 0, 1), eye, Vm, Pm, Wpx, Hpx)
        use = m2 & ~mask
        img[use] = im2[use]
        mask = mask | use
    return Image.fromarray(img), mask
def font(sz):
    for fp in (r'C:/Windows/Fonts/msyh.ttc', r'C:/Windows/Fonts/msyhbd.ttc', r'C:/Windows/Fonts/simhei.ttf'):
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, sz)
            except Exception:
                pass
    return ImageFont.load_default()

CAP = [('1. 正常位 qpos=0（CAD 装配零位＝训练/部署初始位）',
        '两个髋电机都装在机架上：rear1 转大腿、front1 转曲柄；膝 rear2 与所有连杆是被动铰链'),
       ('2. 站起 stance（v16/v17a 策略实际保持的髋角）',
        '大腿 +0.097 rad / 曲柄 +0.222 rad → 膝被动解出 -0.086 rad；筝形+平行四边形仍精确闭合'),
       ('3. 两态叠加：实心=站起，紫色=只有正常位才占的空间',
        '站起来 = 腿收短 17.5 mm（ext 0.2120 → 0.1945 m），紫色区域应当只在腿/轮附近，不能整辆错位'),
       ('4. RL 真正用的碰撞体（站起位，侧视）',
        '车架=1 个 box，大腿/小腿/连杆=capsule，轮=cylinder；零件之间 contype=0 只与世界碰，不自碰'),
       ('5. 左腿特写：正常位 qpos=0',
        '白=大腿/小腿 蓝=筝形连杆 橙=平行四边形 红=气弹簧；两个髋电机同轴挂在机架上'),
       ('6. 左腿特写：站起 stance',
        '与 5 比较：大腿 +0.097 / 曲柄 +0.222 → 膝被动 -0.086，腿收短 17.5 mm，闭环残差 0.00002 mm')]

def legshot(pose):
    global ONLY
    ONLY = LEGSET
    im = panel(pose, cam=LEGC, budget=2400000)[0]
    ONLY = None
    return im

if __name__ == '__main__':
    np.random.seed(7)
    Wp, Hp = 740, 560
    panels = [panel(P0)[0], panel(P1)[0],
          panel(P1, cam=SIDE, extra=P0)[0], panel(P1, cam=SIDE, visual=False)[0],
          legshot(P0), legshot(P1)]
    cols, rows = 2, 3
    gap = 10; head = 74; cap = 46
    FW = cols*Wp + (cols+1)*gap; FH = head + rows*(Hp+cap) + (rows+1)*gap
    sheet = Image.new('RGB', (FW, FH), (8, 12, 18))
    d = ImageDraw.Draw(sheet)
    f1 = font(26); f2 = font(18); f3 = font(16)
    d.text((gap, 12), '轮腿机器人 RL 模型体检：link / joint / 正常位 与 站起位（数据源 = 训练用的同一份 MJCF）', fill=(210, 232, 255), font=f1)
    d.text((gap, 44), 'plant %s/%s ｜ 刚体 %d 个 ｜ 关节 %d 个 ｜ 闭环 connect %d 条 ｜ tendon 限位 %d 条 ｜ 驱动 6 个（4×±40 N·m 髋 + 2×±5.5 N·m 轮） ｜ 总质量 %.2f kg'
           % (M['plant_dir'], M['file'], len(M['bodies']), len(M['joint_order']), len(M['equality']),
              len(M['tendons']), M['total_mass']), fill=(140, 165, 195), font=f2)
    for i, im in enumerate(panels):
        r = i//cols; c = i % cols
        x = gap + c*(Wp+gap); y = head + gap + r*(Hp+cap+gap)
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x+Wp-1, y+Hp-1], outline=(45, 65, 92))
        d.text((x+4, y+Hp+4), CAP[i][0], fill=(150, 215, 255), font=f3)
        d.text((x+4, y+Hp+24), CAP[i][1], fill=(120, 140, 165), font=f3)
    out = os.path.join(VIZ, 'states_check.png')
    sheet.save(out)
    print('wrote', out, sheet.size)
    for i, im in enumerate(panels):
        im.save(os.path.join(VIZ, 'state_panel%d.png' % (i+1)))
    print('triangles rendered', sum(p['count']//3 for p in M['parts']))
