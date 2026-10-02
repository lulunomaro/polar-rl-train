"""Generic planar position analysis of the similar-linkage (kite four-bar) leg.

Both the SJTU/SCUT reference (refs/.../wheelbipeV14_2.xml) and our CAD vehicle use the
same closed chain.  This module is the ground-truth IK + transmission calculator, and
is used to (a) validate the MJCF we generate against MuJoCo's own equality solver and
(b) derive the correct passive-joint ranges for *our* zero-pose convention.

Topology (all hinges are parallel to +Y, so the mechanism is exactly planar):

    hip --[front1 crank, DRIVEN, |hip->P2| = r_c]--> P2
    hip --[rear1 thigh, DRIVEN, |hip->knee| = a]----> knee, and the pin P1 at |hip->P1| = r_c
    P2 --[front2, L2]--> APEX --[front3, L3]--> P1            (loop 1, a kite: L2 = L3)
    front3 is rigid and also carries P3 (|APEX->P3| = R3)
    P3 --[front4, L4]--> Q,  Q is rigidly on rear2 at |knee->Q| = R_q   (loop 2)
    gas spring: S1 pinned on the thigh, S2 on a slider, attached to rear2

Zero pose = the CAD pose, so qpos 0 for every joint closes both loops exactly.
"""
import numpy as np

def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi

def rot(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])

def ang(v):
    return np.arctan2(v[1], v[0])

def circle_int(c1, r1, c2, r2, pick):
    d = np.linalg.norm(c2 - c1)
    if d > r1 + r2 + 1e-9 or d < abs(r1 - r2) - 1e-9 or d < 1e-12:
        return None
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = np.sqrt(max(0.0, r1 * r1 - a * a))
    p = c1 + a * (c2 - c1) / d
    n = np.array([-(c2 - c1)[1], (c2 - c1)[0]]) / d
    return p + pick * h * n

class Kite2D:
    """2-linkage leg.  `pts` are 2-D (x, z) mm positions *relative to the hip* at zero pose."""
    KEYS = ("knee", "axle", "P2", "P1", "apex", "P3", "Q", "S1", "S2")

    def __init__(self, pts, name="leg", pick_apex=-1.0, pick_q=+1.0):
        self.name = name
        self.p = {k: np.asarray(v, float) for k, v in pts.items()}
        p = self.p
        self.hip = np.zeros(2)
        self.r_c    = np.linalg.norm(p["P2"])
        self.r_p1   = np.linalg.norm(p["P1"])
        self.L2     = np.linalg.norm(p["P2"] - p["apex"])
        self.L3     = np.linalg.norm(p["P1"] - p["apex"])
        self.R3     = np.linalg.norm(p["P3"] - p["apex"])
        self.L4     = np.linalg.norm(p["P3"] - p["Q"])
        self.Rq     = np.linalg.norm(p["Q"] - p["knee"])
        self.a      = np.linalg.norm(p["knee"])          # thigh
        self.b      = np.linalg.norm(p["axle"] - p["knee"])  # shank
        self.Lspr0  = np.linalg.norm(p["S2"] - p["S1"])  # gas spring length at zero
        self.A_P1   = ang(p["P1"]); self.A_KNEE = ang(p["knee"])
        self.A_P2   = ang(p["P2"])
        self.PHI3_0 = ang(p["apex"] - p["P1"])           # P1->APEX in the front3 frame
        self.A_P3   = ang(p["P3"] - p["P1"])             # P1->P3 in the front3 frame
        self.A_Q    = ang(p["Q"] - p["knee"])            # knee->Q in the shank frame
        self.A_AX   = ang(p["axle"] - p["knee"])         # knee->axle in the shank frame
        self.A_S2   = ang(p["S2"] - p["knee"])           # knee->S2 in the shank frame
        self.A_S1   = ang(p["S1"])                       # hip->S1 in the thigh frame
        self.pick_apex, self.pick_q = pick_apex, pick_q

    # ---- direct kinematics -------------------------------------------------
    def solve(self, th_thigh, th_crank):
        p = self.p
        Rt = rot(th_thigh)
        P1   = Rt @ p["P1"];  knee = Rt @ p["knee"];  S1 = Rt @ p["S1"]
        P2   = rot(th_crank) @ p["P2"]
        apex = circle_int(P1, self.L3, P2, self.L2, self.pick_apex)
        if apex is None:
            return None
        phi3 = wrap(ang(apex - P1) - self.PHI3_0)       # front3 rotation from zero
        P3   = P1 + rot(phi3) @ (p["P3"] - p["P1"])
        Q    = circle_int(knee, self.Rq, P3, self.L4, self.pick_q)
        if Q is None:
            return None
        th = wrap(ang(Q - knee) - self.A_Q)             # knee (passive) angle
        Rs = rot(th)
        axle = knee + Rs @ (p["axle"] - p["knee"])
        S2   = knee + Rs @ (p["S2"] - p["knee"])
        # NOTE: `shank` is the ABSOLUTE world orientation change of the shank; the
        # rear2 joint value (relative to the thigh, which is what an MJCF hinge stores)
        # is shank - thigh.  The transmission ratio d(shank)/d(crank) is the same either way.
        return dict(thigh=th_thigh, crank=th_crank, shank=th, knee_joint=wrap(th - th_thigh),
                    phi3=phi3,
                    P1=P1, P2=P2, apex=apex, P3=P3, Q=Q, knee=knee, axle=axle,
                    S1=S1, S2=S2, spring=np.linalg.norm(S2 - S1),
                    ext=np.linalg.norm(axle - self.hip),
                    loop1=np.linalg.norm(apex - P2) - self.L2,
                    loop2=np.linalg.norm(Q - P3) - self.L4)

    # ---- checks / utilities ------------------------------------------------
    def selfcheck(self, verbose=True):
        r = self.solve(0.0, 0.0)
        worst = 0.0
        if r:
            for k in ("knee", "axle", "P1", "P2", "apex", "P3", "Q"):
                worst = max(worst, np.linalg.norm(r[k] - self.p[k]))
        if verbose:
            print("  [%s] zero-pose reproduction %.2e mm; loop residuals %.1e/%.1e"
                  % (self.name, worst, r["loop1"] if r else -1, r["loop2"] if r else -1))
            print("  [%s] r_c=%.2f r_P1=%.2f L2=%.2f L3=%.2f R3=%.2f L4=%.2f Rq=%.2f "
                  "| thigh=%.2f shank=%.2f spring0=%.2f  lambda=%.4f"
                  % (self.name, self.r_c, self.r_p1, self.L2, self.L3, self.R3, self.L4,
                     self.Rq, self.a, self.b, self.Lspr0, self.r_p1 / self.a))
        return worst

    def ratio(self, th=0.0, tc=0.0, h=1e-4):
        a, b = self.solve(th, tc - h), self.solve(th, tc + h)
        return float("nan") if not (a and b) else (b["shank"] - a["shank"]) / (2 * h)

    def joint_ranges(self, th_lo=-1.2, th_hi=1.2, tc_lo=-1.2, tc_hi=1.2, n=97):
        """min/max of every passive angle over the driven workspace (for MJCF ranges)."""
        acc = {}
        for th in np.linspace(th_lo, th_hi, n):
            for tc in np.linspace(tc_lo, tc_hi, n):
                r = self.solve(th, tc)
                if r is None or abs(r["loop1"]) > 1e-3 or abs(r["loop2"]) > 1e-3:
                    continue
                for k in ("shank", "phi3", "spring", "ext"):
                    v = r[k] if k in ("spring", "ext") else r[k]
                    acc.setdefault(k, []).append(v)
                # front2 / front4 angles, read off the links
                acc.setdefault("front2", []).append(wrap(ang(r["apex"] - r["P2"]) - self.A_P2 - r["crank"]))
                acc.setdefault("front4", []).append(wrap(ang(r["Q"] - r["P3"]) - ang(self.p["Q"] - self.p["P3"]) - r["phi3"]))
        return {k: (float(np.min(v)), float(np.max(v))) for k, v in acc.items()}


    def qpos_full(self, th_thigh, th_crank):
        """All 8 leg joint angles (this module's x->z convention) for a driven pose.
        MuJoCo hinges about +Y, so its qpos value is the NEGATIVE of what is returned."""
        r = self.solve(th_thigh, th_crank)
        if r is None:
            return None
        p = self.p
        t2 = wrap(ang(r["apex"] - r["P2"]) - ang(p["apex"] - p["P2"]) - th_crank)
        t3 = wrap(r["phi3"] - th_crank - t2)
        t4 = wrap(ang(r["Q"] - r["P3"]) - ang(p["Q"] - p["P3"]) - th_crank - t2 - t3)
        # rear2 and the front hinges are all relative to their parent body
        ts1 = wrap(ang(r["S2"] - r["S1"]) - ang(p["S2"] - p["S1"]) - th_thigh)
        ts2 = r["spring"] - self.Lspr0
        return dict(rear1=th_thigh, front1=th_crank, rear2=r["knee_joint"], front2=t2,
                    front3=t3, front4=t4, spring1=ts1, spring2=ts2, pts=r)

    def report(self):
        print("\n### %s : crank sweep (thigh held at 0)" % self.name)
        print("     crank    knee    d(knee)/d(crank)   1/ratio   axle(x,z)   ext    spring")
        for tc in np.arange(-0.9, 0.95, 0.15):
            r = self.solve(0.0, tc)
            if r is None:
                print("     %+6.2f   chain cannot close" % tc); continue
            print("     %+6.2f %+7.4f      %+6.3f      %6.2f   (%+6.1f,%+6.1f) %6.1f %6.1f"
                  % (tc, r["shank"], self.ratio(0.0, tc),
                     1.0 / self.ratio(0.0, tc) if self.ratio(0.0, tc) else float("nan"),
                     r["axle"][0], r["axle"][1], r["ext"], r["spring"]))

# --- our CAD vehicle (mm, hip-relative) --------------------------------------
CAD = dict(knee=np.array([-200.7, -61.8]), axle=np.array([-0.8, -212.0]),
           P2=np.array([109.7, -34.8]),  P1=np.array([-110.0, -33.9]),
           apex=np.array([-0.5, -116.2]), P3=np.array([-151.3, 18.8]),
           Q=np.array([-242.0, -9.1]),   S1=np.array([0.6, -51.0]),
           S2=np.array([-165.5, -96.6]))
# --- the SJTU/SCUT reference leg, read out of wheelbipeV14_2.xml (m -> mm) -----
REF = dict(knee=np.array([-210.5, -0.01]), axle=np.array([6.11, -124.83]),
           P2=np.array([112.65, 13.05]), P1=np.array([-113.40, -0.01]),
           apex=np.array([3.86, -66.90]), P3=np.array([-161.19, 46.97]),
           Q=np.array([-257.79, 46.97]), S1=np.array([2.36, -44.94]),
           S2=np.array([-162.42, -22.92]))

if __name__ == "__main__":
    for pts, nm in ((CAD, "ours/CAD"), (REF, "SJTU-ref")):
        L = Kite2D(pts, nm); L.selfcheck(); L.report()
        print("     passive-angle workspace:", {k: (round(v[0], 3), round(v[1], 3))
                                                for k, v in L.joint_ranges().items()})
