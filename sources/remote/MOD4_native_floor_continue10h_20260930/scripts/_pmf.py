import io
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("imu = acc + gyro + [qw[1], qw[2], qw[3], qw[0]]",
              "imu = acc + gyro + (list(qw) if os.environ.get(\"H7_QW_WXYZ\") else "
              "[qw[1], qw[2], qw[3], qw[0]])")
t = t.replace('import argparse, math, os, struct, sys, time',
              'import argparse, math, os, struct, sys, time')
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("quaternion order now switchable via H7_QW_WXYZ=1")
