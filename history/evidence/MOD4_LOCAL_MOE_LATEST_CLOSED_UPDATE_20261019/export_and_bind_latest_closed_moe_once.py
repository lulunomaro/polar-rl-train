"""Export the latest closed cohort for the existing requested RM7v7 player."""
from pathlib import Path
import ast, hashlib, json, shutil, sys, time, traceback
import numpy as np
import torch, onnx, onnxruntime as ort

B=Path(__file__).resolve().parent; W=B.parent
D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
G=W/'MOD4_SCUT_FUDAN_SEVENTH_HOUR_20261019'
NAME='latest_moe_scut_fudan_hour7_20261019'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
    p=B/'reports'/name
    with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)

def main():
    (B/'reports').mkdir(exist_ok=True)
    assert not (B/'reports/LATEST_CLOSED_MOE_EXPORT_AND_BIND_ACTUAL.json').exists()
    torch.set_num_threads(2)
    sys.path.insert(0,str(W/'mod4-onnx-mujoco-launcher'))
    from export_latest_moe import ManualMoE,SOURCES
    proof=G/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json'
    report=json.loads(proof.read_bytes());assert report['passed_all_three_whole_final_models_CPU']
    expected={'h1':'a21a82639c332456a7f89c985c838616ab5f8e5771cc71f32894485658ca866a',
              'e2':'dd76c55798ab0f059f168a67cb23b68f90d95fb2b09fab0d119d0ea6d5600c2c',
              'recovery':'6b5215aedd8ef51e8fa4b09fb85b967f0e21203289b025e182e872841c9d79cf'}
    sources={k:v for k,v in SOURCES.items() if k in ('E0','W35','gate148')}
    for role,key in [('H1','h1'),('E2','e2'),('E3','recovery')]:
        row=report['experts'][key];final=row['final']
        assert final['SHA']==expected[key] and final['twohost_complete_SHA'] and row['all_model_runtime_finite']
        sources[role]=(Path(final['local_path']),final['SHA'])
    ck={};index={}
    for role,(p,digest) in sources.items():
        assert H(p)==digest,role
        ck[role]=torch.load(p,map_location='cpu',weights_only=False)
        index[role]=dict(path=str(p),bytes=p.stat().st_size,sha256=digest,iteration=ck[role].get('iter'))
    model=ManualMoE(ck).eval(); output=D/(NAME+'.onnx');assert not output.exists()
    torch.onnx.export(model,torch.zeros(1,35),str(output),input_names=['observation'],output_names=['action'],
        dynamic_axes={'observation':{0:'batch'},'action':{0:'batch'}},opset_version=18,dynamo=False)
    graph=onnx.load(str(output));graph.graph.output[0].type.tensor_type.shape.dim[1].dim_value=6
    onnx.checker.check_model(graph);onnx.save(graph,str(output))
    rng=np.random.default_rng(20261019)
    x=rng.normal(0,.1,(700,35)).astype(np.float32)
    x[350:,:28]*=10; x[:,3]=1.25; x[:,7:10]=[0,0,-1]
    modes=np.arange(len(x))%7; x[:,28:35]=np.eye(7,dtype=np.float32)[modes]
    tx=torch.from_numpy(x)
    with torch.no_grad():
        expected_actions=model(tx).numpy();choices=model.choice(tx).numpy()
        routed=[]
        for i,mode in enumerate(modes):
            role='H1' if mode==4 else 'E3' if mode==3 else 'E2' if mode==6 else ('E0','W35')[choices[i]]
            view=tx[i:i+1] if role in ('H1','E3') else model.normal_view(tx[i:i+1])
            assert torch.equal(model(tx[i:i+1]),model.experts[role](view).clamp(-6,6))
            routed.append(role)
    assert set(routed)=={'E0','W35','H1','E2','E3'}
    session=ort.InferenceSession(str(output),providers=['CPUExecutionProvider'])
    actual=session.run(None,{'observation':x})[0]
    error=float(np.max(np.abs(expected_actions-actual)))
    assert actual.shape==(700,6) and np.isfinite(actual).all() and error<=1e-4,error
    meta=dict(schema_version=1,manual_moe=True,role='latest_closed_scut_fudan_hour7_manual_moe',
        onnx_sha256=H(output),sources=index,input={'name':'observation','shape':['batch',35]},output={'name':'action','shape':['batch',6]},
        observation_semantics='mod4_plain_frame35_v1',latest_closed_cohort='SCUT+Fudan seventh complete hour',
        routing={'normal':'unchanged gate148 E0/W35 argmax','mode4':'H1','mode3':'E3','player_mode6':'E2 with normal-mode observation'},
        deterministic_mean=True,whole_six_action_selection=True,weight_or_action_averaging=False,
        not_a_newly_trained_five_way_gate=True,parity_clipped_action_max_abs_error=error,parity_bound=1e-4,parity_rows=700,
        independent_whole_action_routing_rows=700,routed_roles=sorted(set(routed)),skill_qualification=False,
        closure_proof={'path':str(proof),'SHA':H(proof)},no_remote_transport_or_training_changes=True)
    with output.with_suffix('.json').open('x',encoding='utf8') as f:json.dump(meta,f,ensure_ascii=False,indent=2)
    before={};after={};backup=B/'prechange';backup.mkdir()
    for name in ('rm7v7_moe_sim.py','drive_rm7v7_moe.py','START_WASD.bat','START_RM7V7_MOE.bat','runtime_config.json','current_moe_sim.py'):
        p=D/name;before[name]=H(p);shutil.copy2(p,backup/name)
    sim=D/'rm7v7_moe_sim.py';raw=sim.read_bytes()
    assert raw.count(b'latest_moe_hour4_20261018')==2
    sim.write_bytes(raw.replace(b'latest_moe_hour4_20261018',NAME.encode()))
    driver=D/'drive_rm7v7_moe.py';raw=driver.read_bytes()
    old='第四小时完整 H1跳跃 / E2自旋 / E3恢复 + 原 E0/W35门控'.encode()
    new='SCUT+Fudan 第七小时完整 H1跳跃 / E2自旋 / E3恢复 + 原 E0/W35门控'.encode()
    assert raw.count(old)==1;driver.write_bytes(raw.replace(old,new))
    for name in before:after[name]=H(D/name)
    assert all(before[n]==after[n] for n in before if n not in ('rm7v7_moe_sim.py','drive_rm7v7_moe.py'))
    for name in ('rm7v7_moe_sim.py','drive_rm7v7_moe.py'):ast.parse((D/name).read_text('utf8'))
    save('LATEST_CLOSED_MOE_EXPORT_AND_BIND_ACTUAL.json',dict(epoch=time.time(),status='PASS',onnx_path=str(output),
        bytes=output.stat().st_size,**meta,player_before_SHA=before,player_after_SHA=after,
        exact_changes=['two bundle filename bindings','one displayed cohort label'],old_bundle_preserved=True))
    print(json.dumps(dict(status='PASS',exported=str(output),parity_max=error,roles=sorted(set(routed)))))

if __name__=='__main__':
    try:main()
    except BaseException:
        (B/'reports').mkdir(exist_ok=True)
        save('EXPORT_OR_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
        raise
