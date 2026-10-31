"""Derive a new full-scale0PT contract;old21280env once remains consumed."""
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent;T=HERE.parent;SRC=HERE/'source';R=HERE/'reports'
OLD=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/robot0pt208_v3.py'


def main():
    with (R/'DERIVE214_PROBE_ONCE.json').open('x')as f:json.dump(dict(
        ID='NEW214_20K_MATERIAL_OWN_RESTORE_PROBE_SOURCE_V1',epoch=time.time(),source_only=True),f)
    raw=OLD.read_bytes();value=raw.decode('utf8').replace('\r\n','\n')
    value=value.replace('robot0pt208_v3','material0pt214')
    value=value.replace('ROBOT0PT208_V3_TASK.json','MATERIAL0PT214_TASK.json')
    value=value.replace('NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V3','NEW214_RM70_SHARED_MATERIAL_20K_OWN_RESTORE_ZERO_PT')
    value=value.replace('OWN_MOD4_ROBOT0PT208_V3_ACTUAL','MATERIAL0PT214_NATIVE_RETURNED_ACTUAL')
    value=value.replace('ORIGINAL_ROBOT0PT208_V3_ERROR','ORIGINAL_MATERIAL0PT214_ERROR')
    value=value.replace('from config208_v3 import configure208','from config214 import configure214 as configure208')
    value=value.replace("task['num_envs'] == 80","task['num_envs'] == 20000")
    value=value.replace("task['max_worker_seconds'] == 600","task['max_worker_seconds'] == 1680")
    value=value.replace('cfg.scene.num_envs = 80','cfg.scene.num_envs = 20000')
    value=value.replace('env.num_envs == 80','env.num_envs == 20000')
    value=value.replace('(80, 6)','(20000, 6)').replace('(80, 35)','(20000, 35)').replace('(80, 38)','(20000, 38)')
    value=value.replace('(80, 13)','(20000, 13)').replace('(80, 30)','(20000, 30)')
    value=value.replace('num_envs=80','num_envs=20000').replace('> 600:','> 1680:')
    value=value.replace('admission600s worker bound','material capacity1680s worker bound')
    value=value.replace('actual_D0_D7_fresh80_source_native_integration=True','actual_D0_D7_own20k_restore_then_new_episode_native_integration=True')
    value=value.replace("    started = time.time(); env = None; app = None",
        "    from material214 import phase,counts,finish\n    from usd214 import material_census\n    os.environ['MOD4_MATERIAL214_OUT']=str(output)\n    phase('BEFORE_APP_CONSTRUCTION',num_envs=20000,PT_opens=0,NN_constructors=0)\n    started = time.time(); env = None; app = None")
    value=value.replace('        env = RetentionLearningEnv(cfg=cfg)',
        "        phase('BEFORE_FULL20K_ENV_CONSTRUCTION')\n        env = RetentionLearningEnv(cfg=cfg)\n        phase('AFTER_FULL20K_ENV_CONSTRUCTION',terrain=material_census(env.sim.stage))")
    value=value.replace('        obs, info = env.reset()',
        "        phase('BEFORE_FRESH20K_RESET')\n        obs, info = env.reset()\n        phase('AFTER_FRESH20K_RESET',terrain=material_census(env.sim.stage))\n        from restore214 import own_restore_and_new_episode\n        obs,info,own_restore=own_restore_and_new_episode(env,torch)\n        phase('BEFORE_8_NATIVE_CONTROLS',material_setter_counts=counts())")
    value=value.replace("        put(output / 'MATERIAL0PT214_NATIVE_RETURNED_ACTUAL.json', dict(",
        "        phase('AFTER_8_NATIVE_CONTROLS',terrain=material_census(env.sim.stage),material_setter_counts=counts())\n        put(output / 'MATERIAL0PT214_NATIVE_RETURNED_ACTUAL.json', dict(\n            own20k_restore=own_restore,material_setter_counts=counts(),\n            native_function_only_parent_must_reject_any_64K_error=True,\n            actual_PhysX_material_handle_count='UNKNOWN_NOT_STAGE_PRIM_COUNT',")
    value=value.replace('        if app is not None:\n            app.close()',
        "        if app is not None:\n            phase('APP_CLOSING')\n            app.close()\n        finish()")
    with (SRC/'material0pt214.py').open('x',encoding='utf8',newline='\n')as f:f.write(value)
    with (R/'PROBE214_DERIVATION.json').open('x',encoding='utf8')as f:json.dump(dict(
        ID='NEW214_20K_MATERIAL_OWN_RESTORE_PROBE_SOURCE_V1',original=dict(path=str(OLD),SHA=hashlib.sha256(raw).hexdigest()),
        selected=dict(path=str(SRC/'material0pt214.py'),SHA=hashlib.sha256((SRC/'material0pt214.py').read_bytes()).hexdigest()),
        root_old212_probe_not_rerun=True,PT_NPZ_USD_SDK_GPU_remote_child_calls=0,
        new_scope='20kfullpopulation material sharing and ownDR physical reapplication before one reset/8controls;0PT/NN0',
        original20k_training_and_actualcheckpoint_resume_not_claimed=True),f,indent=2)


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        with (R/('PROBE214_SOURCE_ERROR_'+str(time.time_ns())+'.json')).open('x')as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
