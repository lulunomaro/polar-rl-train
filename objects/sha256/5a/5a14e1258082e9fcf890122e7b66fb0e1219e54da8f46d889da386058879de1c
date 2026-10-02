import json,re,numpy as np,yaml,collections
ROOT=r"D:\claude2\fangzhen"
spec=yaml.safe_load(open(ROOT+r"\robot\vehicle.spec.yaml",encoding="utf-8"))
R=np.array(spec["frame"]["rot"],float); t=-R@np.array(spec["frame"]["origin_cad"],float)
man=json.load(open(ROOT+r"\cad\out\vehicle\manifest.json",encoding="utf-8"))["solids"]
BODY_RULES=[("wheel",[r"24\s+轮毂",r"包胶_2",r"24\s+1_1$",r"外圈铝件",r"行星架端盖",r"双联行星齿",r"太阳齿加固",r"输入齿轮装配",r"id2",r"后轴承座"]),
("shank",[r"24\s+二级腿$",r"二级腿锁盖",r"膝关节",r"连杆轴承座",r"30\.2-39",r"8\s*16\s*4深沟球",r"弹簧外壳端铝件",r"电机座\(镜像\)",r"内8外16法兰"]),
("crank",[r"二级腿曲柄",r"二级腿链轮"]),("link2",[r"等效前二级腿"]),("link3",[r"等效后二级腿"]),
("link4",[r"二级腿连杆"]),("spring1",[r"氮气弹簧推杆"]),("spring2",[r"氮气弹簧外壳"]),
("thigh",[r"24\s+一级腿",r"一级腿链轮",r"锥形轴",r"机械限位",r"限位安装销",r"弹簧推杆端铝件",r"锁紧块",r"锥面螺母",r"47\.8"])]
BASE_SIDE=[r"DM_8116",r"DM80-V3",r"电机铝件",r"电机涨块",r"滑环",r"中心轴",r"装甲",r"防弹板",r"链轮保护"]
def body_of(path,product):
    p=product.strip()
    if not (path.startswith("整车总装/24    髋腿") or path.startswith("整车总装/Mirror24    髋腿")): return "base"
    for pat in BASE_SIDE:
        if re.search(pat,p): return "base"
    for b,pats in BODY_RULES:
        for pat in pats:
            if re.search(pat,p): return b
    return "base"
ml=[s for s in man if s["path"].startswith("整车总装/24    髋腿")]
mr=[s for s in man if s["path"].startswith("整车总装/Mirror24    髋腿")]
other=[s for s in man if s not in ml and s not in mr]
tup=[(side,s) for side,lst in (("L",ml),("R",mr)) for s in lst if body_of(s["path"],s["product"])=="base"]
print("chassis-side leg solids EXCLUDED from the visual mesh: %d"%len(tup))
print("  volume %.1f cm3   triangles %d"%(sum(s["volume_mm3"] for _,s in tup)/1000,sum(s["ntris"] for _,s in tup)))
c=collections.Counter(s["product"].strip() for _,s in tup)
for n,v in c.most_common(30): print("   %4d  %s"%(v,n[:64]))
# per-body lateral centre from CAD
print("\nlateral centre of each leg body per CAD (robot y, mm) vs value used for mesh centring")
USED={"thigh":-223.85,"shank":-223.85,"wheel":-270.25,"crank":-223.85,"link2":-223.85,"link3":-223.85,"link4":-223.85,"spring1":-223.85,"spring2":-223.85}
g=collections.defaultdict(list)
for side,lst in (("L",ml),("R",mr)):
    for s in lst:
        b=body_of(s["path"],s["product"])
        if b!="base": g[b].append((side,s))
for b in sorted(g):
    ys=[]
    for side,s in g[b]:
        bb=np.array(s["bbox_world"],float).reshape(2,3); w=(R@bb.T).T+t
        ys.append((w[:,1].min(),w[:,1].max()) if side=="L" else (-w[:,1].max(),-w[:,1].min()))
    lo=min(a for a,_ in ys); hi=max(c for _,c in ys)
    print("  %-8s CAD y %7.1f..%7.1f  centre %7.2f   used %7.2f   err %6.2f mm"%(b,lo,hi,(lo+hi)/2,USED[b],(lo+hi)/2-USED[b]))