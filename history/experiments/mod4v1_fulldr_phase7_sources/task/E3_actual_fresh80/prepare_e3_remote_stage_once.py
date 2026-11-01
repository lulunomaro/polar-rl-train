"""Authorized E3-only NEW remote staging. No PT, SDK, training or canonical write."""
from pathlib import Path
import datetime,hashlib,json,shlex,sys,time
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'
SOURCE=BASE+'/tasks/MOD4_E3_PPO50_GAS400_2610v97/e2'
OVERLAY=ROOT/'staged_sources/E3_MOD4V1_SOURCE_FINAL'
ASSETS=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets')


def main():
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns())
    job=BASE+'/tasks/MOD4V1_E3_FRESH80_FULLDR_'+stamp
    code='''import pathlib,shutil,json,hashlib
B=pathlib.Path(%r);S=pathlib.Path(%r)
assert not B.exists();assert (S/'runtime').is_dir();assert (S/'original_run_manifest.json').is_file()
SUFFIX={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'}
def ignore(path,names):
 out=[]
 for n in names:
  p=pathlib.Path(path)/n
  if n=='__pycache__' or p.suffix.lower() in SUFFIX or n.upper().startswith('TRAINING_BUDGET'):out.append(n);continue
  if p.is_symlink():
   resolved=p.resolve()
   if resolved.suffix.lower() in SUFFIX:out.append(n);continue
   assert resolved.is_relative_to((S/'runtime').resolve()),'External source symlink requires explicit parent review'
 return out
B.mkdir();shutil.copytree(S/'runtime',B/'runtime',ignore=ignore)
if (S/'lib').is_dir():shutil.copytree(S/'lib',B/'lib',ignore=ignore)
shutil.copy2(S/'original_run_manifest.json',B/'original_run_manifest.json')
assert hashlib.sha256((B/'original_run_manifest.json').read_bytes()).hexdigest()=='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f'
assert not any(p.suffix.lower() in SUFFIX for p in (B/'runtime').rglob('*') if p.is_file())
print(json.dumps({'remote_job':str(B),'source_runtime':str(S/'runtime'),'source_runtime_copied_without_model_files':True,'source_PT_opens':0,'SDK_started':False,'canonical_writes':0}))
'''%(job,SOURCE)
    result={'kind':'E3_FRESH80_NO_PT_STAGE','remote_job':job,'source_job':SOURCE,'model_opens':0,'canonical_writes':0,'SDK_started':False}
    client=None;sf=None
    try:
        client=connect72()
        i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240)
        i.close();stdout=o.read().decode('utf-8',errors='replace');stderr=e.read().decode('utf-8',errors='replace');rc=o.channel.recv_exit_status()
        result.update(stage_returncode=rc,stage_stdout=stdout,stage_stderr=stderr)
        if rc!=0:raise RuntimeError('Original E3 runtime stage failed, see saved scoped report')
        sf=client.open_sftp()
        rows=[]
        def upload(local,relative):
            target=job+'/'+relative
            current=''
            for part in target.rsplit('/',1)[0].split('/'):
                if not part:continue
                current+='/'+part
                try:sf.mkdir(current)
                except OSError:sf.stat(current)
            # New cloned directories are real, not aliases into old frozen trees.
            sf.put(str(local),target)
            raw=local.read_bytes();rows.append({'relative':relative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        for local in OVERLAY.rglob('*'):
            if local.is_file():upload(local,local.relative_to(OVERLAY).as_posix())
        extra=json.loads((OVERLAY/'INSTALL_E3_BASE_AND_OVERLAY_SOURCE_MAP.json').read_bytes())['extra_base_required_files']
        for row in extra:
            local=Path(row['path']);assert hashlib.sha256(local.read_bytes()).hexdigest()==row['SHA'];upload(local,row['relative'])
        for local in ASSETS.rglob('*'):
            if local.is_file():
                assert local.suffix.lower() not in ('.pt','.pth','.ckpt','.onnx','.safetensors')
                upload(local,'runtime/assets/'+local.relative_to(ASSETS).as_posix())
        result.update(status='E3_REMOTE_NONPT_DEPENDENCIES_AND_V1_ASSET_STAGED',files=rows)
        index={'kind':'E3_FRESH80_STAGE_SOURCE_INDEX_NO_SDK','files':rows,'model_opens':0,'canonical_writes':0}
        with sf.open(job+'/E3_STAGE_SOURCE_INDEX.json','wx') as f:f.write(json.dumps(index,indent=2))
    except BaseException as error:
        result.update(status='STAGE_ERROR',error_type=type(error).__name__,error=str(error))
        raise
    finally:
        if sf is not None:sf.close()
        if client is not None:client.close()
        report=ROOT/'reports'/('E3_fresh80_stage_'+stamp+'.json');report.parent.mkdir(exist_ok=True)
        report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        locator=ROOT/'E3_actual_fresh80'/'CURRENT_NEW_STAGE.json'
        if result.get('status')=='E3_REMOTE_NONPT_DEPENDENCIES_AND_V1_ASSET_STAGED':
            with locator.open('x',encoding='utf-8') as f:json.dump({'remote_job':job,'stage_report':str(report)},f,indent=2)
        print(json.dumps({'status':result.get('status'),'remote_job':job,'stage_report':str(report)},indent=2))


if __name__=='__main__':main()
