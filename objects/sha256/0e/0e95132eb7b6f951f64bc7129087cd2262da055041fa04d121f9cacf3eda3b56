"""Minimal probe: can the self-written harness hold the v11 stance at all?"""
import os,sys,numpy as np,mujoco,onnxruntime as ort
XML=r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
ONNX=sys.argv[1] if len(sys.argv)>1 else r"D:/claude2/fangzhen/train/deploy/rm_cc_v11_final.onnx"
DT=0.002; KP,KD,WKD=60.,2.,1.5; S_LEG,S_WHL=0.5,10.
LEG_VLIM,WHEEL_VLIM=17.,63.4; LEG_EFF,WHEEL_EFF=40.,5.5
m=mujoco.MjModel.from_xml_path(XML); d=mujoco.MjData(m); m.opt.timestep=DT
J=lambda n: mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,n)
ACT_J=[mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,m.actuator_trnid[i][0]) for i in range(m.nu)]
LEG=[j for j in ACT_J if "wheel" not in j]; WHL=[j for j in ACT_J if "wheel" in j]
qa={n:m.jnt_qposadr[J(n)] for n in ACT_J}; va={n:m.dof_jntid[m.jnt_dofadr[J(n)]] for n in ACT_J}
va={n:m.jnt_dofadr[J(n)] for n in ACT_J}
site=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_SITE,"imu")
sess=ort.InferenceSession(ONNX,providers=["CPUExecutionProvider"]); inp=sess.get_inputs()[0].name
UP=np.array([0.,0.,-1.]); last=np.zeros(6,np.float32); tgt={n:0.0 for n in ACT_J}
d.qpos[:]=0.; d.qpos[2]=0.075; d.qpos[3]=1.; d.qvel[:]=0.; mujoco.mj_forward(m,d)
def infer(vx=0.0,ry=0.0,yaw=0.0,height=0.22,jump=0.0):
    global last,tgt
    g=d.xmat[site].reshape(3,3).T@UP
    o=np.zeros(35,np.float32)
    o[0],o[1],o[2],o[3]=vx,ry,yaw,height*5.0
    o[4:7]=d.qvel[3:6]*0.5
    o[7:10]=g
    o[10:14]=[d.qpos[qa[n]] for n in LEG]
    o[16:20]=[d.qvel[va[n]]*0.1 for n in LEG]
    o[20:22]=[d.qvel[va[n]]*0.1 for n in WHL]
    o[22:28]=last; o[28]=1.0; o[32]=jump
    a=sess.run(None,{inp:o.reshape(1,35)})[0][0].astype(np.float32); last=a
    for i,jn in enumerate(ACT_J):
        tgt[jn]=a[i]*(S_LEG if jn in LEG else S_WHL)
    return o,a
print("LEG order used for obs[10:14]:",LEG)
o,a=infer(); print("first obs:",np.round(o,3)); print("first act:",np.round(a,3))
frozen=dict(tgt)
for k in range(int(4.0/DT)):
    if k%int(0.02/DT)==0: infer(); frozen=dict(tgt)
    d.qfrc_applied[:]=0.
    for n in LEG:
        w=d.qvel[va[n]]; c=LEG_EFF*max(0.,1-abs(w)/LEG_VLIM)
        d.qfrc_applied[va[n]]=float(np.clip(KP*(frozen[n]-d.qpos[qa[n]])-KD*w,-c,c))
    for n in WHL:
        w=d.qvel[va[n]]; c=WHEEL_EFF*max(0.,1-abs(w)/WHEEL_VLIM)
        d.qfrc_applied[va[n]]=float(np.clip(WKD*(frozen[n]-w),-c,c))
    mujoco.mj_step(m,d)
    if k%int(0.25/DT)==0 or k==int(4.0/DT)-1:
        qu=d.qpos[3:7]
        uw=np.array([2*(qu[1]*qu[3]-qu[0]*qu[2]),2*(qu[2]*qu[3]+qu[0]*qu[1]),1-2*(qu[1]**2+qu[2]**2)])
        tilt=np.degrees(np.arccos(np.clip(uw[2],-1,1)))
        print("t=%.2f  z=%+.4f  tilt=%6.2f deg  vx=%+.3f  wheel w=%+.2f %+.2f  leg q=%s"%(
            (k+1)*DT,d.qpos[2],tilt,d.qvel[0],d.qvel[va[WHL[0]]],d.qvel[va[WHL[1]]],
            np.round([d.qpos[qa[n]] for n in LEG],3)))