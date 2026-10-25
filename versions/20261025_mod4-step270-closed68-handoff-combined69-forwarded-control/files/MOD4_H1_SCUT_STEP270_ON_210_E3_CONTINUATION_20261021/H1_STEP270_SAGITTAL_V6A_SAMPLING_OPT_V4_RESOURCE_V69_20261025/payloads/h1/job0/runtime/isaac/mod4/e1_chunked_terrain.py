"""Exact triangle partition for PhysX cooking; no geometry simplification."""
import hashlib,numpy as np,trimesh
from isaaclab.terrains import TerrainImporter

def chunks(mesh,max_faces=25000):
    if max_faces<=0:raise ValueError('Invalid face partition bound')
    for start in range(0,len(mesh.faces),max_faces):
        faces=np.asarray(mesh.faces[start:start+max_faces],dtype=np.int64)
        vertex_ids,inverse=np.unique(faces,return_inverse=True)
        part=trimesh.Trimesh(vertices=np.asarray(mesh.vertices)[vertex_ids],faces=inverse.reshape(-1,3),process=False)
        # Exact world triangles and winding, not a decimated collision proxy.
        assert np.array_equal(part.vertices[part.faces],np.asarray(mesh.vertices)[faces])
        yield start,part

class ChunkedTerrainImporter(TerrainImporter):
    def import_mesh(self,name,mesh):
        source=hashlib.sha256();partition=hashlib.sha256();rows=[]
        for start,part in chunks(mesh):
            # USD points are float32; compare the same authored precision.
            source.update(np.asarray(mesh.vertices,dtype='<f4')[mesh.faces[start:start+len(part.faces)]].tobytes())
            partition.update(np.asarray(part.vertices,dtype='<f4')[part.faces].tobytes())
            part_name=f'{name}_part{len(rows):04d}'
            super().import_mesh(part_name,part)
            rows.append(dict(name=part_name,faces=len(part.faces),vertices=len(part.vertices),start_face=start))
        assert source.hexdigest()==partition.hexdigest()
        assert sum(p['faces'] for p in rows)==len(mesh.faces)
        self.exact_partition_receipt=dict(pass_=True,source_triangles=len(mesh.faces),collider_count=len(rows),max_faces_per_collider=25000,
            triangle_world_f32_order_sha256=source.hexdigest(),partition_triangle_world_f32_order_sha256=partition.hexdigest(),
            all_faces_and_winding_retained=True,geometry_simplified=False,parts=rows)
