"""Independent saved/source AST and84 live-pins review only. Never import or run project modules."""
from pathlib import Path
import ast,copy,hashlib,json,re,traceback
D=Path(__file__).resolve().parent;R=D.parents[1]
OUT=D/'FINAL_ENTRY_REVIEW_001.json'
checks=[];issues=[];cache={};pin_rows=[]
def ck(name,value):
 ok=bool(value);checks.append((name,ok))
 if not ok:issues.append(name)
 return ok
def sha(b):return hashlib.sha256(b).hexdigest()
def key(p):return str(Path(p).resolve()).casefold()
def raw(p):
 p=Path(p).resolve();k=key(p)
 if k not in cache:cache[k]=p.read_bytes()
 return cache[k]
def js(p):return json.loads(raw(p))
def text(p):return raw(p).decode('utf-8-sig')
def tree(p):return ast.parse(text(p))
def dump(x):return ast.dump(x,include_attributes=False)
def func(t,name):return next(n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name==name)
def klass(t):return next(n for n in t.body if isinstance(n,ast.ClassDef))
def parts(t):
 loops=[n for n in ast.walk(t)if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='k']
 assignments={s:[dump(n)for n in ast.walk(t)if isinstance(n,ast.Assign)and any(isinstance(a,ast.Name)and a.id==s for a in n.targets)]for s in ['target','healthy','good','complete','passed']}
 return len(loops)==1 and all(len(v)==1 for v in assignments.values()),[dump(n)for n in loops],assignments
class ReversePermission(ast.NodeTransformer):
 def __init__(self):self.changed=0
 def visit_If(self,node):
  self.generic_visit(node);t=node.test
  if isinstance(t,ast.Compare)and isinstance(t.left,ast.Attribute)and t.left.attr=='phase'and len(t.ops)==1 and isinstance(t.ops[0],ast.In)and len(t.comparators)==1 and isinstance(t.comparators[0],ast.Tuple):
   q=t.comparators[0]
   if [getattr(e,'value',None)for e in q.elts]==['LIFT_WORLD_SUPPORT','CAPTURE_WORLD_SUPPORT','RETURN_NOMINAL','VERIFY']:
    q.elts=q.elts[1:];self.changed+=1
  return node

def review():
 expected={'CONFIG.json':'1f4d04059a156ba8bf387c9a55365f2b53ed1852372dd0906632dead34cb940f','PROTOCOL.json':'c79773d8e9f9cfc494347b2dc03cbfce2942a1692411d266893a2ea7feb5cfe8','SOURCE_PREEXEC.json':'5bf468e0f96bddb9541ccdcc4a9440f39da6ce0736debcc41c5fff76b770abd0'}
 for name,h in expected.items():ck('frozen_'+name,sha(raw(D/name))==h)
 if issues:return
 idx=js(D/'SOURCE_PREEXEC.json');files=idx['files'];roots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()]
 ck('exact84_unique_paths',len(files)==84 and len({key(x['path'])for x in files})==84)
 for x in files:
  p=Path(x['path']).resolve()
  allowed=any(p.is_relative_to(z)for z in roots)and p.suffix.lower()in('.py','.json','.md','.txt')
  if not ck('bounded_allowed_pin:'+str(p),allowed and p.is_file()and p.stat().st_size<2*1024*1024):continue
  s=p.stat();b=raw(p);observed=dict(path=str(p),bytes=len(b),SHA=sha(b));ok=observed==x
  ck('live_SHA:'+str(p),ok);pin_rows.append(dict(path=str(p),bytes=len(b),SHA=observed['SHA'],size=s.st_size,mtime_ns=s.st_mtime_ns))
 pins={key(x['path']):x for x in files}
 olddir=R/'STARTUP_STAND_V4/front_admission002';oldidx=js(olddir/'SOURCE_PREEXEC.json')
 ck('all57_exact_record_identity',len(oldidx['files'])==57 and all(pins.get(key(x['path']))==x for x in oldidx['files']))
 cfg=js(D/'CONFIG.json');protocol=js(D/'PROTOCOL.json');prep=js(D/'PREPARATION_RECEIPT.json');oldcfg=js(olddir/'CONFIG.json')
 expectedflags=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False,support_geometry_enable=True,lift_pose_enable=True)
 ck('five_exact_bools_and_values',cfg['controller']==expectedflags and all(type(x)is bool for x in cfg['controller'].values()))
 inverse=copy.deepcopy(cfg);inverse['controller'].pop('lift_pose_enable');inverse['case_id']=oldcfg['case_id'];inverse['kind']=oldcfg['kind']
 ck('only_newID_kind_liftflag_config_delta',inverse==oldcfg)
 ck('one_front_nominal_caps',cfg==protocol['config'] and cfg['case_id']=='startup_front065_lift_pose_v5_nominal1'and cfg['nominal']is True and type(cfg['seed'])is int and cfg['seed']==0 and cfg['duration_s']==10. and protocol['max_workers']==1 and protocol['maximum_controls']==1000 and protocol['maximum_physics_steps']==20000 and protocol['profile_B_not_admitted']is True)
 for name in ['no_automatic_DR_back_side_second_variant_or_retry','actual_independent_source_config_launcher_review_required','one_passive_fixture_initialization_no_upright_prior_or_assist','earlier_latch_carryover_part_of_timing_intervention']:
  ck('protocol_'+name,protocol[name]is True)
 core=R/'STARTUP_STAND_V5/controller.py';entry=R/'run_startup_stand_case_v7.py';oldcore=R/'STARTUP_STAND_V4/controller.py';oldentry=R/'run_startup_stand_case_v6.py'
 ck('candidate_scope_pin',sha(raw(core))==prep['candidate_SHA']=='209c0385d1501021b05822f0222228ae78b012570f73fb526a435e8c02b2045a')
 ck('runner_scope_pin',sha(raw(entry))==prep['runner_SHA']=='b96f10a45b79527e63a5afdc126579b480ce87931aeb8de57d2805e0a8b48367')
 n=tree(core);o=tree(oldcore);newbody=copy.deepcopy(func(n,'_command_lift_permission'));newbody.name='command';reverse=ReversePermission();newbody=reverse.visit(newbody)
 ck('independent_core_AST_exact_inverse_rename_plus_one_LIFT',reverse.changed==1 and dump(newbody)==dump(func(o,'command')))
 ck('only_declared_new_methods',set(x.name for x in klass(n).body if isinstance(x,ast.FunctionDef))=={'__init__','command','_notes','_command_lift_permission'})
 wrapper=func(n,'command');delegate=dump(ast.parse('return super().command(e, packet, now, attitude_q)').body[0])
 ck('disabled_and_nonLIFT_real_super_delegate',dump(wrapper.body[0].body[0])==delegate and dump(wrapper.body[1].body[0])==delegate)
 ck('wrapper_flag_defaultoff_exact_bool',"c.pop('lift_pose_enable', False)"in text(core)and 'if type(flag) is not bool:'in text(core)and 'bool(flag and self.support_geometry_active)'in text(core))
 precheck=wrapper.body[2]
 ck('finite_type_precheck_before_permission_body',isinstance(precheck,ast.Try)and not any(isinstance(x,(ast.Assign,ast.AugAssign,ast.AnnAssign))for y in precheck.body for x in ast.walk(y))and isinstance(wrapper.body[-1],ast.Return)and ast.unparse(wrapper.body[-1].value)=='self._command_lift_permission(e, packet, now, attitude_q)')
 ck('clock_reference_caps_and_FF_inherited_not_overridden',not {'_time','_sample','_travel','_reference','_ready','_goal','_ground_reference','prepare_estimator'}&{x.name for x in klass(n).body if isinstance(x,ast.FunctionDef)}and "self.encoder_travel_m > .50"in text(oldcore)and "6.-1e-10"in text(core))
 nt=tree(entry);ot=tree(oldentry);a=parts(nt);b=parts(ot)
 ck('entire_loop_target_healthy_good_complete_passed_AST_equal',a[0]and b[0]and a[1:]==b[1:])
 for name in ['MiniHopAuditPlant','FullDR','StateEstimator','StartupStand']:
  calls=lambda t:[dump(x)for x in ast.walk(t)if isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id==name]
  ck('actual_constructor_same_AST:'+name,calls(nt)==calls(ot)and len(calls(nt))==1)
 et=text(entry)
 ck('actual_queue_receipt_not_fake_API','dr.queue_receipt()'in et and 'runtime_receipt'not in et and re.search(r'^    def queue_receipt\(self\):',text(R.parent/'traditional_control_20261101/dr_components.py'),re.M)is not None)
 ck('both_actual_gain_loaders_and_runtime_records',all("load_gain(ROOT/'TALL_ROUGH_BANK_V1/"+s+"')"in et and "file_record(ROOT/'TALL_ROUGH_BANK_V1/"+s+"')"in et for s in ['gain_delta0.json','gain_delta20.json']))
 ck('gain0_data_pin',pins[key(R/'TALL_ROUGH_BANK_V1/gain_delta0.json')]['SHA']=='05ede4b3425e596fe2f1a9f47258e6c8024d2e0f9732b016442f56dbfb378e3a')
 ck('actual_gain20_29484_data_pin',pins[key(R/'TALL_ROUGH_BANK_V1/gain_delta20.json')]['SHA']=='f97040665db51c4bc1686187f14aa46579d8d6f6eabff6ef2ee69dea5328d099'and pins[key(R/'TALL_ROUGH_BANK_V1/gain_delta20.json')]['bytes']==29484)
 ck('single_passive_initialization_no_assist_or_GT_control',et.count('mujoco.mj_resetData(')==1 and et.count("plant.d.qpos[:]=fixture['final_qpos']")==1 and et.count("plant.d.qvel[:]=fixture['final_qvel']")==1 and 'upright_prior=False'in et and 'xfrc_applied'not in et and 'qfrc_applied'not in et and 'tau=controller.command(e,packet,now,est.q)'in et)
 ck('sensor_prepare_packet_est_command_order',[et.index(s)for s in ['controller.prepare_estimator(est,now)','packet=plant.sensor_packet()','e=est.update(packet)','tau=controller.command(e,packet,now,est.q)']]==sorted(et.index(s)for s in ['controller.prepare_estimator(est,now)','packet=plant.sensor_packet()','e=est.update(packet)','tau=controller.command(e,packet,now,est.q)']))
 ck('exact_bool_keyset_newID_guard',"'lift_pose_enable'}"in et and 'all(type(x)is bool'in et and "assert cfg['case_id']=='startup_front065_lift_pose_v5_nominal1'"in et)
 proof=js(R/'STARTUP_STAND_V5/preflight001/RESULT.json');pr=js(R/'STARTUP_STAND_V5/preflight001/RECEIPT.json');done=js(R/'STARTUP_STAND_V5/preflight001/COMPLETION_RECEIPT.json');accepted=js(R/'STARTUP_STAND_V5/PARENT_MATH_PROOF_ACCEPTANCE.json')
 ck('actual_saved_proof_counts_and_sources',proof['counts']==pr['counts']==done['counts']and [proof['counts'][k]for k in ['enabled_external_new_and_V4_oracle','disabled_external_new_and_V4_oracle','typed_contexts','checks']]==[57,40,16,455]and proof['branch_fired_LIFT_commands']==pr['new_proof_actual_branch_fired']==done['actual_LIFT_branch_command_count']==8 and len(proof['typed'])==16 and all(x['passed']is True for x in proof['typed']))
 ck('synthetic_not_physical_and_old_qa_not_replayed',accepted['approved_synthetic_only']is True and accepted['physical_skill_qualified']is False and proof['old551_not_replayed']is True and proof['model_FK_PHY_DARE_DR_oldQA_native_Git_agents']==0)
 for x in accepted['source_artifacts']+proof['source_before']+done['artifacts']:ck('saved_acceptance_artifact_bound:'+x['path'],pins.get(key(x['path']))==x)
 ck('saved_proof_allthree_hashanchors',sha(raw(core))==accepted['core_SHA']and sha(raw(entry))==accepted['entry_SHA']and sha(raw(R/'STARTUP_STAND_V5/preflight001/RESULT.json'))==accepted['proof_SHA']==prep['saved_proof_SHA'])
 old_receipt=js(R/'STARTUP_STAND_V4/RECEIPT.json');ck('old551_basequalification_metadata_only',old_receipt['counts']['enabled_commands']==551 and old_receipt['entry_not_imported_or_run']is True)
 gen=js(R/'STARTUP_STAND_V5/GENERATION_FAILURE_RECEIPT_001.json');repair=js(R/'STARTUP_STAND_V5/GENERATION_REPAIR_002_DERIVATION.json')
 ck('generator_failure_and_warning_preserved_not_robotfail',gen['proof_started']is False and gen['candidate_imports_or_constructors']==0 and repair['exact_inverse_to_failed_source']is True and 'SyntaxWarning'in text(R/'STARTUP_STAND_V5/preflight001/STDERR_001.txt')and accepted['generator_error_and_original_stderr_warning_preserved']is True)
 prepcode=text(R/'prepare_startup_lift_pose_v5.py');launchcode=text(R/'launch_startup_lift_pose_v5.py');acceptcode=text(R/'accept_startup_lift_pose_v5_math_once.py')
 ck('preparer_requires_actual_saved_acceptance_before_any_case',prepcode.index("accepted=get(acceptance)")<prepcode.index('D.mkdir(')and "counts['disabled_including_oracles']<=40"in prepcode and "accepted['new_feature_branch_fired_in_synthetic'] is True"in prepcode and 'comparison==old'in prepcode and "len(old_index['files'])==57"in prepcode)
 ck('acceptance_strict_saved_counts_and_pins',"==(57,40,16,455)"in acceptcode and "==8"in acceptcode and "rc['all_source_before_after_equal'] is True"in acceptcode and "first_physical_case_requires_independent_review_and_separate_parent_approval=True"in acceptcode)
 required=['PARENT_APPROVAL.json','approved','ONE_NEW_V5_FRONT_NOMINAL_ONLY','config_SHA','protocol_SHA','source_index_SHA','launcher_SHA','independent_review_SHA','proof_acceptance_SHA','saved_proof_SHA','runner_SHA','candidate_SHA']
 ck('launcher_all_approval_review_proof_hashanchors',all(x in launchcode for x in required)and "review['ready_one_front_nominal'] is True and review['issues']==[]"in launchcode and "accepted['physical_skill_qualified'] is False"in launchcode)
 lt=tree(R/'launch_startup_lift_pose_v5.py');lc=[x for x in ast.walk(lt)if isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id=='launch']
 ck('launcher_exact_onecase_worker1_no_other_launch',len(lc)==1 and ast.unparse(lc[0].args[3])=="[(cfg['case_id'], cfg)]"and any(x.arg=='max_workers'and isinstance(x.value,ast.Constant)and x.value.value==1 for x in lc[0].keywords))
 ck('launcher_all_main_assertions_precede_only_launch',all(x.lineno<lc[0].lineno for x in ast.walk(func(lt,'main'))if isinstance(x,ast.Assert)))
 helper=text(R/'fresh_train_batch_v2.py');ck('fresh_unique_output_software_failure_stop_no_retry',"batch.mkdir(exist_ok=False)"in helper and "not(root/'results'/name).exists()"in helper and "if any(row['software_failure']for row in wave):break"in helper and "if result['software_failure']:raise SystemExit(1)"in helper and 'ERROR_artifact_present'in helper)
 ck('parent_approval_absent_and_new_case_unexecuted',not(D/'PARENT_APPROVAL.json').exists()and not(R/'results'/cfg['case_id']).exists()and not(R/'batches'/cfg['case_id']).exists())
 ck('review_scope_postfreeze_not_runtime_input',key(D/'PARENT_REVIEW_SCOPE.json')not in pins and 'PARENT_REVIEW_SCOPE'not in et and 'FINAL_ENTRY_REVIEW_001'not in et)
 stable=all(Path(x['path']).stat().st_size==x['size']and Path(x['path']).stat().st_mtime_ns==x['mtime_ns']for x in pin_rows)
 ck('all84_poststats_stable',len(pin_rows)==84 and stable)
 return dict(config=cfg,protocol=protocol,prep=prep,files=files,pins=pins,accepted=accepted,proof=proof,stable=stable)

def main():
 if OUT.exists():raise RuntimeError('Existing independent review is immutable; do not rerun')
 result=None
 try:result=review()
 except Exception as ex:issues.append('STATIC_REVIEW_EXCEPTION:'+type(ex).__name__+':'+str(ex));error=traceback.format_exc();(D/'INDEPENDENT_REVIEW_ERROR_001.txt').write_text(error,encoding='utf-8')
 good=not issues and result is not None
 anchors={'config_SHA':sha(raw(D/'CONFIG.json')),'protocol_SHA':sha(raw(D/'PROTOCOL.json')),'source_index_SHA':sha(raw(D/'SOURCE_PREEXEC.json')),'runner_SHA':sha(raw(R/'run_startup_stand_case_v7.py')),'candidate_SHA':sha(raw(R/'STARTUP_STAND_V5/controller.py'))}
 out=dict(status='PASS_INDEPENDENT_STATIC_V5_FRONT_ENTRY_REVIEW_NOT_LAUNCH_OR_PHYSICAL_APPROVAL'if good else'HOLD_INDEPENDENT_STATIC_V5_FRONT_ENTRY_REVIEW',ready_one_front_nominal=good,issues=issues,**anchors,
  checks=dict(total=len(checks),passed=sum(v for _,v in checks),failed=[n for n,v in checks if not v],core_AST_inverse='methodrename+onlyLIFTeligibilitytuple'if good else'CHECK_ISSUES',full_loop_target_healthy_good_complete_passed_AST_equal=good),
  live_pin_verification=dict(files=len(pin_rows),bytes=sum(x['bytes']for x in pin_rows),max_file_bytes=max([x['bytes']for x in pin_rows],default=0),SHA_once_per_locked_file=True,post_stat_stable=bool(result and result['stable']),old57_exact_record_identity=good,actual_gain20_data_pinned=good,no_big_assets_or_raw_or_library=True),
  read_counts=dict(semantic_full_selected_text_files=24,queue_receipt_API_excerpt_files=1,long_completion_JSON_UI_truncated_but_full_structured_parse=True,metadata_live_pin_files=len(pin_rows),whole_old_source_semantic_rescan=False),
  saved_evidence_reused=dict(new_enabled_including_oracles=57,total_disabled_including_oracles=40,typed=16,saved_checks=455,actual_synthetic_LIFT_commands=8,old551_and_base_qualification_reused_not_replayed=True,warning_and_generator_failure_preserved=True),
  retained_contract=dict(same_V4_gate_caps_clock_travel_050_timeout6=True,earlier_latch_carryover_is_timing_intervention_not_identical_closedloop_qref=True,one_passive_qpos_qvel_initialization=True,upright_prior=False,original_driver_and_private_gates=True,workers=1,nominal_case_count=1,controls_cap=1000,physics_cap=20000),
  no_new_execution=dict(controller_import_or_command=0,new_proof=0,model=0,FK=0,PHY=0,DR_sample=0,solver=0,ARM_native_or_ASM=0,oldQA=0,Git=0,agents=0,Goal=0),
  known_limits=['Only fixed front065 new nominal TRAIN, no DR/back/side/retry/profileB.','Synthetic fixture K/true gate is not actual support or stability/standing/hardware qualification.','Earlier latch can affect later policy and closedloop reference; not an isolated direct torque or identical realized qref claim.','No PARENT_APPROVAL/physical case executed; parent separately reads reviewer SHA and signs exact hash-bound one-case approval.','PH11pending; PH10/old failures and source index unchanged.'],
  reviewer=dict(scope_postfreeze_nonruntime=True,script_SHA=sha(Path(__file__).read_bytes()),scope_SHA=sha(raw(D/'PARENT_REVIEW_SCOPE.json')),source_index_not_modified=True,only_static_source_AST_JSON_and_hashing=True))
 # Compact values preserve<=25actualJSONlines without truncating findings/check totals.
 lines=['{']+['  '+json.dumps(k)+': '+json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+(','if i<len(out)-1 else'')for i,(k,v)in enumerate(out.items())]+['}']
 if len(lines)>25:raise RuntimeError('Bounded review line count exceeded; preserve real findings')
 with OUT.open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(lines)+'\n')
 print(json.dumps(dict(status=out['status'],ready_one_front_nominal=good,issues=issues,metadata_checks=len(checks),locked_files=len(pin_rows),report_lines=len(lines),bytes=OUT.stat().st_size,SHA=sha(OUT.read_bytes())),ensure_ascii=False))
 if not good:raise SystemExit(1)
if __name__=='__main__':main()
