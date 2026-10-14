"""One new target CPU action and unique native->restore->formal dispatch."""
from pathlib import Path
import json,os,sys,time,traceback
import transport_bodyframe_pipeline_v4 as t

B=Path(__file__).resolve().parent;P=B/'payload_v1'
NAMES=('birth_bodyframe_state_v1.py','birth_bodyframe_reset_adapter_v5.py','birth_bodyframe_full_checkpoint_v4.py',
       'bodyframe_native_worker_v6.py','bodyframe_formal_worker_v4.py','bodyframe_finite_pipeline_parent_v4.py')
STAGE=t.BASE+'/.bodyframe_pipeline_unique_upload_v4_native_rotation_repr_20261014'

def main():
    intent=B/'reports/BODYFRAME_PIPELINE_V4_MATERIALIZE_DISPATCH_INTENT.json';assert not intent.exists()
    files={name:P/name for name in NAMES}
    source=t.W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/payload_v1'
    files.update(left_sameidentity_typed13_receipts=source/'left_sameidentity_typed13_receipts.py')
    files['left_sameidentity_typed13_receipts.py']=files.pop('left_sameidentity_typed13_receipts')
    files['bodyframe_original_CPU_guard.py']=source/'second_target_CPU_pure_guard_v2.py'
    files['bodyframe_target_materialize_CPU_v3.py']=B/'bodyframe_target_materialize_CPU_v3.py'
    for name,p in files.items():compile(p.read_bytes(),str(p),'exec')
    intent.write_text(json.dumps(dict(epoch=time.time(),root=t.ROOT,upload_stage=STAGE,source_SHA=t.SOURCE,
        files={k:dict(path=str(p),bytes=p.stat().st_size,sha256=t.sha(p)) for k,p in files.items()},no_replay=True),indent=2),encoding='utf8')
    c=None;sftp=None
    try:
        c=t.connect()
        t.run(c,"from pathlib import Path\nimport json\ns=Path(CONTEXT['stage']);r=Path(CONTEXT['root']);assert not s.exists() and not r.exists();s.mkdir();print(json.dumps(dict(new_upload_stage=str(s))))",dict(stage=STAGE,root=t.ROOT),'BODYFRAME_NEW_UPLOAD_STAGE_ACTUAL')
        sftp=c.open_sftp()
        for name,p in files.items():sftp.put(str(p),STAGE+'/'+name)
        sftp.close();sftp=None
        context=dict(upload_stage=STAGE,root=t.ROOT,base=t.BASE,old=t.OLD,source_SHA=t.SOURCE,files={k:t.sha(p) for k,p in files.items()})
        result,receipt=t.run(c,(B/'bodyframe_target_materialize_CPU_v3.py').read_text(encoding='utf8'),context,'BODYFRAME_TARGET_CPU_MATERIALIZE_ACTUAL',timeout=240)
        assert result['passed'] and result['GPU_dispatched'] is False
        code=r'''
from pathlib import Path
import json,subprocess,time,os,hashlib
root=Path(CONTEXT['root']);assert not (root/'ROOT_UNIQUE_DISPATCH_INTENT.json').exists() and not (root/'PIPELINE_ONCE_CONSUMED.json').exists()
proof=json.loads((root/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['target_CPU_actual']
with (root/'ROOT_UNIQUE_DISPATCH_INTENT.json').open('x') as f:json.dump(dict(epoch=time.time(),root=str(root),source_SHA=proof['source']['sha256']),f);f.flush();os.fsync(f.fileno())
env=os.environ.copy();env.pop('CUDA_VISIBLE_DEVICES',None)
p=subprocess.Popen([CONTEXT['python'],'-u',str(root/'bodyframe_finite_pipeline_parent_v4.py')],cwd=root,env=env,start_new_session=True,stdin=subprocess.DEVNULL,stdout=(root/'pipeline_parent.log').open('xb'),stderr=subprocess.STDOUT)
import psutil
q=psutil.Process(p.pid)
out=dict(epoch=time.time(),pid=p.pid,created=q.create_time(),argv=q.cmdline(),cwd=q.cwd(),source=proof['source'],target_CPU_passed=True,PPO_NOT_yet_claimed=True)
with (root/'ROOT_UNIQUE_DISPATCH_ACTUAL.json').open('x') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out))
'''
        dispatched,receipt=t.run(c,code,dict(root=t.ROOT,python=t.PY),'BODYFRAME_PIPELINE_UNIQUE_DISPATCH_ACTUAL')
        print(json.dumps(dict(targetCPU=result,dispatch=dispatched)))
    except BaseException:
        print(t.save('BODYFRAME_MATERIALIZE_DISPATCH_ORIGINAL_ERROR',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_read_before_retry=True)))
        raise
    finally:
        if sftp:sftp.close()
        t.close(c)

if __name__=='__main__':main()
