import numpy as np
A=np.load(r"D:\claude2\fangzhen\docs\netio_jump.npz")["data"]
t=A[:,0]; pub=A[:,1]; OBS=A[:,2:37]; ACT=A[:,37:43]
armed=OBS[:,32]>0.5; idle=~armed
print("samples %d  published jump %d  obs[32] armed %d (%.2f s)"%(len(A),int(pub.sum()),int(armed.sum()),armed.sum()*0.02))
print("obs[32] values seen:",np.unique(np.round(OBS[:,32],3))[:8])
lab=["L_front1","L_rear1","R_front1","R_rear1","L_wheel","R_wheel"]
if armed.sum()<10:
    print("\nobs[32] NEVER reached the policy -> the flag is lost between Twist.linear.y and obs[32]")
    print("published linear.y windows: t=%s"%np.round(t[pub>0.5][::25],2)[:12])
    raise SystemExit(0)
print("\n=== policy ACTIONS (raw) ===")
for k in range(6):
    a=ACT[armed,k]; b=ACT[idle,k]
    print("  a[%d] %-9s idle mean %+7.4f span %.4f | armed mean %+7.4f span %.4f | delta %+7.4f"
          %(k,lab[k],b.mean(),b.max()-b.min(),a.mean(),a.max()-a.min(),a.mean()-b.mean()))
print("\n=== commanded targets (legs x0.5 rad, wheels x10 rad/s) ===")
for k in range(6):
    sc=0.5 if k<4 else 10.0
    a=ACT[armed,k]*sc; b=ACT[idle,k]*sc
    print("  tgt %-9s idle %+7.3f | armed %+7.3f .. %+7.3f  swing %.3f"%(lab[k],b.mean(),a.min(),a.max(),a.max()-a.min()))