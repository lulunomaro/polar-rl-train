"""Independent geometry checks; no production environment or policy is launched."""
import json
from pathlib import Path

import numpy as np
from pxr import Gf, Usd, UsdGeom, UsdPhysics

from rough_ground import TerrainTriangles, VerticalMeshOracle, clear_vertical_placement


def mesh(stage, path, points, faces):
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(points)
    m.CreateFaceVertexCountsAttr([3] * len(faces))
    m.CreateFaceVertexIndicesAttr(np.asarray(faces).reshape(-1).tolist())
    UsdPhysics.CollisionAPI.Apply(m.GetPrim())
    UsdPhysics.MeshCollisionAPI.Apply(m.GetPrim()).CreateApproximationAttr("none")
    return m


def plane(stage, path, x0, x1, y0, y1, z):
    return mesh(stage, path, [(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],
                [(0,1,2),(0,2,3)])


def rejected(func, phrase):
    try:
        func()
    except ValueError as e:
        assert phrase in str(e), str(e)
    else:
        raise AssertionError("Expected rejection: " + phrase)


def main():
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    ground = UsdGeom.Xform.Define(stage, "/World/ground")
    ground.AddTranslateOp().Set(Gf.Vec3d(13, -7, 1.7))
    # Local slope z=0.15x; all rays include both translation and this slope.
    mesh(stage, "/World/ground/slope", [(0,0,0),(2,0,.3),(2,2,.3),(0,2,0)],
         [(0,1,2),(0,2,3)])
    geometry = TerrainTriangles.from_stage(stage)
    oracle = VerticalMeshOracle(geometry)
    starts = np.array([[13.5,-6.5,3],[14.5,-5.5,3],[13,-7,3],[15,-5,3]])
    q = oracle.cast(starts)
    np.testing.assert_allclose(q["height"], [1.775,1.925,1.7,2.0], atol=2e-7)
    np.testing.assert_allclose(q["normal"], np.tile(np.array([-.15,0,1])/np.hypot(.15,1),(4,1)), atol=2e-7)
    assert not oracle.cast([[13.5,-6.5,1.6]])["hit"][0]
    assert not oracle.cast([[13.5,-6.5,3]],max_distance=.5)["hit"][0]
    assert not oracle.cast([[12,-7,3]])["hit"][0]

    # A shelf introduces a height discontinuity; a ray starting below the shelf
    # must keep the real lower surface instead of seeing a fictitious roof.
    plane(stage, "/World/ground/shelf", .9,1.1,0,2,.5)
    oracle = VerticalMeshOracle(TerrainTriangles.from_stage(stage))
    q = oracle.cast([[13.899,-6,3],[13.901,-6,3],[14.0,-6,2.0]])
    np.testing.assert_allclose(q["height"], [1.83485,2.2,1.85],atol=2e-7)
    place = clear_vertical_placement([[-.2,0,-.20],[.2,0,-.23]], [14,-6], 0, oracle)
    np.testing.assert_allclose(place["root_z"], 2.112,atol=2e-7)
    np.testing.assert_allclose(place["minimum_point_clearance"], .002,atol=2e-7)
    # Rotate the complete point cloud: the support footprint changes with yaw.
    rotated = clear_vertical_placement([[-.2,0,-.20],[.2,0,-.23]], [14,-6], np.pi/2, oracle)
    np.testing.assert_allclose(rotated["root_z"], 2.432,atol=2e-7)
    rejected(lambda: clear_vertical_placement([[0,0,-.2]], [12,-7], 0,oracle), "outside actual terrain")

    # Disabled and non-ground colliders cannot silently pollute the ground query.
    disabled = plane(stage, "/World/ground/disabled", 0,2,0,2,10)
    UsdPhysics.CollisionAPI(disabled.GetPrim()).GetCollisionEnabledAttr().Set(False)
    plane(stage, "/World/Robot/visual_ground", 0,2,0,2,20)
    q = VerticalMeshOracle(TerrainTriangles.from_stage(stage)).cast([[14,-6,30]],max_distance=40)
    np.testing.assert_allclose(q["height"],[2.2],atol=2e-7)
    UsdPhysics.CollisionAPI(disabled.GetPrim()).GetCollisionEnabledAttr().Set(True)
    UsdPhysics.MeshCollisionAPI(disabled.GetPrim()).GetApproximationAttr().Set("convexHull")
    rejected(lambda: TerrainTriangles.from_stage(stage), "approximation")
    UsdPhysics.MeshCollisionAPI(disabled.GetPrim()).GetApproximationAttr().Set("none")
    UsdPhysics.RigidBodyAPI.Apply(disabled.GetPrim())
    rejected(lambda: TerrainTriangles.from_stage(stage), "rigid body")
    UsdGeom.SetStageMetersPerUnit(stage, .01)
    rejected(lambda: TerrainTriangles.from_stage(stage), "metres")

    report = {"status":"PASS_CPU_GEOMETRY", "checks":[
        "translated_slope_height_and_normal", "ray_start_below_surface", "max_distance",
        "edge_and_out_of_bounds", "discontinuous_shelf", "lower_surface_below_shelf",
        "complete_point_clearance", "yaw_changes_footprint", "disabled_collider_filter",
        "robot_path_exclusion", "reject_convex_approximation", "reject_dynamic_collider",
        "reject_non_metre_stage"],
        "simulation_launched":False, "production_modified":False,
        "runtime_warp_and_physx_comparison":"PENDING",
        "complete_MOD4_reset_FK_and_dynamics":"PENDING"}
    Path(__file__).with_name("GROUND_CPU_VERIFICATION.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
