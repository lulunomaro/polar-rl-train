from pathlib import Path
import os,sys,json,time,hashlib,base64
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
S='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/fullscale20k_latest512_state_v1'
LEGACY='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'

REMOTE=r'''
from pathlib import Path
import shutil,os,json,hashlib,time,ast
P=Path;R=P(S);OLD=P(LEGACY)
assert not R.exists();R.mkdir()
shutil.copytree(OLD/'isaac',R/'runtime/isaac',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(OLD/'train',R/'runtime/train',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
C=R/'runtime/isaac/mod4';f=C/'wave50_entry_runtime_v2.py';old=f.read_text()
node=next(x for x in ast.parse(old).body if isinstance(x,ast.FunctionDef) and x.name=='reset_entry_xy')
lines=old.splitlines(keepends=True);index=node.body[0].lineno-1
hook="    if hasattr(env, '_local_projection_reset_xy'):\n        from selected_source_projection import selected_entry\n        return selected_entry(env, ids)\n"
parameter=node.args.args[1].arg
hook=hook.replace('env, ids)','env, '+parameter+')')
lines.insert(index,hook);fresh=''.join(lines);compile(fresh,str(f),'exec')
(R/'ORIGINAL_ENTRY_RUNTIME_BEFORE_SELECTED_HOOK.py').write_bytes(f.read_bytes());f.write_text(fresh)
src=P('/mnt/mod4_windows_readonly_20261013/system/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_selected_ownstate_production_v1_20261013/attempts/temporary2048_train_v1/output/model_32411.pt')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
(R/'source').mkdir();shutil.copyfile(src,R/'source/WINDOWS512_LAST_COMPLETE_28UPDATES.pt')
print(json.dumps(dict(epoch=time.time(),root=str(R),legacy=str(OLD),runtime_source_copy_only=True,new_selected_entry_hook=True,entry_old_SHA=hashlib.sha256(old.encode()).hexdigest(),entry_new_SHA=hashlib.sha256(f.read_bytes()).hexdigest(),source_SHA=hashlib.sha256((R/'source/WINDOWS512_LAST_COMPLETE_28UPDATES.pt').read_bytes()).hexdigest(),source_original_readonly=True,no_CUDA_PPO_budget_or_old_entry=True),ensure_ascii=False))
'''
def main():
    assert not (D/'reports/LINUX_RUNTIME_DEPLOYED_CPU_ACTUAL.json').exists()
    c=connect_linux_only()
    try:
        text='S='+repr(S)+'\nLEGACY='+repr(LEGACY)+'\n'+REMOTE
        si,so,se=c.exec_command('python3 -',timeout=120);si.write(text);si.flush();si.channel.shutdown_write()
        out=so.read();err=se.read();code=so.channel.recv_exit_status()
        receipt=dict(code=code,stdout=out.decode(),stderr=err.decode(),no_GPU_or_budget=True)
        p=D/'reports/LINUX_RUNTIME_DEPLOYED_CPU_ACTUAL.json';p.write_bytes(json.dumps(receipt,indent=2).encode())
        assert code==0,str(p)
        sf=c.open_sftp();sf.mkdir(S+'/payload')
        files=[]
        for p in sorted((D/'payload_v1').iterdir()):
            sf.put(str(p),S+'/payload/'+p.name);files.append(dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        for name in ('linux_resume_parent.py','independent_linux_COM_warp.py'):
            p=D/name;sf.put(str(p),S+'/payload/'+name);files.append(dict(name=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        sf.close()
        (D/'reports/LINUX_PAYLOAD_INITIAL_UPLOAD_ACTUAL.json').write_text(json.dumps(dict(root=S,files=files,no_GPU_or_budget=True),indent=2),encoding='utf8')
        print(out.decode())
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
