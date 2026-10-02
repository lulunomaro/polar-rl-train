import io, ast
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
a = 'imu = acc + gyro + [qw[1], qw[2], qw[3], qw[0]]'
b = ('# real_bridge remaps the wire quaternion as (x,y,z,w) -> (-y, x, z, w) before\n'
     '# publishing it (the H7 board sits rotated 90 deg about z on the real robot), so\n'
     '# the firmware has to pre-invert that map to deliver the base-frame attitude.\n'
     'imu = acc + gyro + [qw[2], -qw[1], qw[3], qw[0]]')
assert a in t
t = t.replace(a, b)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
ast.parse(t); print("quaternion pre-transform fixed")
