"""Freeze the V11 baseline: every dynamical, control and RL-interface number, plus a
SHA256 manifest of the archived tree.  Later changes are judged by diffing against this.

Cfg-only: it never builds the simulator, so it costs no GPU and cannot disturb training.
"""
import argparse, dataclasses, hashlib, json, os, sys
import numpy as np, mujoco

ROOT = r"D:/claude2/fangzhen"


def _j(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return [round(float(v), 8) for v in o.reshape(-1)]
    if isinstance(o, (list, tuple)):
        return [_j(v) for v in o]
    if isinstance(o, dict):
        return {str(k): _j(v) for k, v in o.items()}
    if isinstance(o, (str, bool, int, float)) or o is None:
        return o
    if dataclasses.is_dataclass(o):
        return _j(dataclasses.asdict(o))
    return repr(o)


def dump_plant(xml):
    m = mujoco.MjModel.from_xml_path(xml)
    nm = lambda t, i: mujoco.mj_id2name(m, t, i) or "?"
    d = {"xml": xml.replace("\\", "/"),
         "options": {"timestep": m.opt.timestep, "integrator": int(m.opt.integrator),
                     "solver": int(m.opt.solver), "iterations": m.opt.iterations,
                     "ls_iterations": m.opt.ls_iterations, "tolerance": m.opt.tolerance,
                     "cone": int(m.opt.cone), "impratio": m.opt.impratio},
         "counts": {"nbody": m.nbody, "njoint": m.njnt, "nq": m.nq, "nv": m.nv,
                    "nu": m.nu, "neq": m.neq, "ngeom": m.ngeom,
                    "mass_total": round(float(m.body_mass.sum()), 4)}}
    bodies = []
    for b in range(m.nbody):
        I = m.body_inertia[b]
        bodies.append({"name": nm(mujoco.mjtObj.mjOBJ_BODY, b),
                       "parent": nm(mujoco.mjtObj.mjOBJ_BODY, m.body_parentid[b]),
                       "pos": _j(m.body_pos[b]), "mass": round(float(m.body_mass[b]), 6),
                       "ipos": _j(m.body_ipos[b]),
                       "inertia": _j(I),
                       "inertia_eig": _j(np.sort(I)) if len(I) else [],
                       "inertia_positive": bool(np.all(I > 0)),
                       "pdm_shapiro": bool(len(I) == 3 and np.all(np.sort(I)[2]
                                            <= np.sort(I)[0] + np.sort(I)[1] + 1e-12))})
    d["bodies"] = bodies
    joints = []
    for j in range(m.njnt):
        jn = nm(mujoco.mjtObj.mjOBJ_JOINT, j)
        lim = m.jnt_range[j]
        joints.append({"name": jn, "type": int(m.jnt_type[j]),
                       "axis": _j(m.jnt_axis[j]), "qposadr": int(m.jnt_qposadr[j]),
                       "dofadr": int(m.jnt_dofadr[j]),
                       "limited": bool(m.jnt_limited[j]), "range": _j(lim),
                       "stiffness": _j(m.jnt_stiffness[j]), "damping": _j(m.dof_damping[j]),
                       "armature": _j(m.dof_armature[j]),
                       "frictionloss": _j(m.dof_frictionloss[j]),
                       "body": nm(mujoco.mjtObj.mjOBJ_BODY, m.jnt_bodyid[j])})
    d["joints"] = joints
    acts = []
    for i in range(m.nu):
        tn = m.actuator_trnid[i, 0]
        acts.append({"name": nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i),
                     "trntype": int(m.actuator_trntype[i]),
                     "target": nm(mujoco.mjtObj.mjOBJ_JOINT, tn) if tn >= 0 else None,
                     "gear": _j(m.actuator_gear[i]), "ctrllimited": bool(m.actuator_ctrllimited[i]),
                     "ctrlrange": _j(m.actuator_ctrlrange[i]),
                     "forcelimited": bool(m.actuator_forcelimited[i]),
                     "forcerange": _j(m.actuator_forcerange[i]),
                     "dyntype": int(m.actuator_dyntype[i])})
    d["actuators"] = acts
    geoms = []
    for g in range(m.ngeom):
        t = int(m.geom_type[g])
        geoms.append({"name": nm(mujoco.mjtObj.mjOBJ_GEOM, g) or "(unnamed)",
                      "type": t, "type_name": mujoco.mjtGeom(t).name.replace("mjGEOM_", ""),
                      "body": nm(mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]),
                      "contype": int(m.geom_contype[g]), "conaffinity": int(m.geom_conaffinity[g]),
                      "group": int(m.geom_group[g]), "condim": int(m.geom_condim[g]),
                      "friction": _j(m.geom_friction[g]), "priority": int(m.geom_priority[g]),
                      "size": _j(m.geom_size[g]), "pos": _j(m.geom_pos[g]),
                      "quat": _j(m.geom_quat[g]),
                      "mesh": (nm(mujoco.mjtObj.mjOBJ_MESH, m.geom_dataid[g])
                               if t == mujoco.mjtGeom.mjGEOM_MESH else None),
                      "rgba": _j(m.geom_rgba[g])})
    d["geoms"] = geoms
    eqs = []
    for e in range(m.neq):
        eqs.append({"type": int(m.eq_type[e]),
                    "obj1": nm(mujoco.mjtObj.mjOBJ_BODY, int(m.eq_obj1id[e])),
                    "obj2": nm(mujoco.mjtObj.mjOBJ_BODY, int(m.eq_obj2id[e])),
                    "data": _j(m.eq_data[e]), "solimp": _j(m.eq_solimp[e]),
                    "solref": _j(m.eq_solref[e])})
    d["equalities"] = eqs
    meshes = []
    for k in range(m.nmesh):
        meshes.append({"name": nm(mujoco.mjtObj.mjOBJ_MESH, k),
                       "file": mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MESH, k),
                       "nvert": int(m.mesh_vertnum[k]), "nface": int(m.mesh_facenum[k])})
    d["meshes"] = meshes
    d["mesh_total_triangles"] = int(sum(x["nface"] for x in meshes))
    return d


def dump_rl(task):
    sys.path.insert(0, os.path.join(ROOT, "train/rmvehicle/src"))
    import rmvehicle  # noqa: F401  registers the tasks
    from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
    out = {"task": task}
    cfg = load_env_cfg(task, play=False)
    obs = {}
    for grp in cfg.observations:
        terms = {}
        for tname, t in cfg.observations[grp].terms.items():
            terms[tname] = {"func": getattr(t.func, "__module__", "") + "." +
                                 getattr(t.func, "__name__", "?"),
                            "params": {k: _j(v) for k, v in dict(t.params or {}).items()},
                            "scale": _j(getattr(t, "scale", None)),
                            "clip": _j(getattr(t, "clip", None)),
                            "noise": getattr(t, "noise", None) and str(t.noise),
                            "history_length": getattr(t, "history_length", None)}
        obs[grp] = {"enable_corruption": getattr(cfg.observations[grp], "enable_corruption", None),
                    "terms": terms}
    out["observations"] = obs
    def cfg_of(t):
        """Best-effort flatten of any mjlab config dataclass across versions."""
        o = {"_cls": type(t).__name__}
        for k in dir(t):
            if k.startswith("_"):
                continue
            try:
                v = getattr(t, k)
            except Exception:
                continue
            if callable(v):
                o[k] = getattr(v, "__module__", "") + "." + getattr(v, "__name__", "?")
                continue
            if dataclasses.is_dataclass(v):
                try:
                    o[k] = _j(dataclasses.asdict(v))
                    continue
                except Exception:
                    pass
            if isinstance(v, (str, bool, int, float, np.number)) or v is None:
                o[k] = _j(v)
            elif isinstance(v, (list, tuple, dict, np.ndarray)):
                o[k] = _j(v)
        return o

    def flat_or_grouped(container):
        items = getattr(container, "items", None)
        data = dict(items()) if callable(items) else dict(container)
        out = {}
        for k, v in data.items():
            inner = getattr(v, "terms", None)
            if isinstance(inner, dict):
                out[k] = {n: cfg_of(t) for n, t in inner.items()}
            else:
                out[k] = cfg_of(v)
        return out

    out["actions"] = flat_or_grouped(cfg.actions)
    out["rewards"] = flat_or_grouped(cfg.rewards)
    out["terminations"] = flat_or_grouped(cfg.terminations)
    out["events_reset_and_domain_rand"] = flat_or_grouped(cfg.events)
    out["curriculum"] = {n: cfg_of(t) for n, t in (cfg.curriculum or {}).items()}
    s = cfg.sim
    out["sim"] = {"dt": s.mujoco.timestep, "decimation": cfg.decimation,
                  "iterations": s.mujoco.iterations, "ls_iterations": s.mujoco.ls_iterations,
                  "impratio": s.mujoco.impratio, "cone": str(s.mujoco.cone),
                  "solver": str(s.mujoco.solver), "integrator": str(s.mujoco.integrator),
                  "nconmax": s.nconmax, "njmax": s.njmax,
                  "policy_hz": 1.0 / (s.mujoco.timestep * cfg.decimation)}
    out["env"] = {"num_envs": cfg.scene.num_envs, "env_spacing": cfg.scene.env_spacing,
                  "episode_length_s": cfg.episode_length_s}
    try:
        rl = load_rl_cfg(task)
        out["rl"] = {"algorithm": type(rl).__name__, "iterations": rl.max_iterations,
                     "num_steps_per_env": rl.num_steps_per_env,
                     "init_noise_std": _j(getattr(rl, "init_noise_std", None)),
                     "actor_hidden": _j(rl.policy.actor_hidden_dims),
                     "critic_hidden": _j(rl.policy.critic_hidden_dims),
                     "act": str(rl.policy.actor_obs_normalization) + "/" + str(rl.policy.critic_obs_normalization),
                     "lr": _j(rl.learning_rate), "desired_kl": _j(getattr(rl, "desired_kl", None)),
                     "max_grad_norm": _j(getattr(rl, "max_grad_norm", None)),
                     "entropy_coef": _j(getattr(rl, "entropy_coef", None)),
                     "gamma": _j(getattr(rl, "gamma", None)), "lam": _j(getattr(rl, "lam", None))}
    except Exception as e:
        out["rl_error"] = "%s: %s" % (type(e).__name__, e)
    return out


def manifest(root):
    out = {}
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git")]
        for f in files:
            p = os.path.join(dirpath, f)
            if f.endswith((".pt", ".onnx", ".stl", ".obj", ".mp4", ".log", ".hf", ".png")):
                continue  # fingerprints of the *code/config* tree; blobs are huge
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for blk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(blk)
            out[os.path.relpath(p, root).replace("\\", "/")] = h.hexdigest()[:16]
    return dict(sorted(out.items()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="RMVehicle-CC-Field-v0")
    ap.add_argument("--out", default=os.path.join(ROOT, "V11_original", "BASELINE_V11.json"))
    a = ap.parse_args()
    rec = {"plant": dump_plant(os.path.join(ROOT, "robot/out_cc/rm_vehicle_cc.xml")),
           "rl": dump_rl(a.task),
           "sha256_code_tree": manifest(os.path.join(ROOT, "V11_original"))}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(_j(rec), open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    p = rec["plant"]
    print("plant: nq=%d nv=%d nu=%d neq=%d mass=%.3f kg  triangles=%d" %
          (p["counts"]["nq"], p["counts"]["nv"], p["counts"]["nu"], p["counts"]["neq"],
           p["counts"]["mass_total"], p["mesh_total_triangles"]))
    bad = [b["name"] for b in p["bodies"] if not b["inertia_positive"] or not b["pdm_shapiro"]]
    print("inertia: all positive & triangle-inequality OK" if not bad else "INERTIA SUSPECT: %s" % bad)
    print("fingerprinted %d code/config files" % len(rec["sha256_code_tree"]))
    print("wrote", a.out)