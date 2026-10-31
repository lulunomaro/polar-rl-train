"""Isolated Kit paths for this exact new task; no global cache/cooking change."""
from pathlib import Path
import os
from isaaclab.app import AppLauncher
class Zonglin2AppLauncher(AppLauncher):
 def _create_app(self):
  root=Path(os.environ['MOD4_188_OWN_KIT_ROOT']).resolve();job=Path(os.environ['MOD4_188_JOB_ROOT']).resolve()
  assert root.is_relative_to(job) and root.name=='kit_isolation' and root.is_dir()
  self._sim_app_config['enable_crashreporter']=False
  self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false','--portable-root',str(root),'--/app/userConfigPath='+str(root/'data/user.config.json'),'--/UJITSO/datastore/localCachePath='+str(root/'DerivedDataCache')]
  super()._create_app()
