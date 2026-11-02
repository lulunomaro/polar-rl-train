"""PreservefirststaticAPIerror; useactualLinkageGeometry.pose side names.
No dynamics/consumedrobotcases. Retryonly0Stepstaticunitinnewattempt.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;D=R/'revisions/attempt001';D.mkdir(parents=True,exist_ok=False)
p=R/'front_geometry.py';old=p.read_bytes();(D/p.name).write_bytes(old);s=old.decode('utf-8');needle="geometry.wheel_kinematics(q[2*i], q[2*i+1], 0., 0., 0., np.zeros(3), i)[1]";assert needle in s;s=s.replace(needle,"geometry.pose(q[2*i], q[2*i+1], ('left', 'right')[i])[0]");ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
s=(R/'static_qa.py').read_text(encoding='utf-8').replace("D=HERE/'attempts/001'","D=HERE/'attempts/002'");ast.parse(s);p=R/'static_qa_v2.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n');print('STATIC_API_FIX_SOURCE_PRESERVED_0STEPS')
