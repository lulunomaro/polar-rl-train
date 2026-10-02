"""Fig C: measured skill ladders (run / gyro / jump). Fig D: training curves v3/v4/v5."""
import glob, json, os, re
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
DOCS = r"D:/claude2/fangzhen/docs/crops"; TR = r"D:/claude2/fangzhen/train"

# ---------------------------------------------------------------- C
fig, axs = plt.subplots(1, 3, figsize=(16.5, 5.0))
try:
    v4 = json.load(open(r"D:/claude2/fangzhen/train/deploy/skills_v4_1600.json", encoding="utf-8"))
    v3 = json.load(open(r"D:/claude2/fangzhen/train/deploy/skills_probe_v3.json", encoding="utf-8"))
    for tag, key, xs, ys, lbl in (("v3 flat-only", "run", [r["cmd"] for r in v3["run"]], [r["achieved"] for r in v3["run"]], "open-chain-trained"),
                                  ("v4 skills", "run", [r["cmd"] for r in v4["run"]], [r["achieved"] for r in v4["run"]], "skills-trained")):
        pass
    ax = axs[0]
    ax.plot([r["cmd"] for r in v3["run"]], [r["achieved"] for r in v3["run"]], "o--", label="v3 平地模型", color="0.5")
    ax.plot([r["cmd"] for r in v4["run"]], [r["achieved"] for r in v4["run"]], "s-", label="v4 技能模型", color="tab:blue", lw=2)
    lim = np.linspace(0, 3, 10); ax.plot(lim, lim, ":", color="k", alpha=.5, label="理想 y=x")
    ax.axhline(2.0, color="tab:red", ls=":", alpha=.8); ax.text(0.05, 2.05, "实战速度 2.0 m/s", color="tab:red", fontsize=9)
    ax.set_xlabel("command vx [m/s]"); ax.set_ylabel("measured vx [m/s]")
    ax.set_title("跑 / run：指令-实测速度阶梯"); ax.legend(fontsize=9); ax.grid(alpha=.25)
    ax = axs[1]
    ax.plot([g["cmd"] for g in v3["gyro"]], [g["achieved"] for g in v3["gyro"]], "o--", label="v3 平地模型", color="0.5")
    ax.plot([g["cmd"] for g in v4["gyro"]], [g["achieved"] for g in v4["gyro"]], "s-", label="v4 技能模型", color="tab:green", lw=2)
    ax.plot(lim, lim, ":", color="k", alpha=.5)
    ax.set_xlabel("command yaw-rate [rad/s]"); ax.set_ylabel("measured yaw-rate [rad/s]")
    ax.set_title("小陀螺 / gyro spin：转速阶梯"); ax.legend(fontsize=9); ax.grid(alpha=.25)
    ax = axs[2]
    ax.bar([j["target"] for j in v3["jump"]], [100 * j["peak"] for j in v3["jump"]], width=.016,
           color="0.6", label="v3 平地模型")
    ax.bar(np.add([j["target"] for j in v4["jump"]], 0.017), [100 * j["peak"] for j in v4["jump"]],
           width=.016, color="tab:orange", label="v4 技能模型")
    ax.plot([0.04, 0.10], [4, 10], "k:", alpha=.6, label="指令目标")
    ax.set_xlabel("commanded rise [m]"); ax.set_ylabel("peak body rise [cm]")
    ax.set_title("跳 / jump：实测抬升（v5 正在地图上训练）"); ax.legend(fontsize=9); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(os.path.join(DOCS, "fig_C_skills.png"), dpi=105); plt.close(fig)
    print("wrote fig_C_skills.png")
except Exception as e:
    print("fig C skipped:", e)

# ---------------------------------------------------------------- D
def curves(exp):
    it, rw, ep = [], [], []
    log = {"rm_cc_v3": r"D:/claude2/fangzhen/docs/_cc_v3.log",
           "rm_cc_v4": r"D:/claude2/fangzhen/docs/_cc_v4.log",
           "rm_cc_v5": r"D:/claude2/fangzhen/docs/_cc_v5.log"}
    out = {}
    for k, f in log.items():
        if not os.path.exists(f): continue
        try:
            t = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        i = [int(m.group(1)) for m in re.finditer(r"Learning iteration (\d+)", t)]
        r = [float(m.group(1)) for m in re.finditer(r"Mean reward: ([\d.]+)", t)]
        e = [float(m.group(1)) for m in re.finditer(r"Mean episode length: ([\d.]+)", t)]
        n = min(len(i), len(r), len(e))
        if n: out[k] = (i[:n], r[:n], e[:n])
    return out
c = curves(None)
fig, axs = plt.subplots(1, 2, figsize=(13.5, 4.6))
col = {"rm_cc_v3": "0.55", "rm_cc_v4": "tab:blue", "rm_cc_v5": "tab:red"}
lbl = {"rm_cc_v3": "v3 闭链·平地", "rm_cc_v4": "v4 闭链·技能(跑/跳/陀螺)", "rm_cc_v5": "v5 闭链·2026 7v7 地图"}
for k, (i, r, e) in c.items():
    axs[0].plot(i, r, lw=1.8, color=col[k], label=lbl[k])
    axs[1].plot(i, e, lw=1.8, color=col[k], label=lbl[k])
axs[0].set_xlabel("iteration"); axs[0].set_ylabel("mean episode reward")
axs[0].set_title("训练曲线：平均回报"); axs[0].legend(fontsize=9); axs[0].grid(alpha=.25)
axs[1].set_xlabel("iteration"); axs[1].set_ylabel("mean episode length (max 1000)")
axs[1].set_title("存活时长（1000 = 整集不摔）"); axs[1].legend(fontsize=9); axs[1].grid(alpha=.25)
fig.tight_layout(); fig.savefig(os.path.join(DOCS, "fig_D_training.png"), dpi=105); plt.close(fig)
print("wrote fig_D_training.png; runs:", {k: len(v[0]) for k, v in c.items()})
