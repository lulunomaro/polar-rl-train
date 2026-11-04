"""One-shot SOURCE derivation from complete frozen typed materializer V1.

No Source loader/builder/prepare/metadata/stage/entry is executed. Never run on
an existing V2 output: every generated member is create-only.
"""
from pathlib import Path
import ast
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / 'source_phase1_typed_capture_materializer_v1'
PIN = (48397, '0fbaad211b341c0d5cce5a429a1832c02230b2cfdfc15fb9100576514477c00b')
OLD = "    need(handoff['status']=='PASS' and handoff['B2_source_seal']['sha256']==DEPENDENCY_SEALS['sensor'][1],'diagnostic B2 final handoff differs')\n"
NEW = """    historical_record=index['original_B2_reference_seal']
    historical_path=reference_path(source_root,historical_record['path'])
    historical_members,_=verify_package(historical_path.parent,'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a',13)
    _,historical_raw=metadata(historical_path)
    historical_binding=verify_published_B2_handoff(index,handoff,historical_raw,
        [dict(relative=rel,bytes=info['bytes'],SHA256=info['SHA']) for rel,(_,info) in historical_members.items() if rel!='SOURCE_SEAL.json'])
"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace_once(text, old, new):
    assert text.count(old) == 1, 'exact complete-module derivation hunk differs'
    return text.replace(old, new, 1)


def nodes(text):
    return {n.name:n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}


def whole_source(text, node):
    # Used only for full-function evidence/diff, never to generate runtime code.
    return ''.join(text.splitlines(keepends=True)[node.lineno-1:node.end_lineno])


def create(name, raw):
    with (HERE/name).open('xb') as out:
        out.write(raw)


def main():
    original = (V1/'stage_phase1_typed_capture_v1.py').read_bytes()
    assert (len(original),sha(original)) == PIN
    old = original.decode('utf-8')
    new = replace_once(old, 'import tempfile\n', 'from historical_b2_binding_v2 import verify_published_B2_handoff\nimport tempfile\n')
    new = replace_once(new, "SOURCE_DERIVATION_LINEAGE='COMPLETE_FROZEN_V4_TO_TYPED_V1'\n",
                       "SOURCE_DERIVATION_LINEAGE='COMPLETE_FROZEN_V4_TO_TYPED_V1'\nMATERIALIZER_SOURCE_PUBLICATION=2\n")
    new = replace_once(new, OLD, NEW)
    new = replace_once(new, '        diagnostic_source_references=4,diagnostic_final_handoff=1,source_dependency_files=len(inputs),\n',
                       '        diagnostic_source_references=4,diagnostic_final_handoff=1,source_dependency_files=len(inputs),\n        historical_B2_reference_binding=historical_binding,\n')
    before,after = nodes(old),nodes(new)
    assert list(before)==list(after) and len(before)==14
    report=[]
    for name,n in before.items():
        m=after[name];a=whole_source(old,n);b=whole_source(new,m)
        same_ast=ast.dump(n,include_attributes=False)==ast.dump(m,include_attributes=False)
        same_source=a==b
        assert (same_ast and same_source)==(name!='verify_B2_source_closure')
        report.append(dict(name=name,old_lines=[n.lineno,n.end_lineno],new_lines=[m.lineno,m.end_lineno],
                           old_source_SHA256=sha(a.encode()),new_source_SHA256=sha(b.encode()),
                           entire_AST_equal=same_ast,entire_function_source_equal=same_source))
    for name,pin in [('static_source_helpers_v1.py',(10078,'11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2')),
                     ('typed_source_support_v1.py',(13308,'6390b2235b416406ac8a6cb21aaf4f1fc2eb6adfe95e50cafbfe234610cbb575')),
                     ('SOURCE_MIRROR_INPUTS.json',(93889,'c47b837bce45d3fa3c917db437181ee83814feef0ca0c2b67df4f0c6f49d9d90'))]:
        raw=(V1/name).read_bytes();assert (len(raw),sha(raw))==pin;create(name,raw)
    create('stage_phase1_typed_capture_v2.py',new.encode())
    changed='verify_B2_source_closure'
    function_diff=''.join(difflib.unified_diff(whole_source(old,before[changed]).splitlines(True),
                         whole_source(new,after[changed]).splitlines(True),
                         fromfile=str(V1/'stage_phase1_typed_capture_v1.py')+':complete '+changed,
                         tofile=str(HERE/'stage_phase1_typed_capture_v2.py')+':complete '+changed,n=1000))
    create('FUNCTION_SOURCE_DIFF.txt',function_diff.encode())
    create('MODULE_SOURCE_DIFF.txt',''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
           fromfile=str(V1/'stage_phase1_typed_capture_v1.py'),tofile=str(HERE/'stage_phase1_typed_capture_v2.py'))).encode())
    packet=dict(kind='COMPLETE_TYPED_V1_TO_V2_HISTORY_FUNCTION_SOURCE_DIFF_V1',materializer_publication=2,
                original_complete_stage=dict(bytes=len(original),SHA256=sha(original)),
                new_complete_stage=dict(bytes=len(new.encode()),SHA256=sha(new.encode())),
                original_top_functions=14,entire_source_and_AST_unchanged=13,
                changed_only_function='verify_B2_source_closure',functions=report,
                complete_runtime_source_generated_by='UNIQUE_LOCAL_HUNKS_IN_ENTIRE_FROZEN_V1_MODULE_NOT_AST_SLICES',
                immutable_shared_helpers=17,typed_support_and_396_mirror_whole_bytes_unchanged=True,
                source_receipt_protocol_family_V1_unchanged=True,actual_source_entry_calls=0)
    create('FUNCTION_SOURCE_DIFF.json',(json.dumps(packet,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps(packet['new_complete_stage']|dict(whole_functions_unchanged=13,helpers_unchanged=17,actual_entry_calls=0)))


if __name__=='__main__':
    main()
