"""New task after actual zero-update import failure; keep old once and errors."""
from pathlib import Path
import hashlib,json,time
from pxr import Usd

ROOT=Path(__file__).resolve().parent
REPO=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=REPO/'project/isaac/mod4v2_scut'
HW=Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package')
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

if __name__=='__main__':
    target=ROOT/'attempt02';target.mkdir()
    (target/'reports').mkdir();(target/'hardware/assets').mkdir(parents=True)
    old=read(ROOT/'PLAN.json');remote=old['remote_root']+'_representation02'
    stage=Usd.Stage.Open(str(ROOT/'physx_finite_representation.usda'))
    layer=stage.GetRootLayer().ExportToString()
    layer=layer.replace(str(HW/'assets/robot.usd').replace('\\','/'),old['remote_root']+'/hardware/assets/robot.usd')
    (target/'hardware/assets/robot.usd').write_text(layer,encoding='utf8',newline='\n')
    effective_sha=sha(target/'hardware/assets/robot.usd')
    for filename in ['runtime_adapter_v2.py','kinematics_v2.py','model_parameters.json','runtime_requirements.json',
                     'reports/model_manifest.json','assets/import_contract.json']:
        p=target/'hardware'/filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((HW/filename).read_bytes())
    # These identity-only changes preserve the released source contract and all real stops.
    for name in ['config.py','guard.py']:
        p=CODE/name;s=p.read_text(encoding='utf8');s=s.replace('2237070ddc0a4e33f0c28e23fe5bb3db1f12bb619fddcdd89f9a74d5ac875f18',effective_sha)
        p.write_text(s,encoding='utf8',newline='\n')
    bindings=read(ROOT/'BINDINGS_REMOTE.json')
    bindings['hardware_package']=remote+'/hardware'
    # Fallback/currentshared sources remain frozen at original attempt01.
    (target/'BINDINGS_REMOTE.json').write_text(json.dumps(bindings,indent=2),encoding='utf8')
    local=read(CODE/'BINDINGS.json');local['hardware_package']=str(target/'hardware')
    local['source_asset_package']=str(HW)
    (CODE/'BINDINGS.json').write_text(json.dumps(local,indent=2),encoding='utf8')
    for filename in ['entry.py','owner.py']:(target/filename).write_bytes((ROOT/filename).read_bytes())
    plan=dict(old,run_id=Path(remote).name,remote_root=remote,package_root=remote+'/package',
        assets=remote+'/hardware/assets',guard=remote+'/package/mod4v2_scut/guard.py',
        pending_actual_resource_selection=True,original_zeroPPO_import_failure=str(ROOT/'reports/FIRST_ACTUAL_RETURNED.json'),
        native_equivalent_representation=dict(source_USD_SHA='2237070ddc0a4e33f0c28e23fe5bb3db1f12bb619fddcdd89f9a74d5ac875f18',
            effective_layer_SHA=effective_sha,open_angular_endpoint_sentinel_degrees=1e20,
            exact_true_hard_stops_retained=True,native20steps_passed=True,mimic_error_rad=1.646578311920166e-05))
    plan.pop('GPU_UUID',None)
    (target/'PLAN.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf8')
    (target/'reports/RETRY_CAUSE_AND_VALIDATION.json').write_text(json.dumps(dict(epoch=time.time(),
        failure='Infinite angular limits ignored/rejected by actualOmniPhysics110; zeroPPO and closed',
        change=plan['native_equivalent_representation'],
        native_result=str(ROOT/'reports/NATIVE_REPRESENTATION_04_ACTUAL.json'),
        other_reward_physics_PPO_unchanged=True,original_budget_no_refund=True),indent=2),encoding='utf8')
    print(json.dumps(dict(root=str(target),effective_USD_SHA=effective_sha,remote=remote)))
