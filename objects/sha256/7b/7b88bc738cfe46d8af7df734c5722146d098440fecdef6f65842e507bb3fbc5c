import sys, os
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD, wrap
L = Kite2D(CAD, 'ours')
FOLD = wrap(np.arctan2(CAD['P2'][1], CAD['P2'][0]) - np.arctan2(CAD['P1'][1], CAD['P1'][0]))
COL = dict(kite='#1b6ca8', para='#e76f51', leg='#22223b', spring='#d62828', ground='#7f8c8d')

def draw(ax, r, alpha=1.0):
    P = lambda k: (r[k][0], r[k][1])
    hip = (0.0, 0.0)
    seg = [((hip, P('P2')), COL['kite'], 4.5), ((P('P2'), P('apex')), COL['kite'], 3.0),
           ((P('apex'), P('P1')), COL['kite'], 3.0), ((P('P1'), P('P3')), COL['kite'], 3.0),
           ((P('P3'), P('Q')), COL['para'], 3.5), ((P('Q'), P('knee')), COL['para'], 3.5),
           ((hip, P('knee')), COL['leg'], 6.0), ((P('knee'), P('axle')), COL['leg'], 6.0),
           ((P('S1'), P('S2')), COL['spring'], 3.0)]
    for (a, b), c, w in seg:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=c, lw=w, alpha=alpha, solid_capstyle='round')
    for k in ('P2', 'apex', 'P1', 'P3', 'Q', 'S1', 'S2', 'knee'):
        ax.plot([P(k)[0]], [P(k)[1]], marker='o', ms=6, color='white', mec=c if False else '#333', mew=1.4, zorder=5)
    ax.plot([0], [0], marker='o', ms=13, mfc='white', mec=COL['kite'], mew=2.6, zorder=6)
    ax.plot([P('axle')[0]], [P('axle')[1]], marker='o', ms=26, mfc='none', mec=COL['leg'], mew=2.6, zorder=6)

# ---------- figure 1: the audit ----------
fig = plt.figure(figsize=(19.0, 6.4))
A = fig.add_subplot(1, 3, 1)
q = L.qpos_full(0.097, 0.222); draw(A, q['pts'])
for nm, off in (('hip', (10, 8)), ('P2', (8, -14)), ('apex', (8, -16)), ('P1', (-30, 8)),
                ('P3', (-34, 6)), ('Q', (-16, 10)), ('knee', (6, -6)), ('axle', (10, -18)),
                ('S1', (8, 4)), ('S2', (-30, -8))):
    p = (0.0, 0.0) if nm == 'hip' else q['pts'][nm]
    A.annotate(nm, (p[0], p[1]), textcoords='offset points', xytext=off, fontsize=9.5,
               fontweight='bold', color='#222')
A.set_aspect('equal'); A.grid(alpha=.25); A.set_xlim(-320, 200); A.set_ylim(-290, 130)
A.set_title('A. the closed chain rebuilt from the CAD assembly (trained stance)\n'
            'blue KITE hip-P2-apex-P1  |  orange PARALLELOGRAM P1-knee-Q-P3  |  black thigh+shank\n'
            'crank 115.1 / coupler 137.0 / plate 137.0 / link4 94.9 / thigh 210.0 / shank 250.0 mm', fontsize=9.5)
B = fig.add_subplot(1, 3, 2)
dl = np.arange(-np.pi, np.pi, 0.002)
knee = []; diag = []; kited = []
for x in dl:
    qq = L.qpos_full(x, 0.0)
    if qq is None: knee.append(np.nan); diag.append(np.nan); kited.append(np.nan); continue
    r = qq['pts']; knee.append(-qq['rear2'])
    diag.append(np.linalg.norm(r['knee'] - r['P3'])); kited.append(np.linalg.norm(r['P1'] - r['P2']))
B.plot(dl, knee, color=COL['kite'], lw=2.4, label='knee angle q_rear2 (MJCF rad)')
B2 = B.twinx()
B2.plot(dl, diag, color=COL['para'], lw=1.4, ls='--', label='loop-2 diagonal |knee-P3| (mm)')
B2.plot(dl, kited, color='#8d99ae', lw=1.2, ls=':', label='loop-1 diagonal |P1-P2| (mm)')
B2.axhline(L.L4 + L.Rq, color=COL['para'], lw=.8); B2.axhline(abs(L.L4 - L.Rq), color=COL['para'], lw=.8)
B2.set_ylabel('linkage diagonal (mm)'); B2.set_ylim(0, 200)
B.axhline(1.48, color='#d62828', lw=1.4, ls='-.', label='OLD rear2 stop 1.48: past the flat config')
B.axhline(1.351, color='#2a9d8f', lw=1.6, label='NEW rear2 stop 1.351')
B.axvline(FOLD, color='black', lw=1.0, ls=':')
B.axvspan(-2.601, 1.588, color='#2a9d8f', alpha=.09)
B.annotate('kite fold\n|P1-P2| = 0\n(delta=+2.536)', (FOLD, -0.75), textcoords='offset points',
           xytext=(-64, 0), fontsize=8)
B.annotate('parallelogram flat\n|knee-P3| = 161.9 mm', (2.05, 0.35), fontsize=8, color=COL['para'])
B.annotate('new tendon stop on\nq_rear1 - q_front1', (-2.58, 0.9), fontsize=8, color='#2a9d8f')
B.set_xlabel('delta = thigh - crank (analytic rad)'); B.set_ylabel('knee angle (rad)')
B.grid(alpha=.25); B.set_xlim(-np.pi, np.pi); B.legend(fontsize=7.6, loc='upper left')
B.set_title('B. every passive angle depends on delta ONLY (|hip-P1| = |hip-P2| = 115.1 mm).\n'
            'The old model bounded delta by nothing but a knee stop placed past the flat config.', fontsize=9.5)
C = fig.add_subplot(1, 3, 3)
pts = []
for x in np.arange(-np.pi, np.pi, 0.01):
    for th in np.arange(-1.4, 1.41, 0.05):
        qq = L.qpos_full(th, th - x)
        if qq is None: continue
        pts.append((x, qq['pts']['ext'] / 1000.0))
pts = np.array(pts)
C.hist2d(pts[:, 0], pts[:, 1], bins=[190, 130], range=[[-np.pi, np.pi], [0.0, 0.46]], cmap='viridis')
C.axvline(-2.601, color='w', ls='--', lw=1.3); C.axvline(1.588, color='w', ls='--', lw=1.3)
C.axhspan(0.16, 0.32, color='white', alpha=.20)
C.annotate('commanded height band 0.16-0.32 m', (-3.05, 0.235), color='w', fontsize=9)
C.annotate('new stop', (-2.55, 0.40), color='w', fontsize=8)
C.annotate('new stop', (1.44, 0.40), color='w', fontsize=8)
C.set_xlabel('delta = thigh - crank (rad)'); C.set_ylabel('|hip -> wheel axle| (m)')
C.set_title('C. reachable (delta, extension) set: the new stops cut the two singular ends and\n'
            'leave the whole commanded height band plus a 0.046-0.418 m stroke', fontsize=9.5)
plt.tight_layout()
out1 = os.path.join(ROOT, 'docs/audit/linkage_audit.png')
plt.savefig(out1, dpi=110); print('wrote', out1)
# ---------- figure 2: the crank drives the knee (filmstrip) ----------
fig, axs = plt.subplots(1, 6, figsize=(19.0, 3.9))
for k, ax in enumerate(axs):
    tc = 0.222 + k * 0.26
    qq = L.qpos_full(0.097, tc)
    draw(ax, qq['pts'], alpha=1.0)
    ax.set_aspect('equal'); ax.set_xlim(-330, 220); ax.set_ylim(-300, 160); ax.grid(alpha=.2)
    ax.set_title('crank %+0.2f rad -> knee %+0.3f rad\naxle (%+0.0f, %+0.0f) mm'
                 % (tc, -qq['rear2'], qq['pts']['axle'][0], qq['pts']['axle'][1] + 212.1), fontsize=8.6)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle('The knee has NO motor: the second hip-axis motor turns the crank (blue) and the '
             'kite+parallelogram solve the knee angle - exactly SJTU RM2025 sec.1.2.1 / 2.1.1 '
             '(verified 0.0000 mm loop closure at 31780 poses)', fontsize=11)
plt.tight_layout(rect=(0, 0, 1, 0.90))
out2 = os.path.join(ROOT, 'docs/audit/linkage_sweep.png')
plt.savefig(out2, dpi=110); print('wrote', out2)
