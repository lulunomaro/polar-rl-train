from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;R=T/'reports';N=T/'H1_STEP270_E3_PAIR_V7_20261022';B=T/'production_candidate_V3_COMMAND_AUDIT_UNINSTALLED'
proof=json.loads((R/'V98_H1_RECORDED_STEP270_COMMAND_VERSUS_LEGACY_ZERO_AUDIT_CPU_ACTUAL.json').read_bytes());assert proof['recorded_command_exactly_matches_already_installed_step270_publisher'] and not proof['original_zero_audit_would_pass']
old=N/'current_pair_closed_text/h1/h1_step270_sdk_runtime_candidate.py';raw=old.read_bytes();assert hashlib.sha256(raw).hexdigest()=='3fa4190fded7d337973b9d222ac09339ee7ebdb0fe2064e25aab4ee27f596e6e';text=raw.decode('utf8')
needle='        self.step270_geometry_receipt=dict(geometry=GEOMETRY,SDK_origins_literal_exact=True,actual_stage_ordered_triangle_SHA=sha,triangles=SPAWN[\'triangles\'],material_inherited_from_original_ground=True,authored_geometry_not_cooked_manifold_certification=True)'
assert text.count(needle)==1
text=text.replace(needle,needle+'\n        import spin_commands\n        spin_commands.audit=audit_step270_external_request')
function='''
def audit_step270_external_request(env):
    # This phase already publishes vx=.8 during its public request; do not alter it.
    from h1_external_operator_command_v1 import H1ExternalOperatorCommand
    from h1_original_directional_runtime import audit as directional_audit
    result=directional_audit(env)
    term=env.command_manager.get_term('twist');phase=env.h1_phase
    assert isinstance(term,H1ExternalOperatorCommand) and isinstance(phase,Step270Phase)
    command=term.command;expected=torch.zeros_like(command)
    expected[:,0]=phase.public_request().to(command.dtype)*.8
    assert torch.equal(command,expected),'Step270 external command differs from its already installed public-request publisher'
    result.update(stage='H1_step270_external_forward_request_audit_v1',public_request_envs=int(phase.public_request().sum()),command_matches_existing_publisher=True,no_position_or_terrain_command_generation=True,operator_mode_request_is_not_phase_truth=True)
    return result
'''
text+=function;newtree=ast.parse(text);oldtree=ast.parse(raw)
normalized=ast.parse(text);normalized.body=[x for x in normalized.body if not isinstance(x,ast.FunctionDef) or x.name!='audit_step270_external_request']
cls=next(x for x in normalized.body if isinstance(x,ast.ClassDef) and x.name=='H1Step270Env');init=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__');assert isinstance(init.body[-2],ast.Import) and isinstance(init.body[-1],ast.Assign);init.body=init.body[:-2]
assert ast.dump(normalized,include_attributes=False)==ast.dump(oldtree,include_attributes=False)
assert not B.exists();B.mkdir();p=B/old.name;p.open('x',encoding='utf8',newline='\n').write(text)
v=dict(epoch=time.time(),candidate_path=str(p),old_runtime_SHA=hashlib.sha256(raw).hexdigest(),candidate_runtime_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),normalized_rest_AST_exact=True,only_new_phase_audit_function_and_binding=True,existing_point8_publisher_unchanged=True,legacy_zero_audit_source_unchanged=True,physics_geometry_reward_actorinputs_STD_optimizer_and_17Adam_unchanged=True,old_native3_query9_reused_no_reexecution=True,not_installed=True,no_new_H1_GO_or_skill_result=True)
with (R/'V98_H1_STEP270_EXTERNAL_COMMAND_AUDIT_CANDIDATE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
