from pathlib import Path
import os,sys,json,time,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_linux_runtime_cpu_once import S,LEGACY
D=Path(__file__).resolve().parent
REMOTE=r'''
from pathlib import Path
import ast,hashlib,json,shutil,time
P=Path;R=P(S);OLD=P(LEGACY);f=R/'runtime/isaac/mod4/wave50_entry_runtime_v2.py';source=OLD/'isaac/mod4/wave50_entry_runtime_v2.py'
assert f.read_bytes()==source.read_bytes(),'first failure was before writing hook'
assert not (R/'ORIGINAL_ENTRY_RUNTIME_BEFORE_SELECTED_HOOK.py').exists()
text=f.read_text();node=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name=='reset_entry_xy')
lines=text.splitlines(keepends=True);ind=' '*node.body[0].col_offset;arg=node.args.args[1].arg
hook=ind+"if hasattr(env, '_local_projection_reset_xy'):\n"+ind+"    from selected_source_projection import selected_entry\n"+ind+"    return selected_entry(env, "+arg+")\n"
lines.insert(node.body[0].lineno-1,hook);fresh=''.join(lines);compile(fresh,str(f),'exec')
(R/'ORIGINAL_ENTRY_RUNTIME_BEFORE_SELECTED_HOOK.py').write_bytes(f.read_bytes());f.write_text(fresh)
src=P('/mnt/mod4_windows_readonly_20261013/system/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_selected_ownstate_production_v1_20261013/attempts/temporary2048_train_v1/output/model_32411.pt')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
(R/'source').mkdir(exist_ok=False);shutil.copyfile(src,R/'source/WINDOWS512_LAST_COMPLETE_28UPDATES.pt')
print(json.dumps(dict(epoch=time.time(),root=str(R),entry_original_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),entry_new_SHA=hashlib.sha256(f.read_bytes()).hexdigest(),source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),independent_unexecuted_prewrite_continuation_only=True,old_failure_preserved=True,no_GPU_budget_or_oldonce_replay=True)))
'''
def main():
    assert not (D/'reports/LINUX_RUNTIME_INDENT_REVIEWED_CONTINUED_CPU_ACTUAL.json').exists()
    c=connect_linux_only()
    try:
        si,so,se=c.exec_command('python3 -',timeout=60);si.write('S='+repr(S)+'\nLEGACY='+repr(LEGACY)+'\n'+REMOTE);si.flush();si.channel.shutdown_write()
        out=so.read();err=se.read();rc=so.channel.recv_exit_status();p=D/'reports/LINUX_RUNTIME_INDENT_REVIEWED_CONTINUED_CPU_ACTUAL.json';p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p)
        sf=c.open_sftp();sf.mkdir(S+'/payload');rows=[]
        for p in sorted((D/'payload_v1').iterdir()):
            sf.put(str(p),S+'/payload/'+p.name);rows.append(dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        for name in ('linux_resume_parent.py','independent_linux_COM_warp.py'):
            p=D/name;sf.put(str(p),S+'/payload/'+name);rows.append(dict(name=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        (D/'reports/LINUX_PAYLOAD_INITIAL_UPLOAD_INDENT_REVIEWED_ACTUAL.json').write_text(json.dumps(dict(root=S,files=rows,no_GPU_or_budget=True),indent=2),encoding='utf8');print(out.decode())
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
