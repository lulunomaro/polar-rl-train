"""Check complete frozen324 package without model reads and save current work."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time
from datetime import datetime,timezone,timedelta
N=Path(__file__).resolve().parent;T=N.parent;D=T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102';R=N/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
index=D/'INDEX324_SOURCE_TASK_CALLERS_FROZEN.json';frozen=read(index)
for row in frozen['files']:
    p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']
task=read(D/'TASK324_FROZEN.json');assert task['worker_SHA']==H(D/'source/worker324.py')
assert H(D/'reference324.npz')==task['reference']['SHA']
for path in D.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
spec=importlib.util.spec_from_file_location('protocol327',D/'teacher_task324.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol);protocol.validate_task(task)
# Generate remote parent solely from its AST assignments and assert actualpaths.
runner=D/'postround325/run325_eval_once_template.py';tree=ast.parse(runner.read_text('utf8'));main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');env={'T':T}
for stmt in main.body:
    if isinstance(stmt,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='parent'for t in stmt.targets):exec(compile(ast.Module(body=[stmt],type_ignores=[]),'<unusedparent327>','exec'),env)
parent=env['parent'];ast.parse(parent)
assert "str(P/'source/evaluate325.py')"in parent and "from contract325 import"in parent and'RESULT325.json'in parent
# The exact CPU320 code maps to324 only through declared naming changes. Use
# normalized syntax to exclude all strings/docstrings and require same logic.
old=read(T/'REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102/reports/CPU320_RESTORED305_H4_REPAIR_NO_STEP.json');assert old['passed']
assert old['synthetic_H4_no_step']['policy_H']==4 and old['synthetic_H4_no_step']['actor_terminal_bootstrap']is False
class Logic(ast.NodeTransformer):
    def visit_Name(self,node):
        node.id=node.id.replace('324','X').replace('320','X').replace('305','X').replace('315','X');return node
    def visit_FunctionDef(self,node):
        node.name=node.name.replace('324','X').replace('320','X').replace('305','X').replace('315','X');return self.generic_visit(node)
    def visit_ClassDef(self,node):
        node.name=node.name.replace('324','X').replace('320','X');return self.generic_visit(node)
    def visit_Constant(self,node):
        if isinstance(node.value,str):node.value='TEXT'
        return node
    def visit_ImportFrom(self,node):
        node.module=node.module.replace('324','X').replace('320','X').replace('305','X').replace('315','X')
        for a in node.names:
            a.name=a.name.replace('324','X').replace('320','X').replace('305','X').replace('315','X')
            if a.asname:a.asname=a.asname.replace('324','X').replace('320','X').replace('305','X').replace('315','X')
        return node
source320=T/'REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102/source/tracking_learner320.py'
left=Logic().visit(ast.parse(source320.read_text('utf8')));right=Logic().visit(ast.parse((D/'source/tracking_learner324.py').read_text('utf8')))
assert ast.dump(left,include_attributes=False)==ast.dump(right,include_attributes=False)
validation=dict(epoch=time.time(),passed=True,INDEX324_SHA=H(index),frozen_files_checked=len(frozen['files']),all_pythons_parse=True,actual_reference_path_exists_hash_matches=True,CPU320_behavior_AST_equal_ignoring_names_reporttext=True,new_checkpoint_reads=0,remoteeval325parent_AST_matches=True,worker_SOURCE_SHA=task['worker_SHA'],modelsource=task['model_SHA'],no_new_GO=True)
put(D/'reports/STATIC327_FULL324_PACKAGE_VALIDATION.json',validation)

probe_root=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102';probe=read(probe_root/'reports/ROOT311_EVALUATION_FULL_RETURNED.json')['result']
wm_root=T/'FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V317_20261102';wm=read(wm_root/'reports/ROOT317_EVALUATION_FULL_RETURNED.json')['result']
other=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_adaptation_snapshot_20261102_021807.json');s=read(other);go=s['files']['GO_PRODUCTION.json']
fmt=lambda v:datetime.fromtimestamp(v,timezone(timedelta(hours=8))).isoformat()
work=dict(epoch=time.time(),status='311_ACTUAL_INIT_NOT_FIX_317_LONG_HORIZON_DRIFT_324_FROZEN_REPAIR_READY_OTHER_WRITER_ACTIVE',
    old_final305=dict(SHA=wm['source_final_SHA'],complete=True,CPU609passed=True,eval308='0/80cross/strict,70orientation10full8s;nativevisualreviewdone',originalfalse_and307recovery_preserved=True),
    actual311=dict(root=str(probe_root),consumed=True,model_reads=0,controls=64,comparison=probe['comparison'],terminations=probe['terminations'],cross=0,strict=0,native_image=str(probe_root/'RECORDED311_NATIVE_FRAMES/ACTUAL311_REFERENCE_TARGET_BODY_POSE_SEQUENCE.png'),natively_reviewed=True,review='default env0pitchesnearstep/env1tipsfarbeforestep;reference40/41advanceclosebuttiltbeforeedge;no cross',interpretation='reference0init plus directplannedq/dqtargets is not a sufficient stability repair. Separate DR draws,not a causal clean single-variable pairedtest; do not adopt it as solved.'),
    diagnosis314=dict(report=str(T/'REFERENCE_LABEL_FEASIBILITY_DIAGNOSIS_V314_20261102/reports/CPU314_EXACT_REFERENCE_LABEL_DIAGNOSIS.json'),model_reads=0,all250times20ms=True,allplannedtargetswithinclip6=True,allsourcejointlimitswithin1e4tolerance=True,posechannelselfcost0=True,terminal_hold_nonzero_velocity_found=True),
    repair315=dict(root=str(T/'REFERENCE_TERMINAL_HOLD_LABEL_REPAIR_V315_20261102'),passedCPU=True,phase0to249unchanged=True,phasegreater249fixedposezeroallvelocitytargets=True,deployed=False,earlyfallcause_not_claimed=True),
    diagnostic316='LocalAST Task-key rejection:missingteacherSHA/wholeCPUreceipt;0networkSDKmodels;originalpreserved',
    actual317=dict(root=str(wm_root),consumed=True,controls=64,ownpairs=5120,physical512_feedback128=True,model_reads=1,normalizer_updates=0,optimizer_steps=0,sourceWM12468unchanged=True,one_step_position_RMSE_m=wm['one_step_position_RMSE_m'],H32_masked_position_RMSE_m=wm['H32_masked_position_RMSE_m'],H32_masked_Rzz_MAE=wm['H32_masked_Rzz_MAE'],H32_masked_motor_q_RMSE_rad=wm['H32_masked_motor_q_RMSE_rad'],horizons=wm['horizons'],samples=wm['samples'],future_depth=False,source='freshactualfinal305actorcontiguousowntransitions,maskbeforereset;firstanchoronly',skill_eval=False,summary_strictzeros_are_placeholders_not_skillmeasurement=True,interpretation='H32actualpositiondrift.340mvsH4.0219m; sufficienttoshowlongrolloutpredictionweakness,notproofgradientfidelityorsinglecause'),
    CPU319=dict(passed=True,checkpointreads1=True,nooptimizerstep=True,H4terminalgradient=29.869930267333984,H4trackinggradient=.5309106707572937,synthetic_fixture_not_actual=True,decision='H4alonewithunchangedterminalvaluegradient not selected'),
    CPU320=dict(passed=True,checkpointreads1=True,nooptimizerstep=True,H4terminalgradient0=True,H4combinedtrackinggradient=.5309106707572937,exactactorcriticSTDallAdam_EMArestored=True,actorAdam48257_critic5317_WM12468=True,synthetic_fixture_not_actual=True),
    unused321='Frozen localreference filename mismatch(reference321expected/reference305actual);rejectedbeforeGO/network;INDEXunchanged. Independent324correctsfilename.',
    next_training=dict(root=str(D),run_id=task['run_id'],task=str(D/'TASK324_FROZEN.json'),INDEX=str(index),INDEX_SHA=H(index),launch=str(D/'launch324_reference_tracking_once.py'),validation=str(D/'reports/STATIC327_FULL324_PACKAGE_VALIDATION.json'),status='UNUSED_READY_WAIT_ORIGINAL_OTHER_OWNER_CLOSE',actorH4=True,WMH32=True,actor_terminal_bootstrap=False,criticonactualTD_EMA=True,allfull305state_preserved=True,reference315resthold=True,finalclassification312included=True,launch_consumed=False,new_GO=False,no_new_budget=True,reference324npz_pathchecked=True),
    postround=dict(script=str(D/'postround325_finalize324_replay_eval_once.py'),index=str(D/'INDEX325_POSTROUND_FOR324_FROZEN.json'),launched=False,bind_after_first=str(D/'bind326_after324_first_and_launch_postround_once.py'),sequence='After actual324FIRST validated, bind326writesexactowner/GO then solelocaltimer to normal900/fullsaveclose/fullCPU/eval325seed9137same27080firstepisodes400controls/nativeposeframes. Nativelyviewimageanddecidecontinuationwithinbudget.'),
    other_writer=dict(local_snapshot=str(other),job=s['job'],pid=1421790,creation=1793556950.73,worker=1421800,worker_creation=1793556951.86,GO=go,GOlocal=fmt(go['learning_started_epoch']),SAVE=fmt(go['save_deadline']),NOMINAL=fmt(go['nominal_end_epoch']),scope='Separate W35MOD4v1singlecanonicalwriter; do not duplicateowner/interfere/clearactive evenGPU1idle',read_local_first=True),
    next='ReadcurrentrootAGENTS/otherlatestlocalfullsaveexit/canonicalreceipt and allknownlocalcontrollers first. IfW35stillownoriginalwriteractive, leave324readyandquiet; no secondowner/watcher. AfteractualW35saveclose and canonicalNone and serialFREE, launchonlyunused324 with exactINDEXSHA viaoriginalfreshresource/authorityadmission. Checkifalreadyconsumedfirst. Thenstatus--labelFIRST_UPDATED;validateFIRST via bind326;solepostround325. Ifnormal/evalfails preserveoriginal and useindependentversion,neverreplayonce.',
    physics='400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/10mmperenvclosure/mimic.01; oldfrozenH1producerassetnotnewMOD4v1adaptation,exactproducerjoinpending',
    budget='originalsinglecanonical3900/save3600/exit300/strictreserve;noincrease/copy/clearactive/refund/secondwriter',
    SSH=dict(last_receipt=str(wm_root/'reports/ROOT317_ALL_SSH_CLOSED_FREE.json'),all_ownedclosed=True,SESSIONrestored=True,serialFREE=True),
    Git=dict(status='PENDING_ACTUAL311_317_H4REPAIR_PHASE_UNIQUE_RECORD',phase='mod4-init311-paired317-short-h4-tracking-repair324',prior307='d80297d27edd78be7d473f9a98a1ae8b0636be58',alloldfalse_raw_once_refs_preserved=True),
    limitations='No324productionGOorrealgradientupdate/evaluationyet. Do not claimrepairworksfromCPU. 315notearlyfallcause.317notgradientfidelityproof. Allsuccessneedsfirstflightcross/fullwheelfootprint/topmanifold/.5sstability. NoLuna/OpenRouter.'
)
put(R/'CURRENT_ACTUAL327_311_317_H4_REPAIR324_WORK_ORDER_V1.json',work)
put(R/'LOCAL327_READER_AND_PRODUCER_ERRORS_RETAINED.json',dict(epoch=time.time(),failures=['ExploratoryPowerShellmissing source paths/wildcardliteralpath and rg accessdenied; no model/network/physics.','316missingmetadata rejectedstatically before execution; original source retained.','321referencefilename mismatch rejectedstatically beforeexecution;original frozenINDEXretained.','Malformed exploratoryPowerShellquoting query exit1 withnooutput; no source/secret exposed.'],all_actual_results_separate=True))
print(json.dumps(dict(passed=True,INDEX324_SHA=H(index),work_order=str(R/'CURRENT_ACTUAL327_311_317_H4_REPAIR324_WORK_ORDER_V1.json'),new_GO=False)))
