"""New71: bind qualified70 and only the reproduced HTTP-channel ownership correction."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V70_20261025'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 assert not any((N/x).exists() for x in ('payloads','controllers'))
 proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');oldq=read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
 assert proof['remaining_actual_snapshot']>82512.86069250107
 network=read(R/'ACTUAL_SEND_PACKET_FRAGMENTATION_CPU_INTEGRATION_ACTUAL.json');assert network['passed'] and len(network['tests'])==7
 shutil.copy2(P/'same_optimized_source_contract_metadata_candidate_v1.py',N/'same_optimized_source_contract_metadata_candidate_v1.py')
 sp=importlib.util.spec_from_file_location('metadata71',N/'same_optimized_source_contract_metadata_candidate_v1.py');md=importlib.util.module_from_spec(sp);sp.loader.exec_module(md)
 for key in ('h1','recovery'):md.validate_closed69_metadata(proof,key,oldq['specs'][key]['source_Adamstep'])
 tree=ast.parse((P/'diagnose70_control_response_channel_lifetime_CPU_once.py').read_text('utf8'))
 adapter=next(x.value.value for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='ADAPTER' for k in x.targets))
 network_check='''
APPROVED_RESPONSE_CHANNEL_VIEW = ADAPTER_LITERAL
def exact_response_channel_lifetime_change(before_text,after_text):
    import ast
    rules=[('def send(spec,row,port):',APPROVED_RESPONSE_CHANNEL_VIEW+'\\n'+'def send(spec,row,port):'),
           ('connection.sock=channel','connection.sock=_ResponseOwnedChannelSocket(channel)'),
           ('   elif channel is not None:channel.close()','   if channel is not None:channel.close()')]
    expected=before_text
    for old,new in rules:
        assert expected.count(old)==1
        expected=expected.replace(old,new,1)
    assert ast.dump(ast.parse(expected))==ast.dump(ast.parse(after_text))
    return dict(passed=True,only_HTTP_channel_ownership_changed=True,all_HMAC_pin_timeout_protocol_and_other_AST_exact=True)
'''.replace('ADAPTER_LITERAL',repr(adapter))
 guard=(P/'same_optimized_installed_source_admission_v3.py').read_text('utf8')
 needle="\ndef load(spec,B):";assert guard.count(needle)==1;guard=guard.replace(needle,network_check+needle,1)
 guard=guard.replace("'actual_closed69_to_same_optimized_source70'","'actual_closed70_to_same_optimized_network71'",1).replace("auth['source69_complete_SHA']","auth['source_complete_SHA']",1)
 needle="    source_start={'h1':790480,'recovery':837420}[key]";assert guard.count(needle)==1
 guard=guard.replace(needle,"    source_start=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['source_Adamstep']",1)
 guard=guard.replace("837420,spec['source_Adamstep']","prior['source_Adamstep'],spec['source_Adamstep']",1)
 needle="if rel.endswith('.py') and rel!=role and not (key=='recovery' and rel=='recovery_worker.py'):";assert guard.count(needle)==1
 guard=guard.replace(needle,"if rel.endswith('.py') and rel!=role and rel!='forwarded_original_owner_control_v1.py' and not (key=='recovery' and rel=='recovery_worker.py'):",1)
 needle="    new_python={r for r in after if r.endswith('.py') and r not in before}";assert guard.count(needle)==1
 guard=guard.replace(needle,"    exact_response_channel_lifetime_change((old/'forwarded_original_owner_control_v1.py').read_text('utf8'),(B/'forwarded_original_owner_control_v1.py').read_text('utf8'))\n    assert H(B/'forwarded_original_owner_control_v1.py')==auth['network_module_SHA']\n    network_CPU=read(B/'NETWORK_HTTP_RESPONSE_CPU_ACTUAL.json')\n    assert network_CPU['passed'] and len(network_CPU['tests'])==7 and H(B/'NETWORK_HTTP_RESPONSE_CPU_ACTUAL.json')==auth['network_CPU_report_SHA']\n"+needle,1)
 guard=guard.replace("assert new_python=={'same_optimized_source_contract_metadata_candidate_v1.py'}","assert new_python==({'same_optimized_source_contract_metadata_candidate_v1.py'}-set(before))",1)
 path=N/'same_optimized_network_source_admission_v4.py'
 with path.open('x',encoding='utf8') as f:f.write(guard)
 ast.parse(guard);sp=importlib.util.spec_from_file_location('guard71',path);checkmodule=importlib.util.module_from_spec(sp);sp.loader.exec_module(checkmodule)
 old_worker=(Path(oldq['payloads']['recovery'])/'recovery_worker.py').read_text('utf8')
 expected='{'+str(oldq['specs']['recovery']['source_Adamstep'])+'+20*updates}';assert old_worker.count(expected)==1
 new_worker=old_worker.replace(expected,'{'+str(proof['models']['recovery']['Adam'])+'+20*updates}',1)
 tests=[checkmodule.exact_recovery_source_adam_change(old_worker,new_worker,oldq['specs']['recovery']['source_Adamstep'],proof['models']['recovery']['Adam'])]
 oldnetwork=(Path(oldq['payloads']['recovery'])/'forwarded_original_owner_control_v1.py').read_text('utf8');newnetwork=(N/'forwarded_original_owner_control_v2.py').read_text('utf8')
 tests.append(checkmodule.exact_response_channel_lifetime_change(oldnetwork,newnetwork))
 for label,bad in [('auth_removed',newnetwork.replace('assert signature and hmac.compare_digest(signature,hmac.new(token,body,hashlib.sha256).hexdigest())','assert True')),('pin_changed',newnetwork.replace("HOST='10.24.5.27'","HOST='127.0.0.1'")),('raw_channel_close_removed',newnetwork.replace('   if channel is not None:channel.close()','   if channel is not None:pass'))]:
  try:checkmodule.exact_response_channel_lifetime_change(oldnetwork,bad)
  except AssertionError:tests.append(dict(test=label,rejected=True))
  else:raise AssertionError(label)
 put(R/'NETWORK71_EXACT_SOURCE_AST_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,tests=tests,new_guard_SHA=H(path),network_module_SHA=H(N/'forwarded_original_owner_control_v2.py'),no_controller_owner_budget_or_task_contract_changes=True,no_remote_install_or_GO=True))
 # Reuse only the reviewed static payload-construction body, never execute old once entry.
 source=(P/'prepare_same_optimized70_guard_v2_and_bound_payloads_CPU_once.py').read_text('utf8')
 start=source.index(" shutil.copytree(P/'controllers',N/'controllers')");end=source.index('\nexcept BaseException:',start)
 body=source[start:end]
 body=body.replace("out/'source_bind_history69'","out/'source_bind_history70'")
 body=body.replace("for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json'):","for name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','job0/TASK.json','SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json'):")
 body=body.replace("  shutil.copy2(path,out/role)","  shutil.copy2(path,out/role)\n  shutil.copy2(N/'forwarded_original_owner_control_v2.py',out/'forwarded_original_owner_control_v1.py')\n  shutil.copy2(R/'ACTUAL_SEND_PACKET_FRAGMENTATION_CPU_INTEGRATION_ACTUAL.json',out/'NETWORK_HTTP_RESPONSE_CPU_ACTUAL.json')",1)
 body=body.replace("latest69_original_cost_closure=proof","latest70_original_cost_closure=proof")
 body=body.replace("kind='actual_closed69_to_same_optimized_source70'","kind='actual_closed70_to_same_optimized_network71'")
 body=body.replace("source69_complete_SHA=final['SHA'],source69_Adam=model['Adam'],source69_updates=model['updates'],source69_complete_original_cost_report_SHA","source_complete_SHA=final['SHA'],source_Adam=model['Adam'],source_updates=model['updates'],source_complete_original_cost_report_SHA")
 body=body.replace("R/'SAME_OPTIMIZED70_EXACT_ADAM_GUARD_V2_CPU_ACTUAL.json'","R/'NETWORK71_EXACT_SOURCE_AST_CPU_ACTUAL.json'")
 needle="  put(out/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json',auth)";assert body.count(needle)==1
 body=body.replace(needle,"  auth.update(network_module_SHA=H(out/'forwarded_original_owner_control_v1.py'),network_CPU_report_SHA=H(out/'NETWORK_HTTP_RESPONSE_CPU_ACTUAL.json'))\n  (out/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json').write_text(json.dumps(auth,indent=2),encoding='utf8')",1)
 body=body.replace("root='H1step270_sampling_opt1_sagtuck6a_2510v70'","root='H1step270_sampling_opt1_sagtuck6a_net2_2510v71'")
 #70 deployer already requires same-reward ready. Preserve its exact production machinery.
 start=body.index(" deploy=(P/'deploy_selected_pair_unused_once.py').read_text('utf8');needle=")
 end=body.index(" with (N/'deploy_selected_pair_unused_once.py')",start)
 body=body[:start]+" deploy=(P/'deploy_selected_pair_unused_once.py').read_text('utf8')\n"+body[end:]
 # Keep a reviewable exact generated source before execution; unindent one enclosing try level.
 generated='\n'.join(line[1:] if line.startswith(' ') else line for line in body.splitlines())+'\n'
 with (N/'PREPARE71_BOUND_PAYLOAD_CONSTRUCTION_EXACT_SOURCE.py').open('x',encoding='utf8') as f:f.write(generated)
 exec(compile(generated,str(N/'PREPARE71_BOUND_PAYLOAD_CONSTRUCTION_EXACT_SOURCE.py'),'exec'),globals())
 # Same wrappers, only new local/remote namespace binding; never replay70 entry.
 source=(P/'deploy_same_optimized70_pinned_route_once.py').read_text('utf8').replace("assert json.loads((R/'ACTUAL_SAVED_CLOCK_NAME_BINDING_V3_CPU_ACTUAL.json').read_bytes())['passed']","assert json.loads((R/'NETWORK71_EXACT_SOURCE_AST_CPU_ACTUAL.json').read_bytes())['passed']").replace('same_optimized70','same_optimized71').replace('sagtuck6a_2510v70/recovery','sagtuck6a_net2_2510v71/recovery').replace('SAME_OPTIMIZED70','SAME_OPTIMIZED71')
 with (N/'deploy_same_optimized71_network_fixed_once.py').open('x',encoding='utf8') as f:f.write(source)
 source=(P/'collect70_first_PPO_pinned_route_once.py').read_text('utf8').replace('New70','New71').replace('SAME_OPTIMIZED70','SAME_OPTIMIZED71')
 with (N/'collect71_first_PPO_pinned_route_once.py').open('x',encoding='utf8') as f:f.write(source)
 B=T/'H1_STEP270_REWARD_PATH_V1_20261022';s=(B/'same_authorized_session_compressed_transport_v102.py').read_text('utf8');needle="        'extract_closed70_last_two_saved_prefixes_CPU_unused_once.py',";assert s.count(needle)==1
 s=s.replace(needle,needle+"\n        'deploy_same_optimized71_network_fixed_once.py',\n        'collect71_first_PPO_pinned_route_once.py',",1)
 with (B/'same_authorized_session_compressed_transport_v103.py').open('x',encoding='utf8') as f:f.write(s)
 print(json.dumps(dict(prepared71=True,qualified70_full_sources=True,exact_network_channel_lifetime_fix=True,no_remote_GO_yet=True)))
except BaseException:
 put(R/('PREPARE71_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),original_error_retained=True,no_retry_same_once_or_remote_GO=True));raise
