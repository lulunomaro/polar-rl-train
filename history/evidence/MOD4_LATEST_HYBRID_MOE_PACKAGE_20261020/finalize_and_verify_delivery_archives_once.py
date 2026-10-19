"""Finalize two user deliveries and verify every ZIP member against its file manifest."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time,traceback,zipfile
B=Path(__file__).resolve().parent;R=B/'reports';P=B/'delivery/MOD4_HybridMoE_20261020';CORE=B/'delivery/MOD4_HybridMoE_Policy_20261020';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def seal(root):
 files=sorted(p for p in root.rglob('*') if p.is_file());assert not any('__pycache__' in p.parts or p.suffix in ('.pyc','.pt','.pth','.npz','.log') or p.name.endswith('.lock') for p in files)
 sums=''.join(H(p)+'  '+p.relative_to(root).as_posix()+'\n' for p in files);(root/'SHA256SUMS.txt').write_text(sums,encoding='utf8')
 rows=[dict(path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(root.rglob('*')) if p.is_file()];(root/'PACKAGE_MANIFEST.json').write_text(json.dumps(dict(schema_version=1,created_epoch=time.time(),files=rows,source_policy_SHA=H(root/'policy/hybrid_moe.onnx'),manifest_self_excluded=True),ensure_ascii=False,indent=2),encoding='utf8')
 proc=subprocess.run([sys.executable,'-B','-X','utf8',str(root/'check_package.py')],cwd=B,capture_output=True,text=True,encoding='utf8');assert proc.returncode==0,(proc.stdout,proc.stderr)
 return dict(files=len(rows),bytes=sum(x['bytes'] for x in rows),checker_stdout=proc.stdout,checker_stderr=proc.stderr)
def zip_and_check(root,name):
 out=B/name;assert not out.exists()
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,root.name+'/'+p.relative_to(root).as_posix())
 m=json.loads((root/'PACKAGE_MANIFEST.json').read_bytes());expected={root.name+'/'+r['path']:r for r in m['files']};expected[root.name+'/PACKAGE_MANIFEST.json']=dict(bytes=(root/'PACKAGE_MANIFEST.json').stat().st_size,SHA=H(root/'PACKAGE_MANIFEST.json'))
 with zipfile.ZipFile(out) as z:
  assert set(z.namelist())==set(expected)
  for name,r in expected.items():
   data=z.read(name);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['SHA']
 result=dict(path=str(out),bytes=out.stat().st_size,SHA=H(out),members=len(expected),all_ZIP_members_exact_SHA_and_size_verified=True);out.with_suffix('.zip.sha256').write_text(result['SHA']+'  '+out.name+'\n',encoding='utf8');return result
def main():
 export=json.loads((R/'LATEST_CLOSED_HYBRID_MOE_EXPORT_AND_ROUTING_CPU_ACTUAL.json').read_bytes());verify=json.loads((R/'RELOCATED_PORTABLE_FULLMAP_AND_BUNDLE_CPU_ACTUAL.json').read_bytes());assert export['passed'] and verify['passed'];(P/'verification').mkdir()
 for n in ('LATEST_CLOSED_HYBRID_MOE_EXPORT_AND_ROUTING_CPU_ACTUAL.json','RELOCATED_PORTABLE_FULLMAP_AND_BUNDLE_CPU_ACTUAL.json'):shutil.copy2(R/n,P/'verification'/n)
 interface=dict(observation_width=35,action_width=6,dtype='float32',rate_Hz=100,observation_terms=[dict(indices=[0,2],term='command_vx_vy_wz',scale=1),dict(indices=[3,3],term='height',scale=5),dict(indices=[4,6],term='body_angular_velocity',scale=.5),dict(indices=[7,9],term='projected_gravity',scale=1),dict(indices=[10,13],term='left_crank_left_hip_right_crank_right_hip_positions',scale=1),dict(indices=[14,15],term='reserved_positions',value=[0,0]),dict(indices=[16,19],term='leg_velocities_same_order',scale=.1),dict(indices=[20,21],term='left_right_wheel_velocities',scale=.1),dict(indices=[22,27],term='previous_clipped_action',scale=1),dict(indices=[28,34],term='mode_one_hot',exactly_one=True)],action_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],not_torque=True,combined_action_clip=[-6,6],individual_experts_output_unclipped=True,routing_modes={'0':'original E0/W35 gate','3':'E3 recover','4':'H1 jump','6':'E2 spin player alias; E2 mode normalized to0'},leg_targets_scale=[.5,.5,.5,.5],wheel_velocity_scale=10,control_reference='player/sim_runtime.py action_to_torque; runtime_config.json',skill_qualification=False)
 (P/'policy/interface.json').write_text(json.dumps(interface,ensure_ascii=False,indent=2),encoding='utf8');source_lines=['MOD4 HybridMoE complete checkpoint provenance (not files required at runtime)','H1: hour16; E2/E3: hour17; current E3 hour18 not closed at export.']+[role+'  '+r['SHA'] for role,r in export['sources'].items()];(P/'MODEL_SOURCE_SHA256.txt').write_text('\n'.join(source_lines)+'\n',encoding='utf8')
 CORE.mkdir();shutil.copytree(P/'policy',CORE/'policy');shutil.copytree(P/'verification',CORE/'verification')
 for n in ('infer.py','check_package.py','requirements_policy.txt','MODEL_SOURCE_SHA256.txt'):shutil.copy2(P/n,CORE/n)
 shutil.copy2(P/'使用说明.md',CORE/'完整使用说明_含播放器操作.md')
 (CORE/'README.md').write_text('''# MOD4 混合MoE策略轻量包

本包用于集成推理，不含GUI、机器人或场地资产。要直接试玩，请使用同批 `MOD4_HybridMoE_20261020_Full.zip`。

最新完整来源：H1第16小时、E2/E3第17小时，保留原E0/W35 gate148。当前E3第18小时未闭合，不使用其中途模型。

安装Python3.12和依赖后运行：

```powershell
python -m pip install -r requirements_policy.txt
python check_package.py
python infer.py
```

程序接口：`from infer import HybridMoE`，`HybridMoE()(obs)`。输入float32 `[batch,35]`，输出已裁剪六维动作；35维语义和动作适配见 `policy/interface.json` 和 `完整使用说明_含播放器操作.md` 第二部分。动作不是扭矩。

组合策略为 `policy/hybrid_moe.onnx`，另附五个独立专家ONNX；专家单独输出需要裁剪。普通模式使用原学习门控，跳跃/恢复/自旋采用手动分派，不是新五路学习门控或动作平均。

`policy/manifest.json` 记录来源SHA、确定性导出和1400行一致性结果；本包不是技能毕业或实车认证。
''',encoding='utf8')
 fullcheck=seal(P);corecheck=seal(CORE);full=zip_and_check(P,'MOD4_HybridMoE_20261020_Full.zip');core=zip_and_check(CORE,'MOD4_HybridMoE_20261020_Policy.zip');out=dict(epoch=time.time(),passed=True,deliveries={'full_player':full,'policy_only':core},folder_checks={'full':fullcheck,'policy':corecheck},source_policy_SHA=H(P/'policy/hybrid_moe.onnx'),source_hours={'H1':16,'E2':17,'E3':17},all_archives_exact_members_verified=True,original_player_unchanged=True,no_remote_training_or_checkpoint_download=True)
 put('FINAL_DELIVERY_ARCHIVES_AND_FILE_MANIFEST_VERIFIED_ACTUAL.json',out);print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:put('FINAL_DELIVERY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_original_player_or_training_change=True));raise
