"""Lossless field-set schemas + positional JSON rows, original192MiB limit.

No sampling, float rounding, success filtering or unknown-field whitelist.
Only the JSON representation changes. Atomic schema publication precedes the
first referencing row; all producer hashes are accumulated without rereads.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import os

FORMAT227 = 'mod4.227.lossless_fieldset_positional_jsonl.v1'
LIMIT227 = 192*1024**2
PRODUCER227 = None
CONSTANT_FIELDS227 = frozenset((
    'source_SHA', 'record_type', 'end_reason', 'axis_semantics',
    'signed_yaw_tolerance', 'not_full_expert_or_signed2pi_cycle_graduation',
    'original_route_x', 'original_route_y', 'original_catalog_goal_radius',
    'goal_is_observer_only_not_a_new_reward_reset_or_skill_gate'))


def configure227_producer(metadata):
    global PRODUCER227
    PRODUCER227 = copy.deepcopy(metadata)


def encoded227(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf8')


def json_native227(value):
    """Reject unsupported values explicitly instead of silently changing keys."""
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError('Original JSON rows disallow NaN/Infinity')
        return
    if type(value) is list:
        for v in value:
            json_native227(v)
        return
    if type(value) is dict:
        for k, v in value.items():
            if type(k) is not str:
                raise TypeError('Lossless JSON requires string object keys')
            json_native227(v)
        return
    raise TypeError('Unsupported JSON row value: '+type(value).__name__)


class PositionalRows227:
    def __init__(self, out, model, *, limit_bytes=LIMIT227, producer_metadata=None):
        self.path = Path(out)/'RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl'
        self.header_path = Path(out)/'RM70_SAME_UID_COMMAND_AND_ROUTE_SCHEMAS227.json'
        if self.path.exists() or self.header_path.exists():
            raise FileExistsError('New producer requires unused output paths')
        self.model = model
        self.limit = limit_bytes
        self.h = hashlib.sha256()
        self.bytes = self.rows = self.dropped = 0
        self.limited = False
        self.schemas = []
        self.schema_ids = {}
        self.schema_rows = []
        self.header_bytes = 0
        self.header_SHA = None
        self.producer_metadata = copy.deepcopy(producer_metadata if producer_metadata is not None else PRODUCER227)
        self.file = self.path.open('xb')
        raw = self._header([])
        if len(raw) > self.limit:
            self.file.close()
            raise ValueError('Limit cannot retain the initial schema header')
        self._commit_header(raw)

    def _header(self, schemas):
        return encoded227(dict(format=FORMAT227, source_model_SHA=self.model,
            producer_metadata=self.producer_metadata,
            data_basename=self.path.name, byte_limit=self.limit,
            byte_limit_scope='retained data plus final schema header',
            float_encoding='Python JSON shortest roundtrip;no truncation',
            row_encoding='[schema_id,[values in positional_fields order]]',
            unknown_fields='Every new field-set is registered;never silently dropped',
            schemas=schemas, field_union=sorted({k for s in schemas for k in s['fields']})))

    def _commit_header(self, raw):
        temporary = self.header_path.with_suffix('.json.partial')
        with temporary.open('xb') as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, self.header_path)
        self.header_bytes = len(raw)
        self.header_SHA = hashlib.sha256(raw).hexdigest()

    def append(self, row):
        full = dict(source_SHA=self.model)
        full.update(row)
        json_native227(full)
        fields = tuple(sorted(full))
        constants = {k: full[k] for k in fields if k in CONSTANT_FIELDS227}
        # Serialized constants distinguish bool/int,1/1.0 and signed zero.
        signature = (fields, encoded227(constants))
        sid = self.schema_ids.get(signature)
        new = sid is None
        if new:
            sid = len(self.schemas)
            positional = [k for k in fields if k not in constants]
            schema = dict(schema_id=sid, fields=list(fields),
                          constants=copy.deepcopy(constants), positional_fields=positional)
            header = self._header(self.schemas+[schema])
        else:
            positional = self.schemas[sid]['positional_fields']
            header = None
        raw = encoded227([sid, [full[k] for k in positional]])+b'\n'
        header_bytes = len(header) if new else self.header_bytes
        if self.bytes+len(raw)+header_bytes > self.limit:
            # Original policy: keep counts, mark loss/UNKNOWN, never increase
            # the quota or preferentially retain successful episodes.
            self.limited = True
            self.dropped += 1
            return
        if new:
            self._commit_header(header)  # Atomic header BEFORE referenced data.
            self.schemas.append(schema)
            self.schema_ids[signature] = sid
            self.schema_rows.append(0)
        self.file.write(raw)
        self.h.update(raw)
        self.bytes += len(raw)
        self.rows += 1
        self.schema_rows[sid] += 1

    def finish(self):
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()
        return dict(path=str(self.path), bytes=self.bytes, rows=self.rows, SHA=self.h.hexdigest(),
            retention_limited=self.limited, dropped_rows=self.dropped,
            producer_SHA_without_reread=True, default_transfer='METADATA_ONLY',
            format=FORMAT227, schema_path=str(self.header_path), schema_bytes=self.header_bytes,
            schema_SHA=self.header_SHA, retained_total_bytes=self.bytes+self.header_bytes,
            retained_byte_limit=self.limit, attempted_rows=self.rows+self.dropped,
            schema_count=len(self.schemas), rows_by_schema=self.schema_rows,
            field_union=sorted({k for s in self.schemas for k in s['fields']}),
            producer_metadata=self.producer_metadata,
            actual_complete_byte_coverage='UNKNOWN_UNTIL_NEW_ACTUAL_CASE',
            limited_or_dropped_full_telemetry_claim='UNKNOWN_IF_ANY_DROP')
