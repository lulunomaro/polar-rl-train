"""Pose the unchanged MOD4v3 R3 asset at its folded stop, then rotate rearward.

This is a static geometric pose viewer. It never advances dynamics or runs a policy.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import math
import os
import sys
import time

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import brentq

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


def pose(front, rear, *, guide_floor=False):
    d.qpos[:3] = (0., 0., .35)
    d.qpos[3:7] = (1., 0., 0., 0.)
    d.qvel[:] = 0.
    d.ctrl[:] = 0.
    d.xfrc_applied[:] = 0.
    kinematics.set_configuration(m, d, left=(front, rear), right=(front, rear), check_limits=True)
    collision = [i for i in range(m.ngeom) if m.geom_bodyid[i]
                 and (m.geom_contype[i] or m.geom_conaffinity[i])]
    supports = [i for i in collision if (m.geom(i).name or "").startswith("guide_wheel_")] if guide_floor else collision
    bottom = min(geometry.min_z(i) for i in supports)
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
        folded_stop_active=abs(front-rear-lo)<1e-8,
        gas_extension_stop_active=abs(front-rear-hi)<1e-8, both_legs_symmetric=True,
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


# User clarified the desired stop: gas spring fully EXTENDED to 200 mm,
# followed by guide-wheel ground contact and both rear tires on the ground.
# The 14.72-degree visual match and the lower CAD fold stop are superseded.
selected_delta = hi
def rear_tire_gap(alpha):
    rear=rear0+float(alpha)
    pose(rear+selected_delta,rear,guide_floor=True)
    return geometry.min_z(m.geom("left_tire").id)

alpha_rear=brentq(rear_tire_gap,0.,math.pi/2,xtol=1e-13)
rear_selected = rear0+alpha_rear
front_selected = rear_selected+selected_delta
guide_first_alpha=math.radians(75.)
STAGES = [
    ("01_initial", "1  模型原装配姿态", front0, rear0, None),
    ("02_gas200_limit", "2  左右气弹簧均拉至 200 mm 限位", rear0+selected_delta, rear0, 0.),
    ("03_guides_ground", "3  导轮贴地，双轮向后抬起", rear0+selected_delta+guide_first_alpha,rear0+guide_first_alpha,guide_first_alpha),
    ("04_gas200_rear_ground", "4  气弹簧 200 mm · 导轮与后方双轮均贴地", front_selected,rear_selected,alpha_rear),
    ("05_rear_before_contact", "5  贴地前 5°，双轮在后方悬起", front_selected+math.radians(5),rear_selected+math.radians(5),alpha_rear+math.radians(5)),
]


def visual_style():
    m.vis.headlight.ambient[:] = (.35, .35, .35)
    m.vis.headlight.diffuse[:] = (.45, .45, .45)
    m.vis.headlight.specular[:] = (.05, .05, .05)
    m.light_diffuse[:] = .35
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
    cam.lookat[:] = (-.03, 0., .20)
    cam.distance = 1.13 if oblique else 1.07
    cam.azimuth = 135. if oblique else 90.
    cam.elevation = -18. if oblique else -3.
    return cam


def annotated(pixels, title, front, rear, alpha, oblique=False):
    w, h = pixels.shape[1], pixels.shape[0]
    canvas=Image.new("RGB", (w, h+112), "#f7f9fc")
    canvas.paste(Image.fromarray(pixels), (0, 62))
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(FONT, 24)
    small=ImageFont.truetype(FONT, 17)
    draw.text((22, 14), "MOD4v3 R3  ·  "+title, font=font, fill="#10243c")
    delta=front-rear
    status="气弹簧伸长限位 200 mm" if abs(delta-hi)<1e-8 else "原装配角度"
    extra="" if alpha is None else f" | 整体后翻 {math.degrees(alpha):.2f}°"
    draw.text((22,h+74), f"{status} | front1={front:+.6f} rad | rear1={rear:+.6f} rad{extra}",font=small,fill="#21364d")
    if not oblique:
        draw.line((w-170,h+30,w-45,h+30),fill="#275987",width=4)
        draw.polygon(((w-45,h+30),(w-59,h+22),(w-59,h+38)),fill="#275987")
        draw.text((w-190,h-4),"机体前方 +X",font=small,fill="#275987")
    return canvas


def build():
    (OUT/"INITIAL_GEOMETRY_PROBE.txt").write_text(probe_log.getvalue(),encoding="utf-8")
    report=dict(kind="MOD4V3_GAS200_GUIDES_GROUND_AND_REAR_TIRES_GROUND_STATIC_POSE",
        source_asset=str(geometry.ASSET),
        source_MJCF_SHA256=hashlib.sha256((geometry.ASSET/"mjcf/scene.xml").read_bytes()).hexdigest(),
        simulator_version=mujoco.__version__, physics_steps=0, policies_run=0,
        coordinate_basis="MOD4v3 anatomical absolute radians; no zero/reference changes",
        delta_fold_stop_rad=lo,delta_gas_extension_stop_rad=hi,
        selected_common_rotation_deg=math.degrees(alpha_rear),
        user_selected_gas_stop="fully extended 200 mm",
        visual_reference=dict(repository="chushanxiaodaoshi/XYEGA_RM2026_WheelLeg_Infatry_RLdeploy",
            commit="fcfdd3959be5c9b00893ec0701a591ddbf55b830", image="pseudocode/example1.png",
            criterion="Fudan-style chassis/guide support plus both wheels resting rearward; user requires 200 mm full-extension stop",
            thigh_angle_is_solved_not_prescribed=True,
            not_copied=["Fudan dimensions", "encoder offsets", "joint coordinates", "physical stops"]),
        pose_method="Both gas springs at 200 mm extension stop; horizontal chassis at guide-floor height; solve rear common rotation for tire-floor contact",
        rendered_colors="Left moving leg blue; right moving leg orange; render appearance only",
        stages={})
    visual_style()
    option=mujoco.MjvOption()
    option.geomgroup[:]=0
    option.geomgroup[0]=1
    option.geomgroup[2]=1
    with mujoco.Renderer(m,height=640,width=960) as renderer:
        side_images=[]
        for key,title,front,rear,alpha in STAGES:
            report["stages"][key]=measurements(front,rear,alpha or 0.)
            for oblique in (False,True):
                renderer.update_scene(d,camera=camera(oblique),scene_option=option)
                raw=renderer.render()
                frame=annotated(raw,title,front,rear,alpha,oblique=oblique)
                frame.save(OUT/(key+("_oblique" if oblique else "_side")+".png"))
                if not oblique and key in ("02_gas200_limit","03_guides_ground","04_gas200_rear_ground"):
                    side_images.append(frame.copy())
        strip=Image.new("RGB", (960*3,752), "white")
        for i,frame in enumerate(side_images):strip.paste(frame,(960*i,0))
        strip.save(OUT/"THREE_STAGES.png")
        frames=[]
        for t in np.linspace(0,1,17):
            front=front0+(rear0+selected_delta-front0)*t
            pose(front,rear0)
            renderer.update_scene(d,camera=camera(),scene_option=option)
            frame=annotated(renderer.render(),"先将两侧气弹簧拉至 200 mm",front,rear0,None)
            frames.append(frame.resize((768,602)))
        for alpha in np.concatenate((np.linspace(0,guide_first_alpha,20),np.linspace(guide_first_alpha,alpha_rear,22))):
            front,rear=rear0+selected_delta+alpha,rear0+alpha
            pose(front,rear)
            renderer.update_scene(d,camera=camera(),scene_option=option)
            frame=annotated(renderer.render(),"保持 200 mm，导轮落地后再让后方双轮落地",front,rear,alpha)
            frames.append(frame.resize((768,602)))
        durations=[75]*len(frames)
        durations[0],durations[16],durations[-1]=650,500,1500
        frames[0].save(OUT/"FOLD_THEN_REAR.gif",save_all=True,append_images=frames[1:],
            duration=durations,loop=0,optimize=True)
    report["source_MJCF_unchanged"]=report["source_MJCF_SHA256"]==hashlib.sha256((geometry.ASSET/"mjcf/scene.xml").read_bytes()).hexdigest()
    (OUT/"POSE_RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    pose(STAGES[3][2],STAGES[3][3])
    selected=report["stages"][STAGES[3][0]]
    selected["wheel_floor_clearance_m"]={side:geometry.min_z(m.geom(side+"_tire").id)
                                           for side in ("left","right")}
    selected["guide_floor_clearance_m"]={m.geom(i).name:geometry.min_z(i)
        for i in range(m.ngeom) if (m.geom(i).name or "").startswith("guide_wheel_")}
    selected["thigh_inclination_deg"]={}
    for side in ("left","right"):
        thigh=d.xpos[m.body(side+"_rear2_link").id]-d.xpos[m.body(side+"_rear1_link").id]
        selected["thigh_inclination_deg"][side]=math.degrees(math.atan2(float(thigh[2]),-float(thigh[0])))
    report["selected_stage"]=STAGES[3][0]
    assert all(abs(v-.2)<1e-7 for v in selected["gas_eye_length_m"].values())
    assert all(abs(v)<1e-7 for v in selected["wheel_floor_clearance_m"].values())
    assert abs(min(selected["guide_floor_clearance_m"].values()))<1e-7
    assert all(v[0]<0 for v in selected["wheel_position_in_base_m"].values())
    (OUT/"POSE_RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
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
        handle.cam.lookat[:]=(-.03,0.,.20)
        handle.cam.distance=1.13
        handle.cam.azimuth=135.
        handle.cam.elevation=-18.
        handle.opt.geomgroup[:]=0
        handle.opt.geomgroup[0]=1
        handle.opt.geomgroup[2]=1
        (OUT/"VIEWER_READY.json").write_text(json.dumps(dict(pid=os.getpid(),ready=bool(handle.is_running()),
            source_asset=str(geometry.ASSET),selected_stage=STAGES[3][0],
            front1_rad=STAGES[3][2],rear1_rad=STAGES[3][3],
            keys="1 assembly; 2 gas200; 3 guides on ground/rear wheels raised; 4 guides and rear tires on ground; 5 rear wheels before contact; arrows +/-5deg; mouse rotates"),
            ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        while handle.is_running():
            if state["changed"]:
                idx=state["index"]
                if idx>=0:front,rear=STAGES[idx][2:4]
                else:rear=rear0+state["alpha"];front=rear+selected_delta
                pose(front,rear)
                state["changed"]=False
            handle.sync()
            time.sleep(.02)


if __name__=="__main__":
    if "--viewer" in sys.argv:viewer()
    else:build()
