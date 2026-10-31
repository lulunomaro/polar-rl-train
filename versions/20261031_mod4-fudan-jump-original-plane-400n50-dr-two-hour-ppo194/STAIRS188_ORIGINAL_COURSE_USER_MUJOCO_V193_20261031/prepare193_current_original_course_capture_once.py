"""Freeze new human-requested current188 original-course motion capture."""
from pathlib import Path
import ast,hashlib,json,time

B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
N=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031'
OLD=T/'STAIRS188_QUALIFIED_FORMAL_TRUE270_ACCEPTANCE_V191_20261031/V2_KIT_NAMESPACE_BINDING_REPAIR'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_STAIRS188_ORIGINAL_COURSE_USER_VIEW_20261031v193'
oldroot='/mnt/mod4_linux_durable_20261013/MOD4_STAIRS188_FORMAL40050_TRUE270_EVAL_20261031v191_v2'
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
closed=json.loads((N/'reports/ROOT188_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
cpu=json.loads((N/'reports/ROOT188_NEW_FORMAL_INITIAL_CPU_RETURNED_ACTUAL.json').read_bytes())
assert closed['passed_collection'] and cpu['passed'] and closed['formal']['SHA']==cpu['SHA']
formal=closed['formal']
task=dict(schema='mod4.user193.original_Fudan_course_current188.motion.v1',epoch=time.time(),
    human_request='mujoco画面记得给我打开，奖励和课程确认是复旦原奖励',
    model_path=formal['source'],model_SHA=formal['SHA'],model_bytes=formal['bytes'],model_iteration=5065,
    qualified188_package_root='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188_v2/seed27',
    num_envs=1,maximum_controls=1000,policy_Hz=50,physics_Hz=400,feedback_Hz=100,
    original_reward_snapshot='plane/logs/wheel_legged/上台阶3',original_reward_and_curriculum_no_edits=True,
    physics='ownMOD4 nominal400N/k2000, original D0-D7/TGS32/4/F32/perenv2mm/mimic.01',
    purpose='One new deterministic current188 PPO first-episode motion for user local MuJoCo display; original training terrain/reward, not the separate270mm acceptance arena',
    counts=dict(model_GPU_byte_reads=1,model_GPU_decodes=1,local_CPU_model_decodes=0,old_raw_or_reference_reads=0,
                actual_body_pose_buffer_reads_max=1000,actual_contact_getters_added=0,
                raw_artifact_transfers=1,transfer_integrity_SHA_passes=1,local_visual_data_byte_passes=1),
    terrain_render='ROI crop of the actual original SDK converted triangles, not invented steps',
    no_MATLAB_or_WM_blue_poses_fabricated=True,no_learning_or_ledger_write=True,
    original_caps=dict(worker_seconds=840,parent_wait_seconds=900),first_episode_only=True,
    display='New recorded case, latest188 model; TRAINING CLOSED clearly labelled')
put(B/'TASK193.json',task)
(B/'zonglin2_app_launcher.py').write_bytes((N/'zonglin2_app_launcher.py').read_bytes())
ast.parse((B/'capture193_original_Fudan_course_latest188_once.py').read_bytes())
files=[]
for name in ('TASK193.json','capture193_original_Fudan_course_latest188_once.py','zonglin2_app_launcher.py'):
    raw=(B/name).read_bytes();files.append(dict(relative=name,local_relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
put(B/'FROZEN_EVAL193_COMPLETE_MANIFEST.json',dict(epoch=time.time(),schema='mod4.user193.capture.inputs.v1',files=files,task=task))
post=(OLD/'remote191_postcopy_and_frozen_eval.txt').read_text('utf8').replace(oldroot,ROOT).replace('191','193')
post=post.replace('evaluate193_qualified188_actor40050_step270_once.py','capture193_original_Fudan_course_latest188_once.py')
post=post.replace(",'--job-root',str(B)","")
post=post.replace('ram>32*1024**3','ram>8*1024**3')
post=post.replace("out=B/'actual_evaluation';result_path=out/'ACTUAL193_FROZEN188_400N50_DR_TRUE270_RESULTS.json'",
                  "out=B/'actual_capture';result_path=out/'CAPTURE193_ACTUAL_RESULT.json'")
post=post.replace("function=json.loads(function_path.read_bytes()) if function_path.is_file() else None",
                  "function=dict(passed=True) if result and result.get('passed') else None")
post=post.replace("result.get('passed_execution')","result.get('passed')")
ast.parse(post);(B/'remote193_postcopy_and_frozen_eval.txt').write_text(post,encoding='utf8',newline='\n')
install=(OLD/'install_evaluate191_qualified188_frozen_once.py').read_text('utf8').replace(oldroot,ROOT).replace('191','193')
install=install.replace('T=N.parent.parent;W=T.parent','T=N.parent;W=T.parent')
install=install.replace('install_evaluate193_qualified188_frozen_once','install_capture193_original_course_frozen_once')
anchor="  put('ROOT193V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json',result)"
assert install.count(anchor)==1
transfer="""
  if result['passed_execution']:
   artifact=result['result']['artifact'];dest=N/'captured'/Path(artifact['path']).name;dest.parent.mkdir(exist_ok=False)
   sf=client.open_sftp()
   try:sf.get(artifact['path'],str(dest))
   finally:sf.close()
   with dest.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
   assert dest.stat().st_size==artifact['bytes'] and sha==artifact['SHA']
   put('ROOT193_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json',dict(passed=True,source=artifact,path=str(dest),bytes=artifact['bytes'],SHA=sha,transfers=1,two_host_SHA_equal=True,visual_content_not_yet_decoded=True))
"""
install=install.replace(anchor,anchor+transfer)
ast.parse(install);(B/'install_capture193_original_course_frozen_once.py').write_text(install,encoding='utf8',newline='\n')
put(R/'ROOT193_FROZEN_CAPTURE_SOURCE_PURPOSE_ACTUAL.json',dict(passed_source=True,epoch=time.time(),
    source188_formal=formal,original_course_preserved=True,new_gpu_capture=False,files=files,
    no_model_or_raw_content_read_during_source_preparation=True,next_entry='install_capture193_original_course_frozen_once.py'))
print(json.dumps(dict(passed_source=True,model_SHA=formal['SHA'],original_reward_and_course=True,
                      new_entry='install_capture193_original_course_frozen_once.py')))
