"""CPU fixtures and saved-query crosscheck; no Kit, SSH, GPU, or rerun."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import time
import numpy as np
import represented_native_plane_CPU_component_v1 as component

D = Path(__file__).parent
OUT = D / "reports/REPRESENTED_NATIVE_PLANE_SOURCE_CPU_COMPONENT_V1_REVIEW.json"


def info(path):
    return dict(path=str(path.resolve()), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    assert not OUT.exists(), "Keep original report; do not overwrite."
    manifest = component.source_sha_manifest()
    metadata = dict(
        source_commit=component.SOURCE_COMMIT,
        source_file_sha256=manifest, approved_axis="Z",
        actual_USD_plane=dict(path="/World/ground/geometry/mesh", type="Plane",
                              axis="Z", CollisionAPI=True, RigidBodyAPI_ancestor_paths=[],
                              world_position=[0, 0, 0], world_rotation_xyzw=[0, 0, 0, 1]),
        actual_actor_getter=dict(path="/World/ground/geometry/mesh", ret_val=True,
                                 position=[0, 0, 0], rotation_xyzw=[0, 0, 0, 1]),
    )
    reference = component.represented_plane_from_readonly_metadata(metadata)
    assert reference["normalized_shape_local_rotation_xyzw"] == [0.7071068286895752, 0, 0.7071068286895752, 0]
    assert reference["represented_plane_normal"] == [1.1920928955078125e-7, 0, 1.0000001192092896]
    translated = copy.deepcopy(metadata)
    translated["actual_USD_plane"]["world_position"] = [1, 2, 3]
    translated["actual_actor_getter"]["position"] = [1, 2, 3]
    translated_reference = component.represented_plane_from_readonly_metadata(translated)
    assert translated_reference["represented_plane_offset_d"] != 0
    negatives = []
    for name, change in [
        ("twisted_actor_USD_identity_mismatch", lambda m: m["actual_actor_getter"].update(rotation_xyzw=[0, 0, 1, 0])),
        ("wrong_source_SHA", lambda m: m["source_file_sha256"].update({"NpShape.cpp": "0"*64})),
        ("wrong_commit", lambda m: m.update(source_commit="0"*40)),
        ("wrong_axis", lambda m: m["actual_USD_plane"].update(axis="Y")),
        ("nonstandalone_body", lambda m: m["actual_USD_plane"].update(RigidBodyAPI_ancestor_paths=["/World/ground"])),
        ("getter_failed", lambda m: m["actual_actor_getter"].update(ret_val=False)),
        ("actor_path_mismatch", lambda m: m["actual_actor_getter"].update(path="/Wrong")),
        ("nonfinite_actor", lambda m: m["actual_actor_getter"].update(position=[float("nan"), 0, 0])),
    ]:
        m = copy.deepcopy(metadata); change(m)
        try:
            component.represented_plane_from_readonly_metadata(m)
        except (ValueError, KeyError) as error:
            negatives.append(dict(case=name, rejected=True, error=str(error)))
        else:
            raise AssertionError(name)
    good_hit = dict(position=[0, 0, 0], normal=reference["represented_plane_normal"])
    assert component.compare_actual_hit_readonly(reference, good_hit)["represented_query_within_original_1e6"]
    bad_hit = dict(position=[0, 0, 2e-6], normal=reference["represented_plane_normal"])
    assert not component.compare_actual_hit_readonly(reference, bad_hit)["represented_query_within_original_1e6"]
    negatives.append(dict(case="original_1e6_query_violation", rejected=True))
    module = ast.parse((D / "represented_native_plane_CPU_component_v1.py").read_text(encoding="utf-8"))
    fn = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == "represented_plane_from_readonly_metadata")
    assert not any(isinstance(n, ast.Name) and n.id in ("hit", "hits", "reported_normal") for n in ast.walk(fn))
    query_dir = D / "actual_collections/retention_baseline1aa_flat_1500_v6/1791949743916981900/attempts/retention_baseline1aa_flat_1500_v6/output"
    query_rows, query_files = [], []
    for phase in ("first_physics", "final"):
        p = query_dir / f"QUERY_{phase}_ALLHITS_ACTUAL.json"
        q = json.loads(p.read_text(encoding="utf-8-sig")); query_files.append(info(p))
        assert q["authored_plane"] == dict(path="/World/ground/geometry/mesh", type="Plane", axis="Z", point=[0, 0, 0], normal=[0, 0, 1])
        for row in q["all_rays"]:
            assert len(row["selected_plane_hits"]) == 1
            hit = row["selected_plane_hits"][0]["hit"]
            comparison = component.compare_actual_hit_readonly(reference, hit)
            reconstructed = component.raycast_source_float32(reference, row["origin"], row["direction"])
            query_rows.append(dict(
                phase=phase, env_id=row["env_id"], comparison=comparison,
                source_reconstruction_distance_exact=(reconstructed["distance"] == hit["distance"]),
                source_reconstruction_position_exact=(reconstructed["position"] == hit["position"]),
                authored_Z0_original_1e6=bool(abs(hit["position"][2]) <= 1e-6),
            ))
    report = dict(
        epoch=time.time(), trial="nativePlane_source_CPU_component_only",
        passed_CPU_synthetic_only=True, no_actual_new_backend_pass=True,
        all_fixtures=dict(identity_reference=reference, translated_reference=translated_reference, negatives=negatives),
        source_files=[info(component.SOURCE_ROOT / n) for n in manifest],
        component=info(D / "represented_native_plane_CPU_component_v1.py"),
        reviewer=info(Path(__file__)), query_files=query_files,
        saved_failed_V6_query_crosscheck=dict(
            count=len(query_rows), normal_matches=sum(r["comparison"]["normal_crosscheck_maxabs"] == 0 for r in query_rows),
            distance_exact=sum(r["source_reconstruction_distance_exact"] for r in query_rows),
            position_exact=sum(r["source_reconstruction_position_exact"] for r in query_rows),
            representation_within_original_1e6=sum(r["comparison"]["represented_query_within_original_1e6"] for r in query_rows),
            maximum_representation_error_m=max(r["comparison"]["represented_query_error_m"] for r in query_rows),
            authored_Z0_failure_count=sum(not r["authored_Z0_original_1e6"] for r in query_rows), rows=query_rows,
        ),
        limitations=[
            "Actor identity pose in this CPU replay is an explicit hypothesis based on captured USD identity; actual native getter was not called.",
            "Public 110.1 source branch is version-family evidence; installed 110.1.13+110.1.2 binary is not source/compile bit-exact certified.",
            "Source-derived normal is computed before reading hits; matches are evidence of mechanism, not actual independent shape-local pose capture.",
            "Original V6 fullcase failed authored-Z ground comparison and remains failed/no COMPLETE. This component does not replace that verdict.",
        ], no_SSH_no_GPU_no_PPO_no_installed_edit=True, pending_Git_by_root=True,
    )
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report["saved_failed_V6_query_crosscheck"].items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
