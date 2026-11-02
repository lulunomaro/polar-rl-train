"""Original proven boot-time storage isolation, bound to a NEW root-owned job."""
from pathlib import Path
import os
from isaaclab.app import AppLauncher


class IsolatedAppLauncher208(AppLauncher):
    def _create_app(self):
        job = Path(os.environ['MOD4_NEW208_JOB_ROOT']).resolve()
        root = Path(os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']).resolve()
        if root != job / 'kit_isolation' or not root.is_dir():
            raise ValueError('Actual NEW208 job-only Kit storage required')
        self._sim_app_config['enable_crashreporter'] = False
        self._sim_app_config['extra_args'] = [
            '--/crashreporter/preserveDump=true', '--/crashreporter/enabled=false',
            '--/app/renderer/enabled=false', '--/renderer/enabled=false',
            '--/app/window/enabled=false', '--portable-root', str(root),
            '--/app/userConfigPath=' + str(root / 'data/user.config.json'),
            '--/UJITSO/datastore/localCachePath=' + str(root / 'DerivedDataCache')]
        super()._create_app()
