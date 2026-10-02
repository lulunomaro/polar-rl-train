"""MOD4 terminal dashboard: curses UI, no browser or HTML rendering."""

from __future__ import annotations

import argparse
import curses
import json
import math
import time
import unicodedata
from datetime import datetime
from urllib.request import urlopen


GLYPHS = "▁▂▃▄▅▆▇█"
BLUE, CYAN, GREEN, YELLOW, RED, DIM = range(1, 7)


def width_of(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def clip(text: str, max_width: int) -> str:
    out, used = [], 0
    for char in str(text):
        size = 2 if unicodedata.east_asian_width(char) in "WF" else 1
        if used + size > max_width:
            break
        out.append(char)
        used += size
    return "".join(out)


def put(screen, y: int, x: int, text: str, color: int = 0, bold=False):
    rows, cols = screen.getmaxyx()
    if y < 0 or y >= rows or x < 0 or x >= cols - 1:
        return
    attr = curses.color_pair(color) | (curses.A_BOLD if bold else 0)
    try:
        screen.addstr(y, x, clip(text, cols - x - 1), attr)
    except curses.error:
        pass


def line(screen, y: int, x: int, count: int, char="─", color=DIM):
    if count > 0:
        put(screen, y, x, char * count, color)


def box(screen, y: int, x: int, height: int, width: int, title: str):
    rows, cols = screen.getmaxyx()
    height, width = min(height, rows - y), min(width, cols - x)
    if width < 4 or height < 3:
        return
    line(screen, y, x + 1, width - 2)
    line(screen, y + height - 1, x + 1, width - 2)
    put(screen, y, x, "┌", DIM)
    put(screen, y, x + width - 1, "┐", DIM)
    put(screen, y + height - 1, x, "└", DIM)
    put(screen, y + height - 1, x + width - 1, "┘", DIM)
    for row in range(y + 1, y + height - 1):
        put(screen, row, x, "│", DIM)
        put(screen, row, x + width - 1, "│", DIM)
    put(screen, y, x + 3, f" {title} ", CYAN, True)


def fmt(value, digits=2):
    if value is None:
        return "--"
    try:
        v = float(value)
        return f"{v:,.{digits}f}" if math.isfinite(v) else "--"
    except (TypeError, ValueError):
        return "--"


def time_label(iso):
    if not iso:
        return "--"
    try:
        return datetime.fromisoformat(iso).astimezone().strftime("%m-%d %H:%M:%S")
    except ValueError:
        return "--"


def gauge(screen, y, x, width, label, value, target, higher=False, suffix="", digits=2):
    if value is None:
        ratio = 0.0
    elif higher:
        ratio = float(value) / target
    else:
        ratio = target / max(float(value), 1e-12)
    ratio = max(0.0, min(1.0, ratio))
    color = GREEN if ratio >= 1 else YELLOW if ratio >= .70 else RED
    bar_width = max(7, min(20, width - 38))
    filled = round(bar_width * ratio)
    put(screen, y, x, clip(label, 14), 0)
    put(screen, y, x + 16, f"{fmt(value, digits)}{suffix}", color, True)
    put(screen, y, x + width - bar_width - 2, "[" + "█" * filled + "·" * (bar_width - filled) + "]", color)


def sparkline(points, length: int) -> tuple[str, float | None, float | None]:
    values = [float(p[1]) for p in points if p and len(p) > 1 and p[1] is not None]
    if not values or length <= 0:
        return "等待数据", None, None
    values = values[-max(length, 1) * 4:]
    if len(values) > length:
        sample = [values[round(i * (len(values) - 1) / max(1, length - 1))] for i in range(length)]
    else:
        sample = values
    low, high = min(values), max(values)
    if high == low:
        glyphs = "▄" * len(sample)
    else:
        glyphs = "".join(GLYPHS[min(7, max(0, round((v - low) / (high - low) * 7)))] for v in sample)
    return glyphs, low, high


def plot(screen, y, x, height, width, title, points, color, unit, target=None):
    box(screen, y, x, height, width, title)
    if height < 5 or width < 20:
        return
    values = [p[1] for p in points if len(p) > 1]
    current = values[-1] if values else None
    target_text = f"  门槛 {target}{unit}" if target is not None else ""
    put(screen, y + 1, x + 2, f"当前 {fmt(current)}{unit}{target_text}", color, True)
    graph, low, high = sparkline(points, width - 6)
    put(screen, y + 2, x + 2, graph, color)
    if height >= 6:
        put(screen, y + 3, x + 2, f"区间 {fmt(low)} ~ {fmt(high)}{unit}    最近 {len(values)} 轮", DIM)


def render(screen, data, error: str | None):
    screen.erase()
    rows, cols = screen.getmaxyx()
    if rows < 44 or cols < 105:
        put(screen, 2, 2, "终端窗口太小，请放大到至少 105 列 × 44 行。", YELLOW, True)
        put(screen, 4, 2, f"当前 {cols} 列 × {rows} 行；按 q 退出。", DIM)
        screen.refresh()
        return
    latest = data.get("latest") or {}
    series = data.get("series") or {}
    gpu = data.get("gpu") or {}
    iteration = data.get("iteration")
    stale = not data or data.get("state") != "training"
    if data.get("last_scalar_utc"):
        try:
            stale |= time.time() - datetime.fromisoformat(data["last_scalar_utc"]).timestamp() > 120
        except ValueError:
            pass
    status_color = RED if stale or error else GREEN
    put(screen, 0, 2, "MOD4  /  RL LIVE TRAINING MONITOR", CYAN, True)
    clock_now = datetime.now().strftime("%H:%M:%S")
    put(screen, 0, cols - 34, f"{clock_now}  " + ("● LIVE" if not stale and not error else "● DATA STALE"), status_color, True)
    line(screen, 1, 1, cols - 2, "═", BLUE)
    envs = data.get("envs")
    env_label = f"{envs:,}" if isinstance(envs, int) else "--"
    put(screen, 2, 2, f"环境 {env_label} × {data.get('steps_per_env','--')}  |  迭代 {iteration or '--'}  |  策略步速 {fmt(latest.get('fps'),0)} step/s  |  奖励 {fmt(latest.get('reward'))}", 0, True)
    put(screen, 3, 2, f"GPU {fmt(gpu.get('util_pct'),0)}%  |  显存 {fmt((gpu.get('used_mib') or 0)/1024,1)}/{fmt((gpu.get('total_mib') or 0)/1024,1)} GiB  |  温度 {fmt(gpu.get('temp_c'),0)}°C  |  功率 {fmt(gpu.get('power_w'),0)} W", DIM)
    progress = data.get("progress_pct") or 0
    budget = max(10, cols - 54)
    fill = round(budget * min(100, max(0, progress)) / 100)
    put(screen, 4, 2, f"有效训练 {fmt(progress,1)}% ", CYAN, True)
    put(screen, 4, 19, "[" + "█" * fill + "·" * (budget - fill) + "]", GREEN)
    put(screen, 4, 22 + budget, f"截止 {time_label(data.get('deadline_utc'))}", DIM)
    scalar_age = "--"
    if data.get("last_scalar_utc"):
        try:
            scalar_age = f"{max(0, int(time.time() - datetime.fromisoformat(data['last_scalar_utc']).timestamp()))}秒前"
        except ValueError:
            pass
    fetch_age = "--" if not data.get("_client_fetched_at") else f"{max(0, int(time.time() - data['_client_fetched_at']))}秒前"
    put(screen, 5, 2, f"检查点 {data.get('latest_checkpoint') or '--'}  |  终端读取 {fetch_age}  |  最新训练指标 {scalar_age}（每轮约32秒）", DIM)
    half = cols // 2
    box(screen, 7, 1, 13, half - 1, "训练批次 / 稳定度与达成度")
    box(screen, 7, half, 13, cols - half - 1, "64环境×15秒 / 确定性验收")
    metrics = [
        ("跑动倾斜", "run_tilt", 8, False, "°", 2),
        ("速度误差", "run_vel_error", .75, False, "m/s", 2),
        ("双主轮接地", "run_wheels", .90, True, "", 3),
        ("动作一阶差分", "action_delta", .18, False, "", 3),
        ("动作二阶差分", "action_d2", .25, False, "", 3),
        ("站立倾斜", "stand_tilt", 8, False, "°", 2),
        ("闭链误差", "closure_m", .002, False, "m", 4),
        ("耦合误差", "mimic_rad", .01, False, "rad", 4),
    ]
    for i, (label, key, target, higher, suffix, digits) in enumerate(metrics):
        gauge(screen, 9 + i, 3, half - 7, label, latest.get(key), target, higher, suffix, digits)
    put(screen, 18, 3, "训练动作含探索噪声；不能直接判定实车达标", YELLOW)
    acceptance = data.get("acceptance")
    if acceptance:
        vals = acceptance.get("values") or {}
        put(screen, 9, half + 2, f"{acceptance.get('checkpoint')}  {'旧检查点参考' if acceptance.get('stale') else '当前检查点'}", YELLOW if acceptance.get("stale") else GREEN, True)
        surv = vals.get("episode_15s_survived")
        passed = vals.get("episode_15s_pass")
        check = [
            f"15秒存活 {fmt((surv or 0)/64*100,1)}% / ≥80%    严格通过 {fmt((passed or 0)/64*100,1)}%",
            f"倾斜 {fmt(vals.get('tilt_deg_rms'))}° / ≤8°        速度误差 {fmt(vals.get('velocity_error_xy_m_s_rms'))}m/s / ≤0.75",
            f"双轮接地 {fmt((vals.get('both_wheels_contact_rate') or 0)*100,1)}% / ≥90%",
            f"动作 Δ {fmt(vals.get('action_delta_rms'),3)} / ≤0.18    Δ² {fmt(vals.get('action_second_diff_rms'),3)} / ≤0.25",
            f"闭链 {fmt(vals.get('max_closure_error_m'),4)}m / ≤0.002    耦合 {fmt(vals.get('max_mimic_error_rad'),4)}rad / ≤0.01",
        ]
        for i, text in enumerate(check):
            put(screen, 11 + i, half + 2, text)
        put(screen, 17, half + 2, "旧检查点不代表当前策略通过验收" if acceptance.get("stale") else "已更新至最新验收", YELLOW if acceptance.get("stale") else GREEN)
    else:
        put(screen, 10, half + 2, "还没有找到同协议确定性评测。", YELLOW)
    available = rows - 24
    chart_height = max(6, min(8, available // 3))
    chart_rows = [21 + i * chart_height for i in range(3)]
    plots = [
        ("奖励曲线", "reward", CYAN, "", None), ("环境步速", "fps", BLUE, "step/s", 28732),
        ("跑动倾斜", "run_tilt", RED, "°", 8), ("双主轮接地", "run_wheels", GREEN, "ratio", .9),
        ("速度误差", "run_vel_error", YELLOW, "m/s", .75), ("动作平滑度 Δ", "action_delta", CYAN, "", .18),
    ]
    for i, (title, key, color, unit, target) in enumerate(plots):
        row = chart_rows[i // 2]
        plot(screen, row, 1 if i % 2 == 0 else half, chart_height, half - 1 if i % 2 == 0 else cols - half - 1,
             title, series.get(key, []), color, unit, target)
    footer = rows - 1
    line(screen, footer - 1, 1, cols - 2, "═", BLUE)
    put(screen, footer, 2, "q 退出  ·  r 立即刷新  ·  终端/后台每2秒读取  ·  奖励等指标每轮约32秒更新", DIM)
    if error:
        put(screen, footer, max(65, cols - len(error) - 3), clip(error, cols // 3), RED)
    screen.refresh()


def run(screen, url: str):
    curses.curs_set(0)
    screen.nodelay(True)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for pair, foreground in [(BLUE, curses.COLOR_BLUE), (CYAN, curses.COLOR_CYAN),
                                  (GREEN, curses.COLOR_GREEN), (YELLOW, curses.COLOR_YELLOW),
                                  (RED, curses.COLOR_RED), (DIM, curses.COLOR_WHITE)]:
            curses.init_pair(pair, foreground, -1)
    data, error, last_fetch, last_draw = {}, None, 0.0, 0.0
    while True:
        if time.monotonic() - last_fetch >= 2:
            last_fetch = time.monotonic()
            try:
                with urlopen(url, timeout=3) as response:
                    data = json.load(response)
                data["_client_fetched_at"] = time.time()
                error = data.get("error")
            except Exception as exc:
                error = f"数据源断开: {type(exc).__name__}"
        if time.monotonic() - last_draw >= 1:
            render(screen, data, error)
            last_draw = time.monotonic()
        key = screen.getch()
        if key in (ord("q"), ord("Q")):
            return
        if key in (ord("r"), ord("R")):
            last_fetch = 0
        if key == curses.KEY_RESIZE:
            last_draw = 0
        time.sleep(.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://10.24.4.210:8765/api/state")
    args = parser.parse_args()
    curses.wrapper(run, args.url)


if __name__ == "__main__":
    main()
