"""Deferred owned callbacks: original module loader and normal startup order."""
import importlib.abc
import importlib.machinery
import sys

class AfterModule(importlib.abc.Loader):
    def __init__(self, loader, callback): self.loader=loader;self.callback=callback
    def create_module(self, spec):
        return self.loader.create_module(spec) if hasattr(self.loader,'create_module') else None
    def exec_module(self, module):
        self.loader.exec_module(module)
        self.callback(module)

class OwnedDeferred(importlib.abc.MetaPathFinder):
    def __init__(self, callbacks):
        assert not any(name in sys.modules for name in callbacks)
        self.callbacks=dict(callbacks)
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.callbacks:return None
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        assert spec and spec.loader and hasattr(spec.loader,'exec_module')
        callback=self.callbacks.pop(fullname)
        spec.loader=AfterModule(spec.loader,callback)
        if not self.callbacks:sys.meta_path.remove(self)
        return spec

def install(callbacks):
    finder=OwnedDeferred(callbacks);sys.meta_path.insert(0,finder);return finder

def own_launcher(module):
    base=module.AppLauncher
    class OwnedLauncher(base):
        def _create_app(self):
            # Public SimulationApp launch setting only. Avoid a fatal crash
            # waiting in the external dump uploader; stderr/faulthandler remain.
            before=dict(self._sim_app_config)
            self._sim_app_config['enable_crashreporter']=False
            assert all(self._sim_app_config[k]==v for k,v in before.items() if k!='enable_crashreporter')
            print('[owned-launch] Only crashreporter plugin disabled; original simulation settings retained',flush=True)
            return super()._create_app()
    module.AppLauncher=OwnedLauncher
