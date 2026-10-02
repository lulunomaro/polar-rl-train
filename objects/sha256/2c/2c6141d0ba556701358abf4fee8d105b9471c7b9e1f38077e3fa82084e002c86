import sys, numpy as np, onnxruntime as ort
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
S = ort.InferenceSession(r'D:/claude2/fangzhen/train/deploy/rm_cc_v16_final.onnx', providers=['CPUExecutionProvider'])
def obs(wz_cmd=0.0, vx_cmd=0.0, yaw_measured=0.0, pitch_deg=0.0):
    o = np.zeros(35, dtype=np.float32)
    o[0] = vx_cmd; o[2] = wz_cmd
    o[3] = 0.22 * 5.0
    o[6] = 0.5 * yaw_measured
    p = np.radians(pitch_deg)
    o[7] = np.sin(p); o[9] = -np.cos(p)
    o[28] = 1.0
    return o
print('wheels are action slots 4,5; unit = rad/s of wheel speed (scale 55)')
print('  wz_cmd  yaw_measured | a_wheelL  a_wheelR   diff(rad/s)  mean(rad/s)')
for wzc in (0.0, 0.1, 0.2, -0.1):
    for ym in (0.0, 0.16, 0.32, -0.16):
        a = S.run(None, {'obs': obs(wz_cmd=wzc, yaw_measured=ym).reshape(1, 35)})[0][0]
        wl = a[4] * 55.0; wr = a[5] * 55.0
        print('   %+5.2f     %+5.2f     |  %+7.2f  %+7.2f    %+7.2f     %+7.2f'
              % (wzc, ym, wl, wr, wl - wr, 0.5 * (wl + wr)))
print()
print('equilibrium yaw rate at wz_cmd = 0 (where the differential vanishes):')
for ym in np.arange(0.0, 0.61, 0.05):
    a = S.run(None, {'obs': obs(wz_cmd=0.0, yaw_measured=ym).reshape(1, 35)})[0][0]
    print('   yaw %+0.2f rad/s -> diff %+6.2f rad/s  (yaw_from_diff %+0.3f)' % (ym, (a[4]-a[5])*55, (a[4]-a[5])*55*0.073/0.27))
