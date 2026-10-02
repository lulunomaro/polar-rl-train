import io, ast
p = r"D:/claude2/fangzhen/train/eval_robust.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('''    elif cond == "push":
        cfg.events["push_robot"].interval_range_s = (2.0, 4.0)
        cfg.events["push_robot"].params["velocity_range"] = {
            "x": (-0.8, 0.8), "y": (-0.4, 0.4), "pitch": (-0.6, 0.6)}''',
'''    elif cond == "push":
        from mjlab.envs import mdp as em
        from mjlab.managers.event_manager import EventTermCfg
        from mjlab.managers.scene_entity_config import SceneEntityCfg
        cfg.events["push_robot"] = EventTermCfg(
            func=em.push_by_setting_velocity, mode="interval",
            interval_range_s=(3.0, 6.0),
            params={"velocity_range": {"x": (-0.8, 0.8), "y": (-0.4, 0.4),
                                       "roll": (-0.5, 0.5), "pitch": (-0.5, 0.5)},
                    "asset_cfg": SceneEntityCfg("robot")})''')
io.open(p, "w", encoding="utf-8", newline="\n").write(t); ast.parse(t); print("push condition rebuilt")
