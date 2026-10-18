from pathlib import Path
import mujoco,time,json,traceback
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
try:
    start=time.perf_counter();m=mujoco.MjModel.from_xml_path(str(D/'rm7v7_latest_moe.xml'))
    report=dict(epoch=time.time(),compiled=True,seconds=time.perf_counter()-start,ngeom=m.ngeom,nmesh=m.nmesh,nq=m.nq,nv=m.nv,nu=m.nu,neq=m.neq)
    mujoco.mj_saveModel(m,str(D/'rm7v7_latest_moe.mjb'))
    (B/'reports/FULL_RM7V7_MODEL_COMPILED_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
except BaseException:
    (B/f'reports/FULL_MAP_COMPILE_ORIGINAL_ERROR_{time.time_ns()}.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
