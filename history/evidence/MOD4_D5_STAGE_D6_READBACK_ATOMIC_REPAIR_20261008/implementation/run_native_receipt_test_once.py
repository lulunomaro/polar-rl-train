from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'NATIVE_WINDOWS_RECEIPT_SHARING_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
    name='test_native_windows_receipt_sharing.py';b=(D/name).read_bytes()
    with c.open_sftp() as f:
        try:f.stat(root+'/'+name)
        except FileNotFoundError:pass
        else:raise AssertionError('Native test already uploaded')
        with f.open(root+'/'+name,'wb') as out:out.write(b)
        with f.open(root+'/'+name) as inp:assert inp.read()==b
    _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/'+name+'"',timeout=20)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
    (R/'NATIVE_WINDOWS_RECEIPT_SHARING_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
