import io, ast
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
a = "period = 1.0 / args.rate\nk = 0"
assert a in t
t = t.replace(a, "period = 1.0 / args.rate\nk = 0\n\n"
                 "import signal\n"
                 "signal.signal(signal.SIGTERM, lambda *a: (_ for _ in ()).throw(KeyboardInterrupt()))\n")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
ast.parse(t); print("SIGTERM now flushes the video")
