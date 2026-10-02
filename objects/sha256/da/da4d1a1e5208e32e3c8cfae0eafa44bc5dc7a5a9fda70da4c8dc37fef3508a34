import io, ast
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
L = io.open(p, encoding="utf-8").read().split("\n")
i = next(k for k, l in enumerate(L) if l.strip().startswith("imu = acc + gyro"))
L[i] = ("        # real_bridge remaps the wire quaternion as (x,y,z,w) -> (-y, x, z, w)\n"
        "        # (the H7 IMU is mounted rotated 90 deg about z), so the firmware must\n"
        "        # pre-invert that map to deliver the base-frame attitude.\n"
        "        imu = acc + gyro + [qw[2], -qw[1], qw[3], qw[0]]")
t = "\n".join(L)
ast.parse(t)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("patched quaternion pre-transform")
