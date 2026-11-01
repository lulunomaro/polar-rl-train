"""Read-only MOD4 rescue terminal. Follows the supervisor's current run."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from tui_rich import LogMonitor, sparkline

ROOT = Path(__file__).resolve().parents[2]
OLD_LOG = Path('/home/egde/fangzhen_linux/runs4090/logs/flat_v7_4090_20k_scut_warm1850.out.log')


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def selected_log(state):
    stage=state.get('stage','')
    if stage.startswith('bench_'):
        path=ROOT/(stage+'.log')
        if path.exists():return path
    if stage!='training' and state.get('evaluation_pid') and state.get('evaluation_path'):
        path=Path(state['evaluation_path']).with_suffix('.log')
        if path.exists():return path
    active = state.get("active_log")
    if active and Path(active).exists():
        return Path(active)
    if state.get('stage') in ('training', 'checkpoint_handover', 'final_evaluation', 'finished', 'attention_required'):
        attempt = int(state.get('attempt') or 0)
        path = ROOT / f'train_{attempt}.log'
        if path.exists():
            return path
    return ROOT / 'train_0.log'



def _dbar(frac, width=14, color=(0, 229, 255)):
    try:
        frac = float(frac)
    except Exception:
        frac = 0.0
    if frac != frac:
        frac = 0.0
    frac = max(0.0, min(1.0, frac))
    n = int(round(frac * width))
    t = Text()
    t.append("━" * n, style="rgb(%d,%d,%d)" % color)
    t.append("─" * (width - n), style="rgb(55,60,70)")
    return t


def _dstatus(ok, warn=False):
    if ok:
        return Text("OK", style="bold green")
    if warn:
        return Text("~", style="bold yellow")
    return Text("!", style="bold red")


def _dtable(rows):
    t = Table.grid(padding=(0, 1), expand=True)
    t.add_column(width=12, no_wrap=True)
    t.add_column(width=10, justify="right", no_wrap=True)
    t.add_column(width=14, no_wrap=True)
    t.add_column(width=3, no_wrap=True)
    t.add_column(width=12, no_wrap=True)
    t.add_column(no_wrap=True)
    for row in rows:
        if row is None:
            t.add_row(Text(""), Text(""), Text(""), Text(""), Text(""), Text(""))
            continue
        label, value, bar, status, trend, note = row
        t.add_row(Text(label, style="dim"), value, bar, status, trend, Text(note, style="dim"))
    return t


def dashboard_header(state, data):
    last = data.get("last") or {}
    ck = state.get("latest_checkpoint") or (state.get("handover_checkpoint") or {}).get("path") or ""
    run_name = Path(ck).parent.name if ck else "-"
    iteration = data.get("iteration") or state.get("iteration") or 0
    speed = state.get("speed_limit_m_s", 1.5)
    deadline = state.get("deadline_epoch") or 0
    ledger=read_json(state.get('canonical_budget') or ROOT/'TRAINING_BUDGET_10H.json')
    active=ledger.get('active_segment') or {}
    pending=max(0.,time.time()-active['accounted_through_epoch']) if active else 0.
    left=max(0.,float(ledger.get('remaining_training_seconds',0))-pending)
    budget = float(state.get("budget_seconds") or 36000)
    progress = max(0.0, min(1.0, (budget - left) / budget)) if budget else 0.0
    fps = (data.get("series") or {}).get("fps") or [0]
    per = data.get("per_iter") or 0

    l1 = Text()
    l1.append(" MOD4 ", style="bold black on bright_cyan")
    l1.append(" 华南虎平地 · 轻度DR准备/试训 ", style="bold white on rgb(28,72,112)")
    l1.append("  " + run_name, style="bold white")
    l1.append("   ")
    stale = data.get("stale_s")
    has_iteration = bool((data.get("series") or {}).get("fps"))
    stage = state.get("stage", "waiting")
    if stage == "finished":
        badge, color = "已结束", "bold yellow"
    elif stage == "attention_required":
        badge, color = "需排查", "bold red"
    elif not has_iteration and stage in ("training", "ppo_preflight", "validating_native_plane"):
        badge, color = "加载场景 / 等待首轮", "bold yellow"
    else:
        live = stale is not None and stale < 120
        badge, color = ("● LIVE", "bold green") if live else ("日志待更新", "bold yellow")
    l1.append(badge, style=color)
    l1.append("   ["+state.get("stage","waiting")+"]",style="yellow")
    l1.append("   " + time.strftime("%H:%M:%S"), style="dim")

    l2 = Text(" 迭代 ")
    l2.append(str(iteration), style="bold white")
    l2.append("   限速 ±%.2f m/s   " % (speed or 0), style="bold green")
    l2.append(str(state.get("num_envs",20000))+"×"+str(state.get("steps_per_env",24)),style="cyan")
    l2.append("   最新 " + (Path(ck).name if ck else "--"), style="dim")

    l3 = Text(" 预算剩余 ")
    l3.append("%.2f h" % (left / 3600.0), style="bold cyan")
    l3.append("   步速 %s 步/s" % format((fps or [0])[-1], ",.0f"), style="bold green")
    l3.append("   每轮 %.1fs" % per, style="bold white")
    start_iteration=(state.get('resume_checkpoint') or {}).get('iteration_stored')
    if start_iteration is not None and state.get('stage')=='training' and has_iteration:
        segment_steps=max(0,iteration-start_iteration+1)*int(state.get("num_envs",20000))*int(state.get("steps_per_env",24))
        l3.append("   本段采样≈%.1fM策略步" % (segment_steps/1e6),style='bold magenta')
    else:
        l3.append("   交接/测速权重不计生产进步",style='yellow')

    l4 = Text(" ")
    l4.append_text(_dbar(progress, 60, (0, 229, 255)))
    l4.append(" %5.1f%%" % (100 * progress), style="bold yellow")
    return Panel(Group(l1, l2, l3, l4), box=box.ROUNDED, border_style="bright_cyan", padding=(0, 1))


def dashboard_body(data):
    last = data.get("last") or {}
    series = data.get("series") or {}

    def g(k, default=0.0):
        try:
            return float(last.get(k, default) or 0.0)
        except Exception:
            return default

    def mini(key, color=(0, 229, 255)):
        return sparkline(series.get(key) or [], 12, color)

    success = g("success")
    err_v = g("err_v")
    err_w = g("err_w")
    hsum = g("height_r") + g("height_tight") + g("height_both")
    ep_len = g("ep_len")
    std = g("std")
    left = [
        ("速度成功率", Text("%.1f%%" % (100 * success), style="bold green"),
         _dbar(success, 14, (0, 255, 133)), _dstatus(success >= .9, success >= .5),
         mini("success", (0, 255, 133)), "≥90%"), None,
        ("线速度误差", Text("%.3f" % err_v, style="bold cyan"),
         _dbar(max(0.0, 1.0 - err_v / .5), 14, (0, 180, 255)), _dstatus(err_v <= .25, err_v <= .5),
         mini("err_v", (0, 180, 255)), "≤.25"), None,
        ("角速度误差", Text("%.3f" % err_w, style="bold cyan"),
         _dbar(max(0.0, 1.0 - err_w / .5), 14, (0, 180, 255)), _dstatus(err_w <= .5, err_w <= 1.0),
         mini("err_w", (0, 180, 255)), "≤.5"), None,
        ("线速度跟踪", Text("%.3f" % g("track_v"), style="bold green"),
         _dbar(g("track_v"), 14, (0, 255, 133)), Text("↑", style="bold green"),
         mini("track_v", (0, 255, 133)), "越高越好"), None,
        ("高度总奖励", Text("%.3f" % hsum, style="bold yellow"),
         _dbar(hsum, 14, (255, 214, 0)), _dstatus(hsum >= .75, hsum >= .5),
         mini("height_r", (255, 214, 0)), "≥.75"), None,
        ("高度紧奖励", Text("%.3f" % g("height_tight"), style="bold yellow"),
         _dbar(g("height_tight") / .5, 14, (255, 214, 0)), Text("·", style="dim"),
         mini("height_tight", (255, 214, 0)), "趋势项"), None,
        ("双轮高度", Text("%.3f" % g("height_both"), style="bold yellow"),
         _dbar(g("height_both") / .3, 14, (255, 214, 0)), Text("·", style="dim"),
         mini("height_both", (255, 214, 0)), "5ms均力门控"), None,
        ("回合长度", Text("%d" % ep_len, style="bold cyan"),
         _dbar(ep_len / 2000.0, 14, (0, 229, 255)), _dstatus(ep_len >= 1600, ep_len >= 800),
         mini("ep_len", (0, 229, 255)), "≥1000"),
    ]
    right = [
        ("平均奖励", Text("%.2f" % g("reward"), style="bold green"),
         _dbar(g("reward") / 80.0, 14, (0, 255, 133)), Text("↑", style="bold green"),
         mini("reward", (0, 255, 133)), "趋势"), None,
        ("姿态 y", Text("%+.4f" % g("orient_r"), style="bold magenta"),
         _dbar(abs(g("orient_r")) / .02, 14, (255, 120, 180)), Text("·", style="dim"),
         mini("orient_r", (255, 120, 180)), "→0"), None,
        ("动作变化", Text("%+.4f" % g("action_rate"), style="bold magenta"),
         _dbar(abs(g("action_rate")) / .02, 14, (255, 120, 180)), Text("·", style="dim"),
         mini("action_rate", (255, 120, 180)), "→0"), None,
        ("动作加速度", Text("%+.4f" % g("action_acc"), style="bold magenta"),
         _dbar(abs(g("action_acc")) / .1, 14, (255, 120, 180)), Text("·", style="dim"),
         mini("action_acc", (255, 120, 180)), "→0"), None,
        ("力矩", Text("%+.4f" % g("torques"), style="bold magenta"),
         _dbar(abs(g("torques")) / .02, 14, (255, 120, 180)), Text("·", style="dim"),
         mini("torques", (255, 120, 180)), "→0"), None,
        ("关节功率", Text("%+.4f" % g("joint_power"), style="bold magenta"),
         _dbar(abs(g("joint_power")) / .01, 14, (255, 120, 180)), Text("·", style="dim"),
         mini("joint_power", (255, 120, 180)), "→0"), None,
        ("动作 std", Text("%.3f" % std, style="bold magenta"),
         _dbar((std - .10) / .30, 14, (255, 120, 180)), _dstatus(.15 <= std <= .35, std > .08),
         mini("std", (255, 120, 180)), ".15-.35"), None,
        ("超时率", Text("%.1f%%" % (100 * g("term_timeout")), style="bold green"),
         _dbar(g("term_timeout"), 14, (120, 200, 120)), _dstatus(g("term_timeout") >= .6, g("term_timeout") >= .3),
         mini("term_timeout", (120, 200, 120)), "越高越满"), None,
        ("姿态崩", Text("%.2f%%" % (100 * g("term_bad")), style="bold red"),
         _dbar(g("term_bad") / .05, 14, (255, 90, 90)), _dstatus(g("term_bad") <= .01, g("term_bad") <= .05),
         mini("term_bad", (255, 90, 90)), "越低越好"), None,
        ("撞地", Text("%.2f%%" % (100 * g("term_base")), style="bold magenta"),
         _dbar(g("term_base") / .02, 14, (255, 120, 200)), _dstatus(g("term_base") <= .005, g("term_base") <= .02),
         mini("term_base", (255, 120, 200)), "越低越好"),
    ]
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(
        Panel(_dtable(left), box=box.ROUNDED, title="[bold]运动 / 高度[/]", border_style="rgb(0,180,160)", padding=(0, 1)),
        Panel(_dtable(right), box=box.ROUNDED, title="[bold]稳定性 / 奖励[/]", border_style="rgb(180,80,160)", padding=(0, 1)),
    )
    return grid


def dashboard_footer(data):
    gpu = data.get("gpu") or {}
    util = float(gpu.get("util", 0.0) or 0.0)
    l1 = Text(" GPU ", style="bold black on bright_green")
    l1.append_text(_dbar(util / 100.0, 18, (0, 255, 133)))
    l1.append(" %3.0f%%  " % util, style="bold green")
    l1.append("%.1f/%.1f GiB  %.0f°C  %.0fW" % (
        gpu.get("used", 0) / 1024, gpu.get("total", 0) / 1024,
        gpu.get("temp", 0), gpu.get("power", 0)), style="white")
    l2 = Text(" 每 5 秒刷新；Ctrl+C 退出；只读监控，不操作训练进程。", style="dim")
    return Panel(Group(l1, l2), box=box.ROUNDED, border_style="rgb(60,60,80)", padding=(0, 1))


def status_panel(state, data):
    stage = state.get('stage', 'waiting')
    iteration = data.get('iteration') or state.get('iteration') or (state.get('handover_checkpoint') or {}).get('iteration_filename',0)
    fresh = data.get('stale_s')
    color = 'green' if stage == 'training' and fresh is not None and fresh < 120 else 'yellow'
    status = Text()
    status.append(f'MOD4 / SCUT 平地提速   {stage}   {time.strftime("%H:%M:%S")}', style=f'bold {color}')
    status.append(f'    iteration {iteration}    20000 env × 24', style='white')
    if state.get('deadline_epoch'):
        status.append(f"\n预算剩余 {max(0,(state['deadline_epoch']-time.time())/3600):.2f} 小时", style='cyan')
    status.append('\n真实平地 z=0；目标 root 高度 0.25 m；SCUT exp(-误差²/σ)；闭链完整重置', style='cyan')
    if state.get('speed_limit_m_s'):
        status.append(f"\n速度指令 ±{state['speed_limit_m_s']:g} m/s；10% 站立；DR 关闭；本轮不自动晋级", style='bold green')
    ck = state.get('latest_checkpoint') or (state.get('handover_checkpoint') or {}).get('path')
    if ck:
        status.append(f'\n当前 run {Path(ck).parent.name}   最新检查点 {Path(ck).name}', style='dim')
    if state.get('error'):
        status.append('\n需要检查 supervisor.log', style='bold red')
    return Panel(status, title='任务和物理合同', border_style=color)


def training_panel(data):
    last = data.get('last') or {}
    series = data.get('series') or {}
    table = Table.grid(padding=(0, 2))
    table.add_column(width=22)
    table.add_column(width=18, justify='right')
    table.add_column(width=42)
    metrics = [
        ('策略步/秒', 'fps', '{:,.0f}', '吞吐；不是物理步/秒'),
        ('训练平均奖励', 'reward', '{:.3f}', '趋势项，不代表验收通过'),
        ('训练回合长度', 'ep_len', '{:.0f}', '带探索动作'),
        ('速度成功率', 'success', '{:.1%}', 'Metrics/success_rate；训练代理'),
        ('线速度误差', 'err_v', '{:.3f}', 'Metrics/twist/error_vel_xy'),
        ('角速度误差', 'err_w', '{:.3f}', 'Metrics/twist/error_vel_yaw'),
        ('线速度跟踪', 'track_v', '{:.4f}', 'track_lin_vel；越高越好'),
        ('高度奖励', 'height_r', '{:.4f}', 'height；越高越好'),
        ('高度紧奖励', 'height_tight', '{:.4f}', 'height_tight；越高越好'),
        ('双轮高度奖励', 'height_both', '{:.4f}', 'height_both_wheels；采样修正后不可与旧值直接比进步'),
        ('姿态奖励 y', 'orient_r', '{:.4f}', 'flat_orientation_y；越接近0越轻'),
        ('动作变化', 'action_rate', '{:.4f}', 'action_rate；越接近0越轻'),
        ('动作加速度', 'action_acc', '{:.4f}', 'action_acc；越接近0越轻'),
        ('力矩惩罚', 'torques', '{:.4f}', 'torques；越接近0越轻'),
        ('关节功率', 'joint_power', '{:.4f}', 'joint_power；越接近0越轻'),
        ('动作 std', 'std', '{:.3f}', '探索噪声'),
        ('超时率', 'term_timeout', '{:.1%}', '越高越接近满回合'),
        ('姿态崩', 'term_bad', '{:.2%}', '越低越好'),
        ('撞地', 'term_base', '{:.2%}', '越低越好'),
        ('陀螺限幅', 'gyro_limit', '{:.2f}', 'Curriculum/gyro_window；rad/s'),
    ]
    for title, key, fmt, note in metrics:
        value = last.get(key)
        if value is not None and key == 'closure':
            value *= 1000
        table.add_row(title, fmt.format(value) if value is not None else '—', note)
    plot = Table.grid(padding=(0, 2))
    plot.add_column(width=14)
    plot.add_column(width=58)
    for title, key in [('奖励曲线', 'reward'), ('高度奖励', 'height_r'), ('线速度跟踪', 'track_v'), ('速度成功率', 'success')]:
        plot.add_row(title, sparkline(series.get(key) or [], 56))
    return Panel(Group(table, Text(' '), plot), title='训练日志（带探索动作）', border_style='blue')


def evaluation_panel(state):
    report = state.get('final_evaluation') or state.get('latest_evaluation') or state.get('baseline') or {}
    if not report:
        return Panel('等待首次无探索动作评测', title='确定性回放', border_style='yellow')
    if 'nominal' in report and 'mild' in report:report=report['mild']
    seconds = float(report.get('seconds') or 0)
    checkpoint = Path(report.get('checkpoint', '?')).name
    title = f'{seconds:g} s 确定性' + ('验收' if seconds >= 15 else '基线探针（不能判定15秒达标）')
    current_ck = Path(state.get('latest_checkpoint') or '').name
    stale = bool(current_ck and checkpoint != current_ck)
    if stale:
        title = '历史 ' + title
    table = Table(show_header=True, header_style='bold cyan', box=None, padding=(0, 1))
    for col in ('指令', '实速', '速度误差', '车高/目标', '倾角', '瞬时双轮', '旧端点双轮', '区间均力双轮', '双轮低载ms', '滑移均近似', '动作 Δ/Δ²', '存活', '旧窗口通过', '旧瞬时通过'):
        table.add_column(col, justify='right')
    pe=report.get('per_environment',{})
    for group_index,group in enumerate(report.get('groups', [])):
        unloads=[x for x,gid in zip(pe.get('longest_both_low_force_s_substep',[]),pe.get('group_ids',[])) if gid==group_index]
        unload=max(unloads)*1000 if unloads else None
        table.add_row(
            f"{group.get('command_vx', 0):.1f}" + ('↔' if group.get('profile')=='ramp_brake_reverse' else ''), f"{group.get('speed', 0):.2f}",
            f"{group.get('vel_error', 0):.2f}", f"{group.get('height', 0):.3f}/.250",
            f"{group.get('tilt', 0):.1f}°", f"{group.get('both_wheels', 0):.0%}",
            f"{group.get('both_wheels_scut_history', 0):.0%}" if 'both_wheels_scut_history' in group else '—',
            f"{group['both_wheels_binned_mean']:.0%}" if 'both_wheels_binned_mean' in group else '—',
            f"{unload:.1f}" if unload is not None else '—',
            f"{max(group['left_support_slip_control'],group['right_support_slip_control']):.3f}" if 'left_support_slip_control' in group else '—',
            f"{group.get('delta', 0):.3f}/{group.get('d2', 0):.3f}",
            f"{group.get('survival_fraction', 0):.0%}",
            f"{group.get('strict_pass', 0):.0%}",
            f"{group['strict_pass_instant_legacy']:.0%}" if 'strict_pass_instant_legacy' in group else '—',
        )
    summary = Text(f'检查点 {checkpoint}   闭链 {1000 * report.get("max_closure_after_grace_m", 0):.3f} mm'
                   f'   耦合 {report.get("max_mimic_after_grace_rad", 0):.5f} rad')
    summary.append('\n窗口判据用于本轮评估；旧瞬时判据并列保留，均不是赛场官方标准。', style='dim')
    if stale:
        summary.append(f'\n注意：该评测对应 {checkpoint}，当前最新 {current_ck}；当前 run 尚无新评测。', style='yellow')
    capture_enabled=report.get('contact_capture_metadata',{}).get('integrated_enabled',False)
    summary.append('\n旧窗口保留10ms端点；区间均力来自2kHz子步的3×5ms积分。统计变好≠策略进步。低载时长取组内最差；滑移为10ms采样近似。' if capture_enabled else '\n这份评测未启用子步积分，新增指标不作积分/子步结论；仅参考旧统计。', style='dim')
    if report.get('ramp_suite'):
        summary.append('\n↔为加速/刹停/反向轨迹；该行实速是全轨迹有符号均值，不是峰值。',style='yellow')
    return Panel(Group(table, Text(' '), summary), title=title, border_style='magenta')


def render(state, data):
    has_iteration = bool((data.get("series") or {}).get("fps"))
    body = dashboard_body(data) if has_iteration else Panel("正在加载场景或等待第一轮日志；训练指标尚未产生。", title="运行准备", border_style="yellow")
    return Group(dashboard_header(state, data), body, evaluation_panel(state), dashboard_footer(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--interval', type=float, default=5)
    args = parser.parse_args()
    console = Console()
    monitor = None
    current_log = None
    while True:
        state = read_json(ROOT / 'status.json')
        log = selected_log(state)
        if log != current_log:
            current_log = log
            monitor = LogMonitor(str(log), int(state.get("target_iteration") or 100000), int(state.get("num_envs",20000)), int(state.get("steps_per_env",24)))
        data = monitor.refresh()
        if args.once:
            console.print(render(state, data))
            return
        console.clear()
        console.print(render(state, data))
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
