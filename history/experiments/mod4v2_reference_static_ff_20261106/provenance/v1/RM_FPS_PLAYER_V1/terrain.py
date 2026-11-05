"""CPU-only SCUT-recipe practice arena; not official arena CAD/PhysX equivalence.

build_model('rm_all'|'latest_rm'|'classic_rm'|'flat', difficulty=.5, seed=9001, imu_offset=(.03,0,.04))
returns (MjModel, meta). No simulator step, controller, reset or SDK import.
Custom bars reuse pinned box construction; custom cliff reuses raw height code.
The eight SDK-standard height families have explicitly labelled local adapters.
"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import math
import types
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT.parent / 'mod4v1_experts_fulldr_rm70_20261101/E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4'
MODEL = ROOT / 'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'
MODEL_SHA = '0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
PIN_SHA = '5f444236205f6ab4a56e0c76387b388d5d2d5a7a83ab63386f5cf15ae5b68d0e'
COMMIT = 'b8ff79f3df855faf9dc92f4a282bd80c42649466'
LABELS = {
    'low_speed_stair_for_rm': '低速大台阶（15–35 cm/阶）',
    'tiny_step': 'SCUT 网格横条（2–6 cm）',
    'slope_for_rm_high': '凸金字塔斜坡',
    'inv_slope_for_rm_low': '凹金字塔缓坡 / 坑',
    'high_speed_stair_for_rm': '高速大台阶（15–40 cm/阶）',
    'stair_slope_for_rm_high': '密集凸阶梯',
    'inv_stair_slope_for_rm_low': '密集凹阶梯（浅）',
    'inv_stair_slope_for_rm_high': '密集凹阶梯（深）',
    'plane_for_rm': '9×9 平地区',
    'random_uniform_for_rm': '随机粗糙面',
    'cliff_inv_stair_slope_short_for_rm': '断崖 + 高台内凹阶梯',
}
HORIZONTAL, VERTICAL, TILE, GAP = .1, .005, 9., 2.


def _numbers(values):
    return ' '.join(format(float(x), '.12g') for x in values)


def _geom(wb, name, kind, pos, rgba, **kw):
    return ET.SubElement(wb, 'geom', name=name, type=kind, pos=_numbers(pos),
                         contype='1', conaffinity='2', friction='1 .003 .0001',
                         group='0', rgba=_numbers(rgba), **kw)


def _box(wb, name, bounds, top=0., bottom=-.15, color=(.43, .46, .50, 1.)):
    x0, x1, y0, y1 = bounds
    if not (x1 > x0 and y1 > y0 and top > bottom):
        raise ValueError('Degenerate terrain box')
    return _geom(wb, name, 'box', ((x0+x1)/2, (y0+y1)/2, (top+bottom)/2),
                 color, size=_numbers(((x1-x0)/2, (y1-y0)/2, (top-bottom)/2)))


class _LocalNumpy:
    """Give extracted functions a private legacy RNG, never seed application RNG."""
    def __init__(self, seed):
        self.random = np.random.RandomState(seed)

    def __getattr__(self, name):
        return getattr(np, name)


def _custom_functions(seed):
    source = AUTH / 'pinned_source/height_field.py'
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN_SHA:
        raise ValueError('Pinned SCUT terrain source changed')
    names = {'discretize_size_to_pixels', '_resolve_fixed_or_difficulty_value',
             '_resolve_fixed_or_difficulty_int', '_resolve_int_bounds', '_force_even_count',
             '_symmetric_bar_centers', '_centered_fraction_span', '_resolve_grid_bars_params',
             'mesh_grid_bars_terrain', '_resolve_height_offset_curriculum',
             'cliff_inverted_pyramid_stairs_terrain'}
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes} != names:
        raise ValueError('Missing pinned pure function')
    for node in nodes:
        node.decorator_list = []  # No Isaac config or height-to-mesh SDK wrapper.
    def translation(pos):
        m = np.eye(4); m[:3, 3] = pos
        return m
    def box(size, transform):
        if not np.array_equal(transform[:3, :3], np.eye(3)):
            raise ValueError('Unexpected rotated source box')
        return tuple(map(float, size)), tuple(map(float, transform[:3, 3]))
    env = {'np': _LocalNumpy(seed), 'trimesh': types.SimpleNamespace(
        transformations=types.SimpleNamespace(translation_matrix=translation),
        creation=types.SimpleNamespace(box=box))}
    module = ast.Module(body=[ast.ImportFrom(module='__future__',
        names=[ast.alias(name='annotations')], level=0)] + nodes, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(source), 'exec'), env)
    return env


def _interpolate(p, name, difficulty):
    lo, hi = p[name]
    return float(lo + difficulty*(hi-lo))


def _stairs(p, difficulty):
    """Local regular-grid pyramid adapter, quantized to recipe h/v scales."""
    n = round(TILE/HORIZONTAL); border = round(p.get('border_width', 0.)/HORIZONTAL)
    side = n-2*border; step = max(1, round(p['step_width']/HORIZONTAL))
    platform = round(p['platform_width']/HORIZONTAL)
    height = round(_interpolate(p, 'step_height_range', difficulty)/VERTICAL)
    if p.get('inverted', False):
        height = -height
    inner = np.zeros((side, side), dtype=np.int16)
    start, stop, level = 0, side, 0
    while stop-start > platform:
        start += step; stop -= step; level += height
        if stop <= start:
            break
        inner[start:stop, start:stop] = level
    out = np.zeros((n, n), dtype=np.int16)
    out[border:n-border or None, border:n-border or None] = inner
    return out


def _step_boxes(wb, prefix, heights, x0, y0, color):
    """Merge constant-height cells into solid rectangles; preserve negative pits.

    NO zero-height filler underneath depressions. Riser faces are vertical boxes,
    not the SDK slope-threshold triangle displacement/contact representation.
    """
    active, rectangles = {}, []
    for i in range(heights.shape[0]+1):
        runs = []
        if i < heights.shape[0]:
            row = heights[i]; cuts = np.r_[0, np.flatnonzero(row[1:] != row[:-1])+1, len(row)]
            runs = [(int(a), int(b), int(row[a])) for a, b in zip(cuts[:-1], cuts[1:])]
        present = set(runs)
        for key in list(active):
            if key not in present:
                rectangles.append((active.pop(key), i, *key))
        for key in runs:
            active.setdefault(key, i)
    bottom = float(heights.min())*VERTICAL-.15
    for k, (ia, ib, ja, jb, height) in enumerate(rectangles):
        _box(wb, f'{prefix}_{k}', (x0+ia*HORIZONTAL, x0+ib*HORIZONTAL,
             y0+ja*HORIZONTAL, y0+jb*HORIZONTAL), height*VERTICAL, bottom, color)
    return len(rectangles)


def _continuous_height(key, p, difficulty, seed):
    n = round(TILE/HORIZONTAL)+1
    if key == 'random_uniform_for_rm':
        from scipy.interpolate import RectBivariateSpline
        coarse = max(4, round(TILE/p['downsampled_scale'])+1)
        choices = np.arange(round(p['noise_range'][0]/VERTICAL),
                            round(p['noise_range'][1]/VERTICAL)+1,
                            max(1, round(p['noise_step']/VERTICAL)))
        values = np.random.RandomState(seed).choice(choices, size=(coarse, coarse))
        axis = np.linspace(0., TILE, coarse); fine = np.linspace(0., TILE, n)
        z = np.rint(RectBivariateSpline(axis, axis, values)(fine, fine))*VERTICAL
        b = round(p.get('border_width', 0.)/HORIZONTAL)
        if b:
            z[:b, :] = 0.; z[-b:, :] = 0.; z[:, :b] = 0.; z[:, -b:] = 0.
        return z, 'fixed recipe noise range; seeded cubic-resampled local grid; not SDK byte-equivalence'
    # Local four-face pyramid, flat surrounding border and optional central platform.
    axis = np.linspace(0., TILE, n)
    depth = np.minimum(axis, TILE-axis)-p.get('border_width', 0.)
    max_depth = max(0., (TILE-2*p.get('border_width', 0.)-p['platform_width'])/2)
    ramp = np.clip(depth, 0., max_depth)
    z = np.minimum(ramp[:, None], ramp[None, :])*_interpolate(p, 'slope_range', difficulty)
    if p.get('inverted', False):
        z = -z
    return np.rint(z/VERTICAL)*VERTICAL, 'local four-face pyramid; SDK interpolation/triangulation not reproduced'


def _classic_scene(wb):
    """Copy only direct static world geoms from the user's familiar arena."""
    old_root = Path(r'C:\Users\lulu\Desktop\claude\mjcf\mod4-onnx-mujoco-launcher')
    path = old_root/'model/rm_training_arena.xml'
    source = ET.fromstring(path.read_bytes())
    geoms = source.find('worldbody').findall('geom')
    for original in geoms:
        if original.get('type') == 'plane':
            continue
        if original.get('type') != 'box' or any(k in original.attrib for k in ('mesh', 'hfield', 'material', 'class')):
            raise ValueError('Classic arena requires an additional explicit static-asset adapter')
        item = ET.fromstring(ET.tostring(original))
        item.set('name', 'classic_'+original.get('name'))
        wb.append(item)
    # Read the literal tuple, never import drive_wasd/ONNX/sim_runtime.
    tree = ast.parse((old_root/'drive_wasd.py').read_text(encoding='utf-8-sig'))
    value = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'SPAWNS' for t in n.targets))
    spawns = ast.literal_eval(value)
    keys = ('flat', 'classic_stairs', 'classic_ramp25', 'classic_tunnel',
            'classic_rough', 'classic_fly', 'classic_island', 'classic_barricade416')
    bounds = ((-7., .1, -1., 1.), (-3.2, .2, -3.3, -1.7), (-3.4, .3, 1.7, 3.3),
              (.1, 2.5, -.9, .9), (-5.8, -.8, 4., 5.6), (-5., 2.5, -5.6, -4.),
              (3., 6.3, 1.8, 4.4), (3., 6., -4., -2.))
    if len(spawns) != 8:
        raise ValueError('Unexpected classic spawn list')
    zones = [dict(key=k, label=s[0], spawn=[float(s[1]), float(s[2]), float(s[4])],
                  yaw=float(s[3]), bounds=list(b), authored_vs_adapter='original static boxes; finite floor replaces infinite plane')
             for k, s, b in zip(keys, spawns, bounds)]
    return zones, str(path)


def _latest_scene(wb, assets):
    """Selected 20261023 full-field STATIC meshes/routes; no old robot/runtime."""
    directory = Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023\player')
    scene_path = directory/'rm7v7_latest_moe.xml'
    source = ET.fromstring(scene_path.read_bytes())
    world = source.find('worldbody')
    if any(b.get('name') != 'chassis' for b in world.findall('body')):
        raise ValueError('Latest scene has unhandled nested terrain bodies')
    geoms = world.findall('geom')
    if not geoms or any(g.get('type') != 'mesh' for g in geoms):
        raise ValueError('Latest field changed from the selected static-mesh layout')
    route_path = directory/'routes.json'
    routes = {r['id']: r for r in json.loads(route_path.read_text(encoding='utf-8'))}
    driver_path = directory/'drive_rm7v7_contact_speed_timebase_v2.py'
    tree = ast.parse(driver_path.read_text(encoding='utf-8-sig'))
    order = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == 'ROUTE_KEYS' for t in n.targets)))
    if len(order) != 15 or len(set(order)) != 15 or any(k not in routes for k in order):
        raise ValueError('Unexpected latest player route order')
    by_asset = {(a.tag, a.get('name')): a for a in source.find('asset')}
    ref_attrs = {'mesh': 'mesh', 'hfield': 'hfield', 'material': 'material', 'texture': 'texture'}
    needed = {(kind, g.get(attr)) for g in geoms for attr, kind in ref_attrs.items() if g.get(attr)}
    pending, selected = list(needed), {}
    while pending:
        key = pending.pop()
        if key in selected:
            continue
        a = by_asset[key]; selected[key] = a
        pending += [(kind, a.get(attr)) for attr, kind in ref_attrs.items() if a.get(attr)]
    files, low, high = [], np.array([np.inf, np.inf]), np.array([-np.inf, -np.inf])
    compiler = source.find('compiler')
    for (kind, name), original in selected.items():
        a = copy.deepcopy(original); a.set('name', 'latest_'+name)
        for attr in ref_attrs:
            if a.get(attr):
                a.set(attr, 'latest_'+a.get(attr))
        if a.get('file'):
            subdir = compiler.get('meshdir' if kind == 'mesh' else 'texturedir', compiler.get('assetdir', '.'))
            path = (directory/subdir/a.get('file')).resolve()
            if not path.is_relative_to(directory) or not path.is_file():
                raise ValueError('Missing/outside latest static terrain asset: '+str(path))
            a.set('file', str(path)); files.append(str(path))
        if kind == 'mesh' and original.get('vertex'):
            vertices = np.fromstring(original.get('vertex'), sep=' ').reshape(-1, 3)
            low = np.minimum(low, vertices[:, :2].min(axis=0))
            high = np.maximum(high, vertices[:, :2].max(axis=0))
        assets.append(a)
    # Reuse one REAL terrain collider's name for the legacy bridge lookup.
    # It is not a new ground plane and does not cover all CAD support contacts.
    ground_original = None
    for original in geoms:
        g = copy.deepcopy(original)
        for attr in ref_attrs:
            if g.get(attr):
                g.set(attr, 'latest_'+g.get(attr))
        if ground_original is None and int(g.get('contype', '1')) != 0:
            ground_original = g.get('name'); g.set('name', 'ground')
        wb.append(g)
    if ground_original is None or not np.all(np.isfinite([low, high])):
        raise ValueError('Latest terrain has no collision geometry/bounded inline mesh data')
    arena = [float(low[0]), float(high[0]), float(low[1]), float(high[1])]
    zones = []
    for key in order:
        r = routes[key]; points = np.asarray(r['waypoints_m'], dtype=float)
        spawn = [float(v) for v in r['spawn_ground_m']]
        zones.append(dict(key=key, label=r['name_zh'], spawn=spawn, yaw=float(r['spawn_yaw_rad']),
            spawn_surface_normal=r.get('spawn_surface_normal'),
            bounds=[float(points[:, 0].min()-1.), float(points[:, 0].max()+1.),
                    float(points[:, 1].min()-1.), float(points[:, 1].max()+1.)],
            bounds_are_route_display_extent_not_collision_wall=True,
            authored_vs_adapter='exact latest static meshes/masks/transforms; original route xyz/yaw; no added slab'))
    return zones, dict(latest_source=str(scene_path), latest_route_source=str(route_path),
        latest_driver_source=str(driver_path), origin_spawn=zones[0]['spawn'], origin_yaw=zones[0]['yaw'],
        arena_bounds=arena, camera_lookat=[0., 0., .4], camera_distance=27.,
        latest_static_geom_count=len(geoms), latest_static_asset_count=len(selected),
        latest_static_file_assets=files, route_count=len(zones), ground_name_alias_of=ground_original,
        ground_alias_is_not_all_terrain_contact_identity=True, no_flat_floor_added=True,
        user_selected_full_field_mesh_source=True, old_robot_policy_force_yaw_assist_imported=False,
        no_sdk_import=True)


def build_model(scene='rm_all', difficulty=.5, seed=9001, imu_offset=(.03, 0., .04)):
    """Build only. Caller owns robot spawn/reset/control, viewer and physics steps.

    zones[0] is always the safe flat origin. Other spawns are on 2m flat entry
    strips OUTSIDE the terrain footprint, with ground z=0; pits have real depth.
    """
    import mujoco
    difficulty = float(difficulty); seed = int(seed)
    if scene not in ('flat', 'rm_all', 'classic_rm', 'latest_rm') or not math.isfinite(difficulty) or not 0 <= difficulty <= 1:
        raise ValueError('scene must be flat/rm_all/classic_rm/latest_rm and difficulty finite in [0,1]')
    if not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError('seed must fit uint32')
    imu = np.asarray(imu_offset, dtype=float)
    if imu.shape != (3,) or not np.isfinite(imu).all():
        raise ValueError('imu_offset must be finite xyz')
    raw = MODEL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MODEL_SHA:
        raise ValueError('Original MOD4 source identity changed')
    xml = ET.fromstring(raw); wb = xml.find('worldbody'); assets = xml.find('asset')
    robot_before = ET.tostring(wb.find("body[@name='chassis']"))
    constraints_before = [ET.tostring(xml.find(tag)) for tag in ('actuator', 'equality', 'default')]
    xml.find('compiler').set('meshdir', str(MODEL.parent))
    xml.find('option').set('timestep', '.0005')
    # Position is the only requested robot edit; no body/joint/actuator parameters change.
    xml.find(".//site[@name='imu']").set('pos', _numbers(imu))
    for geom in list(wb.findall('geom')):
        if geom.get('name') == 'ground' or geom.get('type') == 'plane':
            wb.remove(geom)
    flat_bounds = ([-50., 50., -50., 50.] if scene == 'flat' else
                   [-15., 15., -8., 8.] if scene == 'classic_rm' else [-3., 3., -23., 23.])
    if scene != 'latest_rm':
        _box(wb, 'ground', flat_bounds, color=(.44, .48, .53, 1.))
    zones = [dict(key='flat', label='平地起点 / 平衡区', spawn=[0., 0., 0.], bounds=flat_bounds)]
    meta = dict(scene=scene, difficulty=difficulty, seed=seed, zones=zones,
                model_source=str(MODEL), model_SHA=MODEL_SHA, physics_dt_s=.0005,
                infinite_ground=False, official_arena_CAD=False, Isaac_PhysX_runtime_equivalence=False,
                origin_spawn=[0., 0., 0.], family_count=0)
    fields = []
    if scene == 'latest_rm':
        latest_zones, latest_meta = _latest_scene(wb, xml.find('asset'))
        zones[:] = latest_zones
        meta.update(latest_meta)
    if scene == 'classic_rm':
        classic_zones, classic_path = _classic_scene(wb)
        zones[:] = classic_zones
        wb.find("geom[@name='ground']").set('friction', '.9 .003 .0001')
        meta.update(classic_source=classic_path, origin_spawn=zones[0]['spawn'],
                    arena_bounds=flat_bounds, camera_lookat=[0., 0., .3], camera_distance=12.,
                    classic_static_only=True, old_robot_policy_and_assist_imported=False,
                    no_sdk_import=True)
    if scene == 'rm_all':
        recipe = json.loads((AUTH/'ROUGH_V1_RESOLVED_RECIPE.json').read_text(encoding='utf-8'))
        definitions = recipe['active_terrain_definitions']
        if recipe['commit'] != COMMIT or set(x['key'] for x in definitions) != set(LABELS):
            raise ValueError('Unexpected eleven-family recipe')
        funcs = _custom_functions(seed)
        # Floor ONLY in entry/corridor strips. Never an arena-wide slab under pits.
        for i, (a, b) in enumerate(((12., 14.), (23., 25.), (34., 36.))):
            _box(wb, f'entry_{i}', (a, b, -23., 23.), color=(.38, .43, .48, 1.))
        for i, (a, b) in enumerate(((-23., -21.), (-12., -10.), (-1., 1.), (10., 12.), (21., 23.))):
            _box(wb, f'aisle_{i}', (3., 34., a, b), color=(.38, .43, .48, 1.))
        for i, definition in enumerate(definitions):
            key = definition['key']; p = definition['parameters']; row, col = divmod(i, 4)
            x0 = 3.+row*11.; cy = (col-1.5)*11.; y0 = cy-4.5
            prefix = f'rm{i:02d}_{key}'
            color = (.38+.08*(i % 3), .42+.06*((i+1) % 3), .43+.05*((i+2) % 3), 1.)
            zone = dict(key=key, label=LABELS[key], spawn=[x0-1., cy, 0.],
                        bounds=[x0-2., x0+9., y0, y0+9.],
                        terrain_bounds=[x0, x0+9., y0, y0+9.],
                        source_class=definition['class'], recipe_parameters=p.copy(),
                        negative_height_filled_by_plane=False)
            if key == 'tiny_step':
                cfg = types.SimpleNamespace(size=(9., 9.), num_horizontal=None, num_vertical=None,
                    bar_width=None, bar_height=None, bar_length_ratio=.95, ground_thickness=.05, **p)
                boxes, origin = funcs['mesh_grid_bars_terrain'](difficulty, cfg)
                for j, (size, pos) in enumerate(boxes):
                    center = (pos[0]+x0, pos[1]+y0, pos[2])
                    _geom(wb, f'{prefix}_{j}', 'box', center, color, size=_numbers(np.asarray(size)/2))
                zone.update(authored_vs_adapter='pinned authored box dimensions/positions; translation only',
                            geom_count=len(boxes), height_range_m=[0., _interpolate(p, 'bar_height_range', difficulty)])
            elif key == 'plane_for_rm':
                _box(wb, prefix, (x0, x0+9., y0, y0+9.), color=color)
                zone.update(authored_vs_adapter='finite 9x9 plane as solid box', geom_count=1, height_range_m=[0., 0.])
            elif 'stair' in key:
                if key.startswith('cliff_'):
                    border = round(p['border_width']/HORIZONTAL)
                    cfg = types.SimpleNamespace(size=(TILE-2*p['border_width'],)*2,
                        horizontal_scale=HORIZONTAL, vertical_scale=VERTICAL,
                        height_offset=None, height_offset_curriculum_scale_by_difficulty=False,
                        height_offset_curriculum_num_levels=11, **p)
                    inner = funcs['cliff_inverted_pyramid_stairs_terrain'](difficulty, cfg)
                    heights = np.zeros((90, 90), dtype=np.int16)
                    heights[border:90-border, border:90-border] = inner
                    detail = 'pinned authored raw cliff function; explicit finite border + vertical-box adapter, not SDK mesh'
                else:
                    heights = _stairs(p, difficulty)
                    detail = 'recipe-faithful local stepped-pyramid grid; vertical solid boxes, SDK source/mesh not reproduced'
                count = _step_boxes(wb, prefix, heights, x0, y0, color)
                zone.update(authored_vs_adapter=detail, geom_count=count,
                            height_range_m=[float(heights.min())*VERTICAL, float(heights.max())*VERTICAL])
            else:
                heights, detail = _continuous_height(key, p, difficulty, (seed+i) & 0xFFFFFFFF)
                low, high = float(heights.min()), float(heights.max()); scale = max(high-low, .005)
                field_name = f'hf_{i}'
                ET.SubElement(assets, 'hfield', name=field_name, nrow=str(heights.shape[1]),
                    ncol=str(heights.shape[0]), size=_numbers((4.5, 4.5, scale, .15)))
                _geom(wb, prefix, 'hfield', (x0+4.5, cy, low), color, hfield=field_name)
                fields.append((field_name, np.asarray((heights-low)/scale, dtype=np.float32).T.copy()))
                zone.update(authored_vs_adapter=detail+'; MuJoCo hfield', geom_count=1,
                            height_range_m=[low, high], grid_spacing_m=HORIZONTAL)
            zones.append(zone)
        # The unused twelfth cell is deliberately just another flat practice pad.
        _box(wb, 'last_flat_pad', (25., 34., 12., 21.), color=(.44, .48, .53, 1.))
        meta.update(family_count=11, upstream_commit=COMMIT, pinned_source_SHA=PIN_SHA,
                    recipe_source=str(AUTH/'ROUGH_V1_RESOLVED_RECIPE.json'), grid_columns=4,
                    arena_bounds=[-3., 36., -23., 23.], camera_lookat=[9., 0., 0.],
                    camera_distance=22., no_sdk_import=True)
    # Check unrequested robot changes structurally, not with another simulation.
    check_robot = ET.fromstring(robot_before)
    check_robot.find(".//site[@name='imu']").set('pos', _numbers(imu))
    built_robot = ET.fromstring(ET.tostring(wb.find("body[@name='chassis']")))
    if ET.tostring(check_robot) != ET.tostring(built_robot):
        raise AssertionError('Unexpected robot body edit')
    if constraints_before != [ET.tostring(xml.find(tag)) for tag in ('actuator', 'equality', 'default')]:
        raise AssertionError('Unexpected constraint/actuator/default edit')
    model = mujoco.MjModel.from_xml_string(ET.tostring(xml, encoding='unicode'))
    if scene == 'latest_rm':
        before = int(model.opt.disableflags)
        model.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_MULTICCD)
        meta.update(source_global_collision_option_adopted=True,
                    source_collision_option='mjDSBL_MULTICCD',
                    collision_option_source='rm7v7_contact_stable_candidate_v1.py:8',
                    flag_before=before, flag_after=int(model.opt.disableflags))
    for name, values in fields:
        h = model.hfield(name).id; adr = int(model.hfield_adr[h]); n = values.size
        model.hfield_data[adr:adr+n] = values.ravel()
    meta.update(terrain_geom_count=sum(1 for g in wb.findall('geom')), compiled_nbody=int(model.nbody),
                compiled_ngeom=int(model.ngeom), compiled_nhfield=int(model.nhfield),
                heightfield_data_set_before_viewer_creation=True, new_physics_steps=0)
    return model, meta
