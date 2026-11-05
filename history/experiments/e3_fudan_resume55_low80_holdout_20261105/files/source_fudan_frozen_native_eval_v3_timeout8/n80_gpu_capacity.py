PRESET=dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20)
def capacity_ctor(original):
 def construct(*aa,**kw):
  c=kw['cfg'];assert c.scene.num_envs==80 and c.sim.dt==.0025 and c.decimation==8
  before={k:getattr(c.sim.physics,k)for k in PRESET}
  for k,v in PRESET.items():setattr(c.sim.physics,k,v)
  env=original(*aa,**kw);env._n80_allocation_only_capacity={'SDK_original_capacity':before,'explicit_original_route80_preset':dict(PRESET),'plant_solver_DR_RNG_unchanged':True};return env
 return construct
