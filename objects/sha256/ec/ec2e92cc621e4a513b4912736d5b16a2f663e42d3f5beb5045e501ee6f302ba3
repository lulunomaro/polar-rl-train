import sys,numpy as np,mujoco,onnxruntime as ort
XML=r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
ONNX=r"D:/claude2/fangzhen/train/deploy/rm_cc_v11_final.onnx"
KP,KD,WKD=60.,2.,1.5; S_LEG,S_WHL=0.5,10.; LEG_VLIM,WHEEL_VLIM=17.,63.4; LEG_EFF,WHEEL_EFF=40.,5.5
def trial(dt,policy,secs=3.0):
    m=mujoco.MjModel.from_xml_path(XML); d=mujoco.MjData(m); m.opt.timestep=dt
    J=lambda n: mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)
    ACT_J=[mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,m.actuator_trnid[i][0]) for i in range(m.nu)]
    LEG=[j for j in ACT_J if "wheel" not in j]; WHL=[j for j in ACT_J if "wheel" in j]
    qa={n:m.jnt_qposadr[J(n)] for n in ACT_J}; va={n:m.jnt_dofadr[J(n)] for n in ACT_J}
    site=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_SITE,"imu")
    sess=ort.InferenceSession(ONNX,providers=["CPUExecutionProvider"]); inp=sess.get_inputs()[0].name
    UP=np.array([0.,0.,-1.]); last=np.zeros(6,np.float32)
    tgt={n:0.0 for n in ACT_J}
    def _noop():
        pass
    d.qpos[:]=0.; d.qpos[2]=0.075; d.qpos[3]=1.; d.qvel[:]=0.; mujoco.mj_forward(m,d)
    def infer():
        nonlocal last
        o=np.zeros(35,np.float32)
        o[3]=0.22*5.0; o[4:7]=d.qvel[3:6]*0.5; o[7:10]=d.xmat[site].reshape(3,3).T@UP
        o[10:14]=[d.qpos[qa[n]] for n in LEG]; o[16:20]=[d.qvel[va[n]]*0.1 for n in LEG]
        o[20:22]=[d.qvel[va[n]]*0.1 for n in WHL]; o[22:28]=last; o[28]=1.0
        a=sess.run(None,{inp:o.reshape(1,35)})[0][0].astype(np.float32); last=a
        for i,jn in enumerate(ACT_J): tgt[jn]=a[i]*(S_LEG if jn in LEG else S_WHL)
    frozen=dict(tgt); zs=[]; tl=[]
    for k in range(int(secs/dt)):
        if k%int(0.02/dt)==0:
            if policy: infer()
            frozen=dict(tgt)
        d.qfrc_applied[:]=0.
        for n in LEG:
            w=d.qvel[va[n]]; c=LEG_EFF*max(0.,1-abs(w)/LEG_VLIM)
            d.qfrc_applied[va[n]]=float(np.clip(KP*(frozen[n]-d.qpos[qa[n]])-KD*w,-c,c))
        for n in WHL:
            w=d.qvel[va[n]]; c=WHEEL_EFF*max(0.,1-abs(w)/WHEEL_VLIM)
            d.qfrc_applied[va[n]]=float(np.clip(WKD*(frozen[n]-w),-c,c))
        mujoco.mj_step(m,d); zs.append(d.qpos[2])
        qu=d.qpos[3:7]
        uwz=1-2*(qu[1]**2+qu[2]**2); tl.append(np.degrees(np.arccos(np.clip(uwz,-1,1))))
    return np.mean(zs[-20:]), max(tl), max(abs(np.array(zs[-20:])))
for dt in (0.001,0.002):
    for pol in (False,True):
        z,tm,mz=trial(dt,pol)
        print("dt=%.4f policy=%-5s  mean z(last 20 steps)=%+.4f  max tilt=%.1f deg  max|z|=%.4f"%(dt,pol,z,tm,mz))