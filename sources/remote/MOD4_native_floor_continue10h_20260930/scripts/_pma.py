import io, os
for p in [r"D:/claude2/fangzhen/sim2real/run_sim2real.sh", r"D:/claude2/fangzhen/sim2real/mock_h7.py",
          r"D:/claude2/fangzhen/sim2real/telem.py"]:
    t = io.open(p, encoding="utf-8").read().replace("\r\n", "\n").replace("\r", "\n")
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("LF", os.path.basename(p))
