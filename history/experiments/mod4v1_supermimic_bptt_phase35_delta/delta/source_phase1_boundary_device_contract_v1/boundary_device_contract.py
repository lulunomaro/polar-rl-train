"""SOURCE-only device contract. No Torch/SDK imports or native execution."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import inspect
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
V3=ROOT/'source_phase1_capture_worker_v3'
CORE_PIN=(37927,'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
BRIDGE_PIN=(13125,'8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29')
V3_SEAL='80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da'
V3_ROOT='b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963'
OLD='boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)'
NEW='boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)'


def identity(path):
    path=Path(path)
    if path.suffix.lower() not in ('.py','.json','.md','.txt'):raise ValueError('SOURCE suffix required')
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw,filename=str(path))
    return dict(path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def check(path,pin):
    row=identity(path)
    if (row['bytes'],row['SHA256'])!=pin:raise ValueError('full SOURCE pin mismatch: '+str(path))
    return row


def verify_v3():
    check(V3/'SOURCE_SEAL.json',(2920,V3_SEAL))
    seal=json.loads((V3/'SOURCE_SEAL.json').read_text(encoding='utf-8'))
    if seal['content_root_sha256']!=V3_ROOT or len(seal['files'])!=13:raise ValueError('V3 root/count mismatch')
    raw=json.dumps(seal['files'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    if hashlib.sha256(raw).hexdigest()!=V3_ROOT:raise ValueError('V3 full content root mismatch')
    for row in seal['files']:check(V3/row['relative'],(row['bytes'],row['sha256']))
    return seal


def source_paths():
    verify_v3()
    index=json.loads((V3/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))
    rows={}
    for key,pin in (('canonical',CORE_PIN),('bridge',BRIDGE_PIN)):
        found=[r for r in index['original17'] if (r['bytes'],r['SHA256'])==pin]
        if len(found)!=1:raise ValueError('unique original17 full source required: '+key)
        rows[key]=check(found[0]['path'],pin)
    rows['worker']=identity(V3/'worker_passive_interface_v1.py')
    return rows


def load_full_canonical(path=None):
    """Import complete fixed module; never crop/replace class or predicate."""
    source=Path(path) if path is not None else Path(source_paths()['canonical']['path'])
    row=check(source,CORE_PIN)
    name='_phase1_boundary_device_complete_canonical_metadata'
    spec=importlib.util.spec_from_file_location(name,source)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    try:spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name,None);raise
    if Path(module.__file__).resolve()!=source.resolve():raise ValueError('canonical import origin differs')
    cls=module.OriginalEpisodeBoundary
    expected={'__init__':['self','torch_module','device','n'],'for_action':['self'],
              'after_original_step':['self','terminated','truncated'],'receipt':['self']}
    for method,args in expected.items():
        if list(inspect.signature(getattr(cls,method)).parameters)!=args:raise ValueError('canonical boundary API differs')
    if inspect.signature(cls.__init__).parameters['n'].default!=80:raise ValueError('canonical N80 default differs')
    return module,row


def verify_source_contract():
    rows=source_paths();module,core=load_full_canonical(rows['canonical']['path'])
    text=Path(core['path']).read_text(encoding='utf-8')
    tree=ast.parse(text);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='OriginalEpisodeBoundary')
    expected=("self.t, self.device, self.n = torch_module, device, n",
              "and value.device == self.device", "self.next_start = (terminated | truncated).clone()")
    if any(x not in text for x in expected):raise ValueError('unmodified canonical device/mask predicate missing')
    bridge=Path(rows['bridge']['path']).read_text(encoding='utf-8')
    if 'self.device=torch.device(env.device)' not in bridge or 'terminated=term.bool(),truncated=trunc.bool()' not in bridge:
        raise ValueError('original bridge normalized device/separate bool flags absent')
    worker=(V3/'worker_passive_interface_v1.py').read_text(encoding='utf-8')
    if worker.count(OLD)!=1 or NEW in worker:raise ValueError('V3 old constructor callsite differs')
    return dict(kind='PHASE1_BOUNDARY_DEVICE_SOURCE_CONTRACT_V1',source_only=True,
        cause_status='SOURCE_CANDIDATE_NOT_ACTUAL_V3_ROOT_CAUSE_CONFIRMED',
        actual_V3_flags_shape_dtype_device=None,actual_env_device_type=None,
        actual_reports_read_by_this_child=False,source_paths=rows,
        full_canonical_imported=True,canonical_boundary_class_AST_sha256=hashlib.sha256(ast.dump(cls,include_attributes=False).encode()).hexdigest(),
        canonical_API_unchanged=True,predicate_relaxed=False,bridge_bool_conversion_changed=False,
        old_worker_call=OLD,new_worker_call=NEW,new_SDK_getters=0,
        proposed_change='use existing bridge.device normalized by original bridge constructor',
        Torch_CPU_fixture_executed_here=False,SDK_or_native_executed_here=False,
        actual_flags_claim='UNKNOWN; synthetic fixture is not an SDK observation')
