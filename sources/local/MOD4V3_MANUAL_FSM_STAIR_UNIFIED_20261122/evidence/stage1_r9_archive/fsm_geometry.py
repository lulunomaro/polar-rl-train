"""Geometry and timing shared by the simulator and the independent judge."""
from math import hypot, radians, tan

PHYSICS_DT = .0025
POLICY_SUBSTEPS = 8
SUPPORT_STEPS = 160
TRANSITION_SUPPORT_STEPS = 40
SUPPORT_FORCE_N = 5.
OBLIQUE_SLOPE = tan(radians(22.))


def oblique_edge(lateral, sign):
    return OBLIQUE_SLOPE * sign * lateral


def rm27_profile(west, aa=False):
    floor,offset,lip=(.802,.872,1.602) if west else (.761,.825,1.561)
    # The new A–A fixture uses the brief's 1.0–1.5 m intermediate tread.
    # Published full-field fixtures retain their surveyed collision profile.
    return floor,offset,offset+1.20 if aa else lip


def physx_tire_geometry(plant):
    """Measure the released collision meshes in their wheel-link frames."""
    from pxr import Gf, Usd, UsdGeom, UsdPhysics

    stage = Usd.Stage.Open(str(plant/'assets/robot_physx.usda'))
    scale = UsdGeom.GetStageMetersPerUnit(stage)
    frames = UsdGeom.XformCache()
    geometry = {}
    for side in ('left', 'right'):
        link = f'{side}_wheel_link'
        link_path = f'/Robot/links/{link}'
        wheel = stage.GetPrimAtPath(link_path)
        tire = stage.GetPrimAtPath(f'{link_path}/{side}_tire')
        if not tire.HasAPI(UsdPhysics.CollisionAPI) or not tire.IsA(UsdGeom.Mesh):
            raise ValueError(f'Missing collision mesh for {link}')
        transform = frames.GetLocalToWorldTransform(tire) * frames.GetLocalToWorldTransform(wheel).GetInverse()
        points = [transform.Transform(Gf.Vec3d(point)) for point in UsdGeom.Mesh(tire).GetPointsAttr().Get()]
        geometry[link] = dict(radius_m=scale*max(hypot(point[0], point[2]) for point in points),
                              half_width_m=scale*max(abs(point[1]) for point in points),
                              axle_local=[0., 1., 0.], collision_prim=str(tire.GetPath()))
    return geometry
