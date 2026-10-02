import io,ast
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/rewards.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('''def joint_power(env''','''def lin_vel_z_l2(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
  asset: Entity = env.scene[asset_cfg.name]
  return (asset.data.root_link_lin_vel_b[:, 2] ** 2)


def ang_vel_xy_l2(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
  asset: Entity = env.scene[asset_cfg.name]
  return (asset.data.root_link_ang_vel_b[:, :2] ** 2).sum(dim=1)


def joint_power(env''')
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t)
p2=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/__init__.py"
t2=io.open(p2,encoding="utf-8").read()
t2=t2.replace("  height_tracking,\n  joint_power,\n  leg_symmetry,","  ang_vel_xy_l2,\n  height_tracking,\n  joint_power,\n  leg_symmetry,\n  lin_vel_z_l2,")
io.open(p2,"w",encoding="utf-8").write(t2); ast.parse(t2)
p3=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/env_cfgs.py"
t3=io.open(p3,encoding="utf-8").read()
t3=t3.replace('''    "lin_vel_z": RewardTermCfg(func=envs_mdp.base_lin_vel, weight=-0.4,
                               params={"asset_cfg": SceneEntityCfg("robot")}),''',
'''    "lin_vel_z": RewardTermCfg(func=mdp.lin_vel_z_l2, weight=-0.6),
    "ang_vel_xy": RewardTermCfg(func=mdp.ang_vel_xy_l2, weight=-0.05),''')
io.open(p3,"w",encoding="utf-8").write(t3); ast.parse(t3)
print("rewards/env cfg patched")
