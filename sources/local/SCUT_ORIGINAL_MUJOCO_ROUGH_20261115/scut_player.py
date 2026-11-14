"""Reuse the project's existing WASD MuJoCo control window with SCUT's own robot."""
from pathlib import Path
import argparse, json, subprocess, sys, time, tkinter as tk, traceback
import scut_backend as backend
from scut_backend import SCUTReplay, HERE, VIEWER, RUNTIME, CHECKPOINT, checksum
import manual_control

# Isolate this run's status output from the frozen MOD4 delivery.
manual_control.Replay=SCUTReplay
manual_control.B=RUNTIME
manual_control.EXPECTED=checksum(CHECKPOINT)


class OriginalSCUTControl(manual_control.ManualRoughControl):
    def _build(self):
        super()._build()
        self.root.title('华南虎原模型 · MuJoCo WASD · Rough／台阶／空格起跳')
        self.root.geometry('560x835+10+15')
        self._rewrite_labels(self.root)
        self._jump_button=None
        row=tk.Frame(self.root,bg=self.BG,padx=14)
        row.pack(fill='x',before=self.root.winfo_children()[0])
        tk.Label(row,text='SCUT V14_2 · 公开预训练模型',bg=self.BG,fg=self.YELLOW,font=('Microsoft YaHei UI',11,'bold')).pack(anchor='w')
        tk.Label(row,text='2026-07-23_16-23-21 / model_1000.pt',bg=self.BG,fg=self.MUTED,font=('Consolas',10)).pack(anchor='w')

    def _rewrite_labels(self,widget):
        for child in widget.winfo_children():
            try: text=str(child.cget('text'))
            except tk.TclError: text=''
            if text=='Rough-v1 120m · 手动驾驶与高度控制':child.configure(text='华南虎 · 原有 WASD 手动播放器')
            elif text=='空格 停车':child.configure(text='空格 起跳指令',command=self._jump)
            elif '空格停车' in text:child.configure(text='Q / E 降低／升高；1 / 2 / 3 高度预设\nWASD 驾驶；P 暂停；空格跳跃指令；K 停车；R 复位')
            self._rewrite_labels(child)

    def _handle_key_down(self,key):
        if key=='space':
            if key not in self.keys:
                self.keys.add(key);self._jump()
            return
        if key=='k':
            self._stop();return
        super()._handle_key_down(key)

    def _jump(self):
        self.sim.trigger_jump()
        self._event('空格：发送跳跃模式指令，保留当前 WASD 速度')
        self._focus_control()

    def open_map(self):
        log=(HERE/'evidence/full_map.log').open('w',encoding='utf-8')
        subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(HERE/'scut_player.py'),'--map'],cwd=HERE,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000)

    def _update_ui(self):
        self.sim.args.vx=float(self.speed_var.get());self.sim.args.wz=float(self.turn_var.get())
        if not self._is_control_foreground():
            self.keys.clear();self.sim.cmd_vx=0.;self.sim.cmd_vy=0.;self.sim.cmd_wz=0.
        self._sync_height_widgets()
        state='暂停：按 P 开始' if self.sim.paused else '运行：WASD / 按钮驾驶'
        self.status_var.set(f'{state}\n前进指令 {self.sim.cmd_vx:+.2f} / 实速 {self.sim.env.vx:+.2f} m/s\n转向指令 {self.sim.cmd_wz:+.2f} rad/s\n高度指令 {self.sim.height:.3f} / 离地 {self.sim.z:.3f} m\n闭链 {self.sim.closure*1000:.3f} mm / 重置 {self.sim.reset_count-1}\n{self.sim.last_jump}\n{self.sim.reason or self.last_event}')
        if self.sim.viewer is not None:
            x,y=self.sim.d.qpos[:2];self.sim.viewer.cam.lookat[:]=[x+.6,y,self.sim.ground(x,y)+.25]
        now=time.monotonic()
        if now-self._last_status_write>.5:
            value=dict(manual=True,autoplay=False,paused=self.sim.paused,family=self.sim.family,level=self.sim.level,keys=sorted(self.keys),height_command=self.sim.height,height_measured=self.sim.z,cmd_vx=self.sim.cmd_vx,cmd_wz=self.sim.cmd_wz,vx=float(self.sim.env.vx),physics_time=float(self.sim.d.time),closure=self.sim.closure,checkpoint=str(CHECKPOINT),checkpoint_sha256=self.sim.checkpoint_sha,plant=str(backend.PLANT),jump_requests=self.sim.jump_requests,jump_remaining=self.sim.jump_remaining,jump_status=self.sim.last_jump,jump_external_impulse=False,epoch=time.time())
            (RUNTIME/'MANUAL_STATUS.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');self._last_status_write=now


def run():
    root=tk.Tk();sim=SCUTReplay(show=True);sim.paused=True
    app=OriginalSCUTControl(root,sim)
    root.after(200,app._focus_control)
    print('SCUT_WASD_PLAYER_READY',json.dumps(dict(paused=True,autoplay=False,checkpoint=str(CHECKPOINT),checkpoint_sha256=sim.checkpoint_sha,space='jump mode request; velocity retained; no external impulse')),flush=True)
    root.mainloop()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--map',action='store_true');a=p.parse_args()
    try:
        if a.map:
            backend.showcase.B=RUNTIME;backend.showcase.meshfile=backend.mesh_file
            backend.showcase.map_view()
        else:run()
    except Exception:
        (HERE/'evidence/PLAYER_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise

