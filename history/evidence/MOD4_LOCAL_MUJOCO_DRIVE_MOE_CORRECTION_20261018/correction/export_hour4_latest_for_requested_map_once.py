from pathlib import Path
import sys,json,time,hashlib,traceback
import numpy as np,torch,onnx,onnxruntime as ort
B=Path(__file__).resolve().parent;W=B.parent;D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
sys.path.insert(0,str(W/'mod4-onnx-mujoco-launcher'))
from export_latest_moe import ManualMoE,SOURCES
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    torch.set_num_threads(2)
    report=json.loads((W/'MOD4_THREE_GPU_HOUR4_CONTINUATION_20261018/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    assert report['passed_all_three_whole_final_models_CPU']
    sources=dict(SOURCES)
    for role,key in [('H1','h1'),('E2','e2'),('E3','recovery')]:
        row=report['experts'][key]['final'];sources[role]=(Path(row['local_path']),row['SHA'])
    ck={};index={}
    for role,(p,digest) in sources.items():
        assert H(p)==digest;ck[role]=torch.load(p,map_location='cpu',weights_only=False)
        index[role]=dict(path=str(p),bytes=p.stat().st_size,sha256=digest,iteration=ck[role].get('iter'))
    model=ManualMoE(ck).eval();p=D/'latest_moe_hour4_20261018.onnx';assert not p.exists()
    torch.onnx.export(model,torch.zeros(1,35),str(p),input_names=['observation'],output_names=['action'],
        dynamic_axes={'observation':{0:'batch'},'action':{0:'batch'}},opset_version=18,dynamo=False)
    graph=onnx.load(str(p));graph.graph.output[0].type.tensor_type.shape.dim[1].dim_value=6
    onnx.checker.check_model(graph);onnx.save(graph,str(p))
    x=np.random.default_rng(20261018).normal(0,.1,(350,35)).astype(np.float32)
    x[:,3]=1.25;x[:,7:10]=[0,0,-1];x[:,28:35]=np.eye(7,dtype=np.float32)[np.arange(len(x))%7]
    with torch.no_grad():expected=model(torch.from_numpy(x)).numpy()
    session=ort.InferenceSession(str(p),providers=['CPUExecutionProvider']);actual=session.run(None,{'observation':x})[0]
    error=float(np.max(np.abs(expected-actual)));assert error<=1e-4 and np.isfinite(actual).all(),error
    meta=dict(schema_version=1,manual_moe=True,role='latest_manual_moe_hour4',onnx_sha256=H(p),
        sources=index,input={'name':'observation','shape':['batch',35]},output={'name':'action','shape':['batch',6]},
        routing={'normal':'unchanged gate148 E0/W35 argmax','mode4':'H1','mode3':'E3','player_mode6':'E2 with normal-mode observation'},
        latest_closed_cohort='fourth three-GPU hour',not_five_way_learned_gate=True,whole_six_action_no_averaging=True,
        parity_clipped_action_max_abs_error=error,parity_bound=1e-4,rows=350,skill_qualification=False)
    p.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (B/'reports/LATEST_HOUR4_MOE_FOR_FULLMAP_EXPORTED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),onnx_path=str(p),bytes=p.stat().st_size,**meta),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(exported=str(p),parity_max=error)))
if __name__=='__main__':
    try:main()
    except BaseException:
        (B/f'reports/HOUR4_MOE_EXPORT_ORIGINAL_ERROR_{time.time_ns()}.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
