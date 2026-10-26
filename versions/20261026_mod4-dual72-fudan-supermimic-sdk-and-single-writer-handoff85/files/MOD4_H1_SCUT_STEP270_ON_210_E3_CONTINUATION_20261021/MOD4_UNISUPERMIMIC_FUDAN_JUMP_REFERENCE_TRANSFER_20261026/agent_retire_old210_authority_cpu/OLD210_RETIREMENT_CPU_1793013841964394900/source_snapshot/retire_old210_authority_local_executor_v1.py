"""Prepared source210-local executor. ROOT ONLY, serial AFTER first observer returns.

No SSH/network calls, GPU/model loads, new72 account access, controller stops or
permission changes. Default dry review. Helper does NOT execute this in production.
"""
from pathlib import Path
import argparse,contextlib,hashlib,json,os,sys,time,traceback
import retire_old210_authority_core_v1 as C


def targeted_process_receipt():
    import psutil
    rows=[]
    for pid in (C.OWNER_PID,C.OLD_SOURCE_NODE_PID,C.OLD_SOURCE_WORKER_PID):
        try:p=psutil.Process(pid);rows.append(dict(pid=pid,exists=True,creation=p.create_time()))
        except psutil.NoSuchProcess:rows.append(dict(pid=pid,exists=False))
        # AccessDenied or unknown identity is an error, never "out".
    C.validate_targeted_old_process_rows(rows);return rows


def main():
    p=argparse.ArgumentParser();p.add_argument("--authorization-file",required=True);p.add_argument("--serial-clearance-file",required=True)
    p.add_argument("--execute",action="store_true");args=p.parse_args()
    C.require(sys.platform.startswith("linux"),"production wrapper runs only on actual source210 Linux")
    here=Path(__file__).resolve().parent;receipts=here/"retirement_receipts";receipts.mkdir(exist_ok=True)
    trial="OLD210_AUTHORITY_RETIREMENT_"+str(time.time_ns());report=dict(trial_id=trial,execute_requested=args.execute,epoch=time.time(),new72_account_IO=False)
    try:
        auth=Path(args.authorization_file).read_bytes();C.validate_authorization(auth)
        clearance_raw=Path(args.serial_clearance_file).read_bytes();C.validate_serial_clearance(json.loads(clearance_raw))
        report.update(human_authorization_SHA256=C.sha(auth),serial_clearance_SHA256=C.sha(clearance_raw),
                      targeted_old_process_receipt=targeted_process_receipt())
        source=Path(C.OLD_C)
        C.require(str(source)==C.OLD_C and source.resolve()==source and source.parent.is_dir(),"exact old source path required")
        import fcntl
        with contextlib.ExitStack() as stack:
            locks=[]
            for name in C.OLD_LOCKS:
                path=Path(name);C.require(path.is_file() and not path.is_symlink(),"original lock file absent/symlink; do not create/delete locks")
                f=stack.enter_context(path.open("rb+"));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(name)
            report["original_two_fcntl_held"]=locks
            # Recheck exact targeted identities after acquiring both owner locks.
            report["targeted_old_process_receipt_under_locks"]=targeted_process_receipt()
            report["result"]=C.transaction_under_owned_locks(source,execute=args.execute,locks_held=True)
        report["status"]="PASS_ACTUAL_RETIREMENT" if args.execute else "PASS_DRY_REVIEW_ONLY"
    except BaseException:
        report.update(status="ORIGINAL_ERROR_NO_UNSAFE_FALLBACK",error=traceback.format_exc(),
                      original_history_and_prepared_partial_preserved=True)
        raise
    finally:
        path=receipts/(trial+".json")
        with path.open("x",encoding="utf8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
        print(json.dumps(dict(receipt=str(path),status=report.get("status"),SHA256=hashlib.sha256(path.read_bytes()).hexdigest())),flush=True)


if __name__=="__main__":main()
