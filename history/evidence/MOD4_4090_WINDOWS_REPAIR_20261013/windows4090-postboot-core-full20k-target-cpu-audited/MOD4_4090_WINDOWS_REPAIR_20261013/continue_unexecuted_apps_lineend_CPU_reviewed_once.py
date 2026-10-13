"""Retain first prewrite HEAD-byte assertion; prove working-tree CRLF only."""
from pathlib import Path
import hashlib, json, subprocess, time, traceback
from windows4090_native_transport import connect,powershell,upload
D=Path(__file__).resolve().parent
SDK=Path('F:/isaacsim/IsaacLab')
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    proof=D/'reports/ACTUAL_TESTED_SDK_APPS_HEAD_LINEENDING_CPU_REVIEW.json'
    assert not proof.exists()
    original=json.loads((D/'reports/ACTUAL_TESTED_SDK_APPS21_CPU_PACKAGE_PASSED.json').read_bytes())
    rows=[]
    for row in original['file_rows']:
        raw=Path(row['source_path']).read_bytes()
        head=subprocess.run(['git','-C',str(SDK),'show',original['actual_Git_HEAD']+':'+row['archive']],capture_output=True,check=True).stdout
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        assert raw.replace(b'\r\n',b'\n')==head.replace(b'\r\n',b'\n')
        rows.append(dict(archive=row['archive'],actual_working_tree_sha256=row['sha256'],HEAD_blob_sha256=hashlib.sha256(head).hexdigest(),raw_HEAD_byteexact=raw==head,only_CRLF_LF_lineending_difference=raw!=head,semantic_content_exact=True))
    p=dict(epoch=time.time(),passed=True,no_GPU_or_remote_modification=True,original_failed_HEAD_byteexact_assertion_retained=True,actual_tested_working_tree_files_kept_byteexact=True,HEAD_byteexact_not_claimed=True,actual_Git_HEAD=original['actual_Git_HEAD'],file_rows=rows)
    proof.write_text(json.dumps(p,indent=2),encoding='utf8')
    old=(D/'install_actual_apps_cpu_remote_once.py').read_text(encoding='utf8')
    a="assert row['actual_source_equals_HEAD_blob'] and row['Git_HEAD_blob_available']"
    assert old.count(a)==1
    new=old.replace(a,"assert row['Git_HEAD_blob_available']\n            matching=[x for x in headproof['file_rows'] if x['archive']==row['archive']]\n            assert len(matching)==1 and matching[0]['semantic_content_exact'] and matching[0]['actual_working_tree_sha256']==row['sha256']")
    new=new.replace("rows=[]", "headproof=json.loads((R/'packages/ACTUAL_TESTED_SDK_APPS_HEAD_LINEENDING_CPU_REVIEW.json').read_bytes())\n    assert headproof['passed'] and headproof['actual_tested_working_tree_files_kept_byteexact']\n    rows=[]",1)
    new=new.replace("all21_recursive_apps_rendering_config_exact=True", "all21_recursive_apps_rendering_config_exact=True,actual_working_tree_bytes_exact_HEAD_lineending_only=True,HEAD_raw_byteexact_not_claimed=True,HEAD_lineending_CPU_proof=dict(path=str(R/'packages/ACTUAL_TESTED_SDK_APPS_HEAD_LINEENDING_CPU_REVIEW.json'),sha256=H(R/'packages/ACTUAL_TESTED_SDK_APPS_HEAD_LINEENDING_CPU_REVIEW.json'))")
    helper=D/'install_actual_apps_lineend_CPU_reviewed_remote_once.py'
    assert not helper.exists();compile(new,str(helper),'exec');helper.write_text(new,encoding='utf8')
    s=connect()
    pre=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';@{apps_exists=Test-Path -LiteralPath ($r+'/sdk_exact/apps');ready_exists=Test-Path -LiteralPath ($r+'/install_reports/APPS_EXPERIENCE_RESOURCES_CPU_ACTUAL_READY.json')}|ConvertTo-Json -Compress",timeout=30))
    assert not pre['apps_exists'] and not pre['ready_exists'], 'unknown prior effects: read actual without replay'
    for local,remote in [(proof,R+'/packages/'+proof.name),(helper,R+'/install_helpers/'+helper.name)]:
        assert powershell(s,"if(Test-Path -LiteralPath '"+remote+"'){'PRESENT'}else{'ABSENT'}",timeout=30)=='ABSENT'
        upload(local,remote,timeout=60)
        assert powershell(s,"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==H(local)
    actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' '"+R+"/install_helpers/"+helper.name+"'",timeout=60))
    assert actual['passed'] and actual['actual_working_tree_bytes_exact_HEAD_lineending_only']
    result=dict(epoch=time.time(),passed=True,actual=actual,original_GPU_not_run=True,original_failure_retained=True,pre=pre)
    out=D/'reports/APPS_LINEEND_REVIEWED_CPU_CONTINUATION_ACTUAL.json'
    assert not out.exists();out.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(passed=True,files=len(actual['actual_files']),report=str(out))))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('APPS_LINEEND_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_original_once_replay=True)),encoding='utf8')
        raise
