"""Read-only MOD4 rescue terminal. Follows the supervisor's current run."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

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
    if state.get('stage') in ('training', 'final_evaluation', 'finished', 'attention_required'):
        attempt = int(state.get('attempt') or 0)
        path = ROOT / f'train_{attempt}.log'
        if path.exists():
            return path
    return ROOT / 'train_0.log'


def status_panel(state, data):
    stage = state.get('stage', 'waiting')
    iteration = data.get('iteration') or state.get('iteration') or (state.get('handover_checkpoint') or {}).get('iteration_filename',0)
    fresh = data.get('stale_s')
    color = 'green' if stage == 'training' and fresh is not None and fresh < 120 else 'yellow'
    status = Text()
    status.append(f'MOD4 / SCUT 平地续训   {stage}   {time.strftime("%H:%M:%S")}', style=f'bold {color}')
    status.append(f'    iteration {iteration}    20000 env × 24', style='white')
    if state.get('deadline_epoch'):
        status.append(f"\n预算剩余 {max(0,(state['deadline_epoch']-time.time())/3600):.2f} 小时", style='cyan')
    status.append('\n真实平地 z=0；目标 root 高度 0.25 m；SCUT exp(-误差²/σ)；闭链完整重置', style='cyan')
    ck = state.get('latest_checkpoint') or (state.get('handover_checkpoint') or {}).get('path')
    if ck:
        status.append(f'\n最新检查点 {Path(ck).name}', style='dim')
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
        ('训练平均奖励', 'reward', '{:.3f}', '只用于看趋势，不代表验收通过'),
        ('训练回合长度', 'ep_len', '{:.0f}', '带探索动作'),
        ('训练速度成功率', 'success', '{:.1%}', '训练代理指标，不是15秒通过率'),
        ('线速度误差', 'err_v', '{:.3f}', '训练代理指标'),
        ('姿态奖励 y', 'orient_r', '{:.4f}', 'SCUT平地姿态项；车高看下方实测'),
        ('动作变化惩罚', 'action_rate', '{:.4f}', '训练奖励项，越接近0越轻'),
        ('动作加速度惩罚', 'action_acc', '{:.4f}', '训练奖励项，越接近0越轻'),
        ('动作 std', 'std', '{:.3f}', '探索噪声'),
        ('闭链误差 mm', 'closure', '{:.3f}', '上限 2 mm'),
        ('耦合误差 rad', 'mimic', '{:.5f}', '上限 0.01 rad'),
    ]
    for title, key, fmt, note in metrics:
        value = last.get(key)
        if value is not None and key == 'closure':
            value *= 1000
        table.add_row(title, fmt.format(value) if value is not None else '—', note)
    plot = Table.grid(padding=(0, 2))
    plot.add_column(width=14)
    plot.add_column(width=58)
    for title, key in [('奖励曲线', 'reward'), ('步速曲线', 'fps'), ('速度成功率', 'success')]:
        plot.add_row(title, sparkline(series.get(key) or [], 56))
    return Panel(Group(table, Text(' '), plot), title='训练日志（带探索动作）', border_style='blue')


def evaluation_panel(state):
    report = state.get('final_evaluation') or state.get('latest_evaluation') or state.get('baseline') or {}
    if not report:
        return Panel('等待首次无探索动作评测', title='确定性回放', border_style='yellow')
    seconds = float(report.get('seconds') or 0)
    checkpoint = Path(report.get('checkpoint', '?')).name
    title = f'{seconds:g} s 确定性' + ('验收' if seconds >= 15 else '基线探针（不能判定15秒达标）')
    table = Table(show_header=True, header_style='bold cyan', box=None, padding=(0, 1))
    for col in ('指令', '实速', '速度误差', '车高/目标', '倾角', '瞬时双轮', '历史双轮', '动作 Δ/Δ²', '存活', '窗口通过', '旧瞬时通过'):
        table.add_column(col, justify='right')
    for group in report.get('groups', []):
        table.add_row(
            f"{group.get('command_vx', 0):.1f}", f"{group.get('speed', 0):.2f}",
            f"{group.get('vel_error', 0):.2f}", f"{group.get('height', 0):.3f}/.250",
            f"{group.get('tilt', 0):.1f}°", f"{group.get('both_wheels', 0):.0%}",
            f"{group.get('both_wheels_scut_history', 0):.0%}" if 'both_wheels_scut_history' in group else '—',
            f"{group.get('delta', 0):.3f}/{group.get('d2', 0):.3f}",
            f"{group.get('survival_fraction', 0):.0%}",
            f"{group.get('strict_pass', 0):.0%}",
            f"{group['strict_pass_instant_legacy']:.0%}" if 'strict_pass_instant_legacy' in group else '—',
        )
    summary = Text(f'检查点 {checkpoint}   闭链 {1000 * report.get("max_closure_after_grace_m", 0):.3f} mm'
                   f'   耦合 {report.get("max_mimic_after_grace_rad", 0):.5f} rad')
    summary.append('\n窗口判据用于本轮评估；旧瞬时判据并列保留，均不是赛场官方标准。', style='dim')
    summary.append('\n接触历史3帧：配置5ms，本栈实测相邻样本10ms；窗口通过不代表连续承重。', style='dim')
    return Panel(Group(table, Text(' '), summary), title=title, border_style='magenta')


def render(state, data):
    gpu=data.get('gpu') or {}
    gpu_text=Text(f"GPU {gpu.get('util',0):.0f}%  显存 {gpu.get('used',0)/1024:.1f}/{gpu.get('total',0)/1024:.1f} GiB",style='cyan')
    return Group(status_panel(state, data), training_panel(data), evaluation_panel(state),
                 gpu_text,Text('每 5 秒刷新；Ctrl+C 退出此终端。只读监控，不操作训练进程。', style='dim'))


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
            monitor = LogMonitor(str(log), 4350, 20000, 24)
        data = monitor.refresh()
        if args.once:
            console.print(render(state, data))
            return
        console.clear()
        console.print(render(state, data))
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
