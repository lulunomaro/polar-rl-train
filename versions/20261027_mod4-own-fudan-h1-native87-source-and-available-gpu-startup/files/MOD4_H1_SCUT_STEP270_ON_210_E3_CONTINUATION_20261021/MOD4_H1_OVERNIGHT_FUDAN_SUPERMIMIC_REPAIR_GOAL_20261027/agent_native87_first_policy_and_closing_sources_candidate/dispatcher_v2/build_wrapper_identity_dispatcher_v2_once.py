"""Exact source replacement for the approved72 ld-loader wrapper; no process run."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;L=D.parent.parent
old=L/'agent_native87_actual_install_activate_sources_candidate/native87_closed_source_CPU_v1.py'
raw=old.read_bytes();(D/'ORIGINAL_FROZEN_DISPATCHER_V1_BYTES.txt').write_bytes(raw);s=raw.decode()
helper='''PY210='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
EXE210='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
WRAPPER72='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
LOADER72='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2'
LIBRARY72='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
PYTHON72='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'

def expected_exec_identity(spec,logical_argv):
    """Exact approved interpreter recipe; usable by metadata observers too."""
    assert logical_argv[0]==spec['python']
    if spec['execution_backend']=='source210':
        assert spec['key']=='h1' and spec['python']==PY210
        return dict(exe=EXE210,argv=list(logical_argv),recipe='direct210_approved_python3.12')
    assert spec['execution_backend']=='target72' and spec['key'] in ('e2','recovery') and spec['python']==WRAPPER72
    return dict(exe=LOADER72,argv=[LOADER72,'--library-path',LIBRARY72,PYTHON72,'-B',*logical_argv[1:]],recipe='approved72_glibc240_exact_wrapper')

def wait_exact_exec_identity(p,B,spec,args,timeout_s=5.):
    import psutil
    expected=expected_exec_identity(spec,args);until=time.monotonic()+timeout_s
    process=psutil.Process(p.pid);creation=process.create_time();previous=None
    while True:
        assert p.poll() is None,'CPU child exited before an exact stable exec identity was captured'
        row=dict(pid=p.pid,creation=process.create_time(),argv=process.cmdline(),root=process.cwd(),exe=process.exe())
        assert row['creation']==creation,'CPU process identity changed during wrapper exec'
        exact=row['exe']==expected['exe'] and row['argv']==expected['argv'] and row['root']==str(B)
        if exact and row==previous:return row
        previous=row if exact else None
        if time.monotonic()>=until:raise AssertionError('Approved wrapper failed to reach exact argv/exe/cwd within bounded5s')
        time.sleep(.05)

'''
needle='def validate_proof_data(';assert s.count(needle)==1;s=s.replace(needle,helper+needle,1)
replacements=[
 ('expected_argv,expected_exe):','expected_argv,expected_exe,expected_root):'),
 ("assert identity['argv']==expected_argv and identity['exe']==expected_exe and proof['waited_epoch']>=proof['started_epoch']", "assert identity['argv']==expected_argv and identity['exe']==expected_exe and identity['root']==expected_root and proof['waited_epoch']>=proof['started_epoch']"),
 ('    args=_argv(spec,B)','    args=_argv(spec,B);expected=expected_exec_identity(spec,args)'),
 ("expected_argv=args,expected_exe=str(Path(spec['python']).resolve()))", "expected_argv=expected['argv'],expected_exe=expected['exe'],expected_root=str(B))"),
 ("        identity=b.ident(p.pid);assert identity is not None\n        identity['exe']=str(Path(psutil.Process(p.pid).exe()).resolve());assert identity['argv']==args", "        identity=wait_exact_exec_identity(p,B,spec,args)"),
 ("expected_argv=args,expected_exe=str(Path(spec['python']).resolve()))", "expected_argv=expected['argv'],expected_exe=expected['exe'],expected_root=str(B))")]
for i,(before,after) in enumerate(replacements):
    # The identical validation suffix occurs twice; replace one occurrence each time.
    assert before in s,(i,before);s=s.replace(before,after,1)
ast.parse(s);out=D/'native87_closed_source_CPU_v1.py';out.write_text(s,encoding='utf8')
with (D/'DISPATCHER_WRAPPER_IDENTITY_EXACT_SOURCE_V2_ACTUAL.json').open('x',encoding='utf8') as f:
    json.dump(dict(original_source=str(old),original_SHA=hashlib.sha256(raw).hexdigest(),new_source=str(out),new_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),
        exact72_loader_recipe=True,exact210_python_recipe=True,wrapper_exec_stabilization_s=5.,two_stable_snapshots=True,
        actual_child_executed=False,old_source_unchanged=True),f,indent=2)
print(json.dumps(dict(source_generated=True,new_SHA=hashlib.sha256(out.read_bytes()).hexdigest())))
