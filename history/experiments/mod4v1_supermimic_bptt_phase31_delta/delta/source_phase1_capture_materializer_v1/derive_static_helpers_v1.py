"""Derive only this materializer's stdlib helpers from whole original functions.
No native/runtime/static-tree source is sliced. No old script is imported/run.
"""
from pathlib import Path
import ast
import hashlib

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'
PIN=(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40')
FUNCTIONS=('need','H','is_sha','lexical','model_path','metadata','safe_relative','denied','no_links','identity','tree','digest_tree','semantic_success','paired_plan','verify_close_dependency_imports','put_once','put_json')
CONSTANTS={'MODEL_SUFFIXES','DENIED_SUFFIXES','DENIED_NAMES','POSE_SHA','DEPENDENCY_PIN','APP_CLOSE_PIN'}


def main():
    raw=OLD.read_bytes();assert (len(raw),hashlib.sha256(raw).hexdigest())==PIN
    text=raw.decode();lines=text.splitlines(keepends=True);parsed=ast.parse(text)
    selected=[n for n in parsed.body if isinstance(n,(ast.Import,ast.ImportFrom))
              or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in CONSTANTS for t in n.targets)
              or isinstance(n,ast.FunctionDef) and n.name in FUNCTIONS]
    body='"""17 exact whole original stdlib materializer helpers; never native entrypoints.\n\nOnly helper-component derivation, NOT pruning any installed runtime/static tree.\n"""\n'
    body+='\n'.join(''.join(lines[n.lineno-1:n.end_lineno]) for n in selected)+'\n'
    new=ast.parse(body);old_funcs={n.name:ast.dump(n,include_attributes=False) for n in parsed.body if isinstance(n,ast.FunctionDef)}
    new_funcs={n.name:ast.dump(n,include_attributes=False) for n in new.body if isinstance(n,ast.FunctionDef)}
    assert set(new_funcs)==set(FUNCTIONS) and all(old_funcs[k]==v for k,v in new_funcs.items())
    target=HERE/'static_source_helpers_v1.py';encoded=body.encode()
    if target.exists():assert target.read_bytes()==encoded, 'existing NEW helper source differs'
    else:
        with target.open('xb') as stream:stream.write(encoded)
    print(dict(kind='EXACT_17_HELPERS_DERIVED_NOT_MATERIALIZED',bytes=len(encoded),SHA256=hashlib.sha256(encoded).hexdigest()))


if __name__=='__main__':main()
