"""MOD4 本机训练监控 —— 自适应宽度的 Rich 面板（清屏+写入，不用备用缓冲区）。

关键点（Windows conhost 实测）：
  * 必须先把控制台代码页设成 UTF-8，否则方块字符会抛 UnicodeEncodeError → 黑屏；
  * 不能用 Rich Live(screen=True)（备用缓冲区在 conhost 上会黑屏）→ 改成清屏+写入；
  * 版面按窗口实际宽度自适应（>=132 双栏；96–131 单栏；<96 极简）。
只读：TensorBoard 事件 + nvidia-smi + 检查点。q 退出，r 刷新。
"""
from __future__ import annotations

import argparse, ctypes, glob, io, json, os, re, subprocess, sys, time
from datetime import datetime, timedelta

ROOT = r"D:\claude2\fangzhen"
DEFAULT_RUN = os.path.join(ROOT, "runs3060", "flat_scratch_v1")

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

TAGS = {
    "reward": "Train/mean_reward", "ep_len": "Train/mean_episode_length",
    "std": "Policy/mean_std", "fps": "Perf/total_fps",
    "value_loss": "Loss/value", "height_r": "Episode_Reward/height", "height_def": "Episode_Reward/height_deficit",
    "wheel_r": "Episode_Reward/wheel_contact", "orient_r": "Episode_Reward/flat_orientation",
    "alive_r": "Episode_Reward/alive", "track_v": "Episode_Reward/track_lin_vel",
    "success": "Metrics/velocity_tracking_success_rate",
    "term_bad": "Episode_Termination/bad_orientation", "term_low": "Episode_Termination/low_base",
    "term_base": "Episode_Termination/base_contact", "term_timeout": "Episode_Termination/time_out",
    "closure": "Metrics/plant/closure_err_session_max_m", "mimic": "Metrics/plant/mimic_err_session_max_rad",
    "err_v": "Metrics/twist/error_vel_xy", "err_w": "Metrics/twist/error_vel_yaw",
    "collection_time": "Perf/collection_time", "learning_time": "Perf/learning_time",
}
EP_CAP = 2000.0
GOOD, WARN, BAD = "OK", "!", "X"
RENDER_WIDTH = 150


class ConsoleGone(Exception):
    """The console window went away (user closed it): exit quietly instead of crashing."""


def enable_console():
    if os.name != "nt":
        return
    try:
        k = ctypes.windll.kernel32
        k.SetConsoleOutputCP(65001); k.SetConsoleCP(65001)
        h = k.GetStdHandle(-11); mode = ctypes.c_uint32()
        k.GetConsoleMode(h, ctypes.byref(mode))
        k.SetConsoleMode(h, mode.value | 0x0004)          # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def console_view():
    """(origin_x, origin_y, visible_width, visible_height) of the console window."""
    if os.name == "nt":
        try:
            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
            class SMALL_RECT(ctypes.Structure):
                _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                            ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]
            class CSBI(ctypes.Structure):
                _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", ctypes.c_ushort),
                            ("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]
            h = ctypes.windll.kernel32.GetStdHandle(-11)
            info = CSBI()
            if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, ctypes.byref(info)):
                r = info.srWindow
                return int(r.Left), int(r.Top), int(r.Right - r.Left + 1), int(r.Bottom - r.Top + 1)
        except Exception:
            pass
    try:
        s = os.get_terminal_size()
        return 0, 0, s.columns, s.lines
    except Exception:
        return 0, 0, RENDER_WIDTH, 40


def move_cursor(x, y):
    if os.name == "nt":
        try:
            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
            h = ctypes.windll.kernel32.GetStdHandle(-11)
            ctypes.windll.kernel32.SetConsoleCursorPosition(h, COORD(int(x), int(y)))
            return
        except Exception:
            pass
    sys.stdout.write("\x1b[%d;%dH" % (y + 1, x + 1))


ANSI_RE = None


def _vis_len(s: str) -> int:
    global ANSI_RE
    if ANSI_RE is None:
        import re
        ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
    return len(ANSI_RE.sub("", s))


def _vis_cut(s: str, width: int) -> str:
    """Truncate to `width` visible characters, keeping the escape sequences intact."""
    import re
    out, vis = [], 0
    i = 0
    while i < len(s):
        m = re.match(r"\x1b\[[0-9;?]*[A-Za-z]", s[i:])
        if m:
            out.append(m.group(0)); i += len(m.group(0)); continue
        if vis >= width:
            break
        out.append(s[i]); vis += 1; i += 1
    return "".join(out) + "\x1b[0m"


def write_frame(text, ox, oy, width, height):
    """Overwrite the visible window in place; never write more lines than fit (no scrolling)."""
    lines = text.splitlines()
    lines = lines[:height]
    while len(lines) < height:
        lines.append("")
    padded = []
    for ln in lines:
        vl = _vis_len(ln)
        if vl > width:
            padded.append(_vis_cut(ln, width))
        else:
            padded.append(ln + " " * (width - vl))
    move_cursor(ox, oy)
    try:
        sys.stdout.write("\n".join(padded))
        sys.stdout.flush()
    except OSError as exc:
        raise ConsoleGone(str(exc))


def term_size():
    """Visible viewport size.  os.get_terminal_size() reports the BUFFER height on Windows,
    so a 46-line buffer with a 24-line window made the frame scroll and hide its own header."""
    if os.name == "nt":
        try:
            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
            class SMALL_RECT(ctypes.Structure):
                _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                            ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]
            class CSBI(ctypes.Structure):
                _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", ctypes.c_ushort),
                            ("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]
            h = ctypes.windll.kernel32.GetStdHandle(-11)
            info = CSBI()
            if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, ctypes.byref(info)):
                w = info.srWindow.Right - info.srWindow.Left + 1
                hh = info.srWindow.Bottom - info.srWindow.Top + 1
                if w > 20 and hh > 5:
                    return int(w), int(hh)
        except Exception:
            pass
    try:
        s = os.get_terminal_size()
        return s.columns, s.lines
    except Exception:
        return RENDER_WIDTH, 40


def rgb(r, g, b):
    return "rgb(%d,%d,%d)" % (int(r), int(g), int(b))


def lerp(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))


def hhmmss(x):
    if x is None or x != x:
        return "--:--:--"
    return str(timedelta(seconds=int(max(0, x))))


class Monitor:
    def __init__(self, run_root, total, envs, steps):
        self.run_root, self.total, self.envs, self.steps = run_root, total, envs, steps
        self.acc = None; self.event = None; self.run_dir = None
        self.gpu = {}; self.gpu_t = 0.0; self.started = None; self.pulse = 0

    def refresh(self):
        from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
        files = sorted(glob.glob(os.path.join(self.run_root, "logs", "*", "events.out.tfevents*")), key=os.path.getmtime)
        d = {"total": self.total, "envs": self.envs, "steps": self.steps, "series": {}, "last": {}, "gpu": self.gpu}
        if not files:
            d["error"] = "waiting for first event"
            return d
        newest = files[-1]
        if newest != self.event:
            self.event = newest; self.run_dir = os.path.dirname(newest)
            self.acc = EventAccumulator(newest, size_guidance={"scalars": 20000})
        self.acc.Reload()
        for key, tag in TAGS.items():
            try:
                ev = self.acc.Scalars(tag)
            except Exception:
                ev = []
            if ev:
                d["series"][key] = [e.value for e in ev]
                d["last"][key] = ev[-1].value
        steps = None
        try:
            steps = [e.step for e in self.acc.Scalars("Train/mean_reward")]
        except Exception:
            pass
        d["iteration"] = steps[-1] if steps else 0
        d["run"] = os.path.basename(self.run_dir or "")
        per = None
        try:
            coll = [e.value for e in self.acc.Scalars("Perf/collection_time")]
            learn = [e.value for e in self.acc.Scalars("Perf/learning_time")]
            if coll:
                k = min(10, len(coll)); per = sum(coll[-k:]) / k + (sum(learn[-k:]) / k if learn else 0.0)
        except Exception:
            pass
        d["per_iter"] = per
        if self.started is None:
            try:
                self.started = self.acc.Scalars("Train/mean_reward")[0].wall_time
            except Exception:
                self.started = os.path.getmtime(newest)
        d["elapsed"] = time.time() - self.started
        d["eta"] = max(0.0, (self.total - d["iteration"]) * per) if per else None
        cks = glob.glob(os.path.join(self.run_dir, "model_*.pt"))
        d["ckpt_count"] = len(cks)
        d["ckpt_newest"] = ("model_%d.pt" % max(int(os.path.basename(p).split("_")[1].split(".")[0]) for p in cks)) if cks else "--"
        d["stale_s"] = time.time() - os.path.getmtime(self.event)
        if time.time() - self.gpu_t > 4:
            got = None
            if GPU_JSON:
                try:
                    with open(GPU_JSON, encoding="utf-8") as fh:
                        j = json.load(fh)
                    if time.time() - float(j.get("ts", 0.0)) < 20:
                        got = dict(util=float(j["util"]), used=float(j["used"]), total=float(j["total"]),
                                   temp=float(j["temp"]), power=float(j["power"]))
                except Exception:
                    got = None
            if got is None:
                try:
                    out = subprocess.run(["nvidia-smi",
                                          "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=8).stdout.strip()
                    p = [x.strip() for x in out.split(",")]
                    if len(p) >= 5:
                        got = dict(util=float(p[0]), used=float(p[1]), total=float(p[2]),
                                   temp=float(p[3]), power=float(p[4]))
                except Exception:
                    got = None
            if got:
                self.gpu = got
            self.gpu_t = time.time()
        d["gpu"] = self.gpu
        self.pulse ^= 1; d["pulse"] = self.pulse
        return d


GPU_JSON = None            # --gpu-json: 读远端 nvidia-smi 的 JSON（本地镜像用）
CKPT_JSON = None           # --ckpt-json: 读远端 checkpoint 名字列表（本地镜像用）


class LogMonitor:
    """按训练 stdout 日志出数：4090 上没有 tensorboard+rich 同装的解释器，日志是两边都有的格式。

    日志每个迭代打一个块（Episode_Reward/* / Metrics/* / Episode_Termination/* …），
    这里把整份日志的所有块都解析成 series，key 与 TAGS 的 value 完全同名。
    """

    ITER_RE = re.compile(r"Learning iteration\s+(\d+)\s*/\s*(\d+)")
    TIME_RE = re.compile(r"Iteration time:\s*([\d.]+)s")
    ELAPSED_RE = re.compile(r"Time elapsed:\s*(\d+):(\d+):(\d+)")
    ETA_RE = re.compile(r"ETA:\s*(\d+):(\d+):(\d+)")
    TAG_RE = re.compile(r"^\s*([A-Za-z_][\w/.\- ]*?)\s*:\s*(-?[\d.]+(?:[eE][-+]?\d+)?)\s*$")
    ALIASES = {"Mean reward": "Train/mean_reward",
               "Mean episode length": "Train/mean_episode_length",
               "Mean action std": "Policy/mean_std",
               "Mean value loss": "Loss/value",
               "Mean surrogate loss": "Loss/surrogate",
               "Mean entropy loss": "Loss/entropy"}

    def __init__(self, log_path, total, envs, steps, ckpt_json=None):
        self.log_path, self.total, self.envs, self.steps = log_path, total, envs, steps
        self.series, self.last, self.iteration, self.per_iter = {}, {}, 0, None
        self.gpu, self.gpu_t = {}, 0.0
        self.started = None
        self.ckpt_json = ckpt_json

    def _blocks(self):
        try:
            with open(self.log_path, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()[-40000:]
        except OSError:
            return []
        blocks, cur = [], []
        for ln in lines:
            if self.ITER_RE.search(ln):
                if cur:
                    blocks.append(cur)
                cur = [ln]
            elif cur:
                cur.append(ln)
        if cur:
            blocks.append(cur)
        return blocks

    def refresh(self) -> dict:
        blocks = self._blocks()
        dicts = []
        for blk in blocks:
            m = self.ITER_RE.search(blk[0])
            if not m:
                continue
            rec = {"__iter__": int(m.group(1))}
            for ln in blk:
                t = self.TIME_RE.search(ln)
                if t:
                    rec["__time__"] = float(t.group(1))
                e = self.ELAPSED_RE.search(ln)
                if e:
                    rec["__elapsed__"] = int(e.group(1)) * 3600 + int(e.group(2)) * 60 + int(e.group(3))
                e = self.ETA_RE.search(ln)
                if e:
                    rec["__eta__"] = int(e.group(1)) * 3600 + int(e.group(2)) * 60 + int(e.group(3))
                mm = self.TAG_RE.match(ln)
                if mm:
                    name = self.ALIASES.get(mm.group(1), mm.group(1))
                    rec[name] = float(mm.group(2))
            dicts.append(rec)
        d = {"total": self.total, "envs": self.envs, "steps": self.steps, "series": {}, "last": {},
             "gpu": self.gpu, "run": os.path.basename(self.log_path).split(".out")[0]}
        if not dicts:
            d["error"] = "waiting for first iteration in %s" % os.path.basename(self.log_path)
            return d
        self.iteration = dicts[-1]["__iter__"]
        self.per_iter = dicts[-1].get("__time__")
        for key, tag in TAGS.items():
            vals = [r[tag] for r in dicts if tag in r]
            if vals:
                self.series[key] = vals
                self.last[key] = vals[-1]
        if self.per_iter:
            self.series["fps"] = [self.envs * self.steps / r["__time__"] for r in dicts if r.get("__time__")]
            self.last["fps"] = self.series["fps"][-1]
        d["series"], d["last"] = self.series, self.last
        d["iteration"] = self.iteration
        d["per_iter"] = self.per_iter
        last = dicts[-1]
        if "__elapsed__" in last:
            d["elapsed"] = float(last["__elapsed__"])
        else:
            if self.started is None:
                self.started = time.time() - (self.iteration * self.per_iter if self.per_iter else 0.0)
            d["elapsed"] = time.time() - self.started
        if "__eta__" in last:
            d["eta"] = float(last["__eta__"])
        else:
            d["eta"] = max(0.0, (self.total - self.iteration) * self.per_iter) if self.per_iter else None
        names = []
        if self.ckpt_json:
            try:
                with open(self.ckpt_json, encoding="utf-8") as fh:
                    names = [str(x) for x in json.load(fh)]
            except Exception:
                names = []
        if not names:
            base = os.path.basename(self.log_path)
            stem = base[:-len(".out.log")] if base.endswith(".out.log") else os.path.splitext(base)[0]
            cks = glob.glob(os.path.join(os.path.dirname(self.log_path), "*%s*" % stem, "model_*.pt"))
            names = [os.path.basename(x) for x in cks]
        nums = []
        for n in names:
            try:
                nums.append(int(n.split("_")[1].split(".")[0]))
            except Exception:
                pass
        d["ckpt_count"] = len(nums)
        d["ckpt_newest"] = ("model_%d.pt" % max(nums)) if nums else "--"
        try:
            d["stale_s"] = time.time() - os.path.getmtime(self.log_path)
        except OSError:
            d["stale_s"] = None
        if time.time() - self.gpu_t > 4:
            got = None
            if GPU_JSON:
                try:
                    with open(GPU_JSON, encoding="utf-8") as fh:
                        j = json.load(fh)
                    if time.time() - float(j.get("ts", 0.0)) < 20:
                        got = dict(util=float(j["util"]), used=float(j["used"]), total=float(j["total"]),
                                   temp=float(j["temp"]), power=float(j["power"]))
                except Exception:
                    got = None
            if got:
                self.gpu = got
            self.gpu_t = time.time()
        d["gpu"] = self.gpu
        return d


def gradient_bar(frac, width, c1=(0, 229, 255), c2=(0, 255, 133)):
    t = Text(); n = max(0, min(width, int(round(frac * width))))
    for i in range(width):
        col = lerp(c1, c2, i / max(1, width - 1))
        t.append("█" if i < n else "─", style=rgb(*col) if i < n else "rgb(70,70,80)")
    return t


def sparkline(vals, width, color=(0, 229, 255)):
    blocks = "▁▂▃▄▅▆▇█"; t = Text()
    if not vals:
        return Text(" " * width)
    v = vals[-width:]; lo, hi = min(v), max(v)
    if hi - lo < 1e-9:
        hi = lo + 1e-9
    for x in v:
        f = (x - lo) / (hi - lo)
        t.append(blocks[min(7, int(f * 8))], style=rgb(*lerp((80, 110, 140), color, f)))
    return t


def block_chart(vals, width, height, color=(0, 229, 255)):
    if not vals:
        return [Text("(no data)", style="dim")]
    v = vals[-width:]
    if len(v) < width:
        v = [v[0]] * (width - len(v)) + v
    lo, hi = min(v), max(v)
    if hi - lo < 1e-9:
        hi = lo + 1e-9
    step = len(v) / width
    cols = []
    for i in range(width):
        seg = v[int(i * step):max(int(i * step) + 1, int((i + 1) * step))]
        cols.append(sum(seg) / len(seg))
    rows = []
    for r in range(height - 1, -1, -1):
        t = Text()
        for c in cols:
            f = (c - lo) / (hi - lo)
            t.append("█" if f * (height - 1) >= r else "·",
                     style=rgb(*lerp((60, 90, 120), color, f)) if f * (height - 1) >= r else "rgb(48,48,58)")
        rows.append(t)
    return rows


def verdict(value, ok=None, warn=None, lo=None, hi=None):
    if value is None or value != value:
        return "…", "dim"
    if lo is not None or hi is not None:
        if (lo is None or value >= lo) and (hi is None or value <= hi):
            return GOOD, "bold green"
        near = (lo is not None and value >= lo * 0.85) or (hi is not None and value <= hi * 1.15)
        return (WARN, "bold yellow") if near else (BAD, "bold red")
    if ok and ok(value):
        return GOOD, "bold green"
    if warn and warn(value):
        return WARN, "bold yellow"
    return BAD, "bold red"


def metric_rows(d):
    last = d["last"]
    s = d["series"]
    def trend(key):
        v = s.get(key) or []
        return (v[-1] - v[-21]) if len(v) > 21 else None
    tr = trend("reward")
    return [
        ("回合长度", "%d 步" % (last.get("ep_len") or 0), "≥1000 步/上限2000",
         verdict(last.get("ep_len", 0), ok=lambda v: v >= 1600, warn=lambda v: v >= 800), "ep_len", (0, 229, 255)),
        ("速度跟踪成功", "%.1f%%" % (100 * last.get("success", 0)), "≥90%",
         verdict(last.get("success", 0), ok=lambda v: v >= .9, warn=lambda v: v >= .5), "success", (0, 255, 133)),
        ("线速度误差", "%.3f m/s" % last.get("err_v", 0), "≤0.75 m/s",
         verdict(last.get("err_v", 9), ok=lambda v: v <= .75, warn=lambda v: v <= 1.2), "err_v", (255, 214, 0)),
        ("角速度误差", "%.3f rad/s" % last.get("err_w", 0), "≤1.5 rad/s",
         verdict(last.get("err_w", 9), ok=lambda v: v <= 1.5, warn=lambda v: v <= 2.5), "err_w", (255, 190, 60)),
        ("高度奖励", "%.3f" % last.get("height_r", 0), "≥0.90（≈3cm内）",
         verdict(last.get("height_r", 0), ok=lambda v: v >= .90, warn=lambda v: v >= .80), "height_r", (255, 214, 0)),
        ("高度亏缺罚", "%.4f" % last.get("height_def", 0), "≥ -0.006（越低越差）",
         verdict(last.get("height_def", -1), ok=lambda v: v > -0.006, warn=lambda v: v > -0.012), "height_def", (255, 150, 90)),
        ("动作 std", "%.3f" % last.get("std", 0), "0.15–0.35",
         verdict(last.get("std", 0), lo=.15, hi=.35), "std", (255, 120, 180)),
        ("平均奖励", "%.2f" % last.get("reward", 0), "越高越好 ↑",
         verdict(tr, ok=lambda v: v > .02, warn=lambda v: v > -.02), "reward", (0, 255, 133)),
        ("闭链残差", "%.3f mm" % (1000 * (last.get("closure") or 0)), "≤2 mm",
         verdict(1000 * (last.get("closure") or 0), ok=lambda v: v <= 2, warn=lambda v: v <= 4), "closure", (140, 200, 255)),
        ("耦合残差", "%.5f rad" % (last.get("mimic") or 0), "≤0.01 rad",
         verdict(last.get("mimic") or 0, ok=lambda v: v <= .01, warn=lambda v: v <= .02), "mimic", (180, 140, 255)),
    ]


def header(d, width):
    it, total = d.get("iteration", 0), d.get("total", 1)
    live = d.get("stale_s", 999) < 90
    s = d["series"]
    fps = (s.get("fps") or [0])[-1]
    per = d.get("per_iter")
    coll = (s.get("collection_time") or [0])[-1]
    learn = (s.get("learning_time") or [0])[-1]
    t1 = Text()
    t1.append(" MOD4 本机训练监控 ", style="bold white on rgb(20,60,90)")
    t1.append("  " + (d.get("run") or ""), style="dim")
    t1.append("   " + datetime.now().strftime("%H:%M:%S") + "  ", style="white")
    t1.append(("● LIVE" if live else "✖ 停滞 %ds" % int(d.get("stale_s", 0))),
              style=("bold green" if live else "bold red"))
    t2 = Text()
    t2.append(" 迭代 ", style="dim"); t2.append(str(it), style="bold white")
    t2.append("/%d   " % total, style="dim")
    t2.append("环境 %d×%d   " % (d.get("envs", 0), d.get("steps", 0)), style="cyan")
    t2.append("已训练 " + hhmmss(d.get("elapsed")) + "   剩余 " + hhmmss(d.get("eta")), style="white")
    t3 = Text(" ")
    t3.append_text(gradient_bar(it / total if total else 0, max(20, min(55, width - 60))))
    t3.append(" %5.1f%%" % (100.0 * it / total if total else 0), style="bold yellow")
    t3.append("   检查点 %d 个（%s）" % (d.get("ckpt_count", 0), d.get("ckpt_newest", "--")), style="dim")
    t4 = Text()
    t4.append(" 步速 ", style="dim")
    t4.append("%s 步/秒" % format(fps, ",.0f"), style="bold green")
    if per:
        t4.append("   每轮 ", style="dim"); t4.append("%.1f s" % per, style="bold white")
        if "collection_time" in s or "learning_time" in s:
            t4.append("（采集 %.1f + 学习 %.1f）" % (coll, learn), style="dim")
        t4.append("   %.1f 轮/分" % (60.0 / per), style="bold cyan")
    total_steps = it * d.get("envs", 0) * d.get("steps", 0)
    t4.append("   累计 ≈ ", style="dim")
    t4.append(("%.1f M" % (total_steps / 1e6)) if total_steps else "--", style="bold magenta")
    t4.append(" 策略步", style="dim")
    return Panel(Group(t1, t2, t3, t4), border_style="rgb(0,150,200)", padding=(0, 1))


def metrics_panel(d, spark_w=26, limit=None):
    tbl = Table.grid(padding=0)
    tbl.add_column(width=14, style="bold white", no_wrap=True)
    tbl.add_column(width=12, justify="right", no_wrap=True)
    tbl.add_column(width=22, style="dim", no_wrap=True)
    tbl.add_column(width=3, no_wrap=True)
    tbl.add_column(width=spark_w, no_wrap=True)
    tbl.add_row(Text(" 指标", style="dim"), Text("当前", style="dim"), Text(" 合格线（怎样算好）", style="dim"),
                Text("", style="dim"), Text("趋势", style="dim"))
    rows_all = metric_rows(d)
    if limit:
        rows_all = rows_all[:limit]
    for lab, cur, line, (icon, style), key, color in rows_all:
        tbl.add_row(Text(" " + lab), Text(cur, style="bold " + rgb(*color)), Text(" " + line),
                    Text(icon, style=style), sparkline(d["series"].get(key) or [], spark_w, color))
    return Panel(tbl, title="[bold]指标 / 合格线 / 判定[/]", border_style="rgb(0,120,160)", padding=(0, 0))


def goals_panel(d, bar_w=22, compact=False):
    last = d["last"]
    t = Table.grid(padding=0)
    t.add_row(Text(" 进度条上的白线 = 合格线", style="dim"))
    def bar(label, val, scale, ok_frac, txt, color, lower=False):
        frac = max(0.0, min(1.0, (val / scale) if scale else 0.0))
        ok = (frac <= ok_frac) if lower else (frac >= ok_frac)
        style = "bold green" if ok else ("bold yellow" if (frac <= ok_frac * 1.35 if lower else frac >= ok_frac * 0.6) else "bold red")
        icon = "OK" if ok else ("!" if (frac <= ok_frac * 1.35 if lower else frac >= ok_frac * 0.6) else "X")
        row = Text(" " + label.ljust(11), style="white")
        tick = max(0, min(bar_w - 1, int(round(ok_frac * bar_w))))
        n = int(round(frac * bar_w))
        for i in range(bar_w):
            if i == tick:
                row.append("▏", style="bold white")
            row.append("█" if i < n else "░", style=rgb(*color) if i < n else "rgb(60,60,70)")
        row.append(" %5.1f%% " % (frac * 100), style=style)
        row.append("%s  合格线 %s" % (icon, txt), style="dim")
        return row
    t.add_row(bar("速度跟踪", last.get("success", 0), 1.0, .9, "≥90%", (0, 255, 133)))
    t.add_row(bar("高度奖励", last.get("height_r", 0), 1.0, .8, "≥0.80", (255, 214, 0)))
    t.add_row(bar("回合长度", last.get("ep_len", 0), EP_CAP, .5, "≥1000步", (0, 229, 255)))
    t.add_row(bar("线速度误差", last.get("err_v", 1.5), 1.5, .5, "≤0.75m/s", (140, 200, 255), lower=True))
    if compact:
        row = Text(" 终止：", style="dim")
        row.append("姿态崩 %.2f%%  " % (100 * last.get("term_bad", 0)), style="red")
        row.append("撞地 %.2f%%  " % (100 * last.get("term_base", 0)), style="magenta")
        row.append("超时 %.1f%%  " % (100 * last.get("term_timeout", 0)), style="green")
        row.append("(贴地终止已关闭)", style="dim")
        t.add_row(row)
    else:
        t.add_row(Text(""))
        for lab, key, color in (("姿态崩", "term_bad", (255, 90, 90)), ("贴地(已关闭)", "term_low", (255, 190, 60)),
                                ("撞地", "term_base", (255, 120, 200)), ("超时", "term_timeout", (120, 200, 120))):
            if key == "term_low":
                t.add_row(Text(" 贴地终止已关闭 → 改看「高度亏缺罚」", style="dim"))
                continue
            frac = last.get(key, 0.0); n = int(round(frac * bar_w))
            row = Text(" " + lab.ljust(9), style="white")
            row.append("█" * n, style=rgb(*color)); row.append("░" * (bar_w - n), style="rgb(60,60,70)")
            row.append(" %5.1f%%" % (frac * 100), style="bold " + rgb(*color))
            t.add_row(row)
        t.add_row(Text(" 目标：姿态崩 <10%，越少越好", style="dim"))
    return Panel(t, title="[bold]目标达成度 / 终止原因[/]", border_style="rgb(160,80,160)", padding=(0, 0))


def charts_panel(d, width):
    out = []
    for title, key, color in (("平均奖励", "reward", (0, 255, 133)), ("回合长度（越长越稳）", "ep_len", (0, 229, 255))):
        vals = d["series"].get(key) or []
        rows = block_chart(vals, width - 12, 5, color)
        tt = Text(" " + title, style="bold white")
        if vals:
            tt.append("   当前 %.2f   最好 %.2f" % (vals[-1], max(vals)), style="bold " + rgb(*color))
        g = Table.grid(padding=0)
        g.add_column(width=10, justify="right", style="dim"); g.add_column()
        for i, r in enumerate(rows):
            lab = ("%.1f" % max(vals)) if (i == 0 and vals) else (("%.1f" % min(vals)) if (i == len(rows) - 1 and vals) else "")
            g.add_row(lab, r)
        out.append(Group(tt, g, Text("")))
    return Panel(Group(*out), title="[bold]训练曲线[/]", border_style="rgb(0,120,160)", padding=(0, 0))


def footer(d, width, rows=40):
    last = d["last"]; gpu = d.get("gpu") or {}
    g1 = Text()
    g1.append(" GPU ", style="dim")
    gu = gpu.get("util", 0.0)
    g1.append_text(gradient_bar(gu / 100.0, 16, (0, 255, 133), (255, 90, 90)))
    g1.append(" %4.0f%%  " % gu, style="bold green")
    g1.append("%.1f/%.1f GiB  %.0f°C  %.0fW" % (gpu.get("used", 0) / 1024, gpu.get("total", 0) / 1024,
                                                gpu.get("temp", 0), gpu.get("power", 0)), style="white")
    g2 = Text()
    g2.append(" 闭链 %.3f mm  耦合 %.5f rad   " % (1000 * (last.get("closure") or 0), last.get("mimic") or 0), style="dim")
    g2.append("q 退出  r 刷新  窗口 %d×%d" % (width, rows), style="dim")
    return Panel(Group(g1, g2), border_style="rgb(60,60,80)", padding=(0, 1))


def build(d, width=150, rows=40):
    if d.get("error"):
        return Panel(Text(" " + d["error"], style="yellow"), title="[bold]MOD4 训练监控[/]")
    small = rows < 30
    parts = [header(d, width)]
    if width >= 132 and rows >= 36:
        two = Table.grid(expand=True); two.add_column(ratio=1); two.add_column(ratio=1)
        two.add_row(metrics_panel(d), goals_panel(d))
        parts += [two, charts_panel(d, width)]
    elif width >= 132 and rows >= 26:
        two = Table.grid(expand=True); two.add_column(ratio=1); two.add_column(ratio=1)
        two.add_row(metrics_panel(d, spark_w=16, limit=(7 if small else None)), goals_panel(d, bar_w=18, compact=(rows < 34)))
        parts.append(two)
    elif width >= 88:
        parts += [metrics_panel(d, spark_w=(14 if small else 26), limit=(7 if small else None))]
        if rows >= 22:
            parts.append(goals_panel(d, bar_w=18, compact=(rows < 34)))
    else:
        parts += [metrics_panel(d, spark_w=10, limit=4)]
    if rows < 36:
        parts.append(Text(" 窗口 %d×%d（最大化可显示完整面板与曲线）" % (width, rows), style="dim"))
    parts.append(footer(d, width, rows))
    return Group(*parts)


def _console(buf, width, color=True):
    # NOTE: this Rich build ignores Console(width=...) when a non-tty file is given; the
    # documented escape hatch is the COLUMNS/LINES environment variables.
    os.environ["COLUMNS"] = str(int(width))
    os.environ["LINES"] = "60"
    return Console(file=buf, force_terminal=True, legacy_windows=False,
                   color_system=("truecolor" if color else None), no_color=(not color))


def render_text(d, width, rows=40):
    buf = io.StringIO()
    _console(buf, width, True).print(build(d, width, rows))
    return buf.getvalue()


def snapshot_text(d, width, rows=40):
    buf = io.StringIO()
    _console(buf, width, False).print(build(d, width, rows))
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", default=DEFAULT_RUN)
    ap.add_argument("--source", choices=("events", "log"), default="events",
                    help="events: 读本机 tfevents; log: 读训练 stdout 日志（远端镜像用）")
    ap.add_argument("--log", default=None, help="--source log 时的训练日志路径")
    ap.add_argument("--gpu-json", default=None, help="读远端 nvidia-smi 快照 JSON（本地镜像写）")
    ap.add_argument("--ckpt-json", default=None, help="读远端 checkpoint 名字 JSON（本地镜像写）")
    ap.add_argument("--total", type=int, default=3000)
    ap.add_argument("--envs", type=int, default=4096)
    ap.add_argument("--steps", type=int, default=24)
    ap.add_argument("--interval", type=float, default=2.0)
    ap.add_argument("--width", type=int, default=0, help="0 = follow terminal width")
    ap.add_argument("--rows", type=int, default=0,
                    help="frame height cap; 0 = auto (capped at 26 so it fits every window)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--snapshot", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_frame.txt"))
    a = ap.parse_args()
    enable_console()
    global GPU_JSON, CKPT_JSON
    GPU_JSON, CKPT_JSON = a.gpu_json, a.ckpt_json
    if a.source == "log":
        if not a.log:
            raise SystemExit("--source log 需要 --log <path>")
        mon = LogMonitor(a.log, a.total, a.envs, a.steps, ckpt_json=a.ckpt_json)
    else:
        mon = Monitor(a.run_root, a.total, a.envs, a.steps)
    if a.once:
        d = mon.refresh()
        ox, oy, cw, ch = console_view()
        w = a.width or max(80, cw)
        h = a.rows or ch
        sys.stdout.write(render_text(d, w, h))
        return
    while True:
        d = mon.refresh()
        try:
            ox, oy, cw, ch = console_view()
        except ConsoleGone:
            return
        w = a.width or max(60, cw)
        # 控制台自报高度（含 DPI 缩放）常大于真实可见行数；26 行以内的紧凑版在任何窗口都塞得下
        ch = min(a.rows or 26, ch)
        try:
            frame = render_text(d, w, ch)
            write_frame(frame, ox, oy, w, ch)
        except ConsoleGone:
            return
        except Exception:
            import traceback
            with open(os.path.join(os.path.dirname(a.snapshot), "tui_error.log"), "w", encoding="utf-8") as fh:
                traceback.print_exc(file=fh)
            try:
                write_frame(snapshot_text(d, w, ch), ox, oy, w, ch)
            except ConsoleGone:
                return
        try:
            with open(a.snapshot, "w", encoding="utf-8") as fh:
                fh.write(snapshot_text(d, w, ch))
        except Exception:
            pass
        t0 = time.time()
        while time.time() - t0 < a.interval:
            try:
                import msvcrt
                if msvcrt.kbhit():
                    k = msvcrt.getch().lower()
                    if k == b"q":
                        sys.stdout.write("\x1b[2J\x1b[H"); sys.stdout.flush(); return
                    if k == b"r":
                        break
            except Exception:
                pass
            time.sleep(0.05)


if __name__ == "__main__":
    main()
