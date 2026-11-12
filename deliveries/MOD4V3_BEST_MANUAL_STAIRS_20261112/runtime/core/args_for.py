from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[2]
def args_for(ckpt):
 return argparse.Namespace(ckpt=ckpt,template=str(Path(__file__).resolve().parent/'template_spec.json'),xml=str(ROOT/'plant/MOD4v3_HW300N60_R3/mjcf/scene.xml'),runtime=str(ROOT/'plant/MOD4v3_HW300N60_R3/runtime_config.json'),semantics=str(ROOT/'plant/MOD4v3_HW300N60_R3/semantics.json'),bank=str(ROOT/'plant/reset_bank.json'),device='cpu',height=.28,vx=.9,vy=0.,wz=1.2,term_height=.18,fall_interval=7.,drop_height=1.,drop_tilt=.75,action_ema=0.,start_fall=False,auto_fall=False,headless=True,steps=0,log_every=100)
