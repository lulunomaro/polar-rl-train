"""Offline audit of existing MATLAB and Isaac traces; no simulation or training."""
from pathlib import Path
import hashlib
import json
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.io import loadmat
import numpy as np

D = Path(__file__).resolve().parent
W = D.parent.parent
M = W / 'MOD4_MATLAB_DIRECTIONAL_SPIN_20261005'
H = D.parent / 'health_20261005_2000'
sys.path.insert(0, str(D))
from world_cycle_metrics import measure_world_cycles


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def bounds(t, heading, sign):
    phase = sign * (np.unwrap(heading) - heading[0])
    out = [t[0]]
    for level in np.arange(2 * math.pi, phase.max() + 1e-10, 2 * math.pi):
        i = np.flatnonzero((phase[:-1] < level) & (phase[1:] >= level))[0]
        f = (level - phase[i]) / (phase[i+1] - phase[i])
        out.append(t[i] + f * (t[i+1] - t[i]))
    return np.array(out)


raw = json.loads((H / 'auto_0218_world_world_cap12.5664_white_v2.json').read_text())
trace = D / 'auto_0218_world_world_cap12.5664_white_v2.npz'
assert sha(trace) == raw['whole_trace']['sha256']
a = np.load(trace)
t = np.arange(len(a['root_xy'])) * .01
assert raw['seconds'] == 15 and sum(raw['alive']) == 88
metrics = []
for r in raw['world_cycle_metrics']:
    i = r['env_id']
    xy = a['root_xy'][:, i].astype(float)
    heading = a['heading'][:, i].astype(float)
    sign = 1 if r['command_yaw_rad_s'] > 0 else -1
    m = measure_world_cycles(t, xy, heading, r['world_direction_rad'], sign)
    for key in ('complete_prefix_along_m_s', 'complete_prefix_cross_m_s',
                'whole_prefix_along_m_s', 'whole_prefix_cross_m_s'):
        assert abs(m[key] - r[key]) < 1e-9, (i, key)
    theta = r['world_direction_rad']
    cross = (xy - xy[0]) @ np.array([-math.sin(theta), math.cos(theta)])
    b = bounds(t, heading, sign)
    spans = []
    for start, end in zip(b[:-1], b[1:]):
        use = (t > start) & (t < end)
        tt = np.r_[start, t[use], end]
        cc = np.interp(tt, t, cross)
        drift_line = np.interp(tt, [start, end], cc[[0, -1]])
        spans.append(float(np.ptp(cc - drift_line)))
    remaining = m['cycles'][1:]
    dur = sum(x['duration_s'] for x in remaining)
    rest_cross = sum(x['cross_drift_m_s'] * x['duration_s'] for x in remaining) / dur
    observed_yaw = raw['per_environment']['yaw_rate'][i]
    failures = []
    if abs(m['complete_prefix_along_m_s'] - .5) > .05: failures.append('net_along')
    if abs(m['complete_prefix_cross_m_s']) > .05: failures.append('net_cross')
    if abs(observed_yaw - r['command_yaw_rad_s']) > .2: failures.append('yaw')
    metrics.append(dict(env_id=i, group_id=r['group_id'], yaw=r['command_yaw_rad_s'],
                        **m, detrended_complete_cycle_cross_spans_m=spans,
                        excluding_first_cycle_net_cross_m_s=rest_cross,
                        observed_yaw_rad_s=observed_yaw, factual_failures=failures))

# Verify that the active metric accepts curved ideal motion at all 72 MATLAB
# kinematic conditions; each trajectory contains lateral oscillation.
mr = json.loads((M / 'RESULTS.json').read_text())
ideal_check = []
for q in mr['ideal']:
    v, omega = q['target_m_s'], q['yaw_rad_s']
    alpha, p0 = q['world_direction_rad'], q['initial_relative_heading_rad']
    phase = p0 + omega * t
    along = v*t + v/(2*omega)*(np.sin(2*phase)-math.sin(2*p0))
    cross = v/(2*omega)*(math.cos(2*p0)-np.cos(2*phase))
    xy = np.c_[along*math.cos(alpha)-cross*math.sin(alpha),
               along*math.sin(alpha)+cross*math.cos(alpha)]
    m = measure_world_cycles(t, xy, phase+alpha, alpha, 1 if omega > 0 else -1)
    tol = max(.03, .1*v)
    passed = (abs(m['complete_prefix_along_m_s']-v) <= tol
              and abs(m['complete_prefix_cross_m_s']) <= tol)
    assert passed
    ideal_check.append(dict(v=v, yaw=omega, direction=alpha, phase0=p0, passed=passed))

# Constant BODY forward speed is the closed-circle negative control.
circle = np.c_[.25*np.sin(2*t), .25*(1-np.cos(2*t))]
neg = measure_world_cycles(t, circle, 2*t, 0., 1)
assert abs(neg['complete_prefix_along_m_s']) < 1e-5

mat = loadmat(M / 'TRAJECTORIES.mat', simplify_cells=True)
matlab = {}
for name in ('demo', 'stress_demo', 'corrected_demo'):
    tr = mat[name]
    use = tr['t'] <= 15
    z = tr['z'][use]
    mm = measure_world_cycles(tr['t'][use], z[:, :2], z[:, 2], 0., 1)
    matlab[name] = dict(**mm, observed_yaw_rad_s=float(np.mean(z[1:, 4])),
                       heading0_rad=float(z[0, 2]),
                       progress_fact_pass=bool(abs(mm['complete_prefix_along_m_s']-.5) <= .05
                                               and abs(mm['complete_prefix_cross_m_s']) <= .05
                                               and abs(float(np.mean(z[1:,4]))-2) <= .2))

groups = []
for gid in range(3, 11):
    rows = [r for r in metrics if r['group_id'] == gid]
    groups.append(dict(group_id=gid, yaw=rows[0]['yaw'], n=len(rows),
        fact_pass=sum(not r['factual_failures'] for r in rows),
        net_along_range=[min(r['complete_prefix_along_m_s'] for r in rows), max(r['complete_prefix_along_m_s'] for r in rows)],
        net_cross_range=[min(r['complete_prefix_cross_m_s'] for r in rows), max(r['complete_prefix_cross_m_s'] for r in rows)],
        excluding_first_cycle_abs_cross_range=[min(abs(r['excluding_first_cycle_net_cross_m_s']) for r in rows), max(abs(r['excluding_first_cycle_net_cross_m_s']) for r in rows)],
        detrended_cycle_span_range=[min(s for r in rows for s in r['detrended_complete_cycle_cross_spans_m']),max(s for r in rows for s in r['detrended_complete_cycle_cross_spans_m'])]))

out = dict(scope='Offline existing-trajectory audit; no new PhysX/MATLAB simulation, PPO, gate or budget mutation.',
    policy='model22589', policy_sha256='f5eb9905638c551d037bdc9621b929275e933973d38d74c0c082f4f6ed02a2b2',
    active_goal=.5, net_tolerance_m_s=.05, yaw_tolerance_rad_s=.2,
    final_fact_requires_all_sampled_moving_environments=True,
    learning_veto=False, periodic_motion_not_vetoed=True,
    actual_trace_metrics_reproduced=64, ideal_curved_cases_passed=len(ideal_check),
    constant_body_circle_rejected_as_zero_net_progress=True,
    actual_fact_pass=sum(not r['factual_failures'] for r in metrics), groups=groups,
    per_environment=metrics, matlab_saved_plus2_traces_same15s=matlab,
    matlab_initial_heading_differs_from_actual=True,
    matlab_model_balancing_and_contact_assumed=True,
    corrected_matlab_feedback_not_installed_in_actual=True,
    evidence_sha256={str(p.resolve()):sha(p) for p in [trace,H/'auto_0218_world_world_cap12.5664_white_v2.json',
        M/'RESULTS.json',M/'TRAJECTORIES.mat',D/'world_progress_contract.py',D/'world_cycle_metrics.py']})
(D/'COMPARISON.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False,
                     'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
xy = a['root_xy'][:,5].astype(float);xy-=xy[0]
p0=float(a['heading'][0,5]);omega=2.;v=.5;phase=p0+omega*t
ideal_along=v*t+v/(2*omega)*(np.sin(2*phase)-math.sin(2*p0))
ideal_cross=v/(2*omega)*(math.cos(2*p0)-np.cos(2*phase))
demo=mat['demo'];use=demo['t']<=15
ax=axes[0,0]
ax.plot(ideal_along,ideal_cross,label='理想运动学（同初始朝向）',color='#788b9a',lw=1.8)
ax.plot(demo['along'][use],demo['cross'][use],label='MATLAB 名义动力学（初相位不同）',color='#229c87',lw=1.7)
ax.plot(xy[:,0],xy[:,1],label='实际 PPO +2rad/s，固定 env5',color='#d76d30',lw=2)
for sec in (0,3,6,9,12):
    idx=int(sec/.01);h=a['heading'][idx,5]
    ax.arrow(xy[idx,0],xy[idx,1],.15*np.cos(h),.15*np.sin(h),head_width=.045,color='#d76d30',length_includes_head=True)
ax.set(xlabel='目标方向位移 (m)',ylabel='横向位移 (m)',title='车身持续自转，中心沿摆动曲线推进；箭头为车身朝向')
ax.set_aspect('equal',adjustable='datalim');ax.legend(fontsize=8,loc='upper left');ax.grid(alpha=.2)
ax=axes[0,1]
ax.plot(t,ideal_cross,label='理想：周期摆动',color='#788b9a')
ax.plot(demo['t'][use],demo['cross'][use],label='MATLAB 名义',color='#229c87')
ax.plot(t,xy[:,1],label='实际 +2（env5）',color='#d76d30')
xy6=a['root_xy'][:,6].astype(float);xy6-=xy6[0]
ax.plot(t,xy6[:,1],label='实际 -2（env6）',color='#7772b8')
ax.set(xlabel='时间 (s)',ylabel='横向位移 (m)',title='当前偏差：摆动之上叠加了持续偏移');ax.grid(alpha=.2);ax.legend(fontsize=8)
ax=axes[1,0]
for r in metrics:
    if abs(r['yaw'])==2:
        cc=[q['cross_drift_m_s'] for q in r['cycles']]
        ax.plot(np.arange(1,len(cc)+1),cc,color='#d76d30' if r['yaw']>0 else '#7772b8',alpha=.35,lw=1)
ax.axhspan(-.05,.05,color='#229c87',alpha=.10)
ax.axhline(.05,color='#229c87',ls='--');ax.axhline(-.05,color='#229c87',ls='--')
ax.set(xlabel='实际完整自转圈编号（全部保留）',ylabel='每圈净横向速度 (m/s)',title='48个 ±2 样本：启动圈之后仍有净漂移')
ax.set_xticks([1,2,3,4]);ax.grid(alpha=.2)
ax=axes[1,1]
for yaw,color in [(1.,'#229c87'),(-1.,'#45bbaa'),(2.,'#d76d30'),(-2.,'#7772b8')]:
    rr=[r for r in metrics if r['yaw']==yaw]
    ax.scatter([r['complete_prefix_along_m_s'] for r in rr], [r['complete_prefix_cross_m_s'] for r in rr],s=24,label=f'{yaw:+g}rad/s',c=color,alpha=.85)
ax.add_patch(Rectangle((.45,-.05),.10,.10,fill=False,edgecolor='#229c87',lw=1.8,ls='--'))
ax.set(xlabel='完整圈净前进速度 (m/s)',ylabel='完整圈净横向速度 (m/s)',title='64个样本；虚线框为自定最终方向精度目标')
ax.set_xlim(.445,.555);ax.set_ylim(-.11,.11);ax.legend(fontsize=8);ax.grid(alpha=.2)
fig.suptitle('V=0.5m/s：允许转圈摆动，完整圈后的净偏移另行统计',fontsize=14)
fig.savefig(D/'MATLAB_VS_PPO.png',dpi=155)
plt.close(fig)
print(json.dumps(dict(ideal_cases=72,actual_metrics=64,actual_fact_pass=out['actual_fact_pass'],groups=groups,matlab_same15s=matlab),ensure_ascii=False,indent=2))
