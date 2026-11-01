"""Reuse only the existing project's bound SSH authentication provider and pinned factory.
No legacy launcher main is executed. No credential is printed, serialized or stored in env.
"""
from pathlib import Path
import importlib.util,sys
W=Path(r'C:\Users\lulu\Desktop\claude\mjcf')
FACTORY=W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/deploy_two50_reconciled_original_writer_once.py'
PROVIDER=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def connect72():
    for path in (W,FACTORY.parent):
        if str(path) not in sys.path:sys.path.insert(0,str(path))
    factory=load('mod4v1_existing_connect72_factory',FACTORY)
    provider=load('mod4v1_existing_auth_provider',PROVIDER)
    # Same exact session selected by the existing provider; never search other records.
    original=provider.SESSION
    if not original.exists():
        compressed=Path(str(original)+'.zst')
        if not compressed.is_file():raise FileNotFoundError('Bound project authentication record is absent')
        from compression import zstd
        class BoundCompressedSession:
            def open(self,*,encoding):
                return zstd.open(compressed,'rt',encoding=encoding)
        provider.SESSION=BoundCompressedSession()
    secret=None
    try:
        secret=provider.recover()
        client=factory.connect72(secret)
        return client
    finally:
        secret=None
        provider.SESSION=original

def connect_original():
    """The other existing project Linux node; reuse its same bound compressed transport."""
    for path in (W,FACTORY.parent):
        if str(path) not in sys.path:sys.path.insert(0,str(path))
    wrapper_path=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py'
    wrapper=load('mod4v1_existing_other_transport_wrapper',wrapper_path)
    transport,previous=wrapper.install()
    try:
        transport_module=__import__('strict_original_Linux_transport_memory')
        return transport_module.connect()
    finally:
        transport.SESSION=previous
