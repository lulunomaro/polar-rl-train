"""Matplotlib-only static comparison from already saved actual canonical/own data."""
from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle

HERE=Path(__file__).resolve().parent
D=HERE/"ACTUAL_FUDAN_CONSTRAINED_RETARGET_V2_1793005471832546700"


def main():
    canonical=json.loads((HERE/"ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json").read_text(encoding="utf8"))
    own=json.loads((D/"CONSTRAINED_TASKSPACE_TARGETS.json").read_text(encoding="utf8"))
    drawing=json.loads((D/"STATIC_KINEMATIC_DRAW_DATA.json").read_text(encoding="utf8"))
    height=json.loads((D/"OWN_RECONSTRUCTED_HEIGHT_APPROXIMATION.json").read_text(encoding="utf8"))
    src_t=np.asarray(canonical["time_s"]);sp=np.asarray(canonical["chassis_position_m"]);sw=np.asarray(canonical["wheel_center_m"])
    sb=np.asarray(canonical["wheel_bottom_world_z_m"]);contact=np.asarray(canonical["wheel_contact"],dtype=bool)
    own_t=np.asarray(own["time_s"])+1.;op=np.asarray(own["root_position_m"])
    own_bottom=np.asarray(height["own_kinematic_wheel_bottom_world_z_m"])
    baseline_index=int(np.searchsorted(src_t,1.));source_ground=float(sb[baseline_index].mean())
    own_ground=float(own_bottom[0].mean());colors=("#2667b7","#df8120")
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.spines.top":False,"axes.spines.right":False})
    fig=plt.figure(figsize=(16,9),layout="constrained");gs=fig.add_gridspec(3,2,height_ratios=[1.4,1.25,1.])
    ax_s=fig.add_subplot(gs[0,:]);ax_o=fig.add_subplot(gs[1,:]);ax_h=fig.add_subplot(gs[2,0]);ax_c=fig.add_subplot(gs[2,1])
    frames=drawing["frames"];spacing=.65
    for j,frame in enumerate(frames):
        ts=frame["source_time_s"];i=int(np.argmin(abs(src_t-ts)));origin=j*spacing
        ax_s.plot(origin,sp[i,2]-source_ground,"o",color="#203044",ms=4,zorder=5)
        ax_s.add_patch(Rectangle((origin-.12,sp[i,2]-source_ground-.015),.24,.10,fill=False,lw=1,color="#203044"))
        for k,color in enumerate(colors):
            x=origin+sw[i,k,0]-sp[i,0];z=sw[i,k,2]-source_ground
            ax_s.plot([origin,x],[sp[i,2]-source_ground,z],color=color,lw=1.1,alpha=.8)
            ax_s.add_patch(Circle((x,z),.06,fill=False,color=color,lw=1.1))
            ax_s.plot(x,z-.06,"o" if contact[i,k] else "x",color=color,ms=4)
        ax_s.text(origin,-.12,f"{ts:.2f}s",ha="center",fontsize=9)
        world=frame["body_world_m"];root=np.array(world["chassis"])
        for parent,child in drawing["tree_edges"]:
            if child.startswith("guide_") or "drive_" in child:continue
            a=np.array(world[parent]);b=np.array(world[child]);color=colors[0] if child.startswith("left") else colors[1]
            ax_o.plot([origin+a[0]-root[0],origin+b[0]-root[0]],[a[2]-own_ground,b[2]-own_ground],color=color,lw=.9,alpha=.8)
        ax_o.add_patch(Rectangle((origin-.167,root[2]-own_ground-.144),.334,.154,fill=False,lw=1.1,color="#203044"))
        ax_o.plot(origin,root[2]-own_ground,"o",color="#203044",ms=3)
        for k,wheel in enumerate(("left_wheel","right_wheel")):
            pos=np.array(world[wheel]);ax_o.add_patch(Circle((origin+pos[0]-root[0],pos[2]-own_ground),drawing["own_wheel_radius_m"],fill=False,color=colors[k],lw=1.2))
        ax_o.text(origin,-.12,f"own {frame['own_age_control']/100:.2f}s\nage {frame['own_age_control']:.0f}",ha="center",fontsize=8)
    for ax in (ax_s,ax_o):
        ax.axhline(0,color="#8c98a5",lw=.8);ax.set_xlim(-.35,(len(frames)-1)*spacing+.35);ax.set_ylim(-.19,.92)
        ax.set_xticks([]);ax.set_ylabel("height above initial support (m)");ax.grid(axis="y",alpha=.18)
    ax_s.set_title("FOREIGN RECORDED ROLLOUT  |  original MuJoCo 2 ms; recorded samples ~4 ms; X centered per pose; original surface height removed",loc="left",fontweight="bold")
    ax_o.set_title("OWN STATIC KINEMATIC REFERENCE  |  261 / 261 own closed-chain frames fit; common limb excursion x0.1; no own dynamics or skill success",loc="left",fontweight="bold")
    window=(src_t>=1)&(src_t<=3.6)
    for k,color in enumerate(colors):
        ax_h.plot(src_t[window],sb[window,k]-sb[baseline_index,k],color=color,lw=1,label=f"recorded {'L' if k==0 else 'R'} bottom")
        ax_h.plot(own_t,own_bottom[:,k]-own_bottom[0,k],color=color,lw=1.4,ls="--",label=f"own kinematic {'L' if k==0 else 'R'} bottom")
    ax_h.plot(own_t,op[:,2]-op[0,2],color="#243346",alpha=.65,lw=1,label="own chassis rise")
    ax_h.axvline(1.5,color="#495260",ls=":",lw=1);ax_h.set_xlim(1,3.6);ax_h.set_xlabel("recorded source simulation time (s)")
    ax_h.set_ylabel("height displacement (m)");ax_h.grid(alpha=.2);ax_h.legend(loc="upper right",fontsize=7,ncol=2)
    ax_h.set_title("Wheel path preserved with actual radius scale 0.0637 / 0.06; max mismatch 0.324 mm",loc="left",fontsize=9)
    for k,color in enumerate(colors):
        y=1-k*.5;ax_c.step(src_t[window],contact[window,k]*.32+y,where="post",color=color,lw=1.3,label=f"recorded {'left' if k==0 else 'right'} support")
    ax_c.axvspan(1.5,2.29,color="#e4eef9",alpha=.75,label="own public request age100..179")
    ax_c.axvline(1.5,color="#495260",ls=":",lw=1)
    ax_c.set_xlim(1,3.6);ax_c.set_ylim(.35,1.55);ax_c.set_yticks([.5,1.],labels=["R: low=air / high=support","L: low=air / high=support"])
    ax_c.set_xlabel("source time (s); own time = source time - 0.50 s")
    ax_c.legend(loc="upper right",fontsize=7);ax_c.set_title("Recorded source contact labels; own measured contact is NOT available",loc="left",fontsize=9)
    fig.suptitle("Fudan jump → MOD4 SuperMimic partial reference\nSource onset1.50s maps own age100=1.00s; step270 forward arrival / top contact / stable recovery remain unproven",fontsize=14,fontweight="bold")
    path=D/"ACTUAL_SOURCE_VS_OWN_KINEMATIC_REFERENCE.png"
    if path.exists():raise FileExistsError(path)
    fig.savefig(path,dpi=160,facecolor="white");plt.close(fig)
    report=dict(trial_id="ACTUAL_REFERENCE_STATIC_FIGURE_"+str(time.time_ns()),path=str(path),bytes=path.stat().st_size,
                SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),source="saved actual canonical / own FK coordinates only",
                no_new_npz_policy_model_physics_GPU_GUI_or_renderengine=True,
                foreign_recorded_vs_own_kinematic_labels_explicit=True,git_archive_state="pending_root_stage_archive")
    with (D/"STATIC_KINEMATIC_FIGURE_RECEIPT.json").open("x",encoding="utf8") as stream:json.dump(report,stream,indent=2)
    print(json.dumps(report))


if __name__=="__main__":
    try:main()
    except BaseException:
        with (HERE/("STATIC_FIGURE_ORIGINAL_ERROR_"+str(time.time_ns())+".json")).open("x",encoding="utf8") as stream:json.dump(dict(error=traceback.format_exc(),git_archive_state="pending_root_stage_archive"),stream,indent=2)
        raise
