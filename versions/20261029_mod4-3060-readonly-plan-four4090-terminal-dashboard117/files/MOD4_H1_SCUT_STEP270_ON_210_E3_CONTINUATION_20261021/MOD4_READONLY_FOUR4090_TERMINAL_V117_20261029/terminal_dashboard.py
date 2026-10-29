"""3060-host visible terminal. Reads a local snapshot only; no SSH/model/GPU work."""
from pathlib import Path
import ctypes,json,math,os,sys,time,unicodedata
HERE=Path(__file__).resolve().parent
def width(s):return sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in s)
def spark(values,n=48):
    values=[float(v) for v in values if v is not None and math.isfinite(float(v))]
    if not values:return '无有效数据'
    if len(values)>n:values=[values[round(i*(len(values)-1)/(n-1))] for i in range(n)]
    lo,hi=min(values),max(values);chars='▁▂▃▄▅▆▇█'
    return ''.join(chars[0 if hi-lo<1e-12 else min(7,int((v-lo)/(hi-lo)*7))] for v in values)+f'  [{lo:.4g},{hi:.4g}] now={values[-1]:.5g}'
def main():
    k=ctypes.WinDLL('kernel32');u=ctypes.WinDLL('user32')
    k.GetConsoleWindow.restype=ctypes.c_void_p
    hwnd=k.GetConsoleWindow()
    if not hwnd:k.AllocConsole();hwnd=k.GetConsoleWindow()
    if hwnd:
        u.ShowWindow.argtypes=[ctypes.c_void_p,ctypes.c_int];u.ShowWindow(hwnd,5)
        k.SetConsoleOutputCP(65001);k.SetConsoleTitleW('MOD4 总计划 / 四张4090 / H1奖励曲线 - 只读监控 V117')
        try:
            handle=k.GetStdHandle(-11);mode=ctypes.c_ulong();k.GetConsoleMode(handle,ctypes.byref(mode));k.SetConsoleMode(handle,mode.value|4)
        except Exception:pass
        try:
            from ctypes import wintypes
            class Coord(ctypes.Structure):_fields_=[('X',ctypes.c_short),('Y',ctypes.c_short)]
            class Rect(ctypes.Structure):_fields_=[('Left',ctypes.c_short),('Top',ctypes.c_short),('Right',ctypes.c_short),('Bottom',ctypes.c_short)]
            k.GetStdHandle.restype=wintypes.HANDLE
            handle=k.GetStdHandle(-11)
            k.SetConsoleScreenBufferSize.argtypes=[wintypes.HANDLE,Coord]
            k.SetConsoleWindowInfo.argtypes=[wintypes.HANDLE,wintypes.BOOL,ctypes.POINTER(Rect)]
            k.SetConsoleScreenBufferSize(handle,Coord(160,1000));rect=Rect(0,0,159,49);k.SetConsoleWindowInfo(handle,True,ctypes.byref(rect))
        except Exception:pass
    sys.stdout.reconfigure(encoding='utf8',errors='replace')
    import psutil
    p=psutil.Process();sid=ctypes.c_ulong();k.ProcessIdToSessionId(p.pid,ctypes.byref(sid))
    receipt=dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd(),session_id=sid.value,own_console_handle=int(hwnd or 0),visible_console_requested=True,local_snapshot_only=True,no_network_or_model_or_GPU_queries=True)
    (HERE/'TERMINAL_ACTUAL_STARTED.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    started=time.monotonic()
    while time.monotonic()-started<7200:
        try:
            j=json.loads((HERE/'monitor_snapshot.json').read_bytes());age=time.time()-j['epoch'];lines=[]
            lines.append('MOD4 只读总览 | 北京时间 '+time.strftime('%Y-%m-%d %H:%M:%S')+f' | 数据采集距今 {age:.0f}s')
            lines.append('当前阶段：H1 指令/双轮270mm高度 reward116 有限学习；270mm跨台落稳：尚未验收通过')
            lines.append('总计划：400N/时钟统一[适配模型通过] → 旧专家逐项验收[进行中] → H1真实270mm[进行中] → typed WM数据/整合验收[待完成]')
            lines.append('已知范围：E0完整指令观测通过；W35/E2/E3尚非全技能毕业；gating18配置不等于18个独立专家毕业。')
            lines.append('='*132)
            lines.append('4090资源与任务（占用只读；不查询未知PID、不动第三方；采样时刻见各主机数据）')
            for host in j['hosts']:
                if not host.get('passed'):
                    lines.append(host['label']+' 采集不可用：'+host.get('error','unknown'));continue
                for gpu in host.get('gpus',[]):
                    idx=gpu['index'];job=next((x for x in host.get('jobs',[]) if x.get('GPU_UUID')==gpu['uuid']),None)
                    task=job['label'] if job else ('无已知在运行的MOD4任务；占用来源不识别' if gpu.get('utilization',0)>0 or gpu.get('compute_UUID_rows',0)>0 else '无已知MOD4任务；此采样利用率低')
                    life='' if not job else ' / '+job.get('known_process_state','unknown')
                    lines.append(f"{host['label']:12s} GPU{idx} {gpu['used_MiB']:5d}/{gpu['total_MiB']}MiB util={gpu['utilization']:3d}%  {task}{life}")
            lines.append('-'*132)
            lines.append('STEP速度：100Hz/50Hz为仿真控制频率；下面是墙钟实测，不能混称。')
            for host in j['hosts']:
                for job in host.get('jobs',[]):
                    speed=job.get('speed')
                    if speed:lines.append(f"{job['label']}  control/s={speed['controls_per_wall_second']:.3f}  env-transitions/s={speed['transitions_per_wall_second']:.1f}  physics-callback/s={speed['callbacks_per_wall_second']:.3f}  WM/s={speed['WM_per_second']:.2f} Pi/s={speed['Pi_per_second']:.3f}")
                    else:lines.append(job['label']+'  墙钟STEP速度：无连续计数，保持未知；不以配置Hz代替')
            lines.append('-'*132)
            lines.append('H1实际优化分项曲线 / 仅116，最近日志记录，按记录抽样非等间隔；每点是单control的全4096环境均值')
            names=[('total','总奖励'),('command_world_velocity','世界速度指令'),('both_wheel_height_270_with_forward_command','两轮270mm高度'),('supported_top_landing','台面支撑落地'),('supported_top_quiet','台上静稳'),('original_nonrequest_recovery','请求前恢复')]
            for host in j['hosts']:
                for job in host.get('jobs',[]):
                    curve=job.get('curve',[])
                    if not curve:continue
                    last=curve[-1];lines.append(job['label']+f" | control={last['controls']} WM={last['WM']} Pi={last['Pi']} | crossing/land/stable={last.get('cross',0)}/{last.get('land',0)}/{last.get('stable',0)}")
                    for key,label in names:lines.append('  '+label.ljust(13)+' '+spark([r.get('terms',{}).get(key) for r in curve]))
            lines.append('='*132)
            lines.append('高度项=两轮轮底真实净空追踪270mm，并要求靠近台沿且向前运动；旧flight/jump_reward为诊断，不是优化目标。')
            lines.append('本轮116：19:02:53计划保存 /19:07:53计划结束；时间不是成功证据。尚需真实跨台、全轮落台、稳定0.5秒。')
            lines.append('数据源：各主机GPU统计+仅已知本方进程身份+原始日志缩减快照。关闭此窗口不会停止训练。Ctrl+C关闭。')
            lines.append('采集器：'+j.get('sampler_status','本次有限串行采集')+'；本终端只读本地JSON，每2秒重绘。')
            sys.stdout.write('\033[H\033[2J'+'\n'.join(lines)+'\n');sys.stdout.flush()
        except (FileNotFoundError,json.JSONDecodeError):print('等待第一份已核验快照……',flush=True)
        time.sleep(2)
    (HERE/'TERMINAL_ACTUAL_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),only_own_terminal=True)),encoding='utf8')
if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:pass
