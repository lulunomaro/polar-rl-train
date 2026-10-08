"""Create a new authority and admission, preserving all already executed files."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
old=(D/'eval_worker_com_readback_review.py').read_text(encoding='utf8')
t=old.replace('COM_READBACK_REVIEW','SDK_PREPARATION_ISOLATION')
t=t.replace("('clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk',)","('clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk','clk2500-closure-episode-d3-89-d7-chassis-pd-reset-reviewed-sdk')")
t=t.replace('from job_identifier_contract import partition','from job_identifier_contract import partition\nfrom sdk_preparation_isolation import can_hold_preparation')
t=t.replace("    while True:","    held={}\n    while True:",1)
t=t.replace('            for job in jobs:frozen.execute(job)',r'''            for job in jobs:
                if job in held:continue
                try:frozen.execute(job)
                except RuntimeError as error:
                    folder=D/'jobs'/job
                    try:
                        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
                        result=json.loads((folder/'result.json').read_text(encoding='utf8'))
                    except (OSError,ValueError):raise error
                    if str(error)!='Frozen evaluation failed; retained and returned evidence' or not can_hold_preparation(job,manifest,result):raise error
                    held[job]=dict(epoch=time.time(),result=result,reason='Short isolated D7 SDK preparation failed; original raw retained, no pass, no retry. Other proven-scope evaluation continues.')
                    atomic(D/'SDK_PREPARATION_HELD_JOBS.json',held)''')
ast.parse(t);worker=D/'eval_worker_sdk_preparation_isolation.py';assert not worker.exists();worker.write_text(t,encoding='utf8')
old=(D/'admit_com_readback_worker_once.py').read_text(encoding='utf8')
t=old.replace('COM_READBACK_REVIEW','SDK_PREPARATION_ISOLATION').replace('admit_com_readback_worker_once','admit_sdk_preparation_isolation_once').replace('eval_worker_com_readback_review','eval_worker_sdk_preparation_isolation')
t=t.replace("fault=read(D/'JOB_IDENTIFIER_REVIEW_WORKER_ATTENTION.json')","fault=read(D/'COM_READBACK_REVIEW_WORKER_ATTENTION.json')")
t=t.replace('clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk','clk2500-closure-episode-d3-89-d7-chassis-pd-reset-reviewed-sdk')
t=t.replace('assert "assert result[\'D7_nominal_chassis_PD_initial\'][\'static\']" in error','assert "AssertionError: local_COM_pose_xyz_xyzw" in error')
t=t.replace("old='MOD4_AsyncFrozenEvaluation_v15_job_identifier_review'","old='MOD4_AsyncFrozenEvaluation_v15_com_readback_review'")
t=t.replace('MOD4_AsyncFrozenEvaluation_v15_com_readback_review\'\nif','MOD4_AsyncFrozenEvaluation_v15_sdk_preparation_isolation\'\nif')
ast.parse(t);admit=D/'admit_sdk_preparation_isolation_once.py';assert not admit.exists();admit.write_text(t,encoding='utf8')
old=(D/'deploy_com_readback_worker_once.py').read_text(encoding='utf8')
t=old.replace('COM_READBACK_REVIEW','SDK_PREPARATION_ISOLATION').replace('eval_worker_com_readback_review','eval_worker_sdk_preparation_isolation').replace('admit_com_readback_worker_once','admit_sdk_preparation_isolation_once')
t=t.replace("('eval_worker_sdk_preparation_isolation.py','admit_sdk_preparation_isolation_once.py')","('eval_worker_sdk_preparation_isolation.py','admit_sdk_preparation_isolation_once.py','sdk_preparation_isolation.py')")
t=t.replace(" _,o,e=w.exec_command", " _,test_out,test_err=w.exec_command('\"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe\" \"'+W+'/sdk_preparation_isolation.py\"',timeout=20)\n test_raw=test_out.read();test_error=test_err.read();assert test_out.channel.recv_exit_status()==0,(test_raw+test_error).decode(errors='replace')\n (R/'SDK_PREPARATION_ISOLATION_CPU_PASSED.json').write_text(json.dumps(json.loads(test_raw),indent=2),encoding='utf8')\n _,o,e=w.exec_command",1)
ast.parse(t);dest=D/'deploy_sdk_preparation_isolation_once.py';assert not dest.exists();dest.write_text(t,encoding='utf8')
print('Prepared new SDK isolation worker, actual-exit admission and installer; old files retained.')
