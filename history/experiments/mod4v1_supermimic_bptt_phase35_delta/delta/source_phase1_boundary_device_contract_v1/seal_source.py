"""Write-once stdlib-only boundary source seal; never execute Torch fixture."""
from pathlib import Path
from collections import Counter
import hashlib
import io
import json
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent
BASE=('README.md','boundary_device_contract.py','torch_cpu_fixture.py','test_boundary_device_source.py','seal_source.py')
OUTPUTS=('FAKE_TEST_LOG.txt','SOURCE_PINS.json','SOURCE_RECEIPT.json','SOURCE_SEAL.json')
AUDIT=Counter()


def audit(event,args):
    if event=='import' and str(args[0]).split('.')[0] in ('torch','numpy','isaacsim','isaaclab','omni','pxr','warp','paramiko','psutil'):
        AUDIT['forbidden_native_import']+=1;raise RuntimeError('SOURCE-only native import')
    if event in ('subprocess.Popen','os.system') or event.startswith('socket.'):
        AUDIT['forbidden_process_or_network']+=1;raise RuntimeError('SOURCE-only process/network')
    if event=='open' and isinstance(args[0],(str,bytes)):
        path=Path(args[0]).resolve();mode=args[1] or '';flags=args[2] if len(args)>2 else 0
        if path.suffix.lower() in ('.pt','.pth','.ckpt','.npz','.npy','.raw','.pkl','.pickle'):
            AUDIT['forbidden_model_or_raw']+=1;raise RuntimeError('SOURCE-only model/raw')
        if path.suffix=='.lock' or 'budget' in path.name.lower():
            AUDIT['forbidden_ledger_or_lock']+=1;raise RuntimeError('SOURCE-only ledger/lock')
        if any(x in str(mode) for x in 'wax+') or (isinstance(flags,int) and flags & (1|2|64|512|1024)):
            if path not in {HERE/name for name in OUTPUTS}:
                AUDIT['escaped_write']+=1;raise RuntimeError('SOURCE-only own exclusive outputs')
    if event in ('os.remove','os.rmdir','os.rename','os.replace'):
        AUDIT['delete_or_move']+=1;raise RuntimeError('SOURCE-only no deletion/move')


def raw_id(path):
    raw=path.read_bytes();return dict(relative=path.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def emit(name,value):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def main():
    if not sys.dont_write_bytecode:raise ValueError('Python -B required')
    if any((HERE/name).exists() for name in OUTPUTS):raise ValueError('write-once SOURCE outputs already exist')
    sys.addaudithook(audit)
    import boundary_device_contract as c
    import test_boundary_device_source as test
    contract=c.verify_source_contract()
    capture=io.StringIO();start=time.monotonic()
    result=unittest.TextTestRunner(stream=capture,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test))
    if not result.wasSuccessful():raise RuntimeError(capture.getvalue())
    native=[name for name in sys.modules if name.split('.')[0] in ('torch','numpy','isaacsim','isaaclab','omni','pxr','warp')]
    if native or any(AUDIT.values()):raise RuntimeError('SOURCE audit evidence differs')
    with (HERE/'FAKE_TEST_LOG.txt').open('x',encoding='utf-8',newline='\n') as stream:stream.write(capture.getvalue())
    emit('SOURCE_PINS.json',dict(kind='PHASE1_BOUNDARY_DEVICE_SOURCE_PINS_V1',source_only=True,
        files=[raw_id(HERE/name) for name in BASE+('FAKE_TEST_LOG.txt',)],source_contract=contract))
    receipt=dict(kind='PHASE1_BOUNDARY_DEVICE_SOURCE_RECEIPT_V1',source_only=True,python_version=sys.version.split()[0],python_minus_B=True,
        tests=dict(ran=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),successful=True,elapsed_seconds=time.monotonic()-start,
                   scope='stdlib SOURCE/API/full canonical metadata import only; Torch CPU fixture NOT executed'),
        source_contract=contract,actual_Torch_CPU_fixture_executed=False,actual_reports_read=False,
        actual_SDK_or_native=0,actual_PT_or_raw=0,actual_GPU=0,actual_SSH=0,actual_resources_or_canonical_or_locks=0,
        actual_stage_or_dispatch_or_Git=0,original_sealed_source_edits=0,native_modules_loaded=native,audit=dict(AUDIT),
        actual_V3_flags_shape_dtype_device=None,actual_V3_root_cause_confirmed=False,gate1='UNKNOWN',exact=False,capture_interface_passed=False,stage2_GO=False)
    emit('SOURCE_RECEIPT.json',receipt)
    files=[raw_id(HERE/name) for name in BASE+('FAKE_TEST_LOG.txt','SOURCE_PINS.json','SOURCE_RECEIPT.json')]
    root=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    emit('SOURCE_SEAL.json',dict(kind='PHASE1_BOUNDARY_DEVICE_SOURCE_SEAL_V1',frozen=True,source_only=True,files=files,
         content_root_sha256=root,tests_passed=result.testsRun,actual_Torch_CPU_or_SDK=False,actual_V3_root_cause_confirmed=False))
    print(json.dumps(dict(content_root_sha256=root,seal=raw_id(HERE/'SOURCE_SEAL.json'),fixture=raw_id(HERE/'torch_cpu_fixture.py'),
                         contract=raw_id(HERE/'boundary_device_contract.py'),tests=result.testsRun,actual_Torch_CPU_or_SDK=0),indent=2))


if __name__=='__main__':main()
