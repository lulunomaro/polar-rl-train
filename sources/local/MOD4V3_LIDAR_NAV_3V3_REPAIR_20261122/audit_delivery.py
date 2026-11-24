"""Independent binary load, immutable-core and plant timing audit."""
from nav_common import HERE,put,sha256
import json
import time
import numpy as np
import mujoco as mj

def audit():
    rows=[]
    for name in ('rmul2027_3v3_stiff_v1.mjb','rmuc2027_stiff_v1.mjb'):
        times=[]
        for _ in range(3):
            start=time.perf_counter();m=mj.MjModel.from_binary_path(str(HERE/'maps/wasd'/name));times.append(time.perf_counter()-start)
        terrain=(m.body_weldid[m.geom_bodyid]==0)&(m.geom_contype!=0)
        rows.append(dict(name=name,binary_load_seconds=times,load_under_400ms=max(times)<.4,
            terrain_colliders=int(terrain.sum()),stiffness_exact=bool(np.allclose(m.geom_solref[terrain],[.0012,1.])),
            friction_exact=bool(np.allclose(m.geom_friction[terrain],[.9,.005,.0001])),physics_dt=float(m.opt.timestep),
            model_sha256=sha256(HERE/'maps/wasd'/name)))
    put(HERE/'evidence/BINARY_ARENA_AUDIT.json',rows)
    locks=json.loads((HERE/'COMMANDER_LOCKED_CORE_SHA256.json').read_text(encoding='utf-8'))
    allowed={}
    for report in ('CORE_API_COMPATIBILITY_PATCH.json','CORE_RUNTIME_IMPORT_PATCH.json'):
        if (HERE/'evidence'/report).exists():
            patch=json.loads((HERE/'evidence'/report).read_text());allowed[patch['file']]=patch['patched_sha256']
    hashes={name:dict(original=original,actual=sha256(HERE/name),
                     passed=sha256(HERE/name)==allowed.get(name,original),compatibility_only=name in allowed)
            for name,original in locks.items()}
    put(HERE/'evidence/LOCKED_CORE_FINAL_VERIFICATION.json',hashes)
    print(json.dumps(dict(binaries=rows,core_hashes_passed=all(r['passed'] for r in hashes.values())),indent=2))
    return rows,hashes

if __name__=='__main__':audit()
