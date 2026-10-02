import sys, numpy as np, onnxruntime as ort
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
S = ort.InferenceSession(r'D:/claude2/fangzhen/train/deploy/rm_cc_v16_final.onnx', providers=['CPUExecutionProvider'])
TRIM = 0.1035          # already baked into the network
def obs(vx=0.0, wz=0.0, h=0.22, legs=(0.072, -0.022, 0.029, 0.037), wvel=(0.0, 0.0)):
    o = np.zeros(35, dtype=np.float32)
    o[0] = vx; o[2] = wz
    o[3] = h * 5.0
    o[7], o[8], o[9] = 0.002, 0.027, -0.9996
    o[10:14] = legs
    o[16:20] = np.asarray(legs) * 0.0
    o[20:22] = np.asarray(wvel) * 0.1
    o[28] = 1.0
    return o.reshape(1, 35)
print('policy speed map (standing state, wheel target = action x 55 rad/s; 1 m/s = 13.7 rad/s)')
print('  cmd_vx | wheelL   wheelR   mean(rad/s)  mean m/s | diff(rad/s) | legs front1_L rear1_L')
for vx in (-2.8, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 1.8, 2.8):
    a = S.run(None, {'obs': obs(vx=vx)})[0][0]
    wl, wr = a[4]*55.0, a[5]*55.0
    print('   %+5.2f  | %+7.2f %+7.2f   %+7.2f     %+5.2f   |  %+6.2f     |  %+.3f %+.3f'
          % (vx, wl, wr, 0.5*(wl+wr), 0.5*(wl+wr)*0.073, wl-wr, a[0]*0.5, a[1]*0.5))
print()
print('height sweep at vx=1.0:')
for h in (0.16, 0.20, 0.22, 0.26, 0.32):
    a = S.run(None, {'obs': obs(vx=1.0, h=h)})[0][0]
    print('   h=%.2f -> legs tgt %+.3f %+.3f %+.3f %+.3f, wheels %+.1f %+.1f' %
          (h, a[0]*0.5, a[1]*0.5, a[2]*0.5, a[3]*0.5, a[4]*55, a[5]*55))
