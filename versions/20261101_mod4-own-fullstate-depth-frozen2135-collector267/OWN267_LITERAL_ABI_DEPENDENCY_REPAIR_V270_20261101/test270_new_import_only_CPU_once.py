from pathlib import Path
import hashlib,json,os,sys,time,types
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;S=N/'source';R=N/'reports';rng=torch.random.get_rng_state().clone()
with(R/'ROOT270_NEW_IMPORT_ONLY_CPU_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),raw_models_SDK_GPU_remote=0),f)
pkg=types.ModuleType('supermimic_wheel_leg_v3');pkg.__path__=[str(S/'native')];sys.modules[pkg.__name__]=pkg;sys.path.insert(0,str(S/'code'))
from supermimic_wheel_leg_v3 import geometry
import native_layout270
from measured_state224_v268 import MeasuredStateLayout268
from predicted_literal_frame268 import predicted_literal_frame
from jump194_boundary import LiteralJump194
layout=MeasuredStateLayout268(geometry,native_layout270);assert layout.packed_dim==224 and layout.native.auxiliary_dim==151
assert torch.equal(rng,torch.random.get_rng_state())and not torch.cuda.is_initialized()
report=R/'ROOT270_NEW_LAYOUT_IMPORT_CPU_RETURNED.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),scope='New layout dependency import, no old fixture, numeric dataset, model or optimizer',CUDA_initialized=False,global_RNG_unchanged=True),f,indent=2)
files=json.loads((N/'SOURCE270_FILES_BEFORE_IMPORT_CPU.json').read_bytes())['files']
for p in(report,R/'ROOT270_NEW_IMPORT_ONLY_CPU_CONSUMED.json',N/'SOURCE270_FILES_BEFORE_IMPORT_CPU.json'):files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
idx=N/'INDEX270_DATASET_CPU_SOURCE_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='FROZEN_LAYOUT_ONLY_REPAIR_NEW267_RAW_CPU_PURPOSE',epoch=time.time(),files=files),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest())))
