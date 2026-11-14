"""Open the frozen comprehensive MOD4 policy alongside the SCUT window."""
from pathlib import Path
import hashlib,json,sys,tkinter as tk,subprocess,traceback
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DELIVERY=REPO/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
BEST=REPO/'deliveries/MOD4V3_BEST_COMPREHENSIVE_20261113/model_full_ppo.pt'
SHA='db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283'
assert hashlib.sha256(BEST.read_bytes()).hexdigest()==SHA
sys.path.insert(0,str(DELIVERY/'viewer'))
import showcase as show
import manual_control as controls
show.CKPT=BEST;show.EXPECTED=SHA
# Reuse the already repaired guards for this comprehensive parent's training recipe.
sys.path.insert(0,str(REPO/'sources/local/MOD4V3_STAIRS_MAX_HEIGHT_40M_20261113/manual_replay'))
from replay_training_guards import replay_step
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=HERE/'runtime_mod4/reset_events')
OUT=HERE/'runtime_mod4';OUT.mkdir(exist_ok=True)
controls.B=OUT;controls.EXPECTED=SHA

class BestControl(controls.ManualRoughControl):
    def _build(self):
        super()._build()
        self.root.title('我们的综合最优 · 11月13日最牛逼模型 · db6e9ccf')
        self.root.geometry('550x770+580+25')
        self._labels(self.root)
    def _labels(self,w):
        for child in w.winfo_children():
            try:text=str(child.cget('text'))
            except tk.TclError:text=''
            if text=='Rough-v1 120m · 手动驾驶与高度控制':child.configure(text='我们的综合最优 · 11月13日 · db6e9ccf')
            self._labels(child)
    def open_map(self):
        log=(HERE/'evidence/full_map.log').open('a',encoding='utf-8')
        subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(HERE/'scut_player.py'),'--map'],cwd=HERE,stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000)

if __name__=='__main__':
    try:
        root=tk.Tk();sim=show.Replay(show=True);sim.paused=True
        app=BestControl(root,sim)
        root.after(200,app._focus_control)
        print('BEST_MOD4_MANUAL_PLAYER_READY',json.dumps(dict(checkpoint=str(BEST),sha256=SHA,paused=True,autoplay=False,guard='original comprehensive parent training guards, duration0.2s and closure2mm',scut_window_preserved=True)),flush=True)
        root.mainloop()
    except Exception:
        (HERE/'evidence/BEST_PLAYER_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
