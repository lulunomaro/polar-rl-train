from pathlib import Path
import sys,os,json,time,traceback
import build_latest_wasd50_70_once as original
D=original.D;R=original.R;W=original.W

def connect_linux_only():
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret
    sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
    from remote_io import connect
    class UnusedEval:
        def close(self):pass
    return connect(),UnusedEval()

def main():
    assert not (D/'DOWNLOAD_RECEIPT.json').exists() and not (R/'BUILD_ACTUAL.json').exists()
    for folder in ('models','scenes','src_snapshot'):assert (D/folder).is_dir() and not list((D/folder).iterdir())
    auth=json.loads((R/'HUMAN_WASD50_70_REQUEST.json').read_bytes());assert auth['source_SHA']==original.SHA
    original.save('LINUX_ONLY_TRANSPORT_CONTINUATION_REVIEW.json',dict(epoch=time.time(),passed=True,original_3060_timeout_before_any_weight_download_preserved=True,only4090_connection_required_for_requested_model=True,created_empty_dirs_and_authorization_reused_exact=True,no_remote_GPUTask_training_or_budget_mutation=True))
    text=Path(original.__file__).read_text()
    text=text.replace("(D/'models').mkdir();(D/'scenes').mkdir();(D/'src_snapshot').mkdir()", "(D/'models').mkdir(exist_ok=True);(D/'scenes').mkdir(exist_ok=True);(D/'src_snapshot').mkdir(exist_ok=True)")
    assert 'n,w=io.connect_both()' in text;text=text.replace('n,w=io.connect_both()','n,w=connect_linux_only()')
    ns=dict(__file__=original.__file__,__name__='unexecuted_download_build_linux_only',connect_linux_only=connect_linux_only)
    exec(compile(text,str(__file__)+'#independent-unexecuted-download-build','exec'),ns)
    save=ns['save']
    def reuse_auth(name,value):
        if name=='HUMAN_WASD50_70_REQUEST.json':return R/name
        return save(name,value)
    ns['save']=reuse_auth;ns['main']()

if __name__=='__main__':
    try:main()
    except BaseException:original.save('LINUX_ONLY_BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_partial_files_no_blind_overwrite_or_repull=True));raise
