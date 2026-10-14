"""Platform-neutral tensor inspection; no Linux guard/SDK/launcher imports."""
import torch
def walk(x,key=''):
    if torch.is_tensor(x):yield key,x
    elif hasattr(x,'items'):
        for k,v in x.items():yield from walk(v,key+'/'+str(k))
    elif isinstance(x,(tuple,list)):
        for i,v in enumerate(x):yield from walk(v,key+'/'+str(i))
def equal(a,b):
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if hasattr(a,'items'):return set(a.keys())==set(b.keys()) and all(equal(a[k],b[k]) for k in a.keys())
    if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return type(a)is type(b) and a==b
