from pathlib import Path
import os
from isaaclab.app import AppLauncher
class E1IsolatedAppLauncher(AppLauncher):
 def _create_app(self):
  job=Path(os.environ['MOD4V1_E1_ACTUAL_JOB_ROOT']).resolve();root=Path(os.environ['MOD4V1_E1_KIT_STORAGE_ROOT']).resolve()
  if root!=job/'kit_isolation' or not root.is_dir():raise ValueError('New ownE1 Kitstorage required')
  self._sim_app_config['enable_crashreporter']=False
  self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false','--portable-root',str(root),'--/app/userConfigPath='+str(root/'data/user.config.json'),'--/UJITSO/datastore/localCachePath='+str(root/'DerivedDataCache')]
  super()._create_app()
