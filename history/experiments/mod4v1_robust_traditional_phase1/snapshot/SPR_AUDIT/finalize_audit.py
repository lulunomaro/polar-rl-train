"""Audit metadata validation only; parses selected project XML, hashes artifacts.
Never invokes an archive script, compiler, firmware, simulator or device API.
"""
from pathlib import Path
import hashlib, json, posixpath, re, traceback, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


C = "reference_selected/chassis/chassis/"
M = "reference_selected/LinearMPC.jl-main/LinearMPC.jl-main/"
G = "reference_selected/gimbal/gimbal/"
O = "reference_selected/SPR Balanced-infantry/readme.txt"

def reference(path, first, last):
    return {"path": path, "start_line": first, "end_line": last,
            "citation": f"{path}#L{first}-L{last}"}

# All ranges below were inspected with the host read tool; references are evidence,
# not instructions. Full-file member citations do not imply every line was reviewed.
CLAIMS = [
    ("BOARD-01", "SRC_DECLARATION_CORROBORATED", "SPR declares DM02 chassis and DJI C gimbal; H723 and F407 projects corroborate distinct MCUs, not target MOD4v1 binding.",
     [(O,1,1),(C+"Balanced-infantry.ioc",317,386),(C+"MDK-ARM/Balanced-infantry.uvprojx",10,21),(G+"MDK-ARM/sentry.uvprojx",10,21)]),
    ("MOTOR-01", "ACTIVE_SOURCE", "Four DM_J8009 torque-mode joints plus two 3508-format wheel drives, not an all-Damiao source chassis.",
     [(C+"application/CAN_receive.h",6,22),(C+"application/CAN_receive.c",32,109),(C+"Task/send_task.c",1,1),(C+"Task/send_task.c",70,75)]),
    ("CAN-01", "ACTIVE_SOURCE", "Classic CAN 1Mbps on three FDCAN instances; bus1 left wheel+IDs3/4, bus2 right wheel+IDs1/2, bus3 inter-board and cap from configured send path.",
     [(C+"Balanced-infantry.ioc",255,307),(C+"application/CAN_receive.c",198,347),(C+"application/CAN_receive.c",151,171),(C+"Core/Src/fdcan.c",194,267)]),
    ("SCALE-01", "ACTIVE_SOURCE_CONFLICT", "DM position bounds are +/-3.14 despite +/-12.5 comments; torque +/-54 and speed +/-45 are source constants, not discovered motor registers.",
     [(C+"application/CAN_receive.h",8,13),(C+"application/CAN_receive.c",60,109),(C+"application/CAN_receive.c",182,222)]),
    ("SIGN-01", "ACTIVE_SOURCE", "Joint zero offsets and right-side negations are source-robot calibrations; they are not MOD4v1 calibration.",
     [(C+"Task/chassis_task.c",226,254),(C+"Task/chassis_task.c",737,745),(C+"Task/chassis_task.c",527,534)]),
    ("GEAR-01", "STATIC_DEFECT", "Wheel feedback uses 268/17, active command adds /13.94; isolated (268/17) is C integer division 15, not 15.7647.",
     [(C+"application/CAN_receive.c",32,55),(C+"application/CAN_receive.c",382,395),(C+"Task/chassis_task.h",47,55),(C+"Task/chassis_task.c",652,656)]),
    ("EST-01", "ACTIVE_SOURCE_GAP", "BMI088 QEKF/gravity compensation and 2-state velocity KF exist; fixed dt=0.001, acceleration R=1e12, no lever-arm correction found in audited estimator path.",
     [(C+"boards/BMI088driver.c",64,89),(C+"Task/INS_task.c",77,125),(C+"Task/chassis_task.c",32,43),(C+"Task/chassis_task.c",258,288),(C+"Task/chassis_task.c",522,535)]),
    ("YAW-01", "STATIC_DEFECT", "QEKF yaw total adds integer revolution count directly to radians without 2*pi; main rate loop uses gyro rather than this total.",
     [(C+"Task/INS_task.c",298,313),(C+"Task/chassis_task.c",338,343)]),
    ("SPIN-01", "ACTIVE_SOURCE_NOT_QUALIFICATION", "Self-spin is -13/-9/-5 rad/s counter-based schedule, not constant 4*pi spin/start/stop/reverse qualification.",
     [(C+"application/chassis_behaviour.c",249,284),(C+"Task/chassis_task.c",338,343),(C+"Task/chassis_task.c",625,629)]),
    ("FSM-01", "ACTIVE_SOURCE", "Ground/fall/recovery/jump/climb modes and contact classifiers exist; no uniform per-state measured timeout/qualification is evidenced.",
     [(C+"Task/chassis_task.h",163,190),(C+"Task/chassis_task.c",345,518),(C+"Task/chassis_task.c",827,896),(C+"Task/chassis_task.c",977,1062)]),
    ("CONTACT-01", "ACTIVE_SOURCE_LIMITED", "Liftoff KNN and windowed impact KNN are called. Trained sample/centroid headers intentionally excluded; source comments admit domain limitations.",
     [(C+"algorithm/KNN.c",1,85),(C+"algorithm/ClimbKNN.c",10,77),(C+"Task/chassis_task.c",372,400),(C+"Task/chassis_task.c",666,731)]),
    ("TIME-01", "ACTIVE_SOURCE_GAP", "1000Hz RTOS tick and vTaskDelay(1) plus 200us busy-wait/20ms init delays are scheduling intent, not measured 1ms deadline proof.",
     [(C+"Core/Inc/FreeRTOSConfig.h",58,91),(C+"Core/Src/freertos.c",117,130),(C+"Task/send_task.c",29,75),(C+"application/CAN_receive.c",586,615)]),
    ("FAULT-01", "STATIC_DEFECT", "Motor-offline zero-torque sends in send_task fall through independent DBUS branch; later normal commands can overwrite the gate in the same iteration.",
     [(C+"Task/send_task.c",29,78),(C+"Task/detect_task.c",215,232)]),
    ("POWER-01", "STATIC_DEFECT", "Power allocator writes Right_Leg.Tp in place of Wheel_Right.Tp and divides by MovePower+TurnPower without zero guard; predictor only models 3508 wheels.",
     [(C+"Task/chassis_task.c",1064,1085),(C+"Task/chassis_task.c",1111,1165)]),
    ("CAN-02", "STATIC_DEFECT", "Power high bytes shifted right; receive callback lacks bus/DLC/status checks and shared global TX header/buffer has concurrent task users.",
     [(C+"application/CAN_receive.c",9,30),(C+"application/CAN_receive.c",123,140),(C+"application/CAN_receive.c",198,249),(C+"Task/chassis_task.c",118,153),(C+"Task/send_task.c",29,75)]),
    ("GEOM-01", "STATIC_DOMAIN_GAP", "Generated kinematics hardcode 0.21/0.25 geometry; IK uses different geometry and 0.5m max exceeds ~0.4591m reach; no finite/domain guards.",
     [(C+"algorithm/leg_position.c",92,113),(C+"algorithm/leg_position.c",122,150),(C+"algorithm/leg_force.c",64,111),(C+"application/chassis_behaviour.h",16,19)]),
    ("MPC-01", "SOURCE_VS_DESCRIPTION", "Active chassis MPC.c only initializes A/B matrices; upstream LinearMPC archive has generic templates and codegen notes, not a linked board-qualified solver in the chassis project.",
     [(C+"algorithm/MPC.c",1,31),(C+"MDK-ARM/Balanced-infantry.uvprojx",486,509),(O,3,9),(M+"codegen/mpc_update_qp.c",24,53),(M+"使用linerMPC.txt",42,71)]),
    ("BUILD-01", "CONFIG_PRESENT_NOT_BUILT", "Keil ARMCC5.06u7/H7 DFP4.0.0 project and scatter map exist; no current target build or deployable BIN evidence was generated.",
     [(C+"MDK-ARM/Balanced-infantry.uvprojx",10,21),(C+"MDK-ARM/Balanced-infantry.uvprojx",328,342),(C+"MDK-ARM/Balanced-infantry/Balanced-infantry.sct",5,30),(C+"Core/Src/main.c",104,132)]),
    ("LEGACY-01", "PRESENT_NOT_ACTIVE_ENTRY", "Unitree A1 RS485 and WIT UART IMU files are present but absent from current chassis project file list; live entry uses CAN and BMI088.",
     [(C+"application/RS485_Receive.c",22,27),(C+"application/RS485_Receive.c",43,58),(C+"application/IMU_Receive.c",1,13),(C+"MDK-ARM/Balanced-infantry.uvprojx",423,456),(C+"Core/Src/main.c",104,125)]),
    ("LICENSE-01", "MIXED_COMPONENT_LICENSES", "CMSIS/DSP Apache2, ST HAL BSD3 fallback, FreeRTOS MIT-style, LinearMPC MIT; no root custom SPR project license identified in indexed roots.",
     [(C+"Drivers/CMSIS/LICENSE.txt",1,5),(C+"Drivers/STM32H7xx_HAL_Driver/LICENSE.txt",1,6),(C+"Middlewares/Third_Party/FreeRTOS/Source/LICENSE",1,17),(M+"LICENSE",1,21),(C+"application/chassis_behaviour.h",1,10)]),
]


def main():
    index = load("SPR_SOURCE_INDEX.json")
    original = index["original_archive"]
    archive_path = Path(original["path"])
    assert archive_path.stat().st_size == original["bytes"]
    assert sha(archive_path) == original["sha256"]
    for item in index["selected_members"]:
        path = ROOT / item["extracted_path"]
        assert path.resolve().is_relative_to((ROOT / "reference_selected").resolve())
        assert path.stat().st_size == item["extracted_bytes"]
        assert sha(path) == item["extracted_sha256"]
        assert len(path.read_text(encoding="utf-8").splitlines()) == item["line_count"]
        item["citation"] = f"{item['extracted_path']}#L1-L{item['line_count']}"
        item["evidence_ids"] = []
    evidence = []
    for id_, level, text, refs in CLAIMS:
        source_refs = [reference(*ref) for ref in refs]
        for ref in source_refs:
            lines = (ROOT / ref["path"]).read_text(encoding="utf-8").splitlines()
            assert 1 <= ref["start_line"] <= ref["end_line"] <= len(lines)
            for member in index["selected_members"]:
                if member["extracted_path"] == ref["path"]:
                    member["evidence_ids"].append(id_)
        evidence.append({"id": id_, "level": level, "finding": text, "references": source_refs})
    index["evidence"] = evidence
    build_maps = []
    for label, project_rel, central_file in [
        ("chassis", C+"MDK-ARM/Balanced-infantry.uvprojx", "chassis_central_index.json"),
        ("gimbal", G+"MDK-ARM/sentry.uvprojx", "gimbal_central_index.json")]:
        central = load(central_file)
        names = {i["member"] for i in central["members"]}
        lower_names = {i.lower() for i in names}
        project_member = f"{label}/MDK-ARM/" + Path(project_rel).name
        tree = ET.parse(ROOT / project_rel)
        targets = []
        for target in tree.findall(".//Targets/Target"):
            entries = []
            for group in target.findall("./Groups/Group"):
                for file in group.findall("./Files/File"):
                    source = file.findtext("FilePath", "")
                    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(project_member), source.replace("\\", "/")))
                    entries.append({"group": group.findtext("GroupName"),
                                    "file_name": file.findtext("FileName"), "project_path": source,
                                    "normalized_member": normalized,
                                    "present_exact_case": normalized in names,
                                    "present_case_insensitive": normalized.lower() in lower_names,
                                    "include_in_build_override": file.findtext("./FileOption/CommonProperty/IncludeInBuild")})
            targets.append({"target_name": target.findtext("TargetName"),
                            "device": target.findtext("./TargetOption/TargetCommonOption/Device"),
                            "compiler": target.findtext("pCCUsed"), "entries": entries})
        build_maps.append({"archive": label, "central_index": central_file,
                           "members": len(central["members"]),
                           "root_license_names": [n for n in names if re.match(r"(?i)^"+label+r"/(license|copying|notice)(\.[^/]*)?$", n)],
                           "targets": targets})
    dump("build_entry_map.json", build_maps)
    index["review_bounds"] = {
        "outer_central_members": index["member_count"],
        "nested_central_counts": {p["archive"]: p["members"] for p in build_maps},
        "linear_mpc_central_members": len(load("LinearMPC.jl-main_central_index.json")["members"]),
        "selected_member_count": len(index["selected_members"]),
        "selected_raw_bytes": sum(i["member_bytes"] for i in index["selected_members"]),
        "selected_utf8_bytes": sum(i["extracted_bytes"] for i in index["selected_members"]),
        "source_read_method": "host read tool; glob/grep for discovery; Python only ZIP metadata/extraction/checks",
        "large_nested_archives_persisted": False,
        "excluded_learned_data": ["chassis/algorithm/knn_model.h", "chassis/algorithm/knn_impact_model.h"],
        "not_opened_nested_archives": ["Futile/KNN.zip", "Futile/leso.zip", "matlab/matlab.zip"],
        "not_inspected": ["PCB epro2/images", "draft images", "prebuilt firmware/debug artifacts", "unrelated directories/credentials"]}
    index["target_context_from_parent_not_independently_verified"] = {
        "provenance": "Parent message during this audit; historical model read performed by parent only. Not SPR facts or current hardware verification.",
        "joint_motors": "DM8009P x4", "voltage_v": 24,
        "joint_peak_nm": 40, "joint_continuous_nm": 20, "joint_internal_reduction": 9,
        "wheel_motors": "DM3519 x2 with replacement total reduction 15.8:1",
        "wheel_peak_nm": 5.775909774, "wheel_continuous_nm": 2.59175, "wheel_radius_m": 0.0625,
        "uncalibrated": ["torque-speed envelope", "armature", "current physical BSP/protocol/sign/zero bindings"]}
    index["evidence_status"] = {"source_present": True, "build_configuration_present": True,
                                "firmware_compiled_this_audit": False, "firmware_executed": False,
                                "bench_tested": False, "hil_tested": False,
                                "flashed": False, "simulated": False, "trained": False,
                                "portable_hal": "declarations_only_not_implemented_or_compiled",
                                "codec_vectors": "Python arithmetic only: 15 checks pass, not wire or C ABI proof"}
    index["limitations"] = [
        "No physical board/motor/protocol configuration observation; no target firmware build.",
        "Source-only absence claims are bounded to indexed names, selected text and current Keil entries.",
        "KNN learned tables/centroids intentionally not extracted, so classifier calibration/domain remains unaudited.",
        "Upstream MPC templates/author deployment statement do not prove active chassis integration or realtime tails.",
        "GB18030 source transcoded to UTF8 with unchanged line structure; raw and extracted SHA256 are both recorded.",
        "No firmware/flash/SSH/simulation/training/Git/parent-task actions performed."]
    index["errors"] = {"raw_log": "ERRORS.jsonl", "raw_log_bytes": (ROOT/"ERRORS.jsonl").stat().st_size,
                       "summary": "AUDIT_ERRORS.md"}
    dump("SPR_SOURCE_INDEX.json", index)
    raw_size = (ROOT / "ERRORS.jsonl").stat().st_size
    validation = {"original_archive_unchanged": True, "selected_file_hashes_verified": len(index["selected_members"]),
                  "evidence_ranges_verified": sum(len(i["references"]) for i in evidence),
                  "index_parses": True, "raw_zip_operation_error_bytes": raw_size,
                  "codec_checks": load("codec_vectors_spr.json")["checks_passed"],
                  "target_compilation_attempted": False, "toolchain_inventory": load("toolchain_inventory.json")}
    checked_links = 0
    for markdown_name in ("SPR_DEPLOYMENT_AUDIT.md", "AUDIT_ERRORS.md"):
        markdown = (ROOT / markdown_name).read_text(encoding="utf-8")
        for link in re.findall(r"\]\(<([^>]+)>\)", markdown):
            if link.startswith(("https://", "http://")):
                continue
            filename, _, fragment = link.partition("#")
            destination = (ROOT / filename).resolve()
            assert destination.is_file(), (markdown_name, link)
            if fragment:
                match = re.fullmatch(r"L(\d+)(?:-L(\d+))?", fragment)
                if match:
                    first = int(match.group(1))
                    last = int(match.group(2) or first)
                    assert 1 <= first <= last <= len(destination.read_text(encoding="utf-8").splitlines()), link
            checked_links += 1
    validation["markdown_local_links_verified"] = checked_links
    dump("validation_results.json", validation)
    deliverables = ["SPR_DEPLOYMENT_AUDIT.md", "SPR_SOURCE_INDEX.json", "portable_hal_proposal.h", "codec_vectors_spr.json", "validation_results.json", "AUDIT_ERRORS.md", "ERRORS.jsonl"]
    dump("deliverable_manifest.json", {"files": [{"path": name, "bytes": (ROOT/name).stat().st_size, "sha256": sha(ROOT/name)} for name in deliverables]})
    print(json.dumps({"validation": validation, "review_bounds": index["review_bounds"],
                      "build_summary": [{"archive": m["archive"], "members": m["members"],
                                         "root_license_names": m["root_license_names"],
                                         "targets": [{"name": t["target_name"], "entries": len(t["entries"]),
                                                      "missing_case_insensitive": [e["normalized_member"] for e in t["entries"] if not e["present_case_insensitive"]]}
                                                     for t in m["targets"]]} for m in build_maps]}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        (ROOT / "validation_error.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
