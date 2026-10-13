"""Original CPU strict initialXYZ reader, retained after its real rejection."""
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;A=D/'attempts/geometry_bodypos_worldpos_1500_v1/output/INITIAL_ACTUAL.json';B=D/'attempts/geometry_bodyneg_worldpos_1500_v1/output/INITIAL_ACTUAL.json'
a=json.loads(A.read_bytes());b=json.loads(B.read_bytes());pa=dict(a['parameters']);pb=dict(b['parameters']);sa=pa.pop('private_RNG_SHA');sb=pb.pop('private_RNG_SHA')
assert pa==pb and sa==sb and a['q']==b['q'] and a['actual_assignments']==b['actual_assignments'] and a['geometry']==b['geometry']
ar=np.asarray(a['root_xyzw']);br=np.asarray(b['root_xyzw'])
assert np.array_equal(ar[:,:3],br[:,:3]) and np.array_equal(ar[:,7:],br[:,7:])
