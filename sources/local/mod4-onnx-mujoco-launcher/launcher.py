"""Backend used by the native Windows ONNX/MuJoCo launcher."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import mujoco
import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parent
POLICY_DIR = ROOT / "policies"
IMPORTED_DIR = POLICY_DIR / "imported"
DEFAULT_MODEL = ROOT / "model" / "rm_training_arena.xml"
EXPECTED_INPUTS = {
    35: ("observation", "action", "mod4_plain_frame35_v1"),
    175: ("obs_history", "actions", "mod4_term_major_latest_gather_v1"),
}
EXPECTED_OUTPUT = 6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def adjacent_metadata(path: Path) -> Path | None:
    candidates = [path.with_suffix(".json"), path.with_name(path.stem + ".contract.json"),
                  path.with_name(path.stem + "_metadata.json")]
    return next((item for item in candidates if item.is_file()), None)


def validate_policy(path: Path) -> dict:
    path = path.expanduser().resolve()
    if not path.is_file() or path.suffix.lower() != ".onnx":
        raise ValueError("请选择有效的 .onnx 文件")
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    if len(session.get_inputs()) != 1 or len(session.get_outputs()) != 1:
        raise ValueError("策略必须恰好有一个输入和一个输出")
    inp, out = session.get_inputs()[0], session.get_outputs()[0]
    input_width = int(inp.shape[-1])
    if input_width not in EXPECTED_INPUTS or out.shape[-1] != EXPECTED_OUTPUT:
        raise ValueError(f"维度不匹配：{inp.shape} -> {out.shape}；支持 35→6 或 175→6")
    expected_input_name, expected_output_name, semantics = EXPECTED_INPUTS[input_width]
    if inp.name != expected_input_name or out.name != expected_output_name:
        raise ValueError(f"节点名不匹配：输入 {inp.name!r}，输出 {out.name!r}；"
                         f"该维度要求 {expected_input_name}/{expected_output_name}")
    output = session.run([out.name], {inp.name: np.zeros((1, input_width), np.float32)})[0]
    if output.shape != (1, EXPECTED_OUTPUT) or not np.isfinite(output).all():
        raise ValueError(f"零观测推理输出异常：shape={output.shape}, finite={np.isfinite(output).all()}")
    actual_hash = sha256(path)
    metadata_path = adjacent_metadata(path)
    metadata = {}
    if metadata_path:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        declared_input = metadata.get("input_width", metadata.get("input", {}).get("shape", [None, None])[-1])
        declared_output = metadata.get("output_width", metadata.get("output", {}).get("shape", [None, None])[-1])
        if declared_input not in (None, input_width) or declared_output not in (None, EXPECTED_OUTPUT):
            raise ValueError("旁置 JSON 声明的输入/输出维度与 ONNX 不一致")
        declared_semantics = metadata.get("observation_semantics")
        if declared_semantics and declared_semantics != semantics:
            raise ValueError("旁置 JSON 的 observation_semantics 与 ONNX 接口不一致")
        if input_width == 175 and (metadata.get("frame_width"), metadata.get("history_length")) != (35, 5):
            raise ValueError("175 维策略必须声明 frame_width=35、history_length=5")
        declared_hash = metadata.get("onnx_sha256")
        if declared_hash and declared_hash.lower() != actual_hash:
            raise ValueError("旁置 JSON 的 onnx_sha256 与文件内容不一致")
    return {
        "path": str(path), "sha256": actual_hash,
        "input": {"name": inp.name, "shape": inp.shape},
        "output": {"name": out.name, "shape": out.shape},
        "observation_semantics": semantics,
        "zero_action": np.asarray(output[0], dtype=float).round(5).tolist(),
        "metadata_path": str(metadata_path.resolve()) if metadata_path else None,
        "metadata": metadata,
    }


def validate_model(path: Path = DEFAULT_MODEL) -> dict:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"找不到 MJCF：{path}")
    model = mujoco.MjModel.from_xml_path(str(path))
    if model.nu != 6:
        raise ValueError(f"MJCF 执行器数量为 {model.nu}，训练契约要求 6")
    if model.neq < 10:
        raise ValueError(f"MJCF 等式约束只有 {model.neq}，闭链/耦合约束不完整")
    return {"path": str(path), "nq": model.nq, "nv": model.nv, "nu": model.nu,
            "bodies": model.nbody, "geoms": model.ngeom, "equalities": model.neq}


def import_policy(source: Path) -> dict:
    source = source.expanduser().resolve()
    report = validate_policy(source)
    IMPORTED_DIR.mkdir(parents=True, exist_ok=True)
    try:
        already_local = source.is_relative_to(POLICY_DIR.resolve())
    except AttributeError:
        already_local = str(source).lower().startswith(str(POLICY_DIR.resolve()).lower())
    if already_local:
        destination = source
    else:
        destination = IMPORTED_DIR / source.name
        if destination.exists() and sha256(destination) != report["sha256"]:
            destination = IMPORTED_DIR / f"{source.stem}_{report['sha256'][:8]}.onnx"
        if not destination.exists():
            shutil.copy2(source, destination)
        metadata = adjacent_metadata(source)
        if metadata:
            shutil.copy2(metadata, destination.with_suffix(".json"))
    return {"destination": str(destination.resolve()), "validation": validate_policy(destination)}


def emit(payload: dict, code: int = 0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="validate one ONNX and the MJCF contract")
    inspect_parser.add_argument("--policy", type=Path, required=True)
    inspect_parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    import_parser = sub.add_parser("import", help="validate and copy an ONNX into policies/imported")
    import_parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            emit({"status": "PASS", "policy": validate_policy(args.policy),
                  "model": validate_model(args.model)})
        emit({"status": "PASS", **import_policy(args.source)})
    except Exception as exc:
        emit({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, 1)


if __name__ == "__main__":
    main()
