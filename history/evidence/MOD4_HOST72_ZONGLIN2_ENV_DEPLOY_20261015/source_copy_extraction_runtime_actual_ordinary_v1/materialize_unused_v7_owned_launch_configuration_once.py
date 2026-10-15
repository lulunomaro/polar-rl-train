from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;p=D/'payload/validate_owned_Lab_headless_GPU_PhysX_v6_module_receipt.py';s=p.read_text().replace('v6','v7').replace('V6','V7')
old=" from isaacsim import SimulationApp\n import carb\n carb.settings.get_settings().set_bool('/crashreporter/preserveDump',True)\n carb.settings.get_settings().set_bool('/crashreporter/enabled',False)\n from isaaclab.app import AppLauncher"
new=" from isaaclab.app import AppLauncher\n class OwnedAppLauncher(AppLauncher):\n  def _create_app(self):\n   self._sim_app_config['enable_crashreporter']=False\n   self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false']\n   super()._create_app()"
assert s.count(old)==1;s=s.replace(old,new).replace('launcher=AppLauncher(', 'launcher=OwnedAppLauncher(')
q=p.with_name('validate_owned_Lab_headless_GPU_PhysX_v7_owned_config.py');assert not q.exists();compile(s,str(q),'exec');q.write_text(s)
with (D/'reports/UNUSED_V7_OWNED_SIMULATIONAPP_LAUNCH_CONFIG_SOURCE_BOUND_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),
 actual_source_reason='AppLauncher filters keys not in _SIM_APP_CFG_TYPES, including extra_args/enable_crashreporter. Owned subclass sets only supported SimulationApp launch config before superclass _create_app. No installed source, driver guard, physics, reset, solver or GPU settings bypass.',
 V6_original_error='Carb ISettings unavailable before plugin bootstrap; no SimulationApp or physics constructed in V6.',
 V5_reader_error='Missing parent module attribute after all24 physical data assertions; sys.modules receipt fixed independently.',
 original_all_false_and_archives_retained=True),f,indent=2)
print(json.dumps(dict(prepared=True,sha256=hashlib.sha256(q.read_bytes()).hexdigest())))
