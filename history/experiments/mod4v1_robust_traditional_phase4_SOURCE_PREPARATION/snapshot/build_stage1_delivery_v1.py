"""Package a stable source/evidence cut, no tests/physics/compile/Git.
Explicit module allowlist, never scan external worktrees/assets/personal files.
"""
from pathlib import Path
import hashlib,json,zipfile,datetime
R=Path(__file__).resolve().parent;D=R/'DELIVERY_STAGE1_20261102_V1';D.mkdir(exist_ok=False)
TOP='MOD4v1_Traditional_Stage1_V1'
modules=[
'SPR_AUDIT/portable_control_v3_current','SPR_AUDIT/portable_core_v2_kinematics',
'SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1','SPR_AUDIT/ACTIVE_BOX_QP_V3',
'SPR_AUDIT/portable_spin_h2_v1','SPR_AUDIT/portable_fsm_detector_v1',
'SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1']
diagnostic=['FSM_DETECTOR_V1','CONTACT_PROXY_NOMINAL_V1','DYNAMIC_COM_MOTION_V1',
'INTEGRATED_COM_WINDOW_V1','RAW2K_COM_WINDOW_V1','ROUGH_POSTURE_CAUSAL_V1']
anchors={
'SPR_AUDIT/portable_control_v3_current/INDEX.json':'51cfc25a956539557144208900ab238a3573c63ded0dd3fde4be6ded06c37a09',
'SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/INDEX.json':'6f123646715090474cc49e33f8b2f2827afd113133fc6cf1e2281f9e1bd097ef',
'SPR_AUDIT/ACTIVE_BOX_QP_V3/INDEX.json':'dac32d84d2d4bf0c27b73ef4f8860661b0030874ca52d9b91f486317fa562fbc',
'SPR_AUDIT/portable_spin_h2_v1/INDEX.json':'704e2df0742c62ef89af5b4c721fb487f540025c0846881407070c73d06a295a',
'SPR_AUDIT/portable_fsm_detector_v1/INDEX.json':'40d3adbfad47b6d42a61486fd425cf1e52b6f95b20f246a25e081d2e42aae12a',
'SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/INDEX.json':'0e6ac92a54529e9d9ebc81d45647e2889e27c62fdb898fc02b87f2dacc3817ee',
'RAW2K_COM_WINDOW_V1/INDEX.json':'90384a4b94b43772d7969f17e9cb9a5247509469e19a3882d06e424bbf9d0cd2'}
for name,expected in anchors.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==expected,name
nm=json.loads((R/'SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/VALIDATION.json').read_bytes())
assert nm['failures']==0 and nm['rows']==3717 and nm['total_native_host_checks']==84531
fsm=json.loads((R/'SPR_AUDIT/portable_fsm_detector_v1/VALIDATION.json').read_bytes())
assert fsm['max_numeric_error']==0 and fsm['native_failures']==0
start='''# MOD4v1 传统控制保底 — 阶段性交付包 V1

先读 [当前进度与未完成项](<reports/STAGE1_DELIVERY_PROGRESS_20261102.md>)。

## 交付重点

- C3：V4估计器 + 实际P25 + 独立失效/输出gate，带C2纯FK依赖。
- ASQP：真正active-set boxQP；原生C MPC supervisor直接in-process调用，并保留独立C3 fallback。
- 原生C FSM：None/unknown、时钟、持续窗、hard inhibit/reset与动作默认unbound。
- H2：自转反馈的数学C移植；不是完整发送/启停换向资格。
- 另附已封存的COM/接触proxy/shadow与粗糙失效分析，只作诊断证据，不是可信触地或自动动作许可。

## 入口

1. `SPR_AUDIT/portable_control_v3_current/README.md`
2. `SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/README.md`
3. `SPR_AUDIT/portable_fsm_detector_v1/README.md`
4. `C_P25_SPEC625_H4_V1/PROTOCOL.json`
5. `HARDWARE_BINDING_CHECKLIST.md`

源码本身保持原字节。可单独取用FSM/MPC模块中的source_bundle.zip；相关C代码依赖也按原sibling结构放在本包。

## 使用等级

本包可用于代码审查、host数学/接口联调、板级适配与HIL准备；不是可刷整车固件。原生C MPC的valid/fallback不是发送许可，默认未知接触不能被当作0N。跳跃/预测腾空/非normal/接触许可未绑定时MPC必须显式disabled，最终输出还需caller与driver独立准入。

`BUILD_C_CORES_ONLY.ps1`仅编译host对象的便捷入口，本次打包未执行它；没有BSP链接、BIN或刷写。目标M4/M7的原编译事实/依赖以各模块BUILD_RECEIPT/OBJECT_SUMMARY为准，软件double/libm与目标时序待板级验证。

## 数据与包的边界

本包是源码/验证资料的精选快照，不是完整历史仓库、模型mesh或机器人raw数据镜像。大文件与预构建host EXE/DLL不随本源码包提供，MANIFEST列出遗漏及原因；原数字test/raw/INDEX路径保留历史引用，不保证都在此ZIP内。完整物理重跑需原模型资产、原工作区依赖及相应DR环境。已有host adapter程序在原工程中，包内提供其源码与构建收据。

NATIVE_C_MPC_SUPERVISOR与RAW2K_COM_WINDOW在本次cutoff前已经真正seal；仍BLOCKED的ASQP production stdio、尚未运行的world-leg实验、R39实验控制代码不混作baseline。R39结果仅作进度证据。

此包/新模块目前PH4pending；PH3 Git tag截止R34。当前Goal继续，不把这份阶段包当整车最终防线已毕业。
'''
build=r'''param([string]$CC="gcc",[string]$OutputName="build_core_only")
$ErrorActionPreference="Stop"
$root=$PSScriptRoot
$dest=Join-Path $root $OutputName
if(Test-Path -LiteralPath $dest){throw "Choose a new output directory; preserve existing artifacts."}
New-Item -ItemType Directory -Path $dest | Out-Null
$sources=@(
"SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c",
"SPR_AUDIT/portable_control_v3_current/pc3_estimator.c",
"SPR_AUDIT/portable_control_v3_current/pc3_controller.c",
"SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c",
"SPR_AUDIT/ACTIVE_BOX_QP_V3/active_box_qp.c",
"SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c",
"SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_model.c",
"SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.c",
"SPR_AUDIT/portable_spin_h2_v1/sh2_controller.c",
"SPR_AUDIT/portable_spin_h2_v1/sh2_pipeline.c"
)
foreach($relative in $sources){
 $inputPath=Join-Path $root $relative
 $outputPath=Join-Path $dest ((Split-Path $relative -Leaf)+".o")
 & $CC -std=c99 -O2 -Wall -Wextra -Werror -pedantic -Wvla -fno-fast-math -ffp-contract=off -c $inputPath -o $outputPath
 if($LASTEXITCODE -ne 0){throw "Compilation failed: $relative"}
}
Write-Output "Host objects only. No firmware, BSP, actuator I/O or hardware qualification."
'''
(D/'00_START_HERE.md').write_text(start,encoding='utf-8')
(D/'BUILD_C_CORES_ONLY.ps1').write_text(build,encoding='utf-8')
selected={};omitted=[]
for directory in modules+diagnostic:
    base=R/directory;assert base.is_dir(),directory
    for p in sorted(base.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(R).as_posix();size=p.stat().st_size
        reason=None
        if '__pycache__'in p.parts or p.suffix.lower()in('.pyc','.exe','.dll','.pdb'):reason='not portable source delivery: cache or host executable/debug binary'
        elif size>8*1024*1024:reason='large artifact omitted; original producer/seal metadata retained'
        elif directory in diagnostic and p.suffix=='.jsonl':reason='diagnostic row stream omitted; source and summary/index included'
        if reason:omitted.append(dict(path=rel,bytes=size,reason=reason));continue
        selected[rel]=p
explicit=[
'TASK_SCOPE.md','HARDWARE_BINDING_CHECKLIST.md','nominal_gain_v1.json','sensor_core_v4.py','ground_controller_v4.py',
'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','NORMAL_P25_HOLDOUT_V1/PROTOCOL.json',
'C_P25_SPEC625_H4_V1/PROTOCOL.json','C_P25_SPEC625_H4_V1/run_c_h4_frozen_v1.py',
'reports/STATE14_SCHEMA_ERRATUM.md','reports/R34_C_H4_INDEPENDENT_FACTS.json',
'reports/R36_HEADING_TRAIN_FACTS.json','reports/R36_HEADING_TRAIN_FACTS.md',
'reports/R12_SPIN_H2_FACTS.json','reports/R12_SPIN_H2_FACTS.md',
'reports/STAGE1_DELIVERY_PROGRESS_20261102.md','batches/r39_minihop4/PROTOCOL.json','batches/r39_minihop4/BATCH_RESULT.json']
for rel in explicit:assert (R/rel).is_file(),rel;selected[rel]=R/rel
for name in('00_START_HERE.md','BUILD_C_CORES_ONLY.ps1'):selected[name]=D/name
manifest=dict(kind='STAGE1_SOURCE_AND_QUALIFICATION_DELIVERY_NOT_FIRMWARE',created_at=datetime.datetime.now().astimezone().isoformat(),
 source_root=str(R),stable_modules=modules,diagnostic_only_modules=diagnostic,seal_anchors_verified=anchors,
 includes_native_MPC_supervisor_sealed=True,physics_during_packaging=0,new_tests_or_compilations_during_packaging=0,
 hardware_qualified=False,full_robot_release=False,whole_mpc_robot_closedloop_qualified=False,
 Git_state='PH4_PENDING_NEW_LOCAL_DELIVERY_NOT_IN_PH3',omitted=omitted,files=[])
archive=D/'MOD4v1_Traditional_Stage1_20261102_V1.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    for rel,p in sorted(selected.items()):
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();z.writestr(TOP+'/'+rel,raw)
        manifest['files'].append(dict(path=rel,bytes=len(raw),SHA256=sha))
    blob=json.dumps(manifest,indent=2,ensure_ascii=False).encode('utf-8')
    z.writestr(TOP+'/PACKAGE_MANIFEST.json',blob)
(D/'PACKAGE_MANIFEST.json').write_bytes(blob)
with zipfile.ZipFile(archive)as z:
    assert z.testzip()is None
    archive_paths=set(z.namelist())
    for rel,p in selected.items():assert TOP+'/'+rel in archive_paths
    # Verify the direct, in-bundle C include closure; system headers remain toolchain-owned.
    import re,posixpath
    closure=[]
    for rel in selected:
        if Path(rel).suffix not in('.c','.h','.inc'):continue
        text=z.read(TOP+'/'+rel).decode('utf-8',errors='replace')
        for target in re.findall(r'^\s*#\s*include\s*"([^"]+)"',text,re.M):
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(rel),target))
            # Historical attempts may have generated absolute refs; only current top-level core closure is a required gate.
            current=any(str(Path(rel).parent).replace('\\','/')==m for m in modules)
            if current:assert TOP+'/'+resolved in archive_paths,(rel,target,resolved)
            closure.append(dict(source=rel,include=target,resolved=resolved,in_package=TOP+'/'+resolved in archive_paths,current_top_level=current))
checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
(D/'SHA256SUMS.txt').write_text(checksum+'  '+archive.name+'\n',encoding='utf-8')
receipt=dict(kind='DELIVERY_PACKAGE_CREATED_AND_ZIP_CRC_VALIDATED',archive=str(archive),bytes=archive.stat().st_size,
 SHA256=checksum,payload_files=len(selected),omitted_files=len(omitted),seal_anchors_verified=len(anchors),
 current_C_include_closure_verified=True,include_records=len(closure),zip_crc_check_pass=True,
 no_physics_no_tests_no_compile_no_Git=True,progress_report=str(R/'reports/STAGE1_DELIVERY_PROGRESS_20261102.md'))
(D/'PACKAGE_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
