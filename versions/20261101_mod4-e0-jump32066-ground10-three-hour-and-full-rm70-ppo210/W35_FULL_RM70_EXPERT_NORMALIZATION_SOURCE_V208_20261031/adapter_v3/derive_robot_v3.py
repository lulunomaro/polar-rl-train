"""New source namespace only: actual bound SDK6.1 uses xyzw. No test/run."""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent; PACKAGE=HERE.parent; OLD=PACKAGE/'source'


def main():
    with (HERE/'DERIVE_ROBOT_V3_ONCE.json').open('x') as f:
        json.dump(dict(ID='NEW208_V3_SDK61_XYZW_SOURCE_CORRECTION',epoch=time.time(),
                       source_only=True,model_raw_SDK_test_reads=0),f)
    pairs={
        'reset208.py':('reset208_v3.py',[
            ('# Explicit SDK wxyz encoding for this new pose. The old G3 reset is unedited.',
             '# Actual bound SDK6.1 uses xyzw, as already proven in194-209; preserve SciPy order.'),
            ('xyzw[:, [3, 0, 1, 2]]','xyzw'),
            ("root_quaternion_order='wxyz'","root_quaternion_order='xyzw'")]),
        'terrain208.py':('terrain208_v3.py',[('from reset208 import query, full_reset','from reset208_v3 import query, full_reset')]),
        'command208.py':('command208_v3.py',[('from terrain208 import RoughStraightCommand','from terrain208_v3 import RoughStraightCommand')]),
        'config208.py':('config208_v3.py',[('from command208 import RM70Command208','from command208_v3 import RM70Command208'),
            ('from reset208 import full_reset','from reset208_v3 import full_reset'),
            ('from terrain208 import inactive_rolling','from terrain208_v3 import inactive_rolling')]),
        'base_learning208.py':('base_learning208_v3.py',[('from terrain208 import E1ChassisTerrainEnv,configure_intro','from terrain208_v3 import E1ChassisTerrainEnv,configure_intro')]),
        'evidence208.py':('evidence208_v3.py',[('from base_learning208 import E1TerrainLearningEnv','from base_learning208_v3 import E1TerrainLearningEnv')]),
        'learning208.py':('learning208_v3.py',[('from evidence208 import E1ResetEvidenceLearningEnv','from evidence208_v3 import E1ResetEvidenceLearningEnv')]),
        'train208.py':('train208_v3.py',[('from learning208 import RetentionLearningEnv as Mod4Env','from learning208_v3 import RetentionLearningEnv as Mod4Env'),
            ('from config208 import configure208 as configure_intro','from config208_v3 import configure208 as configure_intro')])}
    rows=[]
    for previous,(name,changes) in pairs.items():
        raw=(OLD/previous).read_bytes(); value=raw.decode('utf8')
        for old,new in changes:
            if value.count(old)!=1:raise ValueError('Unexpected source derivation: '+previous+' '+old)
            value=value.replace(old,new)
        with (HERE/name).open('x',encoding='utf8',newline='\n') as f:f.write(value)
        rows.append(dict(source=str(OLD/previous),source_SHA=hashlib.sha256(raw).hexdigest(),
            output=str(HERE/name),SHA=hashlib.sha256((HERE/name).read_bytes()).hexdigest(),
            bytes=(HERE/name).stat().st_size,changes=changes))
    raw=(PACKAGE/'adapter_v2/robot0pt208_v2.py').read_bytes(); value=raw.decode('utf8')
    for old,new in [('robot0pt208_v2','robot0pt208_v3'),
        ('NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V2','NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V3'),
        ('ROBOT0PT208_V2_TASK','ROBOT0PT208_V3_TASK'),('OWN_MOD4_ROBOT0PT208_V2_ACTUAL','OWN_MOD4_ROBOT0PT208_V3_ACTUAL'),
        ('ORIGINAL_ROBOT0PT208_V2_ERROR','ORIGINAL_ROBOT0PT208_V3_ERROR'),
        ('from config208 import configure208','from config208_v3 import configure208'),
        ('from learning208 import RetentionLearningEnv','from learning208_v3 import RetentionLearningEnv')]:
        value=value.replace(old,new)
    with (HERE/'robot0pt208_v3.py').open('x',encoding='utf8',newline='\n') as f:f.write(value)
    rows.append(dict(source=str(PACKAGE/'adapter_v2/robot0pt208_v2.py'),source_SHA=hashlib.sha256(raw).hexdigest(),
        output=str(HERE/'robot0pt208_v3.py'),bytes=(HERE/'robot0pt208_v3.py').stat().st_size,
        SHA=hashlib.sha256((HERE/'robot0pt208_v3.py').read_bytes()).hexdigest()))
    report=dict(ID='NEW208_V3_SDK61_XYZW_SOURCE_CORRECTION',epoch=time.time(),
        status='SOURCE_ONLY_TARGET_ROBOT_ADMISSION_PENDING',rows=rows,
        original_V1_V2_and_CPU_reports_unchanged=True,
        original_source_error='NEW208 V1 reset reordered SciPy xyzw into wxyz based on an incorrect assumed SDK convention',
        actual_robot_execution_with_wrong_order=False,
        reused_actual_binding='root: original72 SDK6.1/194-209actual binding,mod4_literal_math184_v2.rotation_xyzw and209actual80envxyzw',
        quaternion_scope='Only new root quaternion write in reset208;field/layout have translations only;course has scalar yaw;checkpoint does not reorder quat',
        selected_codec='SciPy Rotation.as_quat() unchanged xyzw for actual bound SDK6.1',
        physical_guards_and_original_Q_bank_unchanged=True,
        local_tests=0,PT_NPZ_USD_raw_SDK_GPU_remote_calls=0,
        entry='robot0pt208_v3.py',task_file='ROBOT0PT208_V3_TASK.json',
        task_kind='NEW208_FULL_RM70_OWN_MOD4_ROBOT_ZERO_PT_V3',
        install_all_new_py_under='runtime/isaac/mod4',
        additional_frozen_shared_sources=['course_math208.py','field208.py','launcher208.py','checkpoint208.py'],
        original_base_runtime_and_binary_install_required=True,
        source_error_preserved_for_root_Git=True)
    with (HERE/'INDEX208_ROBOT_XYZW_V3.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    index=HERE/'INDEX208_ROBOT_XYZW_V3.json'
    print(json.dumps(dict(index=str(index),bytes=index.stat().st_size,SHA=hashlib.sha256(index.read_bytes()).hexdigest(),
        robot_worker_SHA=rows[-1]['SHA'])))


if __name__=='__main__':main()
