"""Newsource-alignednominalcrouch/landinggains for270mmwork. Zero mj_step.
This isnotjumpqualification. Oldcontrollerparameters arereferences, notsuccess.
"""
from pathlib import Path
import json,time,hashlib
import numpy as np,mujoco
from physics_bridge import RobustPlant,serialize_gain,ROOT,MODEL_SHA
D=ROOT/'JUMP270_V1';D.mkdir(exist_ok=False);p=RobustPlant(True);bank={};start=time.perf_counter()
for label,delta in(('crouch',-.4956839978694916),('landing',-.4)):
 g=p.full_lqr(delta);bank[label]=serialize_gain(g)
source=ROOT.parent/'traditional_control_20261101/results/FINAL_EVIDENCE_V2/controllers.json';ref=json.loads(source.read_bytes())['lqr'];out=dict(kind='NOMINALNEWASSET_JUMP_GAIN_BANK_NOT_PHYSICAL_SKILL',model_SHA=MODEL_SHA,engine=mujoco.__version__,physics_steps=0,gains=bank,reference_parameters=ref,reference_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),wall_s=time.perf_counter()-start,notes=['Oldhybridusedworld/contacttruthandcylinderradius; thisstageonlyreusesexplicitphaseparameterreference.','Newcontrollerneedsensor-onlyflight/contactFSMandexactmeshgrading.','NoDRsample/recovery/jumprollout/hardwarequalificationinthisscript.']);(D/'GAIN_BANK.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'gains':{k:{'q':v['q'],'tau':v['tau']}for k,v in bank.items()},'wall':out['wall_s'],'physics_steps':0},indent=2))
