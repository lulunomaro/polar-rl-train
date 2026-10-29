"""Bake original training USD's visual meshes for the explicitly requested window."""
from pathlib import Path
import json,subprocess,sys,time,traceback
from pxr import Usd,UsdGeom
H=Path(__file__).resolve().parent;T=H.parent;W=T.parent;R=H/'reports'
source=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27/job0/assets/robot.usd'
try:
    original=Usd.Stage.Open(str(source))
    wrapper=H/'DISPLAY_ONLY_ZUP_METER_STAGE.usda'
    assert not wrapper.exists()
    stage=Usd.Stage.CreateNew(str(wrapper))
    stage.GetRootLayer().subLayerPaths.append(source.resolve().as_posix())
    stage.SetMetadata('defaultPrim','Robot')
    UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z);UsdGeom.SetStageMetersPerUnit(stage,1.)
    stage.GetRootLayer().Save()
    report=dict(epoch=time.time(),source_asset=str(source),original_up_axis=str(UsdGeom.GetStageUpAxis(original)),original_meters_per_unit=UsdGeom.GetStageMetersPerUnit(original),authored_up_axis=original.HasAuthoredMetadata('upAxis'),authored_units=original.HasAuthoredMetadata('metersPerUnit'),display_context='Z-up meters matching actual recorded runtime world; no geometry transform',source_asset_not_modified=True,stage=str(wrapper),original_failure='Legacy display converter required asset layer to author units/upAxis. Original runtime has these on the enclosing world.',inline_shell_quote_error='Metadata probe did not execute: SyntaxError unterminated string literal; absent wrapper then refused by Usd.Stage.Open. No original source changed.')
    (R/'DISPLAY_USD_METADATA_CONTEXT_ADAPTATION.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    args=[sys.executable,'-B','-X','utf8',str(W/'mod4-onnx-mujoco-launcher-git/build_usd_display.py'),'--usd',str(wrapper),'--output-dir',str(H/'actual_training_USD_visuals')]
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf8')
    (R/'ORIGINAL_USD_VISUAL_BAKE_STDOUT.log').write_text(result.stdout,encoding='utf8')
    (R/'ORIGINAL_USD_VISUAL_BAKE_STDERR.log').write_text(result.stderr,encoding='utf8')
    assert result.returncode==0,result.stderr
    audit=json.loads((H/'actual_training_USD_visuals/DISPLAY_SOURCE_AUDIT.json').read_bytes())
    assert audit['body_count']==31 and audit['visual_count']>100 and audit['triangles']>100000
    print(json.dumps({k:v for k,v in audit.items() if k!='meshes'}))
except BaseException:
    (R/('TRUE_VISUAL_ASSET_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
