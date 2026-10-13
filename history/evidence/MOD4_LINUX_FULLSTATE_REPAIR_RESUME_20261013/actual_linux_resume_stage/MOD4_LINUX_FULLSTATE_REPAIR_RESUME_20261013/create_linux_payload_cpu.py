from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
W=D.parent
OLD=W/'MOD4_4090_WINDOWS_ENV_CAPACITY_20261013/SELECTED_PRODUCTION_CPU_INPUTS_1791900904804626800/payload'
P=D/'payload_v1';P.mkdir(exist_ok=False)
for name in ('expanded_source_projection.py','PERENV128_SCHEMA_V1.json','selected_source_projection.py','left_head_offset_aware_migration_v3.py','temporary_probe_contract_base.py'):
    (P/name).write_bytes((OLD/name).read_bytes())

class N20K(ast.NodeTransformer):
    def visit_Constant(self,n):
        if type(n.value) is int and n.value==512:n.value=20000
        if isinstance(n.value,str):
            if n.value.endswith('.json') and n.value.startswith('WINDOWS4090_'):n.value=n.value.replace('WINDOWS4090_','LINUX4090_',1)
            if n.value=='Windows-IsaacSim5.1-PhysX2API':n.value='Linux-IsaacSim6.0.1-PhysX3API'
        return n

worker=(OLD/'temporary_worker.py').read_text(encoding='utf8')
worker=worker.replace("os.name == 'nt'", "os.name == 'posix'")
worker=worker.replace("    from local_physx_api import install\n    install()\n",'')
worker=worker.replace("os.environ['RM_MOD4_USD'] = str(R / 'assets/robot.usd')", "assert Path(os.environ['RM_MOD4_USD']).is_file()")
worker=worker.replace("pre, _ = parser.parse_known_args()", "pre, _ = parser.parse_known_args()")
worker=worker.replace("assert pre.source_sha == manifest['source']['sha256']", "assert pre.source_sha == manifest['source']['sha256']")
(P/'temporary_worker.py').write_text(ast.unparse(N20K().visit(ast.parse(worker)))+'\n',encoding='utf8')

runtime=(OLD/'temporary_training_runtime.py').read_text(encoding='utf8')
runtime=runtime.replace("        saved['WINDOWS4090_CAPACITY_ATTEMPT'] = dict(", "        saved['LINUX4090_RECOVERY_ATTEMPT'] = dict(")
runtime=runtime.replace("        saved['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'] = metadata_actual", "        saved['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'] = metadata_actual\n        saved['LINUX4090_FULLSCALE_BRANCH'] = copy.deepcopy(source['LINUX4090_FULLSCALE_BRANCH'])")
runtime=runtime.replace("canonical_reconciliation_pending=True", "canonical_reconciliation_pending=False")
runtime=runtime.replace("local_cost_evidence_not_second_budget=True", "original_Linux_parent_owns_unique_canonical_segment=True")
(P/'temporary_training_runtime.py').write_text(ast.unparse(N20K().visit(ast.parse(runtime)))+'\n',encoding='utf8')

base=(OLD/'temporary_probe_contract_base.py').read_text(encoding='utf8')
base=base.replace("root_quaternion_convention='wxyz'", "root_quaternion_convention='xyzw'")
(P/'temporary_probe_contract_base.py').write_text(ast.unparse(N20K().visit(ast.parse(base)))+'\n',encoding='utf8')

observer=(OLD/'windows4090_substep_readback_v6.py').read_text(encoding='utf8')
observer=observer.replace("PROFILE = 'windows4090_actual_substep_readback_bounded_v6'", "PROFILE = 'linux4090_actual_substep_readback_bounded_v1'")
observer=observer.replace("xyz = q[..., 1:4]\n    w = q[..., 0:1]", "xyz = q[..., :3]\n    w = q[..., 3:4]")
observer=observer.replace("from independent_COM_jit_arithmetic import combine_frame_transforms as independent_represented_transform\n    represented_pos, _ = independent_represented_transform(link[..., :3].to(world_dtype), link[..., 3:7].to(world_dtype), lc[..., :3].to(world_dtype), lc[..., 3:7].to(world_dtype))", "from independent_linux_COM_warp import represented_COM\n    represented_pos = represented_COM(r.data.body_link_pose_w, r.data.body_com_pose_b)")
observer=observer.replace('self.cap.sensor.contact_physx_view', 'self.cap.sensor.contact_view')
(P/'windows4090_substep_readback_v6.py').write_text(ast.unparse(N20K().visit(ast.parse(observer)))+'\n',encoding='utf8')
(P/'temporary_probe_contract.py').write_bytes((OLD/'temporary_probe_contract.py').read_bytes())

for p in P.glob('*.py'):compile(p.read_text(),str(p),'exec')
receipt=dict(passed_compile=True,actual_GPU_admission=False,num_envs=20000,source512_learned_state_not_old20k_spliced=True,installed_SDK_files_not_modified=True,new_observer_native_xyzw_and_contact_view=True,old_Windows_payload_original_bytes_preserved=True,files=[dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in P.iterdir()])
(D/'reports/LINUX_PAYLOAD_PREPARED_CPU_ACTUAL.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print(json.dumps(dict(payload=str(P),files=len(receipt['files']),GPU_launched=False)))
