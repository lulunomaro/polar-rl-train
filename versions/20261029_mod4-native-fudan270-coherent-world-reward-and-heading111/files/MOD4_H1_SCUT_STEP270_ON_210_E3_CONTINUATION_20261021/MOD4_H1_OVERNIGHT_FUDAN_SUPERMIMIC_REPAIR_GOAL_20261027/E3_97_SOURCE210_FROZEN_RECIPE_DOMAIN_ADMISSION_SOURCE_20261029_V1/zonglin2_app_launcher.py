"""One unused N1 process: documented boot-time storage paths, no cooking toggle."""
from pathlib import Path
import os
from isaaclab.app import AppLauncher
class Zonglin2AppLauncher(AppLauncher):
 def _create_app(self):
  root=Path(os.environ['MOD4_E3_OWN_KIT_STORAGE_ROOT']).resolve()
  expected=Path('/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v1/e3/kit_isolation')
  assert root==expected and root.is_dir()
  self._sim_app_config['enable_crashreporter']=False
  self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false','--portable-root',str(root),'--/app/userConfigPath='+str(root/'data/user.config.json'),'--/UJITSO/datastore/localCachePath='+str(root/'DerivedDataCache')]
  super()._create_app()
