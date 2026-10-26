"""Narrow old-source fence. No network, model, GPU, new72 account or controller IO.

Preserve exact old bytes by same-directory no-replace rename; install a small
tombstone with NO active/budget fields. Pure validation and transaction primitives
are separately CPU-testable. Production path/locks/authorization are pinned.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import ctypes
import errno
import hashlib
import json
import os
import stat
import sys
import time

OLD_C="/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json"
OLD_LOCKS=("/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock",
           "/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock")
SOURCE_SHA="fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1"
AUTH_SHA="fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf"
NEW_C="/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json"
GENERATION="MOD4_SINGLE_WRITER72_20261026"
TOMBSTONE_SCHEMA="mod4.retired_source_authority_tombstone.v1"
LAST_83B_RUN="THREE4090_EXPERT_ORIGINAL_1792994651814636100"
REMAINING=595256.8240613937
TOTAL=2268000
OWNER_PID=1493851
OWNER_CREATION=1792994651.61
OLD_SOURCE_NODE_PID=1493856
OLD_SOURCE_WORKER_PID=1494050
OLD_SCOPE_ENDED=1792998322.2629082


class RetirementRejected(ValueError):pass
def require(value,message):
    if not value:raise RetirementRejected(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Expected:
    source_sha:str=SOURCE_SHA
    authorization_sha:str=AUTH_SHA
    remaining:float=REMAINING
    total:int=TOTAL
    extensions:int=9
    new_canonical:str=NEW_C
    generation:str=GENERATION


def validate_authorization(raw,expected=Expected()):
    require(sha(raw)==expected.authorization_sha,"human authorization SHA mismatch")
    a=json.loads(raw)
    require(a.get("approved") is True and a.get("old210_Linux_canonical_retired_from_authority") is True and
            a.get("old210_Linux_must_not_resume_a_separate_writer") is True,"explicit old-authority retirement authorization missing")
    require(a.get("new_canonical_path")==expected.new_canonical,"human-authorized new sole72 path mismatch")
    # Temporary spending-mode expiry does not revoke the permanent sole-writer
    # move. This fence never reads or changes72's now-restored finite mode.
    return a


def validate_original(raw,expected=Expected()):
    require(sha(raw)==expected.source_sha,"old canonical exact SHA mismatch; stop without mutation")
    c=json.loads(raw)
    require(c.get("active_segment","MISSING") is None,"old canonical active_segment is not explicit None")
    require(c.get("authorized_training_seconds")==expected.total,"original total mismatch")
    require(c.get("remaining_training_seconds")==expected.remaining,"original83B closing balance mismatch")
    require(isinstance(c.get("budget_extensions"),list) and len(c["budget_extensions"])==expected.extensions,"original nine-extension state mismatch")
    require(isinstance(c.get("completed_segments"),list),"original completed-segment history missing")
    return c


def validate_serial_clearance(receipt):
    require(receipt.get("schema")=="mod4.root.serial_source210_retirement_clearance.v1","root serial-clearance schema required")
    require(receipt.get("root_first_observer_actual_returned") is True,"first observer still live/unknown; no parallel source action")
    require(receipt.get("root_serial_execution_on_source210") is True,"root serial source210 clearance missing")
    require(receipt.get("new72_generation")==GENERATION and receipt.get("new72_canonical_path")==NEW_C,"live sole72 authority mismatch")
    require(receipt.get("new72_authority_already_active") is True and receipt.get("old83B_all_owner_children_out_receipt") is True,
            "existing sole-authority/closed83B receipt missing")
    require(not receipt.get("fixture",False),"fixture clearance cannot authorize a production retirement")
    return receipt


def validate_targeted_old_process_rows(rows):
    """Only three known old source210 PIDs; never enumerate or kill peers/sessions."""
    require({r["pid"] for r in rows}=={OWNER_PID,OLD_SOURCE_NODE_PID,OLD_SOURCE_WORKER_PID},"exact old source PID receipt set required")
    result=[]
    for row in rows:
        if row.get("exists") is False:result.append(dict(pid=row["pid"],old_identity_out=True,basis="PID_absent"));continue
        created=row.get("creation")
        require(isinstance(created,(int,float)),"PID exists but creation identity unavailable")
        if row["pid"]==OWNER_PID:plausibly_old=abs(created-OWNER_CREATION)<=.1
        else:plausibly_old=OWNER_CREATION-.1<=created<=OLD_SCOPE_ENDED
        require(not plausibly_old,"known original writer/source child may still be alive; do not touch canonical")
        result.append(dict(pid=row["pid"],old_identity_out=True,basis="PID_reused_different_creation",current_creation=created))
    return result


def history_path(source,expected=Expected()):
    source=Path(source)
    return source.with_name(source.stem+".RETIRED_SOURCE210_SHA256_"+expected.source_sha+source.suffix)


TOMBSTONE_KEYS={"schema","retired_source_authority","new_sole_authority_host","new_sole_authority_canonical_path",
                "new_sole_authority_generation","original_source_canonical_SHA256","human_authorization_SHA256",
                "preserved_original_bytes_path","retired_at_epoch","old_writer_must_not_resume"}


def tombstone(source,history,expected=Expected(),epoch=None):
    return dict(schema=TOMBSTONE_SCHEMA,retired_source_authority=True,new_sole_authority_host="72",
        new_sole_authority_canonical_path=expected.new_canonical,new_sole_authority_generation=expected.generation,
        original_source_canonical_SHA256=expected.source_sha,human_authorization_SHA256=expected.authorization_sha,
        preserved_original_bytes_path=str(history),retired_at_epoch=time.time() if epoch is None else epoch,
        old_writer_must_not_resume=True)


def validate_tombstone(raw,source,history,expected=Expected()):
    value=json.loads(raw)
    require(set(value)==TOMBSTONE_KEYS,"unexpected tombstone fields; budget/active fields are forbidden")
    require(value["schema"]==TOMBSTONE_SCHEMA and value["retired_source_authority"] is True and value["old_writer_must_not_resume"] is True,"not a retirement tombstone")
    require(value["new_sole_authority_host"]=="72" and value["new_sole_authority_canonical_path"]==expected.new_canonical and
            value["new_sole_authority_generation"]==expected.generation,"tombstone sole authority mismatch")
    require(value["original_source_canonical_SHA256"]==expected.source_sha and value["human_authorization_SHA256"]==expected.authorization_sha,
            "tombstone source/authorization SHA mismatch")
    require(value["preserved_original_bytes_path"]==str(history),"history path mismatch")
    return value


def rename_noreplace(source,target):
    """Atomic within-directory rename, refusing any existing destination.

    Linux production requires renameat2(RENAME_NOREPLACE), with no overwrite
    fallback. Windows uses its native os.rename no-overwrite behavior for local
    synthetic fixtures only. Original bytes are never copied or reserialized.
    """
    source,target=Path(source),Path(target)
    require(source.parent==target.parent,"rename must remain in original directory/filesystem")
    if sys.platform.startswith("linux"):
        libc=ctypes.CDLL(None,use_errno=True);fn=getattr(libc,"renameat2",None)
        require(fn is not None,"renameat2 no-replace unavailable; stop without unsafe fallback")
        fn.argtypes=(ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint);fn.restype=ctypes.c_int
        if fn(-100,os.fsencode(source),-100,os.fsencode(target),1)!=0:
            code=ctypes.get_errno();raise OSError(code,os.strerror(code),str(target))
    elif os.name=="nt":os.rename(source,target)
    else:raise RetirementRejected("unsupported atomic no-replace platform")


def sync_directory(path):
    if os.name=="nt":return # CPU fixture platform; production is Linux only.
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def inspect_files(source,expected=Expected()):
    source=Path(source);history=history_path(source,expected)
    require(not source.is_symlink() and not history.is_symlink(),"source/history symlinks forbidden")
    if source.exists():
        require(source.is_file(),"canonical path is not a regular file")
        raw=source.read_bytes()
        try:decoded=json.loads(raw)
        except Exception:raise RetirementRejected("canonical/tombstone JSON unreadable")
        if decoded.get("schema")==TOMBSTONE_SCHEMA:
            require(history.is_file(),"tombstone without original history")
            validate_tombstone(raw,source,history,expected);validate_original(history.read_bytes(),expected)
            return dict(state="ALREADY_RETIRED",source=source,history=history,source_bytes=raw)
        validate_original(raw,expected)
        require(not history.exists(),"both original C and history exist; refuse ambiguous duplicate/overwrite")
        return dict(state="ORIGINAL_VERIFIED",source=source,history=history,source_bytes=raw)
    require(history.is_file(),"neither original canonical nor exact retired history exists")
    validate_original(history.read_bytes(),expected)
    return dict(state="RESUME_AFTER_EXACT_RENAME",source=source,history=history,source_bytes=None)


def transaction_under_owned_locks(source,expected=Expected(),*,execute=False,locks_held=False,event=None):
    """Narrow transaction primitive. Production wrapper owns authorization/process/locks.

    event is only an injected CPU fault hook; production wrapper never supplies it.
    No permission changes, lock creation/deletion, fake active values or ledger copy.
    """
    state=inspect_files(source,expected);source,history=state["source"],state["history"]
    if not execute:return dict(status="DRY_REVIEW_NO_MUTATION",source_state=state["state"],history_path=str(history))
    require(locks_held,"both original owner locks must be held throughout transaction")
    if state["state"]=="ALREADY_RETIRED":return dict(status="ALREADY_RETIRED_EXACT_IDEMPOTENT",history_path=str(history))
    if state["state"]=="ORIGINAL_VERIFIED":
        before=source.stat();require(stat.S_ISREG(before.st_mode),"source not regular")
        # Recheck current bytes immediately before no-replace rename while locked.
        validate_original(source.read_bytes(),expected)
        rename_noreplace(source,history);sync_directory(source.parent)
        after=history.stat();require(before.st_ino==after.st_ino and before.st_size==after.st_size,"rename inode/size identity changed")
        validate_original(history.read_bytes(),expected)
        if event:event("after_original_rename")
    require(not source.exists(),"unexpected new C after rename; never overwrite it")
    value=tombstone(source,history,expected);raw=(json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    temporary=source.with_name(source.name+".RETIRE_TOMBSTONE_PREPARED_"+str(time.time_ns())+".partial")
    with temporary.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
    validate_tombstone(temporary.read_bytes(),source,history,expected)
    if event:event("before_tombstone_install")
    # The install also uses no-replace; a rogue C appearing in the gap is never
    # replaced. Both exact history and prepared tombstone remain for examination.
    rename_noreplace(temporary,source);sync_directory(source.parent)
    validate_tombstone(source.read_bytes(),source,history,expected);validate_original(history.read_bytes(),expected)
    return dict(status="RETIRED_OLD_SOURCE_EXACT_BYTES_RENAMED_TOMBSTONE_INSTALLED",history_path=str(history),
                original_source_SHA256=expected.source_sha,tombstone_SHA256=sha(source.read_bytes()),
                no_new72_account_IO=True,no_refund_or_cost_history_mutation=True)
