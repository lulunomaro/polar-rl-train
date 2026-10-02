"""Headless replica of docs/viz/model_viewer.html: same FK, same soup, same matrices.

Used to prove the two viewer fixes without a browser:
  * parts.bin must be in metres (mesh_scale applied)
  * every part must be transformed by its BODY matrix (not only shaded by it)
"""
import json, os, sys
sys.path.insert(0, r'D:/claude2/urdf/scripts')
import numpy as np
import render_kine as R
from PIL import Image, ImageDraw

VIZ = r'D:/claude2/fangzhen/docs/viz'
PAL = np.array(R.PALETTE, float) / 255.0


def tr3(x, y, z):
    o = np.eye(4); o[0, 3], o[1, 3], o[2, 3] = x, y, z
    return o


def rotq(w, x, y, z):
    n = np.sqrt(w*w+x*x+y*y+z*z) or 1.0
    w, x, y, z = w/n, x/n, y/n, z/n
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w),   0],
                     [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w),   0],
                     [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y), 0],
                     [0, 0, 0, 1]])


def axis_rot(a, ang):
    a = np.asarray(a, float); a = a/np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    Rm = np.eye(3) + np.sin(ang)*K + (1-np.cos(ang))*(K@K)
    out = np.eye(4); out[:3, :3] = Rm
    return out


def fk_all(M, qv):
    W = []
    for b in M["bodies"]:
        if b["parent"] < 0:
            r = qv.get("__root__", [0, 0, 0.073, 1, 0, 0, 0])
            Mm = tr3(*r[:3]) @ rotq(*r[3:])
        else:
            Mm = W[b["parent"]] @ tr3(*b["pos"])
            if b["quat"] and len(b["quat"]) == 4:
                Mm = Mm @ rotq(*b["quat"])
            j = b["joint"]
            if j:
                val = qv.get(j["name"], 0.0)
                P = tr3(*j["pos"])
                if j["tname"] == "hinge":
                    Mm = Mm @ P @ axis_rot(j["axis"], val) @ tr3(-j["pos"][0], -j["pos"][1], -j["pos"][2])
                elif j["tname"] == "slide":
                    a = np.asarray(j["axis"], float); a = a/(np.linalg.norm(a) or 1)
                    Mm = Mm @ tr3(*(a*val))
            Mm = W[b["parent"]] @ Mm if False else Mm
        W.append(Mm)
    return W


def body_frames(M, qv):
    """proper hierarchical version (parent already in world)"""
    W = [None]*len(M["bodies"])
    for b in M["bodies"]:
        if b["parent"] < 0:
            r = qv.get("__root__", [0, 0, 0.073, 1, 0, 0, 0])
            W[b["id"]] = tr3(*r[:3]) @ rotq(*r[3:])
            continue
        local = tr3(*b["pos"])
        if b["quat"] and len(b["quat"]) == 4:
            local = local @ rotq(*b["quat"])
        j = b["joint"]
        if j:
            val = qv.get(j["name"], 0.0)
            if j["tname"] == "hinge":
                P = tr3(*j["pos"])
                local = local @ P @ axis_rot(j["axis"], val) @ tr3(*[-x for x in j["pos"]])
            elif j["tname"] == "slide":
                a = np.asarray(j["axis"], float); a = a/(np.linalg.norm(a) or 1)
                local = local @ tr3(*(a*val))
        W[b["id"]] = W[b["parent"]] @ local
    return W


def render(bin_name, M, qv, follow, path, az=206, el=18, dist=1.5, centre=(0.0, 0.0, 0.28),
           size=(860, 700), title=""):
    raw = np.fromfile(os.path.join(VIZ, bin_name), dtype="<f4")
    W = body_frames(M, qv)
    P, C = [], []
    for i, g in enumerate(M["parts"]):
        v = raw[g["start"]*6:(g["start"]+g["count"])*6].reshape(-1, 6)[:, :3].astype(np.float64)
        ms = np.asarray(g.get("mesh_scale", [1, 1, 1]), float)
        v = v * ms
        lm = tr3(*g["pos"])
        if g.get("quat") and len(g["quat"]) == 4:
            lm = lm @ rotq(*g["quat"])
        T = (W[g["body"]] @ lm) if follow else np.eye(4)     # follow=False == the old viewer bug
        H = np.hstack([v, np.ones((len(v), 1))])
        P.append((T @ H.T)[:3].T)
        col = np.array(R.PALETTE[g["body"] % len(R.PALETTE)], float)
        if g.get("group") == 3:
            col = np.array([60, 220, 120.0])
        C.append(np.tile(col, (len(v), 1)))
    P = np.vstack(P); C = np.vstack(C)
    keep = np.all(np.abs(P) < 5.0, axis=1)
    cam = R.Cam(centre, az, el, dist, size[0], size[1], fov=36)
    img, zb = R.new_img(size[0], size[1])
    R.splat(img, zb, cam, P[keep], C[keep], size=1)
    im = Image.fromarray(img)
    # joint axes + link frames, exactly as the viewer draws them
    for b in M["bodies"]:
        j = b["joint"]
        if not j:
            continue
        T = W[b["id"]]
        p = T[:3, 3]; a = T[:3, :3] @ np.asarray(j["axis"], float)
        a = a/(np.linalg.norm(a) or 1)
        R.line(im, cam, p-a*0.09, p+a*0.09, (60, 255, 120), 2)
        R.frame(im, cam, T, L=0.05, lw=2)
    d = ImageDraw.Draw(im)
    d.text((8, 6), title, fill=(235, 245, 255))
    bb = P[keep]
    d.text((8, size[1]-16), f"geometry extent = {np.round(bb.max(0)-bb.min(0),3)} m", fill=(150, 200, 255))
    im.save(path)
    print(f"  {path}: extent {np.round(bb.max(0)-bb.min(0),3)} m  tris {sum(g['count']//3 for g in M['parts'])}")
    return bb


if __name__ == "__main__":
    M = json.load(open(os.path.join(VIZ, "model.json"), encoding="utf-8"))
    q0 = M["poses"][0]["q"]
    qs = M["poses"][5]["q"]                       # crank driven -> closed chain solved
    out = r"D:/claude2/fangzhen/docs/viz/check"
    os.makedirs(out, exist_ok=True)
    print("AFTER the fixes (metre soup + body transform applied to vertices):")
    render("parts.bin", M, q0, True, os.path.join(out, "after_q0.png"),
           title="AFTER  CAD assembly pose qpos=0")
    render("parts.bin", M, qs, True, os.path.join(out, "after_crank.png"),
           title="AFTER  crank driven, closed chain solved")
    print("BEFORE (mesh_scale never applied -> 1000x, and bodies ignored):")
    render("parts.bin.bak", M, q0, False, os.path.join(out, "before_q0.png"),
           dist=1.5, centre=(0, 0, 0.28), title="BEFORE  mm soup, no body transform (what you saw)")
    render("parts.bin.bak", M, qs, False, os.path.join(out, "before_crank.png"),
           title="BEFORE  same pose: meshes do not follow their link")
