#!/usr/bin/env python3
"""Small CPU imports and official action encoder shape check, no pretrained load."""
import argparse
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import uuid

os.environ.update(CUDA_VISIBLE_DEVICES='', NVIDIA_VISIBLE_DEVICES='none',
                  OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                  HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  HF_HUB_DISABLE_IMPLICIT_TOKEN='1', HF_HUB_DISABLE_TELEMETRY='1')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'))
    args=p.parse_args()
    src=args.root/'source'
    sys.path.insert(0,str(src))
    rec=dict(epoch=time.time(), kind='CPU_IMPORT_AND_TINY_SYNTHETIC_NOT_GPU_ADMISSION',
             imports={}, no_model_weights_loaded=True, authored_hardware_CUDA_queries=False,
             no_PhysX_no_PPO_no_rollout=True, archive_status='PENDING_ROOT_GIT')
    code=0
    try:
        import torch
        # CPU checks must not query actual GPU state through dependency imports.
        # These process-local stubs never touch the live training interpreter.
        torch.cuda.is_available=lambda:False
        torch.cuda.device_count=lambda:0
        def no_cuda_init(*args,**kwargs):
            raise RuntimeError('CUDA initialization forbidden in CPU preparation')
        torch.cuda.init=no_cuda_init
        torch.cuda._lazy_init=no_cuda_init
        rec['CUDA_query_stubs']='is_available=False; device_count=0; initialization rejected'
    except Exception as exc:
        rec['torch_preimport']=dict(status='FAILED_PRESERVED',error_type=type(exc).__name__)
        code=1
    for name in ('torch','torchvision','torchaudio','diffsynth','accelerate','transformers',
                 'yaml','numpy','omegaconf','imageio','pyarrow','PIL','einops',
                 'safetensors','cv2','scipy','sklearn','lpips','skimage','decord',
                 't2z.config','t2z.chunks','t2z.groups','t2z.metadata','t2z.data'):
        try:
            module=importlib.import_module(name)
            rec['imports'][name]=dict(status='IMPORTED_CPU', version=getattr(module,'__version__',None))
        except Exception as exc:
            rec['imports'][name]=dict(status='FAILED_PRESERVED', error_type=type(exc).__name__)
            code=1
    try:
        import torch
        torch.set_num_threads(1)
        # Direct file import avoids top-level pipeline construction and all weights.
        file=src/'wan_video_action/models/wan_video_action_encoder.py'
        spec=importlib.util.spec_from_file_location('official_tiny_action_encoder',file)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        encoder=mod.WanVideoActionEncoder(action_dim=14,dim=16).cpu()
        action=torch.zeros(1,41,14,device='cpu',dtype=torch.float32)
        with torch.no_grad():
            context,modulation=encoder.encode_ti2v2(action)
        assert tuple(context.shape)==(1,41,16)
        assert tuple(modulation.shape)==(1,11,16)
        assert torch.isfinite(context).all().item() and torch.isfinite(modulation).all().item()
        # It is an interface check, not H1 action semantics or physical validation.
        rec['tiny_official_action_encoder']=dict(status='PASS_CPU_SHAPES_ONLY',
            input=list(action.shape),context=list(context.shape),modulation=list(modulation.shape),
            H1_adapter_validated=False, weights_loaded=False)
    except Exception as exc:
        rec['tiny_official_action_encoder']=dict(status='FAILED_PRESERVED',error_type=type(exc).__name__)
        code=1
    outdir=args.root/'receipts'
    outdir.mkdir(parents=True,exist_ok=True)
    out=outdir/f'{time.time_ns()}_CPU_IMPORT_{uuid.uuid4().hex[:8]}.json'
    rec['status']='PASS_CPU_ONLY' if code==0 else 'FAILED_OR_DEPENDENCY_MISSING'
    with out.open('x') as stream:
        json.dump(rec,stream,indent=2)
    print(json.dumps(dict(receipt=str(out),status=rec['status'])))
    return code


if __name__=='__main__':
    sys.exit(main())
