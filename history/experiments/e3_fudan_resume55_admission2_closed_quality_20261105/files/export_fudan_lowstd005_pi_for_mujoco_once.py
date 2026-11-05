"""Export one derived CPU pi-only artifact after actual positive N20000 closure.
The inline closure front door is the frozen 279-line stager's existing metadata gate.
Never run an evaluation, access input models for status, or restore training state.
"""
from pathlib import Path, PurePosixPath
import argparse
import ast
import hashlib
import json
import shlex
import sys
import time
import traceback

KIND = "MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1"
BRANCH = "FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005"
BASE = dict(updates=0, policy_optimizer_steps=0, encoder_optimizer_steps=0, transitions_seen=0)
COUNTERS = tuple(BASE)
MOTHER_SHA = "1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8"
SOURCE_4K_SHA = "47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d"
LEARNER_SHA = "8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78"
SOURCE_KIND = "fdn_fresh_mlp_warm_1cd_n20000_timeout8_lowstd005"
OVERLAY_SHA = "a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9"
TASKS = "/home/lc01/Zonglin Li/zonglin2/tasks"
FROZEN_SOURCE_SHA = '8b44c3f9d1472acc24cc5f6ed150476af82743648265881eb746791f4b442210'
PREFIX = "FDNLOWSTD005_PI_ONLY_EXPORT_"

# Parsed locally by main before every marker/connector. Not run by a source AST check.
REMOTE_EXPORT = r'''"""One physical whole-source CPU decode for a derived nominal-only pi artifact."""
from pathlib import Path, PurePosixPath
import hashlib,io,json,os,sys,time,traceback


def need(condition,message):
    if not condition:raise ValueError(message)


def put(path,value):
    temporary=path.with_name(path.name+'.partial')
    need(not path.exists()and not temporary.exists(),'Own output collision: '+path.name)
    with temporary.open('x',encoding='utf8')as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


def main():
    B=Path(__file__).resolve().parent
    need(B.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks')and B.name.startswith('FDNLOWSTD005_PI_ONLY_EXPORT_'),'Own new CPU export root required')
    selected=json.loads((B/'selected.json').read_bytes());source=selected['source']
    source_IO=dict(physical_byte_opens=0,physical_reads=0,SHA_calculations=0,CPU_load_calls=0,CPU_decodes=0,
                   input_model_stat_operations=0,original_mother_reads=0,ancestor_N4096_reads=0,ancestor_N20000_reads=0)
    own_save_IO=dict(save_calls=0,hash_physical_opens=0,SHA_calculations=0)
    source_raw=root=pi=payload=None
    try:
        with(B/'PI_EXPORT_STARTED_ONCE.json').open('x',encoding='utf8')as stream:
            json.dump(dict(epoch=time.time(),source=source,CPU_only=True),stream,indent=2)
            stream.flush();os.fsync(stream.fileno())
        need(os.environ.get('CUDA_VISIBLE_DEVICES')=='','CUDA_VISIBLE_DEVICES must already be empty before Torch import')
        frozen_raw=(B/'frozen_sequence_mean.py').read_bytes()
        need(hashlib.sha256(frozen_raw).hexdigest()=='8b44c3f9d1472acc24cc5f6ed150476af82743648265881eb746791f4b442210','Frozen actor/encoder extraction source changed')
        sys.path.insert(0,str(B))
        import torch
        torch.set_num_threads(1)
        from frozen_sequence_mean import validate_checkpoint_provenance,extract_pi_state_dict,PI_SHAPES,MOTHER_PATH,MOTHER_SHA,EXCLUDED_N4096_PATH,EXCLUDED_N4096_SHA,EXCLUDED_PREVIOUS_N20000_PATH,EXCLUDED_PREVIOUS_N20000_SHA,EXCLUDED_TIMEOUT8_PATH,EXCLUDED_TIMEOUT8_SHA,EXCLUDED_FRESH25_PATH,EXCLUDED_FRESH25_SHA,EXCLUDED_HEIGHTGATE_PATH,EXCLUDED_HEIGHTGATE_SHA
        path=PurePosixPath(source['path'])
        need(set(source)=={'path','bytes','sha256','run','source_training_execution_qualified'}and
             source['source_training_execution_qualified']is True and
             path.parent==PurePosixPath('/home/lc01/Zonglin Li/zonglin2/tasks')/source['run']/'roles/E3/production'and
             '..'not in path.parts and path.suffix=='.pt'and
             os.path.normpath(source['path'])not in tuple(os.path.normpath(x)for x in(MOTHER_PATH,EXCLUDED_N4096_PATH,EXCLUDED_PREVIOUS_N20000_PATH,EXCLUDED_TIMEOUT8_PATH,EXCLUDED_FRESH25_PATH,EXCLUDED_HEIGHTGATE_PATH))and
             source['sha256']not in(MOTHER_SHA,EXCLUDED_N4096_SHA,EXCLUDED_PREVIOUS_N20000_SHA,EXCLUDED_TIMEOUT8_SHA,EXCLUDED_FRESH25_SHA,EXCLUDED_HEIGHTGATE_SHA),'Qualified own NEW N20000 source only')
        # No input exists/stat/resolve or preliminary read: this is the export's sole physical source open.
        with Path(source['path']).open('rb')as stream:
            source_IO['physical_byte_opens']+=1;source_IO['physical_reads']+=1
            source_raw=stream.read()
        need(len(source_raw)==source['bytes'],'Selected new source bytes differ')
        source_digest=hashlib.sha256(source_raw).hexdigest();source_IO['SHA_calculations']+=1
        need(source_digest==source['sha256'],'Selected new source SHA differs')
        source_IO['CPU_load_calls']+=1
        root=torch.load(io.BytesIO(source_raw),map_location='cpu',weights_only=False);source_IO['CPU_decodes']+=1
        provenance=validate_checkpoint_provenance(root,require_native_updates=True,expected_run=source['run'])
        need(provenance['learner_counters']==selected['expected_learner_counters']and
             provenance['base_counters']==selected['expected_base_counters']and
             provenance['window_counters']==selected['expected_window_counters']and
             all(value==selected['expected_native_counters'][key]for key,value in provenance['native_counters'].items()),
             'Actual decoded source counters differ from closed producer metadata')
        json.dumps(provenance,allow_nan=False)  # Proof remains actual JSON metadata, not hidden training tensors.
        pi=extract_pi_state_dict(root['learner'])
        need(set(pi)==set(PI_SHAPES)and len(pi)==14 and
             all(value.device.type=='cpu'and value.dtype==torch.float32 and
                 value.data_ptr()!=root['learner']['model'][key].data_ptr()for key,value in pi.items()),
             'Exactly 14 independently cloned CPU actor/encoder tensors required')
        need(all(source_IO[key]==1 for key in('physical_byte_opens','physical_reads','SHA_calculations','CPU_load_calls','CPU_decodes')),
             'Export source I/O is not exactly once')
        payload=dict(kind='FDN_PI_ONLY_EXPORT_FOR_NOMINAL_MUJOCO_V1',not_a_full_training_resume_checkpoint=True,
                     source=dict(source),source_provenance=provenance,pi_state_dict=pi,source_IO=dict(source_IO),
                     CPU_only=True,critic_optimizer_DR_history_or_RNG_restored=False,
                     whole_CPU_root_and_bytes_retained_during_export=True,native_or_original74_skill_acceptance_claim=False)
        destination=B/'pi_export.pt';temporary=B/'pi_export.pt.partial'
        need(not destination.exists()and not temporary.exists(),'Own derived artifact collision')
        with temporary.open('xb')as stream:
            torch.save(payload,stream);own_save_IO['save_calls']+=1;stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,destination)
        # Hash this OWN new derived save once; never reopen or rehash the full input.
        digest=hashlib.sha256();size=0
        with destination.open('rb')as stream:
            own_save_IO['hash_physical_opens']+=1
            while True:
                block=stream.read(1024*1024)
                if not block:break
                digest.update(block);size+=len(block)
        own_save_IO['SHA_calculations']+=1
        need(source_raw is not None and root is not None and pi is not None,'Whole source was released before export completion')
        receipt=dict(kind='FDN_PI_ONLY_EXPORT_RECEIPT_V1',complete=True,epoch=time.time(),
                     artifact=dict(path=str(destination),bytes=size,sha256=digest.hexdigest()),
                     source=dict(source),source_provenance=provenance,source_IO=dict(source_IO),own_save_IO=dict(own_save_IO),
                     pi_tensor_count=len(pi),pi_numel=sum(value.numel()for value in pi.values()),
                     not_a_full_training_resume_checkpoint=True,CPU_only=True,
                     whole_CPU_root_and_source_bytes_retained_until_receipt=True,unknown_source_fields_not_projected_or_applied=True,
                     critic_or_optimizer_object_constructed=False,training_DR_history_or_RNG_restored=False,
                     native_or_original74_skill_acceptance_claim=False)
        put(B/'pi_export_receipt.json',receipt)
        print(json.dumps(receipt,indent=2,allow_nan=False),flush=True)
        return 0
    except BaseException:
        error=dict(kind='FDN_PI_ONLY_EXPORT_ERROR_V1',epoch=time.time(),source=source,error=traceback.format_exc(),
                   source_IO=source_IO,own_save_IO=own_save_IO,complete=False,no_automatic_retry=True)
        error_path=B/'PI_EXPORT_ERROR.json'
        if not error_path.exists():put(error_path,error)
        print(json.dumps(error,indent=2,allow_nan=False),file=sys.stderr,flush=True)
        return 1


if __name__=='__main__':raise SystemExit(main())
'''


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closed", required=True, help="Actual own CLOSED_RESULT.json after N20000 closure")
    args = parser.parse_args()
    D = Path(__file__).resolve().parent
    closed_path = Path(args.closed)
    need(closed_path.name == "CLOSED_RESULT.json" and closed_path.suffix.lower() == ".json",
         "--closed must name CLOSED_RESULT.json, not a model or raw artifact")
    closed_raw = closed_path.read_bytes()
    closed = json.loads(closed_raw)
    need(closed["closed"] is True, "Actual closed observer evidence required")
    m = closed["metadata"]
    owner = m["OWNER_EXIT_ACTUAL.json"]
    outer = m["OUTER_OWNER_WAIT_ACTUAL.json"]
    need(owner["errors"] == [] and owner["all_own_children_waited"] is True and
         owner["original_cost_settled"] is True and owner["original_leases_released"] is True,
         "Error-free original inner wait, cost settlement and lease release required")
    need(outer["original_owner_reaped"] is True and type(outer["actual_wait_returncode"]) is int and
         outer["actual_wait_returncode"] == 0, "Actual outer RC0/reaped required")
    need(m.get("OWNER_ORIGINAL_ERROR.json") is None, "Original owner error evidence present")
    qualification = m["FDN_PARENT_WAIT_QUALIFICATION.json"]
    need(qualification["qualified"] is True and qualification["error"] is None and
         qualification["actual_child_wait_returncode"] == 0 and qualification["checks"] and
         all(value is True for value in qualification["checks"].values()),
         "Actual positive FDN parent-wait qualification required")
    f = m["FDN_FINAL.json"]
    latest = m["FDN_LATEST_COMPLETE_SAVE.json"]
    intent = m["FDN_APP_FAST_CLOSE_INTENT.json"]
    need(f["kind"] == KIND and f["version"] == 6 and f["branch_kind"] == BRANCH and
         f["role"] == "E3" and f["final"] is True and f["complete_save"] is True and
         f["error"] is None and f["close_errors"] == [], "Qualified version6 lowstd005 E3 full save required")
    run = f["run"]
    train_root = PurePosixPath(closed["root"])
    need(train_root.is_absolute() and ".." not in train_root.parts and
         train_root.parent == PurePosixPath(TASKS) and train_root.name == run and
         owner["run_id"] == run, "Closed original run/root binding differs")
    need(type(f["parent_pid"]) is int and type(f["worker_pid"]) is int and
         f["parent_pid"] > 0 and f["worker_pid"] > 0 and
         outer["original_owner_pid"] == m["OWNER_PARENT_IDENTITY.json"]["pid"] ==
         qualification["original_owner_pid"] == f["parent_pid"], "Actual original owner PID binding differs")
    cohort = m["COHORT_FINAL.json"]
    need(cohort["run_id"] == run and cohort["errors"] == [] and
         cohort["all_own_children_waited"] is True and cohort["original_cost_settled"] is True,
         "Actual cohort settlement required")
    rows = list(cohort["rows"].values())
    need(len(rows) == 1 and rows[0]["role"] == "E3" and rows[0]["phase"] == "terminal" and
         rows[0]["terminal_all_own_children_waited"] is True and rows[0]["returncode"] == 0 and
         rows[0]["original_error"] is False and rows[0]["final"] == f, "Actual E3 child wait/FINAL differs")
    need(latest == f["latest_complete_save"] == intent["latest_complete_save"] and
         intent["kind"] == KIND and intent["version"] == 6 and intent["branch_kind"] == BRANCH and
         intent["worker_pid"] == f["worker_pid"] and
         f["resource_binding"]["actual_parent_pid"] == f["parent_pid"] and intent["env_close_returned"] is True and
         intent["worker_final_qualified"] is True and intent["error_before_close"] is None and
         intent["close_errors"] == [], "Producer FINAL/latest/close receipt differs")
    for name in ("FDN_NATIVE_ERROR.json", "FDN_SAVE_ERROR.json", "FDN_FINAL_METADATA_ERROR.json", "FDN_APP_CLOSE_ERROR.json"):
        need(m.get(name) is None, "Preserved producer error: " + name)
    need(latest["kind"] == KIND and latest["version"] == 6 and latest["branch_kind"] == BRANCH and
         all(latest[key] is True for key in ("fullstate_required_components_complete", "both_Adam_states_present",
             "model_and_all_required_RNG_present", "new_asset_and_fresh_D0_D7_state_present")) and
         latest["own_new_save_hash_opens"] == 1, "Producer's complete new-save receipt required")
    base, window, counters = f["base_counters"], f["window_counters"], f["counters"]
    need(base == BASE and window == counters and set(counters) == set(BASE) and
         all(type(counters[k]) is int and counters[k] >= 0 for k in COUNTERS),
         "Fresh zero-base, window-only counters required")
    wu = counters["updates"]
    need(0 < wu <= 25 and counters["policy_optimizer_steps"] == counters["encoder_optimizer_steps"] == 20 * wu and
         counters["transitions_seen"] == 48 * 20000 * wu, "Positive actual finite25 N20000 learning required")
    source_receipt = f["source_checkpoint"]
    need(source_receipt == latest["source_checkpoint"] == intent["source_checkpoint"] and
         source_receipt["source_sha256"] == MOTHER_SHA and source_receipt["source_bytes"] == 14715029 and
         source_receipt["source_iter"] == 43090 and source_receipt["physical_byte_opens"] ==
         source_receipt["SHA_calculations"] == source_receipt["CPU_decodes"] == latest["original_mother_reads"] == 1 and
         all(source_receipt[k] is True for k in ("whole_source_root_and_bytes_retained", "source_tensor_versions_unchanged",
             "actor_critic_MLP_only", "source_optimizer_and_DR_state_not_restored", "old_iteration_not_inherited")),
         "Actual single1cd MLP-only warm receipt and retained source required")
    init, update = m["FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json"], m["FDN_NATIVE_UPDATE.json"]
    need(init["version"] == 6 and init["fresh_envs"] == 20000 and init["initial_counters"] == BASE and
         init["source_checkpoint"] == source_receipt and init["history_initialized_from_new_returned_raw35_repeated_five"] is True and
         init["source_global_RNG_environment_DR_history_queues_or_pending_applied"] is False and
         update["rollout_N"] == 20000 and update["rollout_T"] == 48 and update["actual_native_training_update"] is True and
         update["base_counters"] == BASE and update["window_counters"] == update["counters"] == counters,
         "Actual fresh initialized/trained N20000 and T48 required")
    native = f["native_counters"]
    c = native["actual_native_policy_steps"]
    need(type(c) is int and c > 0 and f["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
         native["actual_native_transitions"] == 20000 * c and native["physical_callbacks"] == 8 * c and
         native["feedback_callbacks"] == 2 * c and native["termination_computations"] == c and
         0 <= c - 48 * wu <= 48, "Current N20000 native clocks/unoptimized partial differ")
    for item in (f, latest, intent):
        need(item["source_kind"] == SOURCE_KIND and item["base_counters"] == BASE and item["window_counters"] == counters and
             item["num_envs"] == 20000 and item["inherited_old_iterations"] == 0 and item["full_learner_resume"] is False and
             item["bad_candidate_reads"] == 0 and item["task_runtime_overlay"] == f["task_runtime_overlay"],
             "All fresh producer/save/intent provenance must match")
    need(latest["counters"] == counters and latest["native_counters"] == native and
         latest["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
         f["task_runtime_overlay"]["bytes"] == 12745 and f["task_runtime_overlay"]["sha256"] == OVERLAY_SHA,
         "Latest full state/current native/unchanged fixed timeout8 metadata required")
    need(init["learner_config"]["initial_std"] == .05, "Actual fresh learner initial policy STD0.05 required")
    summary=f["task_summary"];tracking=summary["tracking_reward_config"];passive=summary["low_rollout_summary"];criteria=summary["low_criterion_summary"]
    need(tracking["height_gate_enabled"] is False and
         set(tracking["terms"]) == {"track_lin_vel","track_lin_vel_tight","track_ang_vel"} and
         all(t["height_gate_installed"] is False for t in tracking["terms"].values()),
         "Actual original positive tracking functions without heightgate required")
    samples=summary["low_envs"]*native["actual_native_policy_steps"]
    need(passive["dtype"] == "float64" and passive["descriptive_only_not_acceptance"] is True and
         passive["samples"] == criteria["samples"] == samples and samples>0 and
         0<=passive["ge023_samples"]<=samples, "Actual pre-reset passive sample clock required")
    criterion_names={"height_ok","upright_ok","speed_ok","angular_ok","wheels_ok","chassis_ok","joint_good"}
    need(criteria["descriptive_only_not_acceptance"] is True and set(criteria["counts"])==criterion_names and
         set(criteria["fractions"])==criterion_names and all(0<=v<=samples for v in criteria["counts"].values()) and
         all(criteria["counts"]["joint_good"]<=v for v in criteria["counts"].values()),
         "Actual seven passive criteria bounded; not acceptance or a new grader")
    selected = dict(path=latest["path"], bytes=latest["bytes"], sha256=latest["sha256"], run=run)
    selected_path = PurePosixPath(selected["path"])
    need(selected_path.parent == train_root / "roles/E3/production" and selected_path.suffix == ".pt" and
         type(selected["bytes"]) is int and selected["bytes"] > 0 and
         isinstance(selected["sha256"], str) and len(selected["sha256"]) == 64 and
         all(ch in "0123456789abcdef" for ch in selected["sha256"]) and
         selected["sha256"] not in (MOTHER_SHA, SOURCE_4K_SHA, LEARNER_SHA, "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e", "246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2", "bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2") and
         selected["path"] != source_receipt["source_path"], "Actual own NEW save path/bytes/SHA required")
    # Every check above is the existing closed metadata gate, before marker/mkdir/connect.
    frozen_path = D / "source_fudan_frozen_native_eval_v6_lowstd005/frozen_sequence_mean.py"
    frozen_raw = frozen_path.read_bytes()
    need(hashlib.sha256(frozen_raw).hexdigest() == FROZEN_SOURCE_SHA, "Frozen extraction source changed")
    ast.parse(REMOTE_EXPORT, filename="cpu_export.py")
    gid = PREFIX + time.strftime("%Y%m%d_%H%M%S") + "_" + str(time.time_ns())
    root = TASKS + "/" + gid
    local = D / gid
    marker = D / (PREFIX + "STARTED_ONCE.json")
    need(not marker.exists() and not local.exists() and root != str(train_root), "Unused own export namespace required")
    source = dict(selected, source_training_execution_qualified=True)
    selection = dict(source=source, expected_learner_counters=counters, expected_base_counters=base,
                     expected_window_counters=window, expected_native_counters=native)
    result = dict(epoch=time.time(), root=root, local_directory=str(local), source=source,
                  closed_metadata_sha256=hashlib.sha256(closed_raw).hexdigest(), input_model_status_operations=0,
                  CPU_only=True, evaluation_executed=False, complete=False, no_automatic_retry=True)
    with marker.open("x", encoding="utf8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    c = s = None
    try:
        local.mkdir()
        sys.path.insert(0, str(D.parent / "mod4v1_experts_fulldr_rm70_20261101"))
        from project_connector import connect72
        c = connect72()
        s = c.open_sftp()
        s.get_channel().settimeout(60)
        try:
            s.lstat(root)
            raise RuntimeError("Unused remote CPU export root required")
        except FileNotFoundError:
            pass
        s.mkdir(root)
        for name, raw in (("cpu_export.py", REMOTE_EXPORT.encode()), ("frozen_sequence_mean.py", frozen_raw),
                          ("selected.json", json.dumps(selection, indent=2, allow_nan=False).encode())):
            with s.open(root + "/" + name, "wx") as stream:
                stream.write(raw)
        command = "env CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 " + shlex.quote("/home/lc01/Zonglin Li/zonglin2/run-python.sh") + " -B " + shlex.quote(root + "/cpu_export.py")
        i, o, e = c.exec_command(command, timeout=600)
        i.close()
        stdout, stderr = o.read().decode("utf8", "replace"), e.read().decode("utf8", "replace")
        rc = o.channel.recv_exit_status()
        result.update(returncode=rc, stdout=stdout, stderr=stderr)
        need(rc == 0, "CPU export failed; preserve own source/error, do not replay: " + stderr)
        # Download only the small new derived artifact and its own receipt, never the source checkpoint.
        with s.open(root + "/pi_export_receipt.json", "rb") as stream:
            receipt_raw = stream.read(256 * 1024 + 1)
        need(len(receipt_raw) <= 256 * 1024, "Own pi receipt exceeds metadata bound")
        receipt = json.loads(receipt_raw)
        artifact = receipt["artifact"]
        need(receipt["kind"] == "FDN_PI_ONLY_EXPORT_RECEIPT_V1" and receipt["complete"] is True and
             receipt["source"] == source and artifact["path"] == root + "/pi_export.pt" and
             type(artifact["bytes"]) is int and 0 < artifact["bytes"] < 8 * 1024 * 1024 and
             isinstance(artifact["sha256"], str) and len(artifact["sha256"]) == 64 and
             all(ch in "0123456789abcdef" for ch in artifact["sha256"]) and
             receipt["pi_tensor_count"] == 14 and receipt["pi_numel"] == 82505 and receipt["CPU_only"] is True and
             receipt["not_a_full_training_resume_checkpoint"] is True and
             receipt["source_IO"]["input_model_stat_operations"] == receipt["source_IO"]["original_mother_reads"] == receipt["source_IO"]["ancestor_N4096_reads"] == receipt["source_IO"]["ancestor_N20000_reads"] == 0 and
             receipt["own_save_IO"] == dict(save_calls=1, hash_physical_opens=1, SHA_calculations=1) and
             all(receipt["source_IO"][key] == 1 for key in ("physical_byte_opens", "physical_reads", "SHA_calculations", "CPU_load_calls", "CPU_decodes")),
             "Actual complete once-export receipt differs")
        with (local / "pi_export_receipt.json").open("xb") as stream:
            stream.write(receipt_raw)
        copied = 0
        with s.open(root + "/pi_export.pt", "rb") as remote, (local / "pi_export.pt").open("xb") as stream:
            while True:
                block = remote.read(1024 * 1024)
                if not block:
                    break
                copied += len(block)
                need(copied <= artifact["bytes"], "Derived transfer exceeds actual receipt; no input checkpoint transfer")
                stream.write(block)
        need(copied == artifact["bytes"], "Derived transfer size differs from own-save receipt")
        result.update(complete=True, artifact=artifact, receipt=receipt, downloaded_derived_bytes=copied,
                      local_pi_export=str(local / "pi_export.pt"), local_receipt=str(local / "pi_export_receipt.json"),
                      full_source_checkpoint_downloaded=False, input_model_reopened_or_rehashed_for_status=False)
    except BaseException:
        result["error"] = traceback.format_exc()
        raise
    finally:
        # Retain the original once binding and actual failure; no automatic retry or false success.
        cleanup_errors = []
        for label, resource in (("sftp", s), ("ssh", c)):
            if resource is not None:
                try:
                    resource.close()
                except BaseException:
                    cleanup_errors.append(dict(resource=label, error=traceback.format_exc()))
        if cleanup_errors:
            result["cleanup_errors"] = cleanup_errors
            result["complete"] = False
        marker.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf8")
        print(json.dumps(result, indent=2, allow_nan=False))
        if cleanup_errors and "error" not in result:
            raise RuntimeError("Own export transport cleanup failed; preserve once evidence without replay")


if __name__ == "__main__":
    main()
