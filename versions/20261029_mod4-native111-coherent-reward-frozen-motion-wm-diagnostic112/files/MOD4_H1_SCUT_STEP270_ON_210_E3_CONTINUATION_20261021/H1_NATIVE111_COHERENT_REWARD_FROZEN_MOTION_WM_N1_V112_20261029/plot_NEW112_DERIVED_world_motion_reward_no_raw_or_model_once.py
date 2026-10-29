from pathlib import Path
import json,os
os.environ["CUDA_VISIBLE_DEVICES"]=""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
S=Path(__file__).resolve().parent
d=json.loads((S/"reports/NEW112_DERIVED_CONTROL_CURVES_FOR_PLOT_ONLY.json").read_bytes())["rows"]
def sc(v):
 while isinstance(v,list) and len(v)==1:v=v[0]
 return float(v)
t=[x["time_s"] for x in d]
fig,axes=plt.subplots(4,1,figsize=(12,10),sharex=True)
axes[0].plot(t,[x["root_x"] for x in d],color="#1768ac",label="Actual root X")
axes[0].axhline(.35,color="#da7b24",ls="--",label="Step edge 0.35 m")
axes[0].axhline(.75,color="#a42e32",ls=":",label="Root goal 0.75 m")
axes[0].set_ylabel("World X (m)")
axes[1].plot(t,[x["world_velocity3"][0] for x in d],color="#1768ac",lw=.7,label="Actual world Vx")
axes[1].plot(t,[.5 if x["request_for_action"] else 0 for x in d],color="#a42e32",ls="--",label="Requested world Vx")
axes[1].set_ylabel("World speed (m/s)")
axes[2].plot(t,[1000*min(x["wheel_bottom2"]) for x in d],color="#1768ac",lw=.7,label="Both-wheel minimum, control endpoints")
axes[2].axhline(5,color="#da7b24",ls="--",label="5 mm diagnostic threshold")
axes[2].set_ylabel("Wheel clearance (mm)")
axes[2].set_title("400 Hz simultaneous physical peak: 11.882 mm; task requires actual 270 mm crossing and stable platform landing",fontsize=9,loc="left")
terms=[x["actual_task_reward_objective"] for x in d]
axes[3].plot(t,[sc(x["total"]) for x in terms],lw=.8,label="Total task reward")
axes[3].plot(t,[sc(x["mode_advantage"])*sc(x["contact_step_modes"]["jump"]) for x in terms],lw=.7,label="Weighted jump-specific advantage")
axes[3].plot(t,[sc(x["task_alignment"]) for x in terms],lw=.7,label="Heading/lateral alignment")
axes[3].set_ylabel("Reward / control")
axes[3].set_xlabel("Physical episode time (s)")
for ax in axes:
 ax.axvspan(0,2,color="#d7dce4",alpha=.35)
 ax.grid(alpha=.2);ax.legend(loc="upper right",fontsize=8);ax.set_xlim(0,20)
fig.suptitle("NEW112: frozen qualified111 mean policy, one fixed 20 s own-plant case\nNo learning; 2,000 controls / 8,000 callbacks; original timeout only",fontsize=13)
fig.tight_layout(rect=(0,0,1,.95))
path=S/"NEW112_ACTUAL20S_WORLD_MOTION_AND_REWARD_ALLOCATION.png"
fig.savefig(path,dpi=160);plt.close(fig)
print(json.dumps({"plot":str(path),"bytes":path.stat().st_size,"source":"derived NEW112 curves only; no raw or model reread"}))

