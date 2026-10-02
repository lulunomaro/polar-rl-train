
# Emit the RMUC2026 7v7 field as a MuJoCo scene, from the SAME measured JSON that
# isaac/rmuc2026_field.py and train/rmvehicle/.../field_cfg.py use
# (cad/out_map/field_dims.json <- RMUC2026_V2.0.0.stp).
#
#   python scripts/make_rmuc2026_field.py            -> robot/out_cc_linkfix/field_cc.xml
import io, json, math, os, sys
ROOT = r'D:/claude2/fangzhen'
DIMS = os.path.join(ROOT, 'cad', 'out_map', 'field_dims.json')
OUT = os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'field_cc.xml')
PLANT = 'rm_vehicle_cc.xml'
CAP = float(os.environ.get('RM_TERRAIN_CAP_H', '0.20'))
D = dict(field_size_m=[29.75, 16.0], slope_deg=[9.4, 25.0], step_height_m=[0.02, 0.22],
         step_run_m=[0.15, 1.084], obstacle_height_m=[0.074, 0.416], obstacle_width_m=[0.2, 1.088],
         slope_median_deg=12.1)
if os.path.isfile(DIMS):
    D.update(json.load(open(DIMS, encoding='utf-8')))

fx, fy = D['field_size_m']
s_med = float(D['slope_median_deg'])
s_max = float(D['slope_deg'][1])
h = min(float(D['step_height_m'][1]), CAP)
run = min(max(float(D['step_run_m'][0]), 0.28), 0.45)
o_cap = min(float(D['obstacle_height_m'][1]), CAP)
o_wall = float(D['obstacle_height_m'][1])
W = 6.0
X0 = 6.0
g = []
g.append('    <geom name="arena" type="box" size="%.3f %.3f 0.05" pos="%.3f 0 -0.05" '
         'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.34 0.37 0.42 1"/>'
         % (fx / 2, fy / 2, fx / 2 - 2.0))
x = X0
n = 5
for i in range(n):
    hh = (i + 1) * h
    g.append('    <geom name="stair_%d" type="box" size="%.3f %.3f %.3f" pos="%.3f 0 %.3f" '
             'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.48 0.53 0.60 1"/>'
             % (i, run / 2, W / 2, hh / 2, x + i * run, hh / 2))
x += n * run + 1.2
top = n * h
L = top / math.tan(math.radians(s_med))
c = math.cos(math.radians(s_med)); sn = math.sin(math.radians(s_med))
g.append('    <geom name="ramp_down" type="box" size="%.3f %.3f 0.03" pos="%.3f 0 %.3f" zaxis="%.4f 0 %.4f" '
         'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.50 0.55 0.62 1"/>'
         % (math.hypot(L, top) / 2, W / 2, x + L / 2, top / 2, -sn, c))
x += L + 1.2
H = 1.2
L2 = H / math.tan(math.radians(s_max))
c2 = math.cos(math.radians(s_max)); s2 = math.sin(math.radians(s_max))
g.append('    <geom name="ramp_up" type="box" size="%.3f %.3f 0.03" pos="%.3f 0 %.3f" zaxis="%.4f 0 %.4f" '
         'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.50 0.55 0.62 1"/>'
         % (math.hypot(L2, H) / 2, W / 2, x + L2 / 2, H / 2, s2, c2))
x += L2 + 0.6
g.append('    <geom name="highland" type="box" size="1.0 %.3f %.3f" pos="%.3f 0 %.3f" '
         'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.55 0.60 0.66 1"/>'
         % (W / 2, H / 2, x + 1.0, H / 2))
x += 2.6
for k, hh in enumerate((o_cap, o_wall)):
    g.append('    <geom name="barricade_%d" type="box" size="0.10 %.3f %.3f" pos="%.3f 0 %.3f" '
             'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.62 0.50 0.42 1"/>'
             % (k, W / 2, hh / 2, x + k * 1.4, hh / 2))
scene = io.open(os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'scene_cc.xml'), encoding='utf-8').read()
import re
kf = re.search(r'<keyframe>.*?</keyframe>', scene, re.S).group(0)
txt = ('<mujoco model="rm_vehicle_cc on RMUC2026 7v7 field (measured from RMUC2026_V2.0.0.stp)">\n'
       '  <include file="' + PLANT + '"/>\n'
       '  <visual><global offwidth="1400" offheight="800"/>\n'
       '    <headlight ambient="0.42 0.42 0.44" diffuse="0.55 0.55 0.55" specular="0.2 0.2 0.2"/>\n'
       '    <map znear="0.02"/></visual>\n'
       '  <asset><texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" rgb2="0.25 0.28 0.33" width="256" height="256"/></asset>\n'
       '  <worldbody>\n' + chr(10).join(g) + '\n'
       '    <camera name="field" pos="1.2 -7.5 2.6" xyaxes="1 0 0 0 0.35 0.94" mode="fixed"/>\n'
       '    <camera name="side" pos="6 -6 0.9" xyaxes="1 0 0 0 0 1" mode="fixed"/>\n'
       '    <light name="key" pos="8 -6 6" dir="-0.2 0.2 -1" diffuse="0.9 0.9 0.9" cutoff="60"/>\n'
       '  </worldbody>\n  ' + kf + '\n</mujoco>\n')
io.open(OUT, 'w', encoding='utf-8', newline=chr(10)).write(txt)
print('wrote', OUT)
print('field: arena %.1fx%.1f m | stairs %dx%.3f m | ramp %.1f/%.1f deg | barricade %.3f + %.3f m | features %d'
      % (fx, fy, n, h, s_med, s_max, o_cap, o_wall, len(g)))
