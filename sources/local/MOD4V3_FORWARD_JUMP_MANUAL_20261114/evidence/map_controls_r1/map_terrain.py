"""Reuse the adjacent player's saved Isaac Lab Rough-v1 terrain meshes."""
from pathlib import Path
import hashlib
import json
import struct
import time
import xml.etree.ElementTree as ET

import mujoco
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/viewer"
MESHES = REPO.parent / "tmp/rough_v1_local_showcase_20261112/mesh"
PLANT = REPO / "sources/local/MOD4V3_FORWARD_JUMP_REPAIR_2H_20261114/native_package/mjcf/scene.xml"
CACHE = HERE / "map_cache"
COLORS = [".72 .51 .29 1", ".36 .59 .64 1", ".39 .63 .42 1", ".30 .56 .48 1",
          ".78 .47 .28 1", ".48 .53 .73 1", ".44 .57 .67 1", ".60 .46 .68 1",
          ".48 .52 .56 1", ".64 .61 .39 1", ".70 .41 .48 1"]
NAMES = ["Wide stairs", "Grid bars", "Slope", "Inverse slope", "High stairs", "Shallow stairs",
         "Shallow inverse stairs", "Inverse stairs", "Flat", "Random rough", "Cliff stairs"]


class SavedMap:
    def __init__(self):
        self.manifest = json.loads((SOURCE / "MAP_MANIFEST.json").read_bytes())
        assert self.manifest["rows"] == 10 and self.manifest["cols"] == 75
        assert len(self.manifest["tiles"]) == 750
        self.families = self.manifest["families"]
        self.row, self.family = 3, 0

    def tile(self):
        return next(t for t in self.manifest["tiles"] if t["row"] == self.row
                    and t["family"] == self.families[self.family])

    def center(self, tile):
        return (tile["row"] + .5) * 9. - 45., (tile["col"] + .5) * 9. - 337.5

    def start(self):
        x, y = self.center(self.tile())
        return x - 3.9, y

    def build(self):
        CACHE.mkdir(exist_ok=True)
        scene = CACHE / "full_map_with_robot.xml"
        if scene.exists() and (CACHE / "heightfields.npz").exists() and (CACHE / "BUILD.json").exists():
            return scene
        start = time.time()
        tree = ET.parse(PLANT)
        root = tree.getroot()
        root.set("model", "MOD4v3_IsaacLab_Rough_v1_750_tiles_Space_Jump")
        root.find("compiler").set("meshdir", str(PLANT.parent / "assets"))
        asset, world = root.find("asset"), root.find("worldbody")
        world.remove(world.find("geom[@name='ground']"))
        fields, records = {}, []
        for index, tile in enumerate(self.manifest["tiles"]):
            name, family = tile["name"], self.families.index(tile["family"])
            mesh = MESHES / (name + ".msh")
            original = SOURCE / "tiles" / (name + ".npz")
            with np.load(original) as source:
                vertices = source["vertices"]
                faces = source["faces"]
            raw = mesh.read_bytes()
            nv, nn, nt, nf = struct.unpack("<4i", raw[:16])
            mesh_v = np.frombuffer(raw, dtype="<f4", count=nv*3, offset=16).reshape(nv, 3)
            assert np.array_equal(mesh_v[:len(vertices)], vertices), name
            assert nn == nt == 0 and nf >= len(faces), name
            mesh_f = np.frombuffer(raw, dtype="<i4", count=nf*3, offset=16+nv*12).reshape(nf, 3)
            assert np.array_equal(mesh_f[:len(faces)], faces), name
            x, y = self.center(tile)
            ET.SubElement(asset, "mesh", name="map_"+name, file=str(mesh))
            ET.SubElement(world, "geom", name="map_visual_"+name, type="mesh", mesh="map_"+name,
                          pos=f"{x} {y} 0", contype="0", conaffinity="0", group="1", rgba=COLORS[family])
            if family in (0, 4, 8):
                ET.SubElement(world, "geom", name="map_floor_"+name, type="box", pos=f"{x} {y} -.05",
                              size="4.5 4.5 .05", contype="1", conaffinity="2", group="5", friction=".9 .005 .0001")
                if family != 8:
                    for step, z in enumerate(np.unique(vertices[:, 2])):
                        if z <= 1e-6:
                            continue
                        top = vertices[vertices[:, 2] >= z-1e-6]
                        lo, hi = top[:, :2].min(0), top[:, :2].max(0)
                        center, half = (lo+hi)*.5, (hi-lo)*.5
                        ET.SubElement(world, "geom", name=f"map_step_{name}_{step}", type="box",
                                      pos=f"{x+center[0]} {y+center[1]} {z/2}",
                                      size=f"{half[0]} {half[1]} {z/2}", contype="1", conaffinity="2",
                                      group="5", friction=".9 .005 .0001")
            else:
                previous = MESHES.parent / (name+"_hf_v2.npz")
                if previous.exists():
                    with np.load(previous) as cached:
                        h = cached["h"].copy()
                else:
                    m = mujoco.MjModel.from_xml_string(
                        f'<mujoco><asset><mesh name="t" file="{mesh.as_posix()}"/></asset>'
                        '<worldbody><geom type="mesh" mesh="t"/></worldbody></mujoco>')
                    d = mujoco.MjData(m)
                    mujoco.mj_forward(m, d)
                    h = np.empty((181, 181), dtype=np.float32)
                    ray, direction = np.array([0., 0., 10.]), np.array([0., 0., -1.])
                    geomid = np.zeros(1, dtype=np.int32)
                    grid = np.linspace(-4.5, 4.5, 181)
                    for iy, py in enumerate(grid):
                        for ix, px in enumerate(grid):
                            ray[0] = np.clip(px+1.7e-5, -4.5+2e-4, 4.5-2e-4)
                            ray[1] = np.clip(py+2.9e-5, -4.5+3e-4, 4.5-3e-4)
                            dist = mujoco.mj_ray(m, d, ray, direction, None, True, -1, geomid)
                            if dist < 0:
                                # Avoid floating point triangle-edge misses in the ray query.
                                for dx, dy in ((.0007,.0003),(-.0003,.0007),(-.0007,-.0003)):
                                    ray[:2] = np.clip([px+dx,py+dy], -4.499, 4.499)
                                    dist = mujoco.mj_ray(m, d, ray, direction, None, True, -1, geomid)
                                    if dist >= 0:
                                        break
                            if dist < 0:
                                raise ValueError(f"Saved map ray miss: {name} {ix} {iy}")
                            h[iy, ix] = 10.-dist
                fields[name] = h
                low, span = float(h.min()), max(float(np.ptp(h)), .001)
                ET.SubElement(asset, "hfield", name="map_hf_"+name, nrow="181", ncol="181", size=f"4.5 4.5 {span} .2")
                ET.SubElement(world, "geom", name="map_collision_"+name, type="hfield", hfield="map_hf_"+name,
                              pos=f"{x} {y} {low}", contype="1", conaffinity="2", group="5", friction=".9 .005 .0001")
            records.append(dict(name=name, source=str(original), source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                                mesh=str(mesh), mesh_sha256=hashlib.sha256(raw).hexdigest(), geometry_verified=True))
            if (index+1) % 25 == 0:
                print(f"MAP_BUILD {index+1}/750 elapsed={time.time()-start:.1f}s", flush=True)
        np.savez_compressed(CACHE / "heightfields.npz", **fields)
        tree.write(scene, encoding="utf-8", xml_declaration=True)
        receipt = dict(epoch=time.time(), elapsed_s=time.time()-start, rows=10, cols=75, tiles=750,
                       tile_size_m=[9,9], families=self.families, source_manifest=str(SOURCE/"MAP_MANIFEST.json"),
                       source_manifest_sha256=hashlib.sha256((SOURCE/"MAP_MANIFEST.json").read_bytes()).hexdigest(),
                       same_saved_map_as_adjacent_player=True, source_scope=self.manifest["scope"],
                       visual="Original saved meshes, all 750; exact source vertices and faces checked",
                       collision="Existing MuJoCo player conversion: exact wide stair boxes; 5cm sampled heightfields elsewhere",
                       native_plant_sha256=hashlib.sha256(PLANT.read_bytes()).hexdigest(), artifacts=records)
        (CACHE/"BUILD.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
        print("MAP_BUILD_READY "+str(scene), flush=True)
        return scene

    def populate(self, model):
        with np.load(CACHE / "heightfields.npz") as fields:
            for name in fields.files:
                field = model.hfield("map_hf_"+name)
                h = fields[name]
                model.hfield_data[field.adr:field.adr+h.size] = ((h-h.min())/max(float(np.ptp(h)),.001)).ravel()

    def ground(self, model, data, x, y):
        geomid = np.zeros(1, dtype=np.int32)
        dist = mujoco.mj_ray(model, data, np.array([x,y,10.]), np.array([0.,0.,-1.]),
                            np.array([0,0,0,0,0,1], dtype=np.uint8), True, -1, geomid)
        return 10.-dist if dist >= 0 else 0.


if __name__ == "__main__":
    SavedMap().build()
