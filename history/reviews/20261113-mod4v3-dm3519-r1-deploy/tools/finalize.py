"""Freeze final source identity, validation, original-ZIP diffs and delivery ZIP."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FW=ROOT/'firmware'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def files():
    # Exclude generated object trees, toolchains, .git, and full upstream models.
    for folder in ('firmware','upper','docs','tests','tools','model','reports'):
        base=ROOT/folder
        for p in sorted(base.rglob('*')):
            if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts:continue
            rel=p.relative_to(ROOT)
            if folder=='firmware' and 'standard_tpye_c' in rel.parts:continue
            if folder=='firmware' and p.suffix.lower() in ('.uvguix','.uvoptx','.bak'):continue
            yield p
    for p in sorted(ROOT.glob('*')):
        if p.is_file() and p.suffix in ('.json','.md') and p.name not in ('DELIVERY_MANIFEST.json','DELIVERY_ZIP.json','ARTIFACT_INDEX.json'):
            yield p
    refs=ROOT/'reference'
    for p in sorted(refs.glob('*.json')):yield p
    for p in sorted((refs/'damiao').rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.json','.pdf','.txt','.png','.md','.py','.h','.c'):yield p

if __name__=='__main__':
    inputs=load('SOURCE_INPUTS.json')
    model=ROOT/'model';model.mkdir(exist_ok=True)
    old=Path(r'F:\RMPOLAR-RL\mod4v3_gas200_stand_test_20261113')
    for src,dest in [('bundle/model/policy.onnx','policy.onnx'),('bundle/config/deployment_contract.json','deployment_contract.json')]:
        shutil.copyfile(old/src,model/dest)
    identity=json.loads((old/'SOURCE_IDENTITY.json').read_text(encoding='utf-8'))
    write(model/'SELECTED_POLICY.json',identity)
    runtime=Path(identity['asset'])/'runtime_config.json'
    cfg=json.loads(runtime.read_text(encoding='utf-8'))
    names=('left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint')
    write(model/'MODEL_ZERO_REFERENCE.json',dict(user_choice='authored model initial pose / zero Newton displacement',source=str(runtime),source_SHA256=sha(runtime),policy_order=names,absolute_MJCF_q=[cfg['initial_joint_positions'][n] for n in names],images_source=str(old.parent/'mod4v3_limit_fold_pose_20261113'),encoder_zero_measured=False))
    origin=Path(identity['checkpoint_archive'])
    unchanged=[]
    with zipfile.ZipFile(origin) as z:
        for name in ('mod4_runtime.c','mod4_runtime.h','mod4_contract.h','policy_weights.h'):
            member=next(n for n in z.namelist() if n.endswith('/firmware/'+name))
            p=FW/'application/mod4_rl'/name
            assert z.read(member)==p.read_bytes(),name
            unchanged.append(dict(path=str(p),member=member,SHA256=sha(p),byte_identical=True))
    manifest=load('FIRMWARE_PATCHES.json')
    with zipfile.ZipFile(inputs['original_zip']) as z:
        rel='application/chassis/chassis_task.c'
        member=next(n for n in z.namelist() if n.endswith('/'+rel))
        if not any(r['path'].replace('\\','/')==rel for r in manifest):
            manifest.append(dict(path=rel,original_SHA256=hashlib.sha256(z.read(member)).hexdigest()))
        for row in manifest:
            p=FW/row['path'];row['modified_SHA256']=sha(p)
            member=next(n for n in z.namelist() if n.endswith('/'+row['path'].replace('\\','/')))
            assert hashlib.sha256(z.read(member)).hexdigest()==row['original_SHA256']
    write(ROOT/'FIRMWARE_PATCHES.json',manifest)
    builddir=FW/'MDK-ARM/standard_tpye_c'
    for name in ('standard_tpye_c.map','standard_tpye_c.htm'):
        dest=ROOT/'reports/compiler'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(builddir/name,dest)
    for ext in ('hex','axf'):
        dest=ROOT/'binaries'/('MOD4V3_MODEL_ZERO_UNCALIBRATED.'+ext);dest.parent.mkdir(exist_ok=True);shutil.copyfile(builddir/('standard_tpye_c.'+ext),dest)
    report=load('reports/portable_attempt5_model_zero.json');assert report['passed']
    upper=load('reports/upper_attempt1.json');assert upper['passed']
    ros=load('reports/ros_attempt2_gcc13.json');assert ros['passed']
    loops=[load('reports/ros_loopback_'+mode+'_attempt1.json') for mode in ('node','rmcs')]
    assert all(x['passed'] for x in loops)
    log=(ROOT/'reports/keil_attempt6_final.log').read_text(encoding='utf-8',errors='replace')
    assert '0 Error(s), 0 Warning(s)' in log
    sizes=list(map(int,re.search(r'Code=(\d+) RO-data=(\d+) RW-data=(\d+) ZI-data=(\d+)',log).groups()))
    write(ROOT/'VALIDATION_SUMMARY.json',dict(firmware_compile='pass',compiler='ARMCC5.06u6 build750',bytes=dict(code=sizes[0],ro_data=sizes[1],rw_data=sizes[2],zi_data=sizes[3],static_RAM=sizes[2]+sizes[3]),portable_controller=report['controller_tests']['stdout'],golden_vectors=report['golden_policy'],policy_sources_unchanged=unchanged,upper_PTY=upper['passed'],real_ROS_build=ros['passed'],real_ROS_node_loopback=loops[0]['passed'],real_RMCS_plugin_loopback=loops[1]['passed'],hardware_calibration_verified=False,hardware_commands=0,new_training_updates=0,hardware_deadline_measurement='not_run',new_wheel_real_response='not_measured',full_autoaim_camera_gimbal_run='not_run'))
    refs=[]
    for p in sorted((ROOT/'reference').rglob('*')):
        if not p.is_file() or p.is_symlink() or '.git' in p.parts:continue
        # All downloaded official inputs; full upstream checkout pinned by commit.
        if (ROOT/'reference/rmcs_auto_aim_v2') in p.parents:continue
        refs.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=sha(p)))
    write(ROOT/'SOURCE_INDEX.json',dict(original=inputs,selected_policy=identity,upstream_RMCS_commit='a27e3d14c36ef8d780287e154b32ed4a70bbbdc9',official_inputs=refs,official_damiao='https://gitee.com/kit-miao/damiao',manual='reference/damiao/DM-S3519-1EC/说明书/DM-S3519-1EC减速电机（含DM3520-1EC驱动器）使用说明书V1.2.pdf'))
    chosen=sorted(set(files()))+sorted((ROOT/'binaries').glob('*'))
    rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,SHA256=sha(p)) for p in chosen]
    write(ROOT/'DELIVERY_MANIFEST.json',dict(files=rows,self_hash_not_recursive=True,hardware_calibration_verified=False))
    chosen.append(ROOT/'DELIVERY_MANIFEST.json')
    suffix='_'+sys.argv[1] if len(sys.argv)>1 else ''
    archive=ROOT.parent/('MOD4V3_DM3519_R1_DEPLOY_20261113'+suffix+'.zip')
    assert not archive.exists(),'Do not overwrite an earlier delivery.'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in chosen:z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    write(ROOT/'DELIVERY_ZIP.json',dict(path=str(archive),bytes=archive.stat().st_size,SHA256=sha(archive),files=len(chosen),original_inputs_preserved=True))
    print(json.dumps(load('DELIVERY_ZIP.json'),indent=2))
