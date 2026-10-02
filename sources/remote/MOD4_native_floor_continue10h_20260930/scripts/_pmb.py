import io
for a, b in [
    (r"D:/claude2/fangzhen/sim2real/run_sim2real.sh",
     [("--link /tmp/wheelbipe_h7", "--link /dev/wheelbipe_h7"),
      ("[[ -e /tmp/wheelbipe_h7 ]]", "[[ -e /dev/wheelbipe_h7 ]]"),
      ("ls -l /tmp/wheelbipe_h7", "ls -l /dev/wheelbipe_h7"),
      ("real_serial_port:=/tmp/wheelbipe_h7", "real_serial_port:=/dev/wheelbipe_h7")]),
]:
    t = io.open(a, encoding="utf-8").read()
    for x, y in b:
        if x not in t:
            print("MISS", x)
        t = t.replace(x, y)
    io.open(a, "w", encoding="utf-8", newline="\n").write(t)
    print("patched", a)
