import numpy as np, onnxruntime as ort
D=np.load(r"D:\claude2\fangzhen\docs\netio_v11.npz")
OBS=D["obs"]; ACT=D["act"]
print("deployed pairs: obs%s act%s"%(OBS.shape,ACT.shape))
ONNX=r"D:\claude2\fangzhen\train\deploy\rm_cc_v11_final.onnx"
s=ort.InferenceSession(ONNX,providers=["CPUExecutionProvider"]); ip=s.get_inputs()[0].name
print("onnx input %s shape %s"%(ip,s.get_inputs()[0].shape))
pred=np.stack([s.run(None,{ip:o.reshape(1,-1).astype(np.float32)})[0][0] for o in OBS])
err=np.abs(pred-ACT)
print("\nobs slots actually used (non-constant):")
for k in range(35):
    lo,hi=float(OBS[:,k].min()),float(OBS[:,k].max())
    if hi-lo>1e-6 or abs(hi)>1e-6: print("   obs[%2d] %+8.4f .. %+8.4f"%(k,lo,hi))
print("\naction comparison (deployed vs offline ONNX on the SAME obs):")
for k in range(6):
    print("   a[%d] deployed %+7.4f..%+7.4f | offline %+7.4f..%+7.4f | max|diff| %.2e"
          %(k,ACT[:,k].min(),ACT[:,k].max(),pred[:,k].min(),pred[:,k].max(),err[:,k].max()))
print("\nverdict: %s"%("IDENTICAL -> export + obs build are correct; the gap is in the plant/dynamics"
      if err.max()<1e-4 else "MISMATCH -> export or obs build is wrong (max diff %.2e)"%err.max()))
print("\naction amplitude: leg |a| max %.3f rad-equiv(%.3f rad), wheel |a| max %.3f -> %.1f rad/s"
      %(np.abs(ACT[:,0]).max(),np.abs(ACT[:,0]).max()*0.5,np.abs(ACT[:,4]).max(),np.abs(ACT[:,4]).max()*10))