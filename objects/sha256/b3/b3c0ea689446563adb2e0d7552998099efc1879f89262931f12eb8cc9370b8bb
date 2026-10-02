import io, os, re, sys, math
import numpy as np, mujoco
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
SRC = os.path.join(ROOT, 'robot/out_cc/rm_vehicle_cc.xml')
base = io.open(SRC, encoding='utf-8').read()

def build(tag, txt):
    p = os.path.join(ROOT, 'robot/out_cc', '_t_%s.xml' % tag)
    io.open(p, 'w', encoding='utf-8').write(txt)
    return p

def load(tag, txt):
    return mujoco.MjModel.from_xml_path(build(tag, txt))

def gaps(m, d):
    out = []
    for e in range(m.neq):
        o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = np.asarray(m.eq_data[e])
        a1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
        a2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
        out.append(1000.0 * np.linalg.norm(a1 - a2))
    return np.array(out)

def run(m, steps=4000, hold=False):
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0)
    nwarn = 0; worst_qacc = 0.0; worst_gap = 0.0
    z = []; prev_err = 0
    import contextlib
    buf = io.StringIO()
    for i in range(steps):
        if hold:
            d.ctrl[:] = 0.0
        with contextlib.redirect_stderr(buf):
            mujoco.mj_step(m, d)
        if len(buf.getvalue()) > prev_err:
            prev_err = len(buf.getvalue()); nwarn += 1
        worst_qacc = max(worst_qacc, np.abs(d.qacc).max())
        worst_gap = max(worst_gap, gaps(m, d).max())
        z.append(d.qpos[2])
    return dict(warn=nwarn, qacc=worst_qacc, gap=worst_gap, z0=z[0], zend=z[-1],
                zmin=min(z), zmax=max(z), txt=buf.getvalue()[:200])

print('timestep of the source plant: %s' % re.search(r'timestep=.([0-9.]+)', base).group(1))
cases = []
cases.append(('as-is', base))
cases.append(('implicit-flag', base.replace('<option timestep=', '<option flag=' + chr(34) + 'implicitdpi=enable implicitdfi=enable' + chr(34) + ' timestep=')))
cases.append(('c=5', base.replace('damping=' + chr(34) + '150' + chr(34), 'damping=' + chr(34) + '5' + chr(34))))
cases.append(('c=20', base.replace('damping=' + chr(34) + '150' + chr(34), 'damping=' + chr(34) + '20' + chr(34))))
for tag, txt in cases:
    try:
        m = load(tag, txt)
    except Exception as ex:
        print('   %-14s COMPILE FAILED: %s' % (tag, str(ex)[:120])); continue
    r = run(m)
    print('   %-14s warn_steps=%-4d max|qacc|=%10.1f  max gap=%7.3f mm  base_z %.4f -> %.4f (min %.4f max %.4f)'
          % (tag, r['warn'], r['qacc'], r['gap'], r['z0'], r['zend'], r['zmin'], r['zmax']))
    if r['txt']: print('        first warning: %s' % r['txt'].strip().split(chr(10))[0])
