"""Freeze the user-selected Nov12 manual-stair model and its complete recipe."""
from pathlib import Path
import shutil,json,hashlib,sys,importlib.metadata as md
import torch,numpy as np
R=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106')
S=R/'sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112'
V=Path(r'D:/claude2/fangzhen/tmp/rough_v1_local_showcase_20261112')
A=Path(r'D:/claude2/fangzhen/tmp/mod4v3_r3_extract_20261107/MOD4v3_HW300N60_R3')
C=Path(r'D:/claude2/fangzhen/runs3060/mod4v3_play_20261107')
P=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
assert not P.exists(),P
P.mkdir(parents=True)
for d in ['model','training','runtime/core/vendor','plant','viewer','evidence/local_workflow_source','evidence/local_playback','media','tools']:(P/d).mkdir(parents=True,exist_ok=True)
def cp(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cp(S/'weights/model_120m.pt',P/'model/training_checkpoint.pt')
assert sha(P/'model/training_checkpoint.pt')=='7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103'
# Complete saved training sources, effective parameters, launch records and reports.
for file in S.iterdir():
 if file.is_file() and file.suffix in {'.py','.md','.json'}:cp(file,P/'training'/file.name)
shutil.copytree(S/'support',P/'training/support',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(P/'training/evidence').mkdir()
for name in ['STARTUP.json','RESTORE.json','PPO_EFFECTIVE.json','TRAIN_LAUNCH.json','UPLOADED_MANIFEST.json','PINNED_ASSET_FILES_VERIFIED.json','TRAINING_COMPLETION.json','TERRAIN_STARTUP.json','TERRAIN_RESTORED.json','MODEL_ARCHIVE_INDEX.json','EXECUTED_SOURCE_LOCAL_VERIFIED.json','FINAL_GIT_PUSH_RECEIPT.json']:
 if (S/'evidence'/name).exists():cp(S/'evidence'/name,P/'training/evidence'/name)
shutil.copytree(A,P/'plant/MOD4v3_HW300N60_R3',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
cp(Path(r'D:/claude2/fangzhen/tmp/mod4v3_asset/reset_bank.json'),P/'plant/reset_bank.json')
assert sha(P/'plant/MOD4v3_HW300N60_R3/mjcf/scene.xml')=='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f'
# Preserve the existing controller; adapt only input file locations and the spec loader.
for name in ['play_mod4v3.py','play_ppo_flatv1.py','play_ppo_flatv1_control.py']:
 text=(C/name).read_text(encoding='utf8')
 if name=='play_mod4v3.py':
  text=text.replace('REPO = Path(r"D:\\claude2\\fangzhen\\refs\\supermimic_wheelbipe_20261106_repo\\RadiantForever-supermimic_wheelbipe-0bf3456")','REPO = Path(__file__).resolve().parent / "vendor"')
 else:
  text=text.replace('ROOT = Path(r"D:\\claude2\\fangzhen")','ROOT = Path(__file__).resolve().parents[2]')
  replacements={
   'DEFAULT_XML =':'ROOT / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"',
   'DEFAULT_RUNTIME =':'ROOT / "plant/MOD4v3_HW300N60_R3/runtime_config.json"',
   'DEFAULT_SEMANTICS =':'ROOT / "plant/MOD4v3_HW300N60_R3/semantics.json"',
   'DEFAULT_BANK =':'ROOT / "plant/reset_bank.json"',
   'DEFAULT_TEMPLATE =':'HERE / "template_spec.json"',
   'DEFAULT_CKPT =':'ROOT / "model/training_checkpoint.pt"'}
  text='\n'.join((next((key+' '+value for key,value in replacements.items() if line.startswith(key)),line)) for line in text.splitlines())+'\n'
  text=text.replace('template = torch.load(args.template, map_location="cpu", weights_only=False)','template = json.loads(Path(args.template).read_text(encoding="utf-8"))')
 (P/'runtime/core'/name).write_text(text,encoding='utf8')
ref=Path(r'D:/claude2/fangzhen/refs/supermimic_wheelbipe_20261106_repo/RadiantForever-supermimic_wheelbipe-0bf3456')
shutil.copytree(ref/'supermimic_wheelbipe',P/'runtime/core/vendor/supermimic_wheelbipe',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
cp(ref/'LICENSE',P/'runtime/core/vendor/LICENSE')
def plain(v):
 if isinstance(v,torch.Tensor):return v.detach().cpu().tolist()
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [plain(x) for x in v]
 return v
spec=plain(torch.load(C/'ckpt_013000.pt',map_location='cpu',weights_only=False)['spec'])
(P/'runtime/core/template_spec.json').write_text(json.dumps(dict(spec=spec),indent=2),encoding='utf8')
(P/'runtime/core/args_for.py').write_text('''from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[2]
def args_for(ckpt):
 return argparse.Namespace(ckpt=ckpt,template=str(Path(__file__).resolve().parent/'template_spec.json'),xml=str(ROOT/'plant/MOD4v3_HW300N60_R3/mjcf/scene.xml'),runtime=str(ROOT/'plant/MOD4v3_HW300N60_R3/runtime_config.json'),semantics=str(ROOT/'plant/MOD4v3_HW300N60_R3/semantics.json'),bank=str(ROOT/'plant/reset_bank.json'),device='cpu',height=.28,vx=.9,vy=0.,wz=1.2,term_height=.18,fall_interval=7.,drop_height=1.,drop_tilt=.75,action_ema=0.,start_fall=False,auto_fall=False,headless=True,steps=0,log_every=100)
''',encoding='utf8')
# The viewer is portable and carries all 750 generated source tiles.
text=(V/'showcase.py').read_text(encoding='utf-8-sig')
text=text.replace("ROOT=Path(r'D:/claude2/fangzhen')","ROOT=Path(__file__).resolve().parents[1]")
text=text.replace("STAGE=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112'","STAGE=ROOT/'training'")
text=text.replace("sys.path.insert(0,str(ROOT/'runs3060/mod4v3_play_20261107'))","sys.path.insert(0,str(ROOT/'runtime/core'))")
text=text.replace('from eval_flatv2_final import args_for','from args_for import args_for')
text=text.replace("CKPT=STAGE/'weights/model_120m.pt'","CKPT=ROOT/'model/training_checkpoint.pt'")
(P/'viewer/showcase.py').write_text(text,encoding='utf8')
cp(V/'manual_control.py',P/'viewer/manual_control.py');cp(V/'MAP_MANIFEST.json',P/'viewer/MAP_MANIFEST.json')
shutil.copytree(V/'tiles',P/'viewer/tiles')
for name in ['full_map_overview.png','full_map_three_panels.png']:cp(V/name,P/'media'/name)
for file in V.iterdir():
 if not file.is_file():continue
 if file.suffix=='.py':cp(file,P/'evidence/local_workflow_source'/file.name)
 elif file.suffix in {'.json','.log','.png'} and file.name not in {'MAP_MANIFEST.json','MANUAL_STATUS.json'}:cp(file,P/'evidence/local_playback'/file.name)
 elif file.suffix=='.mp4':cp(file,P/'media'/file.name)
cp(V/'MANUAL_STATUS.json',P/'evidence/local_playback/USER_MANUAL_STATUS_AT_ARCHIVE.json')
(P/'viewer/.gitignore').write_text('mesh/\n*_hf*.npz\nscene_*.xml\nfull_map_scene.xml\n*STATUS.json\n*.log\n__pycache__/\n',encoding='utf8')
versions={k:md.version(k) for k in ['torch','numpy','mujoco','pynput','Pillow','imageio','imageio-ffmpeg']}
(P/'evidence/REPLAY_VERSIONS.json').write_text(json.dumps(versions,indent=2),encoding='utf8')
(P/'requirements-replay.txt').write_text('\n'.join(k+'=='+v.split('+')[0] for k,v in versions.items())+'\n',encoding='utf8')
(P/'打开手动回放.ps1').write_text('''param([string]$Python = "", [switch]$Map)
if (-not $Python) {
    $localPython = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../.venv/Scripts/python.exe'))
    if (Test-Path -LiteralPath $localPython) { $Python = $localPython } else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$scriptPath = Join-Path $PSScriptRoot 'viewer/showcase.py'
$mode = if ($Map) { 'map' } else { 'play' }
Start-Process -FilePath $Python -ArgumentList @('-X','utf8',('"'+$scriptPath+'"'),'--mode',$mode) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
''',encoding='utf-8-sig')
recipe=json.loads((S/'EFFECTIVE_RECIPE.json').read_text(encoding='utf8'))
identity=dict(display_name='2026年11月12日最牛逼的模型',selection='User-selected named snapshot of the currently playing Rough-v1 120m policy',date='2026-11-12',timezone='Asia/Shanghai',model='model/training_checkpoint.pt',sha256=sha(P/'model/training_checkpoint.pt'),iteration=24482,parent_sha256=recipe['parent_sha256'],source_stage=S.relative_to(R).as_posix(),source_model='weights/model_120m.pt',training_recipe='training/EFFECTIVE_RECIPE.json',training_recipe_sha256=sha(P/'training/EFFECTIVE_RECIPE.json'),nominal_stairs=dict(tile='r00_c00',step_height_m=.165,steps=2,platform_height_m=.33,height_commands_m=[.365,.4],height_ramp_s=2.,forward_command_mps=2.2,forward_start_s=3.,evidence='evidence/local_playback/HEIGHT_STAIRS_RUNUP_CHECK.json'),mechanics='MOD4v3 HW300N60 R3',plant_source_sha256=sha(P/'plant/MOD4v3_HW300N60_R3/mjcf/scene.xml'),interface=dict(actor=35,critic=78,action=6,physics_dt=.0025,pd_dt=.01,policy_dt=.02,closure_guard_m=.002),previous_full_DR_results='training/PAIRED_COMPARISON.md',real_robot_certified=False)
(P/'MODEL_IDENTITY.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
readme='''# 2026年11月12日最牛逼的模型

用户选定名称，保存当前手动播放的 **Rough-v1 120分钟完整PPO权重**，iteration **24482**。模型、完整训练配方、实际训练源码、机械资产、手动回放和原始结果一起保存。

**已复现上台阶：** 本机MuJoCo名义条件，机身高度在2秒内从0.28m调至 **0.365m或0.40m**，3秒后给予 **2.2m/s前进指令**，均登上 **连续两级、每级16.5cm** 的宽台阶，进入 **33cm高平台**。踏面配置1.5m，使用本轮导出的低档宽阶 `r00_c00`。这条记录保留了高度和速度条件。

模型SHA256：`7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103`。

| 需要找什么 | 入口 |
|---|---|
| 当前播放模型本体、完整PPO续训状态 | [model/training_checkpoint.pt](model/training_checkpoint.pt) |
| 模型身份、真实父权重与上阶条件 | [MODEL_IDENTITY.json](MODEL_IDENTITY.json) |
| 全部实际训练参数和DR范围 | [training/EFFECTIVE_RECIPE.json](training/EFFECTIVE_RECIPE.json) |
| 训练方法、启动命令和延迟语义 | [training/TRAINING_RECIPE.md](training/TRAINING_RECIPE.md) |
| 训练源码、地形、奖励与控制实现 | [training/support](training/support) |
| PPO有效参数、启动/恢复/资产原记录 | [training/evidence](training/evidence) |
| 成功上阶的逐步轨迹 | [HEIGHT_STAIRS_RUNUP_CHECK.json](evidence/local_playback/HEIGHT_STAIRS_RUNUP_CHECK.json) |
| 手动方向和高度控制检查 | [MANUAL_CONTROL_CHECK.json](evidence/local_playback/MANUAL_CONTROL_CHECK.json) |
| 本机上下阶和完整地图 | [media](media) |
| 原始完整DR逐地形对照 | [training/PAIRED_COMPARISON.md](training/PAIRED_COMPARISON.md) |

## 手动回放

安装 `requirements-replay.txt` 中的依赖后运行：

```sh
python viewer/showcase.py --mode play
python viewer/showcase.py --mode map
```

Windows也可运行 `打开手动回放.ps1`；加 `-Map` 打开全地图，`-Python` 可指定Python路径。

默认暂停。先点击控制窗，P开始/暂停；W/S前后，A/D转向，松键回零；空格停车；R复位并暂停。Q/E降低/升高站立高度，1/2/3切换0.20/0.28/0.40m，滑条范围0.20～0.42m。面板显示高度指令和离地实测。上台阶、下台阶、各类地形起点与0～9档难度可选择。

当前机械MJCF和全部277个网格、runtime/semantics/reset bank及原有控制框架随包保存。750块地形由本轮Isaac Lab配置、seed66在本机重建；原始网格保存在viewer/tiles。MuJoCo名义可视回放使用2.5ms物理、10ms PD、20ms策略，闭链2mm保护。宽台阶碰撞按各级平台建箱体；其他地形碰撞由5cm射线采样高度场建立。runtime/core/template_spec.json只提供原模板的RobotSpec，策略权重始终读取本包的training_checkpoint.pt。

## 训练配方与能力记录

本模型从Rough-v0 100m、iteration23665、SHA `001028396205e7d44d69ac5af36cdbb638cc26b97daeea29439f84952a58f6e9` 接续。完整DR、20%名义与20%平地独立交叉；11族地形/10档，4096环境、seed66、rollout24、固定学习率3e-5、clip0.1、3个学习epoch；原奖励−1.5e²及指数项1.2；前进指令上限2.2m/s。实际训练7206.600秒、817次PPO更新，每5分钟完整保存。全部细节以effective recipe、启动、恢复和训练日志原件为准。

能力逐条件保存：高度0.365/0.40m、2.2m/s助跑条件已上两级16.5cm；高度0.28m、1m/s的旧录制卡在第一级；直接设高到0.40m而不缓慢调高的短测试也有重置。各次成功和失败都保留在evidence/local_playback。已有完整DR PhysX最高档宽阶上行仍是0/10，见原报告；本快照的命名和本机上阶演示不改写这些结果。原Step6/Step7冻结与R1实车调试包保留。

完整训练历史、原始26份完整PT和后续恢复入口，仍见仓库 `sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112`。本包保存的是当前播放的120分钟点，未新增训练更新。
'''
(P/'README.md').write_text(readme,encoding='utf8')
cp(Path(__file__),P/'tools/assemble_snapshot.py')
print(json.dumps(dict(package=str(P),model_sha256=identity['sha256'],source_tiles=750,training_sources=len(list((P/'training/support').rglob('*.py'))),files=sum(1 for p in P.rglob('*') if p.is_file())),ensure_ascii=False),flush=True)
