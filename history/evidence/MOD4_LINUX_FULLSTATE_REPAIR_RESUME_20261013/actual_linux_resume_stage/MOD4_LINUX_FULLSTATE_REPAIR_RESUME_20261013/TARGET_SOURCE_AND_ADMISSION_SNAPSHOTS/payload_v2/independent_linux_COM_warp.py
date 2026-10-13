"""Independent represented native6 xyzw transform arithmetic; no setters/step.

The double-precision diagnostic remains separate from the actual SDK float32
representation. This checks consistency, not physical COM calibration.
"""
import warp as wp
import torch
@wp.kernel
def _represented(link:wp.array2d(dtype=wp.transform),local:wp.array2d(dtype=wp.transform),out:wp.array2d(dtype=wp.vec3)):
    i,j=wp.tid()
    out[i,j]=wp.transform_get_translation(wp.transform_multiply(link[i,j],local[i,j]))
def represented_COM(link,local):
    a=link.warp if hasattr(link,'warp') else link
    b=local.warp if hasattr(local,'warp') else local
    assert a.shape==b.shape and len(a.shape)==2
    out=wp.empty(a.shape,dtype=wp.vec3,device=a.device)
    wp.launch(_represented,dim=a.shape,inputs=[a,b],outputs=[out],device=a.device)
    return wp.to_torch(out)
