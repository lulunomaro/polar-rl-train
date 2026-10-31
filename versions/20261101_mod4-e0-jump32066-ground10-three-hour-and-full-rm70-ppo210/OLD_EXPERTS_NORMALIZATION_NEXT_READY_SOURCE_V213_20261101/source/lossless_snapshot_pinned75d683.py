"""Only verified generic serialization reused; no W35 profile/guard/model code."""
import math
from collections.abc import Mapping
from types import SimpleNamespace
from tensordict import TensorDictBase

def encode_snapshot_mapping_key(key):
    if key is None:return dict(kind='none')
    if isinstance(key,bool):return dict(kind='bool',value=key)
    if isinstance(key,int):return dict(kind='int',value=key)
    if isinstance(key,str):return dict(kind='str',value=key)
    if isinstance(key,float) and math.isfinite(key):return dict(kind='float',value=key)
    if isinstance(key,tuple):return dict(kind='tuple',items=[encode_snapshot_mapping_key(k) for k in key])
    raise TypeError('Unsupported snapshot mapping key type: ' + type(key).__name__)

class LosslessSnapshot:
    def __init__(self,torch,num_envs,selected):
        self.t=torch;self.real=SimpleNamespace(num_envs=num_envs);self.selected=selected

    def _snapshot(self, value, path=''):
        t = self.t
        if t.is_tensor(value):
            rng = any(x in path.lower() for x in ('rng', 'generator'))
            per_env = value.ndim > 0 and value.shape[0] == self.real.num_envs and not rng
            v = value[self.selected] if per_env else value
            return dict(dtype=str(v.dtype), shape=list(v.shape), original_shape=list(value.shape),
                        axis0_is_selected_env=per_env, value=v.detach().cpu().tolist())
        if isinstance(value, TensorDictBase):
            items = list(value.items())
            if not all(isinstance(k, str) for k, _ in items):
                raise TypeError('Non-string TensorDict key at ' + path)
            original_batch = list(value.batch_size)
            selected_batch = list(original_batch)
            if original_batch and original_batch[0] == self.real.num_envs and not any(x in path.lower() for x in ('rng', 'generator')):
                selected_batch[0] = len(self.selected)
            return dict(container_type='tensordict.TensorDictBase',
                        concrete_type=type(value).__module__ + '.' + type(value).__qualname__,
                        original_batch_size=original_batch, snapshot_batch_size=selected_batch,
                        original_device=str(value.device) if value.device is not None else None,
                        entries={k: self._snapshot(v, path + '/' + k) for k, v in items})
        if isinstance(value, Mapping):
            items = list(value.items())
            if all(isinstance(k, str) for k, _ in items):
                return {k: self._snapshot(v, path + '/' + k) for k, v in items}
            return dict(container_type='typed_key_mapping',
                        concrete_type=type(value).__module__ + '.' + type(value).__qualname__,
                        entries=[dict(key=encode_snapshot_mapping_key(k), value=self._snapshot(v, path + '/' + str(k))) for k, v in items])
        if isinstance(value, (tuple, list)):
            return [self._snapshot(v, path + '/' + str(i)) for i, v in enumerate(value)]
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        raise TypeError('Unsupported actual domain value at ' + path + ': ' + type(value).__name__)
