"""CorrectR15APIerror in NEWsource, addpartialerrortrace, mathpreflight0steps."""
from pathlib import Path
import ast,numpy as np
from physics_bridge import geometry
R=Path(__file__).resolve().parent;g=geometry()
for s in('left','right'):
 _,_,J,_=g.wheel_kinematics(.45417412979711813,-.0415098680723735,0.,0.,0.,np.zeros(3),s);assert J.shape==(3,2)and np.isfinite(J).all();assert np.linalg.matrix_rank(J[[0,2],:])==2
src=(R/'run_jump270_roll_v2.py').read_text(encoding='utf-8');old='J=est.geom.jacobian(float(qq[0]),float(qq[1]),side)[:3,:];';assert old in src;src=src.replace(old,'_,_,J,_=est.geom.wheel_kinematics(float(qq[0]),float(qq[1]),0.,0.,0.,np.zeros(3),side);');old="except BaseException:dump(out/'ERROR.json',dict(error=traceback.format_exc(),controls=len(rows),physics_steps=None if p is None else p.tick_phys));raise";assert old in src
new="""except BaseException:
  error=traceback.format_exc();ph=hashlib.sha256();nb=0
  with(out/'partial_trace.jsonl').open('xb')as f:
   for rr in rows:
    bb=(json.dumps(rr,separators=(',',':'),allow_nan=False)+'\\n').encode('utf-8');f.write(bb);ph.update(bb);nb+=len(bb)
  dump(out/'ERROR.json',dict(error=error,controls=len(rows),physics_steps=None if p is None else p.tick_phys,partial_trace={'path':str(out/'partial_trace.jsonl'),'bytes':nb,'SHA':ph.hexdigest()}));raise"""
src=src.replace(old,new).replace("ROOT/'prepare_jump_roll_v2.py',","ROOT/'prepare_jump_roll_v2.py',ROOT/'prepare_jump_roll_v3.py',");ast.parse(src);p=R/'run_jump270_roll_v3.py';assert not p.exists();p.write_text(src,encoding='utf-8',newline='\n');print('MATH_API_PREFLIGHT_PASS_0STEPS',p)
