import io
F=r"D:\claude2\fangzhen\scripts\baseline_record.py"
s=io.open(F,encoding="utf-8").read()
helper = '''    def flat_or_grouped(container):
        items = getattr(container, "items", None)
        data = dict(items()) if callable(items) else dict(container)
        out = {}
        for k, v in data.items():
            inner = getattr(v, "terms", None)
            if isinstance(inner, dict):
                out[k] = {n: cfg_of(t) for n, t in inner.items()}
            else:
                out[k] = cfg_of(v)
        return out

'''
# drop any existing (mis-placed) definition, then insert it right after cfg_of
marker = "    def flat_or_grouped(container):"
while marker in s:
    i = s.index(marker); j = s.index("\n\n", i) + 2
    s = s[:i] + s[j:]
anchor = "    out[\"actions\"] = flat_or_grouped(cfg.actions)"
assert anchor in s, "actions anchor missing"
s = s.replace(anchor, helper + anchor, 1)
io.open(F,"w",encoding="utf-8").write(s)
print("flat_or_grouped hoisted above first use")