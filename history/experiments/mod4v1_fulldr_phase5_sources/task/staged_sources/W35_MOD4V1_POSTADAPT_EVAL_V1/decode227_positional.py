"""Explicit inverse for producer227. No file opens or implicit artifact reads.

Caller supplies the one admitted header byte buffer and an iterable of row
byte/string lines. These functions do not download, display or reread data.
"""
import copy
import json

FORMAT227 = 'mod4.227.lossless_fieldset_positional_jsonl.v1'


def header227(header_bytes):
    header = json.loads(header_bytes)
    if header['format'] != FORMAT227:
        raise ValueError('Unknown positional format')
    for i, s in enumerate(header['schemas']):
        fields = s['fields']
        dynamic = s['positional_fields']
        fixed = s['constants']
        if (s['schema_id'] != i or len(fields) != len(set(fields)) or
            len(dynamic) != len(set(dynamic)) or set(dynamic)&set(fixed) or
            set(fields) != set(dynamic)|set(fixed)):
            raise ValueError('Schema cannot reconstruct every original field')
    return header


def decode227(header, lines):
    for line in lines:
        record = json.loads(line)
        if not isinstance(record, list) or len(record) != 2:
            raise ValueError('Expected [schema_id, positional_values]')
        sid, values = record
        if type(sid) is not int or not 0 <= sid < len(header['schemas']):
            raise ValueError('Unknown schema ID; data is not silently skipped')
        s = header['schemas'][sid]
        if not isinstance(values, list) or len(values) != len(s['positional_fields']):
            raise ValueError('Positional value count mismatch')
        row = copy.deepcopy(s['constants'])
        row.update(zip(s['positional_fields'], values))
        # Original dict insertion order is not a measurement; all key/value
        # pairs, nested JSON types, finite floats and chronological rows remain.
        yield {k:row[k] for k in s['fields']}
