"""Build ONLY a new, narrow V6 source copy. Never execute SDK or old workers."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

B=Path(__file__).resolve().parent;ROOT=B.parent;OLD=ROOT/'source_app_close_semantics_v5'

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('exact V5 anchor count differs: '+old[:90])
    return text.replace(old,new,1)

def build():
    source=(OLD/'app_close_semantics_v5.py').read_text(encoding='utf-8')
    new=once(source,'Stdlib only.  No automatic installation, SDK import, checkpoint byte read,',
      'V6 narrow published export aliases; logical installation ABI app_close_semantics_v5.py.\nStdlib only.  No automatic installation, SDK import, checkpoint byte read,')
    new=once(new,"INTENT_NAME = 'APP_FAST_CLOSE_INTENT_V5.json'", "SOURCE_CODE_VERSION = 'V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES'\nINTENT_NAME = 'APP_FAST_CLOSE_INTENT_V5.json'")
    new=once(new,'    close_firstlineno: int\n','    close_firstlineno: int\n    module_aliases: tuple[str, ...] = ()\n')
    new=once(new,"'6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903', 848,\n)",
      "'6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903', 848,\n    module_aliases=('simulation_app.simulation_app',),\n)")
    new=once(new,'def _pin_original_app_close(application):', '''def _allowed_app_modules(pin):
    return (pin.module,) + pin.module_aliases


def _plain_actual_app_names(application):
    """Only type-level Python metadata, not SDK instance properties/getters."""
    cls = type(application)
    label = lambda c: (type.__getattribute__(c, '__module__') + '.'
                       + type.__getattribute__(c, '__qualname__'))
    return dict(actual_module=type.__getattribute__(cls, '__module__'),
                actual_type_name=type.__getattribute__(cls, '__name__'),
                actual_qualname=type.__getattribute__(cls, '__qualname__'),
                actual_class=label(cls),
                actual_MRO=[label(c) for c in type.__getattribute__(cls, '__mro__')])


def _helper_source_receipt():
    path = Path(__file__).resolve(strict=True)
    raw = path.read_bytes()
    return dict(source_code_version=SOURCE_CODE_VERSION, helper_source_file=str(path),
                helper_source_bytes=len(raw), helper_source_SHA256=hashlib.sha256(raw).hexdigest())


def _pin_original_app_close(application):
    actual = _plain_actual_app_names(application)
    try:
        return _pin_original_app_close_exact(application)
    except BaseException as exc:
        raise AppCloseEvidenceError(str(exc) + '; V6_ACTUAL_APP_PYTHON_NAMES='
                                    + json.dumps(actual, sort_keys=True)) from exc


def _pin_original_app_close_exact(application):''')
    new=once(new,"    _need(cls.__module__ == pin.module and cls.__qualname__ == pin.class_name,",
      "    actual_module = cls.__module__\n    _need(actual_module in _allowed_app_modules(pin) and cls.__qualname__ == pin.class_name,")
    new=once(new,'    _need(definition.__module__ == pin.module\n','    _need(definition.__module__ == actual_module\n')
    new=once(new,'    module = sys.modules.get(pin.module)\n','    module = sys.modules.get(actual_module)\n')
    new=once(new,"        close_module=pin.module, close_qualname=definition.__qualname__,",
      "        actual_module=actual_module, actual_type_name=cls.__name__,\n        close_module=actual_module, close_qualname=definition.__qualname__,")
    new=once(new,'    return receipt\n\n\ndef _validate_binding_receipt(value):',
      '    receipt.update(_helper_source_receipt())\n    return receipt\n\n\ndef _validate_binding_receipt(value):')
    new=once(new,"    class_id = pin.module + '.' + pin.class_name\n", "    actual_module = value.get('actual_module')\n    _need(type(actual_module) is str and actual_module in _allowed_app_modules(pin),\n          'pinned close receipt has unpublished actual module')\n    class_id = actual_module + '.' + pin.class_name\n")
    new=once(new,"        close_module=pin.module, close_qualname=pin.class_name + '.close',",
      "        actual_module=actual_module, actual_type_name=pin.class_name,\n        close_module=actual_module, close_qualname=pin.class_name + '.close',")
    new=once(new,'    for key, item in expected.items():\n', "    helper = _helper_source_receipt()\n    for key in ('source_code_version', 'helper_source_bytes', 'helper_source_SHA256'):\n        expected[key] = helper[key]\n    helper_path = value.get('helper_source_file')\n    _need(type(helper_path) is str and Path(helper_path).is_absolute()\n          and Path(helper_path).suffix == '.py', 'V6 helper source path is not absolute Python source')\n    for key, item in expected.items():\n")
    oldtree=ast.parse(source);newtree=ast.parse(new)
    changed={'_AppPin','_pin_original_app_close','_validate_binding_receipt'}
    untouched=[]
    for node in oldtree.body:
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name not in changed:
            match=next(n for n in newtree.body if isinstance(n,type(node)) and n.name==node.name)
            assert ast.dump(node,include_attributes=False)==ast.dump(match,include_attributes=False),node.name
            untouched.append(node.name)
    allowed={'_allowed_app_modules','_plain_actual_app_names','_helper_source_receipt','_pin_original_app_close_exact'}
    assert {n.name for n in newtree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}-{n.name for n in oldtree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}==allowed
    target=B/'app_close_semantics_v6.py';assert not target.exists(),'NEW output only'
    target.write_text(new,encoding='utf-8')
    (B/'SOURCE_PATCH_V5_TO_V6.diff').write_text(''.join(difflib.unified_diff(source.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='sealed_V5/app_close_semantics_v5.py',tofile='NEW_V6/app_close_semantics_v6.py')),encoding='utf-8')
    receipt=dict(kind='SOURCE_ONLY_TWO_PUBLISHED_EXPORT_ALIASES_V6',logical_stage_name='app_close_semantics_v5.py',
      source_file=str(target),bytes=len(target.read_bytes()),SHA256=hashlib.sha256(target.read_bytes()).hexdigest(),
      old_source_file=str(OLD/'app_close_semantics_v5.py'),old_SHA256=hashlib.sha256(source.encode()).hexdigest(),
      unchanged_function_or_class_AST=untouched,close_intent_error_FINAL_wait_gate_AST_unchanged=True,
      original_worker_owner_account_lease_deadline_learner_or_physics_written=False,actual_native_module=None)
    with (B/'BUILD_APP_CLOSE_COMPAT_V6.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(receipt))

if __name__=='__main__':build()
