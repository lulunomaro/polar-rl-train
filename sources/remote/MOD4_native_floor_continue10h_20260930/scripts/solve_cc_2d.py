"""Planar position analysis of the similar-linkage (kite four-bar) leg.

Topology recovered from the CAD B-rep (scripts/verify_axes.py, leg_graph.py) and
cross-checked against the SJTU PDF p06 + the wheelbipeV14_2 reference MJCF:

    hip ---[crank front1, DRIVEN]--- P2         |hip->P2| = L_crank
    hip ---[thigh rear1, DRIVEN]--- P1, knee    |hip->P1| = L_p1
    P2 ---[front2 L_2]--- APEX ---[front3 L_3]--- P1     (the kite apex joint)
    P3 is a third hole rigidly on front3; Q is on the shank (rear2); |P3->Q| = L_4
    gas spring: S1 on the thigh, S2 sliding on the shank housing

Loop 1 (hip,P2,APEX,P1) + loop 2 (knee,P3,Q) => Gruebler 3*9-2*12 = 3 DOF/leg,
so the knee is a *passive* joint driven through the linkage.  This module is the
ground-truth IK / transmission-ratio calculator for the closed chain.
"""
import numpy as np

# --- measured hinge points (robot frame, mm, left leg; x = longitudinal, z = up)
HIP   = np.array([0.0, 212.1])
KNEE0 = np.array([-200.7, 150.3])
AXLE0 = np.array([-0.8, 0.1])
P2_0  = np.array([109.7, 177.3])   # crank pin (二级腿曲柄)
P1_0  = np.array([-110.0, 178.2])  # thigh pin
APEX0 = np.array([-0.5, 95.9])     # front2 / front3 joint (kite apex)
P3_0  = np.array([-151.3, 230.9])  # third hole of front3
Q0    = np.array([-242.0, 203.0])  # front4 <-> shank
S1_0  = np.array([0.6, 161.1])     # gas-spring rod end (thigh)
S2_0  = np.array([-165.5, 115.5])  # gas-spring housing end (shank)

def ang(v):                       # in-plane angle of a 2-vector
    return np.arctan2(v[1], v[0])

def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi

def rot(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])

# --- link lengths (all measured, then verified to close the loops) ------------
L_crank = np.linalg.norm(P2_0 - HIP)     # 115.1  crank on the hip axis
L_p1    = np.linalg.norm(P1_0 - HIP)     # 115.1  thigh pin on the hip axis
L_2     = np.linalg.norm(P2_0 - APEX0)   # 137.0  front2 (equivalent forward upper leg)
L_3     = np.linalg.norm(P1_0 - APEX0)   # 137.0  front3 (equivalent rearward upper leg)
L_4     = np.linalg.norm(P3_0 - Q0)      # 94.9   front4 (二级腿连杆)
R_P3    = np.linalg.norm(P3_0 - APEX0)   # 202.4  |APEX->P3| on front3
R_Q     = np.linalg.norm(Q0 - KNEE0)     # 67.0   |knee->Q| on the shank
THIGH   = np.linalg.norm(KNEE0 - HIP)    # 210.0  |hip->knee|  (PDF: 0.210 m)
SHANK   = np.linalg.norm(AXLE0 - KNEE0)  # 250.0  |knee->axle| (PDF: 0.250 m)
L_SPR   = np.linalg.norm(S2_0 - S1_0)    # 172.2  gas-spring free length

# zero-pose reference directions, expressed in the body they belong to
A_P1    = ang(P1_0 - HIP)                # hip->P1 in the thigh frame
A_KNEE  = ang(KNEE0 - HIP)               # hip->knee in the thigh frame
A_P2    = ang(P2_0 - HIP)                # hip->P2 in the crank frame
A_S1    = ang(S1_0 - HIP)                # hip->S1 in the thigh frame
PHI3_0  = ang(APEX0 - P1_0)              # P1->APEX in the front3 frame
A_P3_31 = ang(P3_0 - P1_0)               # P1->P3 in the front3 frame
A_Q_K   = ang(Q0 - KNEE0)                # knee->Q in the shank frame
A_AX_K  = ang(AXLE0 - KNEE0)             # knee->axle in the shank frame
A_S2_K  = ang(S2_0 - KNEE0)              # knee->S2 in the shank frame

# assembly branch: the apex sits *below* the P1-P2 chord at the CAD zero pose
# (mid(P1,P2) = (-0.15, 177.75), APEX = (-0.5, 95.9) -> dz = -81.9 mm), and Q
# stays on the +normal side of the knee->P3 chord.  Verified numerically below.
PICK_APEX, PICK_Q = -1.0, +1.0

def circle_int(c1, r1, c2, r2, pick):
    """intersection of two circles; pick=+-1 selects the branch."""
    d = np.linalg.norm(c2 - c1)
    if d > r1 + r2 + 1e-9 or d < abs(r1 - r2) - 1e-9 or d < 1e-12:
        return None
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = np.sqrt(max(0.0, r1 * r1 - a * a))
    p = c1 + a * (c2 - c1) / d
    n = np.array([-(c2 - c1)[1], (c2 - c1)[0]]) / d
    return p + pick * h * n

def solve(th_thigh, th_crank, pick_apex=PICK_APEX, pick_q=PICK_Q):
    """Direct kinematics.  th_* are rotations (rad) from the CAD zero pose.
    Returns a dict, or None when the chain cannot close."""
    R_t = rot(th_thigh)
    P1   = HIP + R_t @ (P1_0 - HIP)
    knee = HIP + R_t @ (KNEE0 - HIP)
    S1   = HIP + R_t @ (S1_0 - HIP)
    P2   = HIP + rot(th_crank) @ (P2_0 - HIP)
    apex = circle_int(P1, L_3, P2, L_2, pick_apex)
    if apex is None:
        return None
    phi3 = wrap(ang(apex - P1) - PHI3_0)          # front3 rotation from zero pose
    P3 = P1 + rot(phi3) @ (P3_0 - P1_0)
    Q = circle_int(knee, R_Q, P3, L_4, pick_q)
    if Q is None:
        return None
    th_shank = wrap(ang(Q - knee) - A_Q_K)        # knee joint angle (passive)
    R_s = rot(th_shank)
    axle = knee + R_s @ (AXLE0 - KNEE0)
    S2 = knee + R_s @ (S2_0 - KNEE0)
    return dict(thigh=th_thigh, crank=th_crank, shank=th_shank, phi3=phi3,
                P1=P1, P2=P2, apex=apex, P3=P3, Q=Q, knee=knee, axle=axle,
                S1=S1, S2=S2, spring=np.linalg.norm(S2 - S1),
                loop1=np.linalg.norm(apex - P2) - L_2,
                loop2=np.linalg.norm(Q - P3) - L_4,
                ext=np.linalg.norm(axle - HIP))

def selfcheck():
    r = solve(0.0, 0.0)
    assert r is not None, "zero pose does not close - check the branch picks"
    worst = 0.0
    for name, got, ref in (("P1", r["P1"], P1_0), ("P2", r["P2"], P2_0),
                           ("APEX", r["apex"], APEX0), ("P3", r["P3"], P3_0),
                           ("Q", r["Q"], Q0), ("knee", r["knee"], KNEE0),
                           ("axle", r["axle"], AXLE0)):
        worst = max(worst, np.linalg.norm(got - ref))
    print("[self-check] branch picks %+d/%+d  zero-pose reproduction error = %.3e mm"
          % (PICK_APEX, PICK_Q, worst))
    print("[self-check] loop residuals at zero: loop1=%.2e mm loop2=%.2e mm"
          % (r["loop1"], r["loop2"]))
    print("[self-check] link lengths  crank %.1f  thigh-pin %.1f  L2 %.1f  L3 %.1f  "
          "L4 %.1f  R_Q %.1f | thigh %.1f shank %.1f spring %.1f"
          % (L_crank, L_p1, L_2, L_3, L_4, R_Q, THIGH, SHANK, L_SPR))
    print("[self-check] kite similarity ratio 115.1/210.0 = %.3f (PDF 0.54), "
          "transmission ~%.2fx" % (L_crank / THIGH, THIGH / L_crank))
    return worst

if __name__ == "__main__":
    selfcheck()

    print("\n[1] crank sweep, thigh held at the CAD pose:")
    print("     crank    knee     ratio    front3     apex(x,z)      axle(x,z)   ext")
    base = solve(0.0, 0.0)
    for tc in np.arange(-0.9, 0.95, 0.15):
        r = solve(0.0, tc)
        if r is None:
            print("     %+6.2f    -            CHAIN CANNOT CLOSE" % tc); continue
        print("     %+6.2f  %+7.4f  %+6.3f  %+7.4f  (%+6.1f,%+6.1f) (%+6.1f,%+6.1f) %6.1f"
              % (tc, r["shank"], r["shank"] / tc, r["phi3"],
                 r["apex"][0] - HIP[0], r["apex"][1] - HIP[1],
                 r["axle"][0] - HIP[0], r["axle"][1] - HIP[1], r["ext"]))

    print("\n[2] numerical transmission ratio d(knee)/d(crank) at the nominal pose")
    for tc in (0.0, 0.2, 0.4, -0.3):
        h = 1e-4
        a, b = solve(0.0, tc - h), solve(0.0, tc + h)
        if a and b:
            print("     crank=%+.2f -> %.3f   (PDF states the crank turns 1.85x the knee)"
                  % (tc, (b["shank"] - a["shank"]) / (2 * h)))

    print("\n[3] thigh sweep with the crank held (leg swings about the hip):")
    for tt in np.arange(-1.2, 1.25, 0.3):
        r = solve(tt, 0.0)
        print("     thigh=%+5.2f  knee=%s  axle=(%s)  spring=%s mm"
              % (tt, "%+.4f" % r["shank"] if r else "  n/a ",
                 "%+6.1f,%+6.1f" % (r["axle"][0] - HIP[0], r["axle"][1] - HIP[1]) if r else " n/a",
                 "%.1f" % r["spring"] if r else " n/a"))

    print("\n[4] workspace: |hip->axle| and the height it can hold, thigh x crank grid")
    for tt in np.arange(-0.9, 0.95, 0.3):
        row = []
        for tc in np.arange(-0.9, 0.95, 0.3):
            r = solve(tt, tc)
            row.append("  ----  " if r is None else "%7.1f" % (r["axle"][1] - HIP[1]))
        print("     thigh %+5.2f |%s" % (tt, "".join(row)))

    print("\n[5] IK: crank angle needed for a knee angle target (thigh held)")
    for target in np.arange(-0.6, 0.65, 0.15):
        lo, hi = -1.4, 1.4
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            r = solve(0.0, mid)
            if r is None:
                break
            if r["shank"] < target:
                lo = mid
            else:
                hi = mid
        r = solve(0.0, 0.5 * (lo + hi))
        print("     knee=%+.3f -> crank=%+.4f rad (%+.1f deg)  axle z=%+.1f mm  %s"
              % (target, 0.5 * (lo + hi), np.degrees(0.5 * (lo + hi)),
                 r["axle"][1] - HIP[1] if r else float("nan"),
                 "" if r else "unreachable"))
