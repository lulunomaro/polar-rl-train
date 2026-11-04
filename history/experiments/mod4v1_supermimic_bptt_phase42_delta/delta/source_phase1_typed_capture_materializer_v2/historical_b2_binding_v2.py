"""Pure-memory historical B2 publication selector; no filesystem or runtime probes.

The expected raw-seal pin is the separately published B2 source artifact, not a
handoff claim, active sensor selector, observed module, or generated expectation.
The caller supplies actual member identities from complete verify_package(...).
"""
from __future__ import annotations
import hashlib
import json

PUBLISHED_B2_BYTES = 2909
PUBLISHED_B2_SHA256 = 'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'
PUBLISHED_B2_MEMBERS = 13
PUBLISHED_B2_PROVENANCE = 'F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json'


def _need(condition, message):
    if not condition:
        raise ValueError('historical B2 publication: ' + message)


def _provenance(value):
    _need(type(value) is str, 'path must be a literal source string')
    normalized = value.replace('\\', '/')
    _need(normalized == PUBLISHED_B2_PROVENANCE, 'independent published source path differs')
    return normalized


def _members(rows, digest_key):
    _need(type(rows) is list and len(rows) == PUBLISHED_B2_MEMBERS, 'complete13 member rows required')
    result = {}
    for row in rows:
        _need(type(row) is dict and set(row) == {'relative', 'bytes', digest_key}, 'member row shape differs')
        rel, size, digest = row['relative'], row['bytes'], row[digest_key]
        _need(type(rel) is str and rel and '\\' not in rel and ':' not in rel,
              'member source relative path differs')
        _need(all(part not in ('', '.', '..') for part in rel.split('/')), 'member source traversal')
        _need(rel not in result, 'duplicate historical member')
        _need(type(size) is int and size > 0, 'member byte count must be exact positive int')
        _need(type(digest) is str and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest),
              'member digest must be exact lowercase SHA256')
        result[rel] = (size, digest)
    return result


def verify_published_B2_handoff(index, handoff, published_seal_raw, verified_member_rows):
    """Bind original_B2_reference_seal + handoff + actual13 to fixed raw B2.

    verified_member_rows is a complete list of {relative,bytes,SHA256} from the
    caller's actual pinned B2 package verification; True/claims are not proof.
    This function neither reads nor selects index['dependency_seals']['sensor'].
    """
    _need(type(published_seal_raw) is bytes, 'published raw seal bytes required')
    _need(len(published_seal_raw) == PUBLISHED_B2_BYTES and
          hashlib.sha256(published_seal_raw).hexdigest() == PUBLISHED_B2_SHA256,
          'fixed independently published raw seal pin differs')
    # Derive the declared member table only AFTER anchoring the immutable raw
    # publication. Actual member bytes/claims never generate the expected pin.
    published = json.loads(published_seal_raw)
    expected = _members(published['files'], 'sha256')
    _need(type(index) is dict and type(handoff) is dict, 'literal index and handoff mappings required')
    record = index.get('original_B2_reference_seal')
    _need(type(record) is dict and set(record) == {'path','bytes','SHA256','members','content_root_sha256'},
          'independent historical index record missing or changed')
    _provenance(record['path'])
    _need(type(record['bytes']) is int and record['bytes'] == PUBLISHED_B2_BYTES and
          type(record['SHA256']) is str and record['SHA256'] == PUBLISHED_B2_SHA256,
          'index claim differs from fixed publication')
    _need(record['content_root_sha256'] is None, 'original unprovided root must remain null')
    _need(_members(record['members'], 'SHA256') == expected, 'index complete13 differs from publication')
    _need(handoff.get('status') == 'PASS' and type(handoff.get('status')) is str,
          'diagnostic source handoff status differs')
    claim = handoff.get('B2_source_seal')
    _need(type(claim) is dict and set(claim) == {'path','bytes','sha256'}, 'historical handoff seal claim missing')
    _provenance(claim['path'])
    _need(type(claim['bytes']) is int and claim['bytes'] == PUBLISHED_B2_BYTES and
          type(claim['sha256']) is str and claim['sha256'] == PUBLISHED_B2_SHA256,
          'handoff claim differs from fixed publication')
    _need(_members(handoff.get('B2_members'), 'sha256') == expected,
          'handoff complete13 differs from publication')
    _need(_members(verified_member_rows, 'SHA256') == expected,
          'actual complete13 source identities differ from publication')
    return dict(kind='PHASE1_TYPED_MATERIALIZER_PUBLISHED_B2_HISTORY_BINDING_V2',
                source_only=True, expected_source='INDEPENDENT_FIXED_PUBLISHED_B2_RAW_SEAL',
                historical_index_selector='original_B2_reference_seal',
                raw_seal_bytes=PUBLISHED_B2_BYTES, raw_seal_SHA256=PUBLISHED_B2_SHA256,
                complete_members=PUBLISHED_B2_MEMBERS, actual_source_identity_rows=13,
                original_content_root_sha256=None, active_sensor_used_as_expected=False,
                native_enabled=False, exact=False, gate1='UNKNOWN', stage2_GO=False)
