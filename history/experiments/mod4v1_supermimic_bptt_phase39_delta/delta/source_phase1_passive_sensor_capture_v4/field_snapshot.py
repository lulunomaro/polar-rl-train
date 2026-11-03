"""V3 explicit field semantics over the independently published typed codec.

No leading-dimension heuristic, new device index, cast, MDP evaluation or export.
Cache/episode state trees are explicitly ENV_ROWS_WITNESS by their call site;
reset arguments and original bool masks have separate non-recursive entry points.
"""
from typed_capture_codec import CaptureCodec


class FieldSnapshot:
    def __init__(self, codec):
        if type(codec) is not CaptureCodec:
            raise TypeError('Exact published CaptureCodec instance required')
        self.codec = codec

    def rows(self, value, *, source_ref, source_field, clock):
        return self.codec.capture(value, role='ENV_ROWS_WITNESS',
                                  source_ref=source_ref, source_field=source_field,
                                  clock=clock, env_axis=0)

    def ids(self, value, *, source_ref, source_field, clock):
        return self.codec.capture(value, role='ENV_IDS_FULL',
                                  source_ref=source_ref, source_field=source_field,
                                  clock=clock, env_axis=None)

    def mask(self, value, *, source_ref, source_field, clock):
        return self.codec.capture(value, role='TERMINAL_BOOL_FULL',
                                  source_ref=source_ref, source_field=source_field,
                                  clock=clock, env_axis=0)

    def state(self, value, *, source_ref, source_field, clock):
        """Only an explicitly designated per-env state/queue metadata tree.

        Not the entry point for bridge.pre, reset IDs, actor trees or arbitrary
        unknown structures. Every tensor in THIS tree has declared env axis 0.
        Codec validation rejects a mismatched axis instead of guessing by shape.
        """
        if isinstance(value, self.codec.tensor_type):
            return self.rows(value, source_ref=source_ref,
                             source_field=source_field, clock=clock)
        if type(value) is dict:
            if not all(type(key) is str for key in value):
                raise TypeError('State field keys must be strings')
            return {key: self.state(item, source_ref=source_ref,
                                    source_field=source_field + '.' + key, clock=clock)
                    for key, item in value.items()}
        if type(value) in (tuple, list):
            return [self.state(item, source_ref=source_ref,
                               source_field=source_field + '[' + str(index) + ']', clock=clock)
                    for index, item in enumerate(value)]
        if value is None or type(value) in (bool, int, float, str):
            return value
        raise TypeError('Unsupported explicit state field: ' + type(value).__name__)


def tensor_snapshot_adapter(tensor_class, row_ids, num_envs, *, witness_env_ids):
    """V3 API: caller supplies the existing same-device index AND Python mapping.

    The codec records CALLER_DECLARED_INDEX_BINDING_NOT_READBACK; no index
    readback or equality claim is made. This is intentionally not B2's generic
    callable snapshot API. Reset ID dtype is never inferred from this index.
    """
    return FieldSnapshot(CaptureCodec(tensor_class, witness_index=row_ids,
                                     witness_env_ids=witness_env_ids, n=num_envs))
