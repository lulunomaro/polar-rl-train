"""Create narrow material-only214 namespaces; never import SDK or touch binaries."""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent;T=HERE.parent;SRC=HERE/'source';R=HERE/'reports'
P=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
MOD=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4'
PINS=[]


def source(path):
    assert path.suffix=='.py';raw=path.read_bytes()
    PINS.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    return raw.decode('utf8').replace('\r\n','\n')


def one(value,old,new):
    if value.count(old)!=1:raise ValueError('Exact material source delta mismatch: '+old)
    return value.replace(old,new)


def output(name,value):
    with (SRC/name).open('x',encoding='utf8',newline='\n') as f:f.write(value)


def main():
    with (R/'SOURCE214_PREPARATION_ONCE.json').open('x')as f:json.dump(dict(
        ID='NEW214_MATERIAL_SHARING_SOURCE_DERIVATION_V1',epoch=time.time(),source_only=True),f)
    field=source(P/'source/field208.py')
    start=field.index("    path = output / 'full_RM70_layout.usda'")
    end=field.index("    (output / 'layout.json').write_text",start)
    field=field[:start]+"    from usd214 import author_original_shared_material_layout\n    path = author_original_shared_material_layout(root,output,origins)\n"+field[end:]
    output('field214.py',field)
    cfg=source(P/'adapter_v3/config208_v3.py')
    cfg=one(cfg,'def configure208(cfg):','def configure214(cfg):')
    cfg=one(cfg,'from field208 import make_terrain_cfg','from field214 import make_terrain_cfg')
    cfg=one(cfg,'    recipe = configure_intro(cfg)',
        "    recipe = configure_intro(cfg)\n    from mild_dr214 import MildDR214\n    assert cfg.events.mild_dr_white is not None\n    cfg.events.mild_dr_white.func = MildDR214")
    output('config214.py',cfg)
    mild=source(MOD/'mild_dr.py')
    mild=one(mild,'class MildDR(ManagerTermBase):','class MildDR214(ManagerTermBase):')
    mild=one(mild,'        super().__init__(cfg, env)',
        "        from material214 import log\n        from usd214 import material_census\n        log('BEFORE_MILD_DR_CONSTRUCTION',num_envs=env.num_envs,terrain=material_census(env.sim.stage))\n        super().__init__(cfg, env)")
    mild=one(mild,"        self.materials = tensor(robot.root_view.get_material_properties()).clone().cpu()",
        "        self.materials = tensor(robot.root_view.get_material_properties()).clone().cpu()\n        from material214 import cached_summary\n        log('AFTER_ORIGINAL_MATERIAL_CACHE_READ',num_envs=env.num_envs,**cached_summary(torch,self.materials))")
    mild=one(mild,'        self.robot.root_view.set_material_properties(wp.from_torch(materials, dtype=wp.float32),\n                                                    wp.from_torch(cpu_ids, dtype=wp.int32))',
        '        from material214 import set_material_once\n        set_material_once(torch,wp,self.robot.root_view,materials,cpu_ids)')
    mild=one(mild,"cfg.events.mild_dr_white = EventTermCfg(func=MildDR, mode='reset')",
        "cfg.events.mild_dr_white = EventTermCfg(func=MildDR214, mode='reset')")
    output('mild_dr214.py',mild)
    with (R/'SOURCE214_DERIVATION_PINS.json').open('x',encoding='utf8')as f:json.dump(dict(
        ID='NEW214_MATERIAL_SHARING_SOURCE_DERIVATION_V1',inputs=PINS,
        original_208_V3_210_files_unchanged=True,
        geometry_source_stays_original_mesh_prim=True,original_material_values_reference_only=True,
        original33bucket_MildDR_sampling_RNG_and_one_actual_setter_call_per_reset_preserved=True,
        prototype_and_material_composition_target_unexecuted=True,
        model_NPZ_USD_SDK_GPU_remote_or_Git_calls=0),f,indent=2)


if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        with (R/('SOURCE214_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x')as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
