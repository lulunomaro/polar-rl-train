"""Pose the unchanged MOD4v3 R3 asset at its folded stop, then rotate rearward.

This is a static geometric pose viewer. It never advances dynamics or runs a policy.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import math
import sys
import time

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()) as probe_log:
    import probe_geometry as geometry

m, d = geometry.m, geometry.d
kinematics = geometry.kinematics
runtime = geometry.runtime
lo, hi = geometry.lo, geometry.hi
rear0, front0 = geometry.rear0, geometry.front0
base = m.body("base_link").id
FONT = "C:/Windows/Fonts/msyh.ttc"


def pose(front, rear):
    d.qpos[:3] = (0., 0., .35)
    d.qpos[3:7] = (1., 0., 0., 0.)
    d.qvel[:] = 0.
    d.ctrl[:] = 0.
    d.xfrc_applied[:] = 0.
    kinematics.set_configuration(m, d, left=(front, rear), right=(front, rear), check_limits=True)
    collision = [i for i in range(m.ngeom) if m.geom_bodyid[i]
                 and (m.geom_contype[i] or m.geom_conaffinity[i])]
    bottom = min(geometry.min_z(i) for i in collision)
    d.qpos[2] -= bottom
    mujoco.mj_forward(m, d)


def closure():
    errors = {}
    for side in ("left", "right"):
        for name, a, b in (("front3", "proximal_a", "proximal_b"),
                           ("f4r2", "distal_a", "distal_b"),
                           ("s2r2", "gas_end", "gas_mount")):
            errors[f"{side}_{name}"] = float(np.linalg.norm(
                d.site_xpos[m.site(f"{side}_{a}").id] -
                d.site_xpos[m.site(f"{side}_{b}").id]))
    return errors


def measurements(front, rear, alpha):
    pose(front, rear)
    errors = closure()
    bounds = []
    limits = []
    for j in range(m.njnt):
        if m.jnt_type[j] == mujoco.mjtJoint.mjJNT_FREE or not m.jnt_limited[j]:
            continue
        q = float(d.qpos[m.jnt_qposadr[j]])
        lower, upper = m.jnt_range[j]
        if q < lower-1e-8 or q > upper+1e-8:
            bounds.append(dict(joint=m.joint(j).name, angle=q, range=[float(lower), float(upper)]))
        if np.isfinite(lower) and abs(q-lower) < 1e-8:
            limits.append(m.joint(j).name+":lower")
        if np.isfinite(upper) and abs(q-upper) < 1e-8:
            limits.append(m.joint(j).name+":upper")
    contacts = [dict(geom1=m.geom(c.geom1).name, geom2=m.geom(c.geom2).name,
                     distance_m=float(c.dist)) for c in d.contact if c.dist < -1e-4]
    result = dict(front1_rad=float(front), rear1_rad=float(rear),
        front1_deg=float(np.degrees(front)), rear1_deg=float(np.degrees(rear)),
        relative_angle_rad=float(front-rear), common_rearward_rotation_deg=float(np.degrees(alpha)),
        folded_stop_active=abs(front-rear-lo)<1e-8, both_legs_symmetric=True,
        root_height_m=float(d.qpos[2]), closure_errors_m=errors,
        max_closure_error_m=max(errors.values()), joint_limit_violations=bounds,
        active_equivalent_stop_constraints=limits, reported_penetrations_over_0_1mm=contacts,
        gas_eye_length_m={}, wheel_position_in_base_m={}, qpos=d.qpos.tolist(),
        joint_positions={m.joint(j).name:float(d.qpos[m.jnt_qposadr[j]])
                        for j in range(m.njnt) if m.jnt_type[j] != mujoco.mjtJoint.mjJNT_FREE})
    for side in ("left", "right"):
        result["wheel_position_in_base_m"][side] = (d.xpos[m.body(side+"_wheel_link").id]-d.xpos[base]).tolist()
        gas = d.qpos[m.joint(side+"_spring2_joint").qposadr[0]]
        neutral = kinematics._modules()[1].PARAMS["gas_spring"]["slider_bounds_m"]
        result["gas_eye_length_m"][side] = float(.14 + gas-neutral[0])
    assert not bounds, bounds
    assert result["max_closure_error_m"] < 1e-8, result["max_closure_error_m"]
    return result


# At the folded stop, rotate the whole leg until each wheel axle is directly
# behind its hip at equal height. Both active axes receive the same angle.
pose(rear0+lo, rear0)
hip = d.xpos[m.body("left_rear1_link").id]
wheel = d.xpos[m.body("left_wheel_link").id]
v = wheel-hip
alpha_rear = math.pi-math.atan2(-float(v[2]), float(v[0]))
STAGES = [
    ("01_initial", "1  模型原装配姿态", front0, rear0, None),
    ("02_folded_stop", "2  左右腿均收至机械限位", rear0+lo, rear0, 0.),
    ("03_rear_90", "3  保持贴限位，整体向后翻 90°", rear0+lo+math.pi/2, rear0+math.pi/2, math.pi/2),
    ("04_rear_horizontal", "4  贴限位并后翻，轮轴位于髋轴正后方", rear0+lo+alpha_rear, rear0+alpha_rear, alpha_rear),
    ("05_rear_150", "5  保持贴限位，继续后翻至 150°", rear0+lo+5*math.pi/6, rear0+5*math.pi/6, 5*math.pi/6),
]


def visual_style():
    m.vis.headlight.ambient[:] = (.7, .7, .7)
    m.vis.headlight.diffuse[:] = (.7, .7, .7)
    m.vis.headlight.specular[:] = (.15, .15, .15)
    m.vis.map.fogstart = 10.
    m.vis.map.fogend = 20.
    m.geom_rgba[m.geom("ground").id] = (.88, .90, .93, 1.)
    for gid in range(m.ngeom):
        if m.geom_contype[gid] or m.geom_conaffinity[gid]:
            continue
        bid = int(m.geom_bodyid[gid])
        name = m.body(bid).name or ""
        m.geom_matid[gid] = -1
        if geometry.leg_descendant(bid) and "wheel" not in name:
            m.geom_rgba[gid] = (.15, .48, .78, 1.) if name.startswith("left_") else (.89, .47, .17, 1.)
        elif "wheel" in name:
            m.geom_rgba[gid] = (.16, .18, .21, 1.)
        else:
            m.geom_rgba[gid] = (.55, .59, .64, 1.)


def camera(oblique=False):
    cam=mujoco.MjvCamera()
    cam.lookat[:] = (-.03, 0., .22)
    cam.distance = 1.18 if oblique else 1.13
    cam.azimuth = 135. if oblique else 90.
    cam.elevation = -18. if oblique else -3.
    return cam


def annotated(pixels, title, front, rear, alpha):
    w, h = pixels.shape[1], pixels.shape[0]
    canvas=Image.new("RGB", (w, h+112), "#f7f9fc")
    canvas.paste(Image.fromarray(pixels), (0, 62))
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(FONT, 24)
    small=ImageFont.truetype(FONT, 17)
    draw.text((22, 14), "MOD4v3 R3  ·  "+title, font=font, fill="#10243c")
    delta=front-rear
    status="已贴折叠机械限位" if abs(delta-lo)<1e-8 else "原装配角度"
    extra="" if alpha is None else f" | 整体后翻 {math.degrees(alpha):.2f}°"
    draw.text((22,h+74), f"{status} | front1={front:+.6f} rad | rear1={rear:+.6f} rad{extra}",font=small,fill="#21364d")
    # Side-view cameras at azimuth 90 show +X (front) toward image right.
    draw.line((w-170,h+30,w-45,h+30),fill="#275987",width=4)
    draw.polygon(((w-45,h+30),(w-59,h+22),(w-59,h+38)),fill="#275987")
    draw.text((w-190,h-4),"机体前方 +X",font=small,fill="#275987")
    return canvas


def build():
    (OUT/"INITIAL_GEOMETRY_PROBE.txt").write_text(probe_log.getvalue(),encoding="utf-8")
    report=dict(kind="MOD4V3_STATIC_BILATERAL_FOLDED_STOP_THEN_REAR_ROTATION",
        source_asset=str(geometry.ASSET),
        source_MJCF_SHA256=hashlib.sha256((geometry.ASSET/"mjcf/scene.xml").read_bytes()).hexdigest(),
        simulator_version=mujoco.__version__, physics_steps=0, policies_run=0,
        coordinate_basis="MOD4v3 anatomical absolute radians; no zero/reference changes",
        delta_fold_stop_rad=lo, rear_horizontal_rotation_deg=math.degrees(alpha_rear),
        pose_method="Both sides at lower relative mechanical stop; common rotation of front1 and rear1",
        rendered_colors="Left moving leg blue; right moving leg orange; render appearance only",
        stages={})
    visual_style()
    option=mujoco.MjvOption()
    option.geomgroup[:]=0
    option.geomgroup[2]=1
    with mujoco.Renderer(m,height=640,width=960) as renderer:
        side_images=[]
        for key,title,front,rear,alpha in STAGES:
            report["stages"][key]=measurements(front,rear,alpha or 0.)
            for oblique in (False,True):
                renderer.update_scene(d,camera=camera(oblique),scene_option=option)
                raw=renderer.render()
                frame=annotated(raw,title,front,rear,alpha)
                frame.save(OUT/(key+("_oblique" if oblique else "_side")+".png"))
                if not oblique and key in ("01_initial","02_folded_stop","04_rear_horizontal"):
                    side_images.append(frame.copy())
        strip=Image.new("RGB", (960*3,752), "white")
        for i,frame in enumerate(side_images):strip.paste(frame,(960*i,0))
        strip.save(OUT/"THREE_STAGES.png")
        frames=[]
        for t in np.linspace(0,1,17):
            front=front0+(rear0+lo-front0)*t
            pose(front,rear0)
            renderer.update_scene(d,camera=camera(),scene_option=option)
            frame=annotated(renderer.render(),"双腿收至限位",front,rear0,None)
            frames.append(frame.resize((768,602)))
        for t in np.linspace(0,1,34):
            alpha=alpha_rear*t
            front,rear=rear0+lo+alpha,rear0+alpha
            pose(front,rear)
            renderer.update_scene(d,camera=camera(),scene_option=option)
            frame=annotated(renderer.render(),"保持限位，双腿整体向后翻折",front,rear,alpha)
            frames.append(frame.resize((768,602)))
        durations=[75]*len(frames)
        durations[0],durations[16],durations[-1]=650,500,1500
        frames[0].save(OUT/"FOLD_THEN_REAR.gif",save_all=True,append_images=frames[1:],
            duration=durations,loop=0,optimize=True)
    report["source_MJCF_unchanged"]=report["source_MJCF_SHA256"]==hashlib.sha256((geometry.ASSET/"mjcf/scene.xml").read_bytes()).hexdigest()
    (OUT/"POSE_RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    pose(STAGES[3][2],STAGES[3][3])
    np.savez_compressed(OUT/"POSES.npz",qpos=np.stack([np.asarray(report["stages"][s[0]]["qpos"]) for s in STAGES]),
                        names=np.asarray([s[0] for s in STAGES]))
    print(json.dumps({k:{f:v[f] for f in ("front1_rad","rear1_rad","relative_angle_rad","common_rearward_rotation_deg","root_height_m","max_closure_error_m","joint_limit_violations","wheel_position_in_base_m","gas_eye_length_m")} for k,v in report["stages"].items()},ensure_ascii=False,indent=2))


def viewer():
    import mujoco.viewer
    visual_style()
    state=dict(index=3, alpha=alpha_rear, changed=True)
    def key(code):
        if ord("1")<=code<=ord("5"):
            state["index"]=code-ord("1")
            state["alpha"]=STAGES[state["index"]][4] or 0.
            state["changed"]=True
        elif code in (262,263):
            state["index"]=-1
            state["alpha"]+=math.radians(5 if code==262 else -5)
            state["changed"]=True
    pose(STAGES[3][2],STAGES[3][3])
    with mujoco.viewer.launch_passive(m,d,key_callback=key) as handle:
        handle.cam.lookat[:]=(-.03,0.,.22)
        handle.cam.distance=1.18
        handle.cam.azimuth=135.
        handle.cam.elevation=-18.
        handle.opt.geomgroup[:]=0
        handle.opt.geomgroup[2]=1
        while handle.is_running():
            if state["changed"]:
                idx=state["index"]
                if idx>=0:front,rear=STAGES[idx][2:4]
                else:rear=rear0+state["alpha"];front=rear+lo
                pose(front,rear)
                state["changed"]=False
            handle.sync()
            time.sleep(.02)


if __name__=="__main__":
    if "--viewer" in sys.argv:viewer()
    else:build()
