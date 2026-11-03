"""Own stdlib tensor-shaped test object. NOT torch/SDK/numerical evidence.
Only supports metadata and passive detach/index_select/clone/deferred list export.
Forbidden observer operations are deliberate hard failures in these fake tests.
"""
from collections import Counter
from copy import deepcopy


class FakeTensor:
    operations = Counter()
    is_synthetic_fixture = True

    def __init__(self, values, dtype='torch.float64'):
        self.values = deepcopy(values)
        self.dtype = dtype

    @property
    def shape(self):
        value = self.values
        result = []
        while type(value) is list:
            result.append(len(value))
            if not value:
                break
            value = value[0]
        return tuple(result)

    @property
    def ndim(self):
        return len(self.shape)

    def numel(self):
        result = 1
        for width in self.shape:
            result *= width
        return result

    def detach(self):
        type(self).operations['detach'] += 1
        return self

    def clone(self):
        type(self).operations['clone'] += 1
        return type(self)(self.values, self.dtype)

    def index_select(self, axis, rows):
        type(self).operations['index_select'] += 1
        if axis != 0 or not isinstance(rows, FakeTensor):
            raise AssertionError('Only explicit pre-existing fake witness row selection')
        return type(self)([self.values[i] for i in rows.values], self.dtype)

    def cpu(self):
        type(self).operations['cpu'] += 1
        return self

    def tolist(self):
        type(self).operations['tolist'] += 1
        return deepcopy(self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, item, value):
        self.values[item] = deepcopy(value)

    def __iter__(self):
        return iter(self.values)

    def nonzero(self, *args, **kwargs):
        raise AssertionError('Observer must not compute reset IDs')

    def any(self, *args, **kwargs):
        raise AssertionError('Observer must not calculate terminal masks')

    def sum(self, *args, **kwargs):
        raise AssertionError('Observer must not reduce terminal masks')

    def to(self, *args, **kwargs):
        raise AssertionError('Observer must not cast original dtype')

    def bool(self, *args, **kwargs):
        raise AssertionError('Observer must not recreate original flags')

    def long(self, *args, **kwargs):
        raise AssertionError('Observer must preserve original reset ID dtype')

    def int(self, *args, **kwargs):
        raise AssertionError('Observer must preserve original reset ID dtype')
