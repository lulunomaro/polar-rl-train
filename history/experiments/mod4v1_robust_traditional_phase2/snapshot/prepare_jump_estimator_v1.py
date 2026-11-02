"""Newjump-onlysensorvariant; no frozennormal/spin source edits.
Wheelmeasurement andgroundnoslipconstraint canbeexplicitlydisabled inairmode.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;p=R/'sensor_core_jump_v1.py';assert not p.exists();s=(R/'sensor_core_v4.py').read_text(encoding='utf-8');s=s.replace('self.upright_prior=upright_prior;','self.wheel_measurement_enabled=True;self.ground_kinematic_constraint_enabled=True;self.upright_prior=upright_prior;',1).replace('if self.accel_reference=="wheel_midpoint":','if self.accel_reference=="wheel_midpoint"and self.ground_kinematic_constraint_enabled:');needle='K=self.P[:,0]/S;';assert needle in s;s=s.replace(needle,'K=self.P[:,0]/S if self.wheel_measurement_enabled else np.zeros(2);');ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');print(p)
