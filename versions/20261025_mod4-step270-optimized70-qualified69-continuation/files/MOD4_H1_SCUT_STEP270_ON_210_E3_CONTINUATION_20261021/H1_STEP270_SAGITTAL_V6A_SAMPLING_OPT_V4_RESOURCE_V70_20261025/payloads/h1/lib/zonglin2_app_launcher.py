from isaaclab.app import AppLauncher
class Zonglin2AppLauncher(AppLauncher):
 def _create_app(self):
  self._sim_app_config["enable_crashreporter"] = False
  self._sim_app_config["extra_args"] = ["--/crashreporter/preserveDump=true", "--/crashreporter/enabled=false", "--/app/renderer/enabled=false", "--/renderer/enabled=false", "--/app/window/enabled=false"]
  super()._create_app()
