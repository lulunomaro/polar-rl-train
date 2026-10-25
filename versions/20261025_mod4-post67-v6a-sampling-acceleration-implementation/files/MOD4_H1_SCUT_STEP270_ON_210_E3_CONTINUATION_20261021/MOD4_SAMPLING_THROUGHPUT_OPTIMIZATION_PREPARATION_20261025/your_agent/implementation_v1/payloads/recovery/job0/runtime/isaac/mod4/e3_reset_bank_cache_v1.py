"""Immutable source-bound E3 fixed-recipe geometry. No reset/SDK/RNG calls.

The original full SHA is checked once on startup from one bank byte read. Each
reset checks file identity metadata, joint order and cached tensor identity /
mutation counters before returning fresh selected tensors. A changed input raises;
it is never silently reloaded or accepted as a new geometry source.
"""
from pathlib import Path
import hashlib
import io
import stat
import numpy as np
import torch
from e1_rough_reset_tensor import joint_permutation

EXPECTED_BANK_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
EXPECTED_BANK_BYTES=32022178


def _identity(path):
    if path.is_symlink():
        raise RuntimeError('E3 immutable reset bank must be its own regular file')
    s=path.stat()
    if not stat.S_ISREG(s.st_mode):
        raise RuntimeError('E3 reset bank is not a regular file')
    return (str(path.resolve()),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


def _tensor_identity(value):
    return (id(value),value._version,value.data_ptr(),tuple(value.shape),tuple(value.stride()),
            value.dtype,value.device)


def _geometry(points,recipe):
    # Literal original float32 arithmetic; all original points, no approximation.
    device=points.device
    degrees=torch.tensor([-90.,-60.,-30.,30.,60.,90.],device=device)
    angle=torch.where(recipe<12,degrees[recipe.clamp(max=11)%6],0.)*torch.pi/180
    quat=torch.zeros((len(recipe),4),device=device)
    quat[torch.arange(len(recipe),device=device),torch.where(recipe<6,0,1)]=torch.sin(angle/2)
    quat[:,3]=torch.cos(angle/2)
    minimum=torch.empty(len(recipe),device=device)
    for first in range(0,len(recipe),128):
        last=min(first+128,len(recipe));v=quat[first:last,None,:3]
        p=points[None].expand(last-first,-1,-1)
        rot=p+2*torch.cross(v.expand_as(p),torch.cross(v.expand_as(p),p,dim=-1)+quat[first:last,None,3:4]*p,dim=-1)
        minimum[first:last]=rot[:,:,2].amin(-1)
    return quat,minimum,(1+torch.cos(angle))/2


class E3ResetBankCache:
    def __init__(self,path,robot_joint_names,device):
        self._path=Path(path).absolute()
        before=_identity(self._path)
        if before[3]!=EXPECTED_BANK_BYTES:
            raise RuntimeError('E3 immutable reset bank byte size differs from source manifest')
        raw=self._path.read_bytes()
        self._source_sha=hashlib.sha256(raw).hexdigest()
        if self._source_sha!=EXPECTED_BANK_SHA or _identity(self._path)!=before:
            raise RuntimeError('E3 immutable reset bank source SHA/identity mismatch')
        self._joint_names=tuple(robot_joint_names)
        with np.load(io.BytesIO(raw),allow_pickle=False) as bank:
            self._pick=int(np.argmin(abs(bank['root_height']-.25)))
            perm=joint_permutation(list(bank['joint_names']),list(self._joint_names))
            self._q=torch.as_tensor(bank['q'][self._pick,perm],device=device,dtype=torch.float32).clone()
            points=torch.as_tensor(bank['points_root'][self._pick],device=device,dtype=torch.float32)
        self._point_count=int(points.shape[0])
        if points.ndim!=2 or points.shape[1]!=3 or self._q.shape!=(30,):
            raise RuntimeError('E3 source-bound bank selected geometry shape mismatch')
        self._quat,self._minimum,self._initial=_geometry(points,torch.arange(13,device=device,dtype=torch.long))
        self._file_identity=before
        self._cache_identity=self._signature()
        # No bank bytes, all-pose arrays, or selected point cloud is held thereafter.
        del raw,points

    def _signature(self):
        return (self._pick,self._source_sha,self._joint_names,self._point_count,
                tuple(_tensor_identity(v) for v in (self._q,self._quat,self._minimum,self._initial)))

    def validate(self,robot_joint_names):
        if _identity(self._path)!=self._file_identity:
            raise RuntimeError('E3 immutable reset bank file changed after startup')
        if tuple(robot_joint_names)!=self._joint_names or self._signature()!=self._cache_identity:
            raise RuntimeError('E3 immutable reset cache or robot joint order changed')

    @property
    def source_sha(self):return self._source_sha

    @property
    def pick(self):return self._pick

    def selected_geometry(self,recipe,robot_joint_names):
        self.validate(robot_joint_names)
        if recipe.ndim!=1 or recipe.dtype!=torch.long or recipe.device!=self._q.device:
            raise RuntimeError('E3 original reset recipe dtype/shape/device mismatch')
        if not bool(((recipe>=0)&(recipe<=12)).all()):
            raise RuntimeError('E3 original reset recipe outside declared 0..12')
        # All returned tensors are fresh; SDK callers cannot mutate cached values.
        return (self._q[None].repeat(len(recipe),1),self._quat[recipe],self._minimum[recipe],self._initial[recipe])
