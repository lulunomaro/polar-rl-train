import io
F=r"D:\claude2\fangzhen\scripts\passive_range_solver.py"
s=io.open(F,encoding="utf-8").read()
s=s.replace('name = {"rear2": "shank", "front2": "link2", "front3": "link3", "front4": "link4",\n           "spring1": "spring1"}',
            'name = {"rear2": "shank", "front2": "link2", "front3": "link3", "front4": "link4",\n'
            '           "spring1": "spring1", "spring2": "spring2"}')
s=s.replace('    c = cur.get(name[k])',
            '    c = cur.get(name[k])\n'
            '    if k == "spring2":\n'
            '        c = ("-0.030", "0.085")   # SPRING_SLIDE, metres of slider travel')
s=s.replace('    flag = ""\n    if c:',
            '    flag = ""\n    if c and k != "spring2":')
s=s.replace('    if c:\n        cl, ch = float(c[0]), float(c[1])',
            '    if c:\n        cl, ch = float(c[0]), float(c[1])')
s=s.replace('    print("  %-8s %-26s [%+8.4f %+8.4f]      (%+.2f, %+.2f)%s" %\n'
            '          (k, str(c), a, b, lo, hi, flag))',
            '    print("  %-8s %-26s [%+9.4f %+9.4f]      (%+.4f, %+.4f)%s" %\n'
            '          (k, str(c), a, b, lo, hi, flag))')
io.open(F,"w",encoding="utf-8").write(s)
print("spring2 reporting fixed")