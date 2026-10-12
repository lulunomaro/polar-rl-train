import json,time,traceback
import end_human_authorized_failed_startup_once as original

def main():
    # Original call failed locally before any remote command or signal.
    auth=json.loads((original.R/'FAILED_STARTUP_HUMAN_END_AUTHORIZATION.json').read_bytes())
    assert auth['human_text']==original.AUTH and auth['scope']['pid']==3340979 and auth['scope']['start_ticks']==94499270
    save=original.save;run=original.run
    def reuse_auth(name,value):
        if name=='FAILED_STARTUP_HUMAN_END_AUTHORIZATION.json':return original.R/name
        return save(name,value)
    def reviewed_run(connection,code,timeout=None):
        assert timeout==50
        return run(connection,code)
    original.save=reuse_auth;original.run=reviewed_run
    save('FAILED_END_CALL_CONTRACT_REVIEW.json',dict(epoch=time.time(),original_TypeError_pre_remote_pre_signal=True,only_drop_unsupported_local_timeout_parameter=True,original_authorization_bytes_retained=True,remote_identity_guard_and_signal_protocol_unchanged=True))
    original.main()

if __name__=='__main__':
    try:main()
    except BaseException:original.save('REVIEWED_HUMAN_END_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_inspect_remote_receipt_no_blind_signal_replay=True));raise
