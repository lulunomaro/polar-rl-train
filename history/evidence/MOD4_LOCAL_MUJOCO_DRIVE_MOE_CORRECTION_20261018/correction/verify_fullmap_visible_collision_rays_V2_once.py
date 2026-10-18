"""Correct only mj_ray visibility, preserving the original all-miss reader result."""
from pathlib import Path
import sys,json,time,traceback
import mujoco,numpy as np
B=Path(__file__).resolve().parent;W=B.parent;D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
sys.path.insert(0,str(D))
from rm7v7_moe_sim import RM7V7MoESim
try:
    s=RM7V7MoESim();s.data.qpos[:3]=[100,100,5];mujoco.mj_forward(s.model,s.data)
    ids=[i for i in range(s.model.ngeom) if (mujoco.mj_id2name(s.model,mujoco.mjtObj.mjOBJ_GEOM,i) or '').startswith('rm_col_')]
    assert len(ids)==47282
    alpha=s.model.geom_rgba[ids,3].copy();s.model.geom_rgba[ids,3]=1
    checks=json.loads((W/'rmuc2026_training/data/source_ray_checks.json').read_text());rows=[]
    mask=np.array([0,0,0,1,0,0],dtype=np.uint8)
    for c in checks:
        geom=np.zeros(1,dtype=np.int32);actual=mujoco.mj_ray(s.model,s.data,np.array(c['origin_m']),np.array(c['direction']),mask,True,-1,geom)
        error=None if actual<0 else abs(actual-c['expected_distance_m'])
        rows.append(dict(id=c['id'],actual=actual,expected=c['expected_distance_m'],error=error,source_tolerance=c['tolerance_m'],
            passed=error is not None and error<=c['tolerance_m']))
    s.model.geom_rgba[ids,3]=alpha
    failed=[r for r in rows if not r['passed']]
    out=dict(epoch=time.time(),source_CAD_ray_checks=len(rows),passed=not failed,
        max_error=max((r['error'] for r in rows if r['error'] is not None),default=None),failures=failed,
        original_source_tolerances_not_relaxed=True,ray_visibility_alpha_only_temporarily_changed=True,
        original_transparent_all_miss_reader_report_retained=True,geometry_physics_source_unchanged=True,all_rows=rows)
    (B/'reports/FULL_MAP_CAD_RAYS_CORRECT_VISIBILITY_V2_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({k:out[k] for k in ('source_CAD_ray_checks','passed','max_error')})+f' failed={len(failed)}')
    assert not failed
except BaseException:
    (B/f'reports/FULL_MAP_RAY_V2_ORIGINAL_ERROR_{time.time_ns()}.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
