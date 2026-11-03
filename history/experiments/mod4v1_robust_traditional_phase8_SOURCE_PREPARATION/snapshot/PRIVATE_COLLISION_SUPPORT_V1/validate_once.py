"""New preregistered geometry-only validation, not an old QA/episode replay."""
from pathlib import Path
import hashlib
import itertools
import json
import math
from types import SimpleNamespace
import sys
import traceback
import numpy as np
from scipy.spatial.transform import Rotation

D = Path(__file__).resolve().parent
ROOT = D.parent
sys.path[:0] = [str(D), str(ROOT / 'MODEL_AUDIT' / 'mesh_support_helper_v1')]
SOURCES = [D/'PLAN.json', D/'support.py', Path(__file__),
           ROOT/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',
           ROOT/'MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py',
           ROOT/'MANUAL_FIRST_BAR_V1/grade_rows.py']
COUNT = 0
PHASE = 'preexec'
COUNTERS = dict(model_compiles=0, explicit_mj_forward=0, integrator_entries=0)
MAX_ERROR = 0.


def record(p):
    return dict(path=str(p), bytes=p.stat().st_size,
                SHA=hashlib.sha256(p.read_bytes()).hexdigest())


def save(p, obj):
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, allow_nan=False)


def ck(ok, label):
    global COUNT
    COUNT += 1
    if not bool(ok):
        raise AssertionError(str(COUNT) + ': ' + label)


def close(a, b, label):
    global MAX_ERROR
    err = float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    MAX_ERROR = max(MAX_ERROR, err)
    ck(math.isfinite(err) and err <= 2e-12, label + ' error=' + repr(err))


def fails(fn, label):
    try:
        fn()
    except (ValueError, TypeError):
        ck(True, label)
    else:
        ck(False, label)


def support_point_oracle(typ, size, R, p, vertices):
    """Independent supporting POINT/corner/end-sphere constructions."""
    if typ in (6, 7):
        points = (np.asarray(list(itertools.product(*[(-v, v) for v in size])))
                  if typ == 6 else vertices)
        w = points @ R.T + p
        return w.min(axis=0), w.max(axis=0)
    if typ == 3:
        endpoints = np.asarray([[0., 0., -size[1]], [0., 0., size[1]]]) @ R.T + p
        return endpoints.min(axis=0)-size[0], endpoints.max(axis=0)+size[0]
    lo, hi = [], []
    for axis in range(3):
        answers = []
        for sign in (-1., 1.):
            u = sign * R[axis, :]
            if typ == 2:
                local = size[0] * u
            elif typ == 4:
                local = size**2 * u / np.linalg.norm(size*u)
            else:
                local = np.zeros(3)
                planar = np.linalg.norm(u[:2])
                if planar:
                    local[:2] = size[0]*u[:2]/planar
                local[2] = size[1] * (1. if u[2] >= 0 else -1.)
            answers.append(float((R@local+p)[axis]))
        lo.append(answers[0]); hi.append(answers[1])
    return np.asarray(lo), np.asarray(hi)


def main():
    global PHASE
    out = D/'validation001'
    out.mkdir(exist_ok=False)
    source_before = [record(p) for p in SOURCES]
    save(out/'SOURCE_PREEXEC.json', dict(sources=source_before, plan='PLAN.json'))
    from support import shape_bounds, CompiledCollisionSupport
    PHASE = 'new_synthetic'
    angles = [(0., 0., 0.), (.3, -.4, .2), (-1.1, .6, -.4),
              (2., -.7, .8), (3., .2, -.6)]
    rots = [Rotation.from_euler('xyz', a).as_matrix() for a in angles]
    vertices = np.asarray([[-.2, -.1, -.3], [.4, -.2, .1],
                           [.1, .5, .2], [-.3, .2, .4], [.2, .1, -.4]])
    for typ, R in itertools.product(range(2, 8), rots):
        size = np.asarray([.13, .21, .09])
        p = np.asarray([.7, -.8, 1.3])
        lo, hi = shape_bounds(typ, size, R, p, vertices)
        a, b = support_point_oracle(typ, size, R, p, vertices)
        close(lo, a, 'independent negative support type ' + str(typ))
        close(hi, b, 'independent positive support type ' + str(typ))
        ck(np.all(lo <= hi), 'ordered extrema')
    fails(lambda: shape_bounds(1, np.ones(3), np.eye(3), np.zeros(3)), 'heightfield unbound')
    fails(lambda: shape_bounds(2, [-1, 1, 1], np.eye(3), np.zeros(3)), 'negative sphere size')
    fails(lambda: shape_bounds(6, np.ones(3), np.eye(3)*2, np.zeros(3)), 'bad rotation')
    fails(lambda: shape_bounds(7, np.ones(3), np.eye(3), np.zeros(3), [[0, 0, 0]]), 'mesh size')
    fails(lambda: shape_bounds(6, np.ones(3), np.eye(3), [math.nan, 0, 0]), 'nonfinite')
    # Model metadata selection, including maskless explicit pairs, ignored mesh_pos/quaternion.
    m = SimpleNamespace(ngeom=8, pair_geom1=np.array([3, 7]), pair_geom2=np.array([0, 0]),
        geom_bodyid=np.array([0, 1, 1, 1, 1, 1, 1, 1]),
        geom_contype=np.array([1, 2, 0, 0, 2, 2, 0, 0]),
        geom_conaffinity=np.array([1, 0, 1, 0, 0, 0, 0, 0]),
        geom_type=np.array([6, 2, 3, 4, 5, 6, 7, 7]),
        geom_size=np.tile([.13, .21, .09], (8, 1)), geom_rbound=np.full(8, 2.),
        geom_margin=np.full(8, .001), geom_dataid=np.array([-1]*6+[0, 0]),
        mesh_vertadr=np.array([0]), mesh_vertnum=np.array([len(vertices)]),
        mesh_vert=vertices, mesh_pos=np.array([[9., 8., 7.]]),
        mesh_quat=np.array([[0., 1., 0., 0.]]),
        geom=lambda gid: SimpleNamespace(name='g'+str(gid)))
    cache = CompiledCollisionSupport(m)
    ck(cache.geom_ids == (1, 2, 3, 4, 5, 7), 'mask OR explicit pair and world exclusion')
    data = SimpleNamespace(geom_xpos=np.arange(24, dtype=float).reshape(8, 3)/7,
                           geom_xmat=np.tile(rots[1].reshape(1, 9), (8, 1)))
    before = (data.geom_xpos.tobytes(), data.geom_xmat.tobytes())
    bounds = cache.bounds(data, stage_time_s=1.25)
    ck(before == (data.geom_xpos.tobytes(), data.geom_xmat.tobytes()), 'cached data unchanged')
    mesh = next(p for p in bounds['per_geom'] if p['geom_id'] == 7)
    expected = vertices@rots[1].T + data.geom_xpos[7]
    close(mesh['min_xyz_m'], expected.min(axis=0), 'compiled mesh single transform trap')
    ck(bounds['contact_margin_included'] is False, 'geometry/contact-shell distinction')
    saved = bounds['per_geom'][0]['min_xyz_m'][0]
    bounds['per_geom'][0]['min_xyz_m'][0] = -999.
    ck(cache.bounds(data, stage_time_s=1.25)['per_geom'][0]['min_xyz_m'][0] == saved,
       'result independent ownership')
    fails(lambda: cache.bounds(data, stage_time_s=math.nan), 'nonfinite stage')
    PHASE = 'new_real_model_compile_and_five_geometric_poses'
    import mujoco as mj
    from mesh_support import TireMeshSupport
    xml = ROOT/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'
    ck(record(xml)['SHA'] == '0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324', 'authoritative XML')
    def forbidden(*args, **kwargs):
        COUNTERS['integrator_entries'] += 1
        raise RuntimeError('integrator forbidden by geometry-only plan')
    for name in ('mj_step', 'mj_step1', 'mj_step2', 'mj_Euler', 'mj_RungeKutta', 'mj_implicit'):
        if hasattr(mj, name): setattr(mj, name, forbidden)
    COUNTERS['model_compiles'] += 1
    model = mj.MjModel.from_xml_path(str(xml))
    real_cache = CompiledCollisionSupport(model)
    tire = TireMeshSupport(model)
    d = mj.MjData(model)
    free = np.flatnonzero(np.asarray(model.jnt_type) == 0)
    ck(len(free) == 1, 'single free root in current model')
    adr = int(model.jnt_qposadr[int(free[0])])
    real_snapshots = []
    for k, angle in enumerate(angles):
        d.qpos[:] = model.qpos0
        d.qvel[:] = 0.
        d.ctrl[:] = 0.
        d.qpos[adr:adr+3] = [.2 + .1*k, -.03*k, 2.]
        q = Rotation.from_euler('xyz', angle).as_quat()
        d.qpos[adr+3:adr+7] = q[[3, 0, 1, 2]]
        COUNTERS['explicit_mj_forward'] += 1
        mj.mj_forward(model, d)
        before = tuple(np.asarray(a).tobytes() for a in
                       (d.qpos, d.qvel, d.ctrl, d.geom_xpos, d.geom_xmat)) + (float(d.time),)
        b = real_cache.bounds(d, stage_time_s=0.)
        env = tire.envelopes(d)
        after = tuple(np.asarray(a).tobytes() for a in
                      (d.qpos, d.qvel, d.ctrl, d.geom_xpos, d.geom_xmat)) + (float(d.time),)
        ck(before == after, 'real data geometry/read-only byte equality')
        ck(float(d.time) == 0., 'no elapsed integration')
        for row in b['per_geom']:
            gid = row['geom_id']
            p = d.geom_xpos[gid]
            r = float(model.geom_rbound[gid]) + 1e-8
            ck(np.all(np.asarray(row['min_xyz_m']) >= p-r-2e-12), 'raw lower inside original certificate')
            ck(np.all(np.asarray(row['max_xyz_m']) <= p+r+2e-12), 'raw upper inside original certificate')
            local = real_cache.geoms[real_cache.geom_ids.index(gid)]
            a, c = support_point_oracle(local.typ, local.size, d.geom_xmat[gid].reshape(3, 3),
                                        p, local.vertices)
            close(row['min_xyz_m'], a, 'real lower supporting-point oracle')
            close(row['max_xyz_m'], c, 'real upper supporting-point oracle')
        for name, v in env.items():
            row = next(vv for vv in b['per_geom'] if vv['geom_name'] == name)
            close(row['min_xyz_m'], v['min_xyz_m'], 'tire helper minimum compatibility')
            close(row['max_xyz_m'], v['max_xyz_m'], 'tire helper maximum compatibility')
        real_snapshots.append(b)
    ck(COUNTERS == dict(model_compiles=1, explicit_mj_forward=5, integrator_entries=0), 'fixed new budget')
    after_sources = [record(p) for p in SOURCES]
    ck(source_before == after_sources, 'source before/after unchanged')
    save(out/'REAL_GEOMETRIC_SNAPSHOTS.json', real_snapshots)
    inventory = [dict(geom_id=g.gid, geom_name=g.name, type=g.typ,
                      type_name=__import__('support').TYPE_NAMES[g.typ]) for g in real_cache.geoms]
    save(out/'RESULT.json', dict(status='PASS_NEW_GEOMETRY_ONLY_NO_EPISODES_NO_OLD_REGRADING',
        checks=COUNT, failures=0, max_support_oracle_error_m=MAX_ERROR, counters=COUNTERS,
        model=dict(nbody=int(model.nbody), ngeom=int(model.ngeom), nmesh=int(model.nmesh)),
        collision_inventory=inventory, sources_before_after=source_before,
        interpretation='compiled shapes, not contact shells/formal intervals/stability; geometric poses not admissible equilibria',
        R62_scores_changed=False, old_raw_reads=0, PH8pending=True))
    print(json.dumps(dict(status='PASS', checks=COUNT, counters=COUNTERS,
                          collision_geoms=len(inventory), max_error_m=MAX_ERROR)))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        p = D/'validation001'
        if p.is_dir():
            with (p/'ERROR.json').open('x', encoding='utf-8') as f:
                json.dump(dict(status='FAILED_NEW_GEOMETRY_VALIDATION', phase=PHASE,
                    completed_checks=COUNT, counters=COUNTERS, traceback=traceback.format_exc(),
                    no_old_scores_rewritten=True), f, indent=2, allow_nan=False)
        raise
