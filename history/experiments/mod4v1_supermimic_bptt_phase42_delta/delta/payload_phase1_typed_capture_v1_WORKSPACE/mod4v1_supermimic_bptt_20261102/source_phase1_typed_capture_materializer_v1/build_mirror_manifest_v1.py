"""Build only a textual R/T SOURCE-input manifest; never prepare or stage a root.

All old 332 R entries are retained unchanged. Only the one already-pinned T
source is admitted. Historical report references in a source seal are metadata,
not SOURCE dependencies, and are rejected lexically before any filesystem call.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from static_source_helpers_v1 import denied, need, no_links, safe_relative

HERE = Path(__file__).resolve().parent
R = HERE.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'
PRODUCER = 'source_phase1_typed_native_capture_v1'
OLD = 'source_phase1_capture_materializer_v4'
T_RELATIVE = 'NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py'
T_PIN = (653, 'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc')
PATCHES = {
 ('source_phase1_passive_sensor_capture_v4', 'SOURCE_DIFF.patch'):
   (8378, 'd59e5c2587e93d057c5b9c3498ddfb6b28fdeeecb15189880210de4bb3565fa3'),
 ('source_phase1_actuation_clock_scope_v2', 'C1_TO_C2_SOURCE_DIFF.patch'):
   (6231, 'fe80994ac0db9e24e89a40138b6a62d6825c1bd0c794c9b8c2183a51676b9793'),
}


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def products():
    files = {}
    excluded = set()
    roots = {'R': R, 'T': T}
    def add(root, relative, expected=None):
        relative = safe_relative(relative)
        need(not any(denied(p) for p in relative.split('/')), 'non-SOURCE mirror input')
        if root == 'T':
            need(relative == T_RELATIVE and expected == T_PIN, 'only the original fixed T SOURCE is admitted')
        suffix = Path(relative).suffix.lower()
        need(suffix in ('.py', '.json', '.md', '.txt', '.patch'), 'non-textual SOURCE mirror input')
        if suffix == '.patch':
            parts = relative.split('/')
            need(len(parts) == 2 and (parts[0], parts[1]) in PATCHES,
                 'only two exact published SOURCE proof patches are admitted')
            need(expected == PATCHES[(parts[0], parts[1])], 'SOURCE proof patch pin differs')
        # No stat, classify, symlink or open operation precedes lexical denial.
        path = no_links(roots[root], relative)
        raw = path.read_bytes()
        actual = (len(raw), H(raw))
        need(expected is None or actual == expected, 'SOURCE mirror bytes differ: ' + relative)
        if suffix == '.py':
            ast.parse(raw, filename=str(path))
        row = dict(root=root, relative=relative, bytes=actual[0], SHA256=actual[1])
        key = (root, relative)
        need(key not in files or files[key] == row, 'conflicting deduplicated SOURCE input')
        files[key] = row
        return raw

    def reference(value, expected):
        value = str(value).replace('\\', '/')
        for root, base in roots.items():
            marker = '/' + base.name + '/'
            if marker in value:
                need(value.count(marker) == 1, 'ambiguous SOURCE provenance')
                relative = value.split(marker, 1)[1]
                # Deliberately never follow actual-report/model/raw provenance.
                if any(denied(p) for p in safe_relative(relative).split('/')):
                    excluded.add(value)
                    return
                add(root, relative, expected)
                return
        raise ValueError('unknown SOURCE provenance root')

    def path_rows(value):
        if type(value) is dict:
            path = value.get('path')
            size = value.get('bytes')
            sha = value.get('SHA256', value.get('sha256'))
            if type(path) is str and type(size) is int and type(sha) is str:
                reference(path, (size, sha))
            for item in value.values():
                path_rows(item)
        elif type(value) is list:
            for item in value:
                path_rows(item)

    old_raw = add('R', OLD + '/SOURCE_MIRROR_INPUTS.json')
    old = json.loads(old_raw)
    need(old['file_count'] == len(old['files']) == 332, 'original complete 332 SOURCE mirror required')
    for row in old['files']:
        add('R', row['relative'], (row['bytes'], row['SHA256']))
    index_raw = add('R', PRODUCER + '/CAPTURE_SOURCE_INDEX.json',
        (148229, '92da4a44ca9b7b6246c82d4dd281b73fa176bc1bdfbac981aa3403e43d7873d8'))
    index = json.loads(index_raw)
    path_rows(index)
    # Complete publisher and dependency packages, not just their active aliases.
    package_paths = [PRODUCER + '/SOURCE_SEAL.json']
    package_paths += [row['path'].replace('\\', '/').split('/' + R.name + '/', 1)[1]
                      for row in index['dependency_seals'].values()]
    package_paths += [index['original_B2_reference_seal']['path'].replace('\\', '/').split('/' + R.name + '/', 1)[1]]
    for relative in package_paths:
        seal_raw = add('R', relative)
        seal = json.loads(seal_raw)
        members = seal.get('files', seal.get('members'))
        if type(members) is dict:
            members = [dict(relative=name, **row) for name, row in members.items()]
        need(type(members) is list, 'complete SOURCE seal member list required')
        package = relative.rsplit('/', 1)[0]
        for row in members:
            name = row.get('relative', row.get('name'))
            add('R', package + '/' + safe_relative(name),
                (row['bytes'], row.get('sha256', row.get('SHA256'))))
        path_rows(seal)
    # The CODEC metadata deliberately retains the identical V3 field-source path.
    codec = json.loads(add('R', 'source_phase1_passive_sensor_capture_v4/CODEC_SOURCE_PINS.json',
        (19153, '5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452')))
    def codec_rows(value):
        if type(value) is dict:
            path, sha = value.get('source_path'), value.get('source_sha256')
            if type(path) is str and type(sha) is str:
                # Size comes only from an already-frozen whole-file row, not live expectations.
                known = {row['SHA256']: row['bytes'] for row in files.values()}
                need(sha in known, 'CODEC function source lacks a complete frozen whole-file pin')
                reference(path, (known[sha], sha))
            for item in value.values():
                codec_rows(item)
        elif type(value) is list:
            for item in value:
                codec_rows(item)
    codec_rows(codec)
    rows = [files[key] for key in sorted(files)]
    need(sum(row['root'] == 'T' for row in rows) == 1, 'exact one explicit fixed T SOURCE required')
    old_rows = {(row['relative'], row['bytes'], row['SHA256']) for row in old['files']}
    new_r = {(row['relative'], row['bytes'], row['SHA256']) for row in rows if row['root'] == 'R'}
    need(old_rows <= new_r, 'old complete 332 R inputs must be retained unmodified')
    return dict(kind='PHASE1_TYPED_MATERIALIZER_R_T_SOURCE_MIRROR_INPUTS_V1', source_only=True,
        roots={'R': dict(provenance=str(R).replace('\\', '/'), cli='--source-root'),
               'T': dict(provenance=str(T).replace('\\', '/'), cli='--t-source-root',
                         only_relative=T_RELATIVE, bytes=T_PIN[0], SHA256=T_PIN[1])},
        file_count=len(rows), R_file_count=sum(row['root'] == 'R' for row in rows), T_file_count=1,
        original_R_332_unmodified=True, files=rows,
        excluded_denied_historical_metadata_references=len(excluded),
        exclusion_rule='model/operational/raw/reports names denied lexically before stat/classify/open',
        explicit_mirrors_only=True, windows_provenance_is_not_runtime_path=True,
        no_windows_fallback=True, B2_full_source_files=155, B2_source_pin_references=435,
        C1_original_source_pins=182, active_aliases=34, overlay_aliases=32,
        independent_baseline_bootstrap_aliases=2, materialized_runtime_roots=0,
        prepare_calls=0, preflight_calls=0, stage_calls=0, parent_launches=0,
        native_enabled=False, exact=False, gate1='UNKNOWN', stage2_GO=False)


def main():
    value = products()
    target = HERE / 'SOURCE_MIRROR_INPUTS.json'
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    with target.open('xb') as stream:
        stream.write(raw)
    print(json.dumps(dict(status='SOURCE_ONLY_MANIFEST_WRITTEN', bytes=len(raw), SHA256=H(raw),
                         files=value['file_count'], R=value['R_file_count'], T=value['T_file_count'])))


if __name__ == '__main__':
    main()
