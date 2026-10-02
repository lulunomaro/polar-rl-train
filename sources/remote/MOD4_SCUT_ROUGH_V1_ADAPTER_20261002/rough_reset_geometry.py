"""CPU FK and collision samples from the actual MOD4 USD, for Rough reset audits.

This is geometry evidence only. It neither writes robot state nor establishes
PhysX reset validity, stable wheel support or nonpenetration of continuous solids.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics


def quat_matrix(quat):
    """USD Gf quaternion -> conventional column-vector rotation."""
    w = float(quat.GetReal()); x, y, z = np.asarray(quat.GetImaginary(), float)
    n = np.linalg.norm([w, x, y, z])
    if n < 1e-12:
        raise ValueError('Invalid joint-frame quaternion')
    w, x, y, z = np.array([w, x, y, z])/n
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def frame(position, rotation):
    out = np.eye(4); out[:3, :3] = quat_matrix(rotation); out[:3, 3] = position
    return out


@dataclass
class Joint:
    name: str
    parent: str
    child: str
    kind: str
    axis: int
    frame0: np.ndarray
    frame1: np.ndarray


class CollisionFK:
    def __init__(self, usd_path):
        self.usd_path = Path(usd_path)
        self.stage = Usd.Stage.Open(str(self.usd_path))
        if self.stage is None or UsdGeom.GetStageUpAxis(self.stage) != 'Z':
            raise ValueError('Expected a valid Z-up MOD4 stage')
        if abs(UsdGeom.GetStageMetersPerUnit(self.stage)-1) > 1e-9:
            raise ValueError('Asset geometry must be in metres')
        self.bodies = {str(p.GetPath()): p for p in self.stage.Traverse()
                       if p.HasAPI(UsdPhysics.RigidBodyAPI)}
        self.joints, self.external_joints = [], []
        for p in self.stage.Traverse():
            if not p.IsA(UsdPhysics.Joint):
                continue
            j = UsdPhysics.Joint(p)
            if j.GetExcludeFromArticulationAttr().Get():
                self.external_joints.append(str(p.GetPath())); continue
            if p.IsA(UsdPhysics.RevoluteJoint): kind = 'hinge'
            elif p.IsA(UsdPhysics.PrismaticJoint): kind = 'slide'
            elif p.IsA(UsdPhysics.FixedJoint): kind = 'fixed'
            else: raise ValueError(f'Unsupported tree joint {p.GetPath()}')
            parent, child = j.GetBody0Rel().GetTargets(), j.GetBody1Rel().GetTargets()
            if len(parent) != 1 or len(child) != 1:
                raise ValueError('This robot requires explicit two-body tree joints')
            axis = str(p.GetAttribute('physics:axis').Get() or 'X')
            self.joints.append(Joint(p.GetName(), str(parent[0]), str(child[0]), kind,
                                     'XYZ'.index(axis),
                                     frame(j.GetLocalPos0Attr().Get(), j.GetLocalRot0Attr().Get()),
                                     frame(j.GetLocalPos1Attr().Get(), j.GetLocalRot1Attr().Get())))
        children = [j.child for j in self.joints]
        roots = set(self.bodies)-set(children)
        if len(roots) != 1 or len(set(children)) != len(children):
            raise ValueError('Asset articulation is not a rooted tree')
        self.root = roots.pop()
        self.neutral = self.forward({})
        cache = UsdGeom.XformCache()
        root_world = np.asarray(cache.GetLocalToWorldTransform(self.bodies[self.root])).T
        self.neutral_authored_error = max(float(np.max(np.abs(
            self.neutral[name]-np.linalg.inv(root_world) @
            np.asarray(cache.GetLocalToWorldTransform(p)).T))) for name,p in self.bodies.items())
        if self.neutral_authored_error > 2e-6:
            raise ValueError('Joint-frame FK does not match authored neutral body transforms')
        self.colliders = []
        for p in self.stage.Traverse():
            if not p.HasAPI(UsdPhysics.CollisionAPI): continue
            if not UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get(): continue
            body = p
            while body and str(body.GetPath()) not in self.bodies: body = body.GetParent()
            if not body: raise ValueError('Robot collider without a rigid body')
            local = np.linalg.inv(np.asarray(cache.GetLocalToWorldTransform(body)).T) @ \
                np.asarray(cache.GetLocalToWorldTransform(p)).T
            vertices = self._sample_shape(p)
            points_body = (np.column_stack((vertices, np.ones(len(vertices)))) @ local.T)[:, :3]
            self.colliders.append(dict(path=str(p.GetPath()), body=str(body.GetPath()),
                                       kind=p.GetTypeName(), points_body=points_body,
                                       shape_to_body=local, prim=p))

    def forward(self, positions):
        unknown = set(positions)-{j.name for j in self.joints}
        if unknown or not all(np.isfinite(float(v)) for v in positions.values()):
            raise ValueError(f'Unexpected or nonfinite joint state: {unknown}')
        out = {self.root: np.eye(4)}; pending = self.joints.copy()
        while pending:
            progressed = False
            for j in pending.copy():
                if j.parent not in out: continue
                q = float(positions.get(j.name, 0.)); motion = np.eye(4)
                if j.kind == 'hinge':
                    axis = np.eye(3)[j.axis]
                    k = np.array([[0,-axis[2],axis[1]], [axis[2],0,-axis[0]], [-axis[1],axis[0],0]])
                    motion[:3,:3] = np.eye(3)+np.sin(q)*k+(1-np.cos(q))*(k@k)
                elif j.kind == 'slide': motion[j.axis,3] = q
                elif q != 0: raise ValueError('Fixed joint cannot have a nonzero q')
                out[j.child] = out[j.parent] @ j.frame0 @ motion @ np.linalg.inv(j.frame1)
                pending.remove(j); progressed = True
            if not progressed: raise ValueError('Disconnected/cyclic USD articulation')
        return out

    @staticmethod
    def _sample_shape(p):
        if p.IsA(UsdGeom.Mesh):
            approx = UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get()
            if approx not in (None, 'none', 'convexHull'):
                raise ValueError('Unsupported robot mesh cooking approximation')
            return np.asarray(UsdGeom.Mesh(p).GetPointsAttr().Get(), float)
        if p.IsA(UsdGeom.Cube):
            half = float(UsdGeom.Cube(p).GetSizeAttr().Get())/2
            grid = np.linspace(-half, half, 9)
            uv = np.array(np.meshgrid(grid,grid)).reshape(2,-1).T
            result=[]
            for axis in range(3):
                for side in [-half, half]:
                    pts=np.zeros((len(uv),3));pts[:,axis]=side;pts[:,[i for i in range(3) if i!=axis]]=uv
                    result.append(pts)
            return np.unique(np.concatenate(result),axis=0)
        if p.IsA(UsdGeom.Cylinder) or p.IsA(UsdGeom.Capsule):
            radius=float(p.GetAttribute('radius').Get()); half=float(p.GetAttribute('height').Get())/2
            axis='XYZ'.index(str(p.GetAttribute('axis').Get())); other=[i for i in range(3) if i!=axis]
            theta=np.linspace(0,2*np.pi,64,endpoint=False); result=[]
            for h in [-half,0,half]:
                pts=np.zeros((len(theta),3));pts[:,axis]=h
                pts[:,other[0]]=radius*np.cos(theta);pts[:,other[1]]=radius*np.sin(theta);result.append(pts)
            if p.IsA(UsdGeom.Capsule):
                for phi in np.linspace(-np.pi/2,np.pi/2,17):
                    pts=np.zeros((len(theta),3));pts[:,axis]=np.sign(phi)*half+radius*np.sin(phi)
                    pts[:,other[0]]=radius*np.cos(phi)*np.cos(theta);pts[:,other[1]]=radius*np.cos(phi)*np.sin(theta)
                    result.append(pts)
            return np.concatenate(result)
        raise ValueError(f'Unhandled actual collider shape {p.GetTypeName()}')

    def points(self, positions):
        poses=self.forward(positions); result=[]; labels=[]
        for i,c in enumerate(self.colliders):
            pts=c['points_body']; tf=poses[c['body']]
            result.append(pts@tf[:3,:3].T+tf[:3,3]);labels.extend([i]*len(pts))
        return np.concatenate(result),np.asarray(labels,dtype=np.int32),poses

    def closure_errors(self, positions, contract):
        poses=self.forward(positions); by_name={Path(n).name:p for n,p in poses.items()}
        errors={}
        for name,c in contract['closures'].items():
            anchors=[]
            for side in [0,1]:
                tf=by_name[c[f'body{side}']];anchors.append(tf[:3,:3]@np.array(c[f'anchor{side}_m'])+tf[:3,3])
            errors[name]=float(np.linalg.norm(anchors[0]-anchors[1]))
        return errors


def build_bank(usd, bank_file, contract_file, output):
    model=CollisionFK(usd);bank=json.loads(Path(bank_file).read_text());contract=json.loads(Path(contract_file).read_text())
    if hashlib.sha256(Path(contract_file).read_bytes()).hexdigest()!=bank['contract_sha256']:
        raise ValueError('Pose bank and actual contract fingerprint differ')
    if len(model.joints)!=contract['articulation_joint_count']:
        raise ValueError('Actual joint count differs from contract')
    all_points=[];q=[];heights=[];closure=[];mimic=[]
    for pose in bank['poses']:
        positions=pose['joint_pos'];pts,labels,transforms=model.points(positions)
        all_points.append(pts);q.append([positions.get(j.name,0.) for j in model.joints]);heights.append(pose['root_height_m'])
        closure.append(max(model.closure_errors(positions,contract).values()))
        mimic.append(max(abs(positions[n]+m['gearing']*positions[m['reference_joint']]+m['offset'])
                         for n,m in contract['mimics'].items()))
    if max(closure)>2e-6 or max(mimic)>1e-8:
        raise ValueError('USD FK does not reproduce the legal closed-chain library')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(output,points_root=np.asarray(all_points),collider_ids=labels,
                        q=np.asarray(q),joint_names=np.asarray([j.name for j in model.joints]),root_height=np.asarray(heights))
    receipt=dict(stage='CPU_FK_COLLISION_SAMPLING_ONLY',usd_sha256=hashlib.sha256(Path(usd).read_bytes()).hexdigest(),
                 contract_sha256=bank['contract_sha256'],poses=len(q),bodies=len(model.bodies),tree_joints=len(model.joints),
                 bank_explicit_joints=len(bank['poses'][0]['joint_pos']),
                 omitted_joints_written_zero=[j.name for j in model.joints if j.name not in bank['poses'][0]['joint_pos']],
                 external_closures=len(model.external_joints),colliders=len(model.colliders),points_per_pose=len(labels),
                 neutral_authored_matrix_max_error=model.neutral_authored_error,
                 maximum_closed_chain_fk_error_m=max(closure),maximum_mimic_error_rad=max(mimic),
                 colliders_metadata=[{k:v for k,v in c.items() if k in ['path','body','kind']} for c in model.colliders],
                 sampled_surfaces_not_exact_continuous_collision=True,physx_fk_verified=False,
                 terrain_reset_installed=False,production_modified=False)
    output.with_suffix('.json').write_text(json.dumps(receipt,indent=2))
    return receipt


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--usd',required=True);p.add_argument('--bank',required=True);p.add_argument('--contract',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(build_bank(a.usd,a.bank,a.contract,a.output),indent=2))
