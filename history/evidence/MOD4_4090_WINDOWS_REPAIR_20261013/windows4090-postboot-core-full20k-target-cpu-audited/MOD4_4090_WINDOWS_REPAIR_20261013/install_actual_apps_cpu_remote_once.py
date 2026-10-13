"""Exact tested experience resources, CPU only. No package code is edited."""
from pathlib import Path, PurePosixPath
import hashlib, json, os, time, zipfile
R=Path(__file__).resolve().parents[1]
SHA='dffde73532bc1ceb765632493ae0531777d97eb438a52ffe7596ac7e19126230'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    report=R/'install_reports/APPS_EXPERIENCE_RESOURCES_CPU_ACTUAL_READY.json'
    assert not report.exists(), 'consumed resource extraction; read actual result'
    package=R/'packages/TESTED_ISAACLAB_APPS21_EXPERIENCE_RESOURCES_CPU_20261013.zip'
    assert H(package)==SHA
    target=R/'sdk_exact'
    assert not (target/'apps').exists(), 'unknown prior extraction requires separate read-only review'
    rows=[]
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        m=json.loads(z.read('ACTUAL_TESTED_SDK_APPS_MANIFEST.json'))
        assert m['actual_Git_HEAD']=='b0542fe2d45bf91c4e1d9ef6952b9c709c80b4e8'
        assert m['actual_Git_apps_status']=='' and len(m['file_rows'])==21
        assert set(z.namelist())=={r['archive'] for r in m['file_rows']}|{'ACTUAL_TESTED_SDK_APPS_MANIFEST.json'}
        for row in m['file_rows']:
            name=PurePosixPath(row['archive'])
            assert name.parts[0]=='apps' and not name.is_absolute() and '..' not in name.parts and ':' not in row['archive']
            assert row['actual_source_equals_HEAD_blob'] and row['Git_HEAD_blob_available']
            b=z.read(row['archive']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
            p=(target/Path(*name.parts)).resolve();assert p.is_relative_to(target.resolve())
            p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as out:out.write(b);out.flush();os.fsync(out.fileno())
            rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)))
    manifest=target/'ACTUAL_TESTED_SDK_APPS_MANIFEST.json'
    with manifest.open('x',encoding='utf8') as out:json.dump(m,out,indent=2);out.flush();os.fsync(out.fileno())
    result=dict(epoch=time.time(),passed=True,CPU_resources_only=True,no_Kit_or_GPU_or_PPO=True,package=dict(path=str(package),bytes=package.stat().st_size,sha256=SHA),actual_files=rows,actual_Git_HEAD=m['actual_Git_HEAD'],actual_manifest=dict(path=str(manifest),sha256=H(manifest)),all21_recursive_apps_rendering_config_exact=True,original_installed_SDK_code_and_metadata_not_changed=True,new_GPU_experience_loading_still_pending=True)
    with report.open('x',encoding='utf8') as out:json.dump(result,out,indent=2);out.flush();os.fsync(out.fileno())
    print(json.dumps(result))
if __name__=='__main__':main()
