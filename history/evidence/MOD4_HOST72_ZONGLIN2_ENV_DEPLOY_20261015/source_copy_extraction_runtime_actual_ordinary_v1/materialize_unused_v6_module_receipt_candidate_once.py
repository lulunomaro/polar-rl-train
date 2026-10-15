from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;p=D/'payload/validate_owned_Lab_headless_GPU_PhysX_v5_warp_reader.py';s=p.read_text()
s=s.replace('v5','v6').replace('V5','V6')
old="imports={x.__name__:getattr(x,'__file__',None) for x in (isaaclab,isaaclab.envs,isaaclab.assets,isaaclab_physx,tensordict,rsl_rl)}"
new="imports={name:getattr(sys.modules[name],'__file__',None) for name in ('isaaclab','isaaclab.envs','isaaclab.assets','isaaclab_physx','tensordict','rsl_rl')}"
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace(' from isaaclab.app import AppLauncher'," from isaacsim import SimulationApp\n import carb\n carb.settings.get_settings().set_bool('/crashreporter/preserveDump',True)\n carb.settings.get_settings().set_bool('/crashreporter/enabled',False)\n from isaaclab.app import AppLauncher")
s=s.replace('original_V4_Warp_array_reader_error_preserved=True','original_V4_Warp_array_reader_error_preserved=True,original_V5_parent_package_attribute_metadata_error_preserved=True')
q=p.with_name('validate_owned_Lab_headless_GPU_PhysX_v6_module_receipt.py');assert not q.exists();compile(s,str(q),'exec');q.write_text(s)
with (D/'reports/UNUSED_V6_SYS_MODULE_RECEIPT_AND_EARLY_DUMP_PRESERVE_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),
 reason='V5 reached all24 physical steps and data assertions, then metadata reader accessed a missing parent-package attribute. New probe reads the already imported modules from sys.modules. No source/physics changes. Set preserveDump before AppLauncher constructor to preserve historical copied crash metadata.',
 original_V3_V4_V5_failures_kept=True,no_manual_deletion_or_system_change=True),f,indent=2)
print(json.dumps(dict(prepared=True,sha256=hashlib.sha256(q.read_bytes()).hexdigest())))
