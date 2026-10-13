"""Actual tested SDK experiences, exact files only, no SDK edits or GPU."""
from pathlib import Path
import hashlib, json, subprocess, time, zipfile
D=Path(__file__).resolve().parent
SDK=Path('F:/isaacsim/IsaacLab')
EXPECTED_HEAD='b0542fe2d45bf91c4e1d9ef6952b9c709c80b4e8'
def h(b):return hashlib.sha256(b).hexdigest()
def main():
    head=subprocess.run(['git','-C',str(SDK),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
    assert head==EXPECTED_HEAD
    status=subprocess.run(['git','-C',str(SDK),'status','--porcelain','--','apps'],check=True,capture_output=True,text=True).stdout
    rows=[];data={}
    for p in sorted((SDK/'apps').rglob('*')):
        if not p.is_file():continue
        assert p.suffix in ('.kit','.toml') and p.stat().st_size<2_000_000
        b=p.read_bytes();n=p.relative_to(SDK).as_posix();data[n]=b
        committed=subprocess.run(['git','-C',str(SDK),'show',head+':'+n],capture_output=True)
        rows.append(dict(source_path=str(p),archive=n,bytes=len(b),sha256=h(b),Git_HEAD_blob_available=committed.returncode==0,actual_source_equals_HEAD_blob=committed.returncode==0 and b==committed.stdout,actual_source_not_assumed_unmodified=True))
    assert len(rows)==21 and 'apps/isaaclab.python.headless.kit' in data
    marker='[settings.app.exts]';text=data['apps/isaaclab.python.headless.kit'].decode('utf8')
    assert marker in text and '${app}/../source' in text
    manifest=dict(epoch=time.time(),passed=True,CPU_package_only=True,actual_tested_local_SDK_root=str(SDK),actual_Git_HEAD=head,actual_Git_apps_status=status,file_rows=rows,source_not_changed=True,target_extraction_CPU_and_GPU_still_pending=True,experience_and_recursive_rendering_config_all21_files_exact=True,no_KIT_or_GPU_import=True)
    package=D/'TESTED_ISAACLAB_APPS21_EXPERIENCE_RESOURCES_CPU_20261013.zip'
    assert not package.exists()
    with zipfile.ZipFile(package,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,b in data.items():z.writestr(name,b)
        z.writestr('ACTUAL_TESTED_SDK_APPS_MANIFEST.json',json.dumps(manifest,indent=2).encode())
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        for row in rows:assert h(z.read(row['archive']))==row['sha256']
    result=dict(manifest,package=dict(path=str(package),bytes=package.stat().st_size,sha256=h(package.read_bytes())),no_remote_upload_or_lease_or_PPO=True)
    report=D/'reports/ACTUAL_TESTED_SDK_APPS21_CPU_PACKAGE_PASSED.json'
    assert not report.exists();report.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(package=result['package'],report=str(report),apps_HEAD_status=status)))
if __name__=='__main__':main()
