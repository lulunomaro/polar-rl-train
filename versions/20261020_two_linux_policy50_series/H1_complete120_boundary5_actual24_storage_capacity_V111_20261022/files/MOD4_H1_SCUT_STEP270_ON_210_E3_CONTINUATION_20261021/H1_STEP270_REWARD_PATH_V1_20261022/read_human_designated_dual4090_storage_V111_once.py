from pathlib import Path
import importlib.util, json, sys, time, traceback

B = Path(__file__).resolve().parent
T = B.parent
W = T.parent
R = B / 'reports'

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

CODE = r'''
from pathlib import Path
import json, os, shutil, time
base=Path('/home/lc01/Zonglin Li/zonglin2')
rows=[]
for p in (base,base/'forensic_originals'):
    real=p.resolve(strict=True)
    assert real==base or base in real.parents
    s=real.stat(); disk=shutil.disk_usage(real)
    rows.append(dict(path=str(p),resolved=str(real),device=s.st_dev,inode=s.st_ino,
      free=disk.free,total=disk.total,used=disk.used,
      disk25_passed=disk.free>25*1024**3,
      available_above_original25_bytes=max(0,disk.free-25*1024**3),
      writable_permission_metadata=os.access(real,os.W_OK)))
print(json.dumps(dict(epoch=time.time(),host='10.24.0.72',human_designated_root=str(base),
  paths=rows,only_metadata_no_write_or_training_GPU_process_peer_identity_or_budget_access=True)))
'''

def main():
    put('V111_HUMAN_TEMPORARY_DESIGNATED_DUAL4090_STORAGE_AUTH_ACTUAL.json', dict(
        epoch=time.time(), question_item_id='call_96265a71fcd14d06bdea306cb12a10b1',
        exact_question='刚才转存后，210仅比25GiB准入线多约82MiB；72本批写入前的余量约1.77GiB，已写入约0.97GiB。后续取证需要新的可写位置：请提供可用存储路径，或指定一台机器供我核查容量。',
        exact_human_reply='可以暂时转入那两台4090的我指定的那个文件夹里',
        explicit_temporary_storage_authorization_received=True,
        established_host_identity_report=str(W/'MOD4_V7_FINALS_AND_CLOSED101_FROZEN_RESIDUAL_20261017/reports/HUMAN_STORAGE_QUESTION_210_SINGLE72_DUAL_HOST_CLARIFICATION_ACTUAL.json'),
        original_designated_folder_evidence=str(W/'MOD4_HOST72_ZONGLIN2_ENV_DEPLOY_20261015/MONITOR_HUMAN_ZONGLIN2_DEPLOY_ACTIVE_TRANSPORT_OWNER_ACTUAL_20261015.txt'),
        established_host='10.24.0.72 dual4090', designated_root='/home/lc01/Zonglin Li/zonglin2',
        scope='Temporary storage in the previously designated root. Fresh capacity required; no inference of other folders, deletion, permission changes or training authority.',
        no_duplicate_permission_question=True))
    put('V111_LOCAL_READONLY_STORAGE_SEARCH_ERRORS_ACTUAL.json', dict(
        epoch=time.time(), errors=[
            dict(operation='local rg --files broad filename search', actual_exit=1,
                 error='rmuc2026_work/unpack_verify_4zomhj13: Permission denied (os error 5)'),
            dict(operation='local targeted report search', actual_exit=1,
                 error='MOD4_HUMAN_RECOVERY_CHECK_20261018/reports: path not found (os error 3)',
                 stdout_truncated=True, reason='An overly broad existing path pattern matched embedded historical worker logs.'),
            dict(operation='local guessed unused helper read', actual_exit=1,
                 error='prepare_next_boundary_resource24_unused_workflow_CPU_once.py does not exist; actual source subsequently located with rg --files')],
        no_remote_helper_executed_by_these_reads=True, no_permission_change=True,
        current24_preparer_nonfatal_SyntaxWarning='invalid escape sequence \\S',
        current24_preparer_actual_returncode=0, no_rerun=True))
    sys.path.insert(0, str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    spec=importlib.util.spec_from_file_location('memory', W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(spec); spec.loader.exec_module(memory)
    secret=memory.recover()
    try:
        c=d.connect72(secret)
    finally:
        secret=None
    try:
        value=d.code(c,d.PY72,CODE,{},timeout=45)
    finally:
        c.close()
    put('V111_HUMAN_DESIGNATED_DUAL4090_STORAGE_FRESH_METADATA_ACTUAL.json',value)
    print(json.dumps(value,ensure_ascii=False))

if __name__=='__main__':
    try:
        main()
    except BaseException:
        put('V111_HUMAN_DESIGNATED_STORAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()))
        raise
