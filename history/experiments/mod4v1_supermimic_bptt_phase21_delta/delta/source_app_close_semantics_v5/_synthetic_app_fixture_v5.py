"""OWN CPU FIXTURE ONLY, not an SDK class/source or native binding receipt."""
import os


class ForbiddenSDKProxy:
    def __getattr__(self, name):
        raise AssertionError('unexpected SDK getter in pure CPU fixture: ' + name)


class FakeApp:
    def __init__(self, behavior='return', *, fast_shutdown=True, log=None):
        self.config = {'fast_shutdown': fast_shutdown, 'unchanged_fixture_entry': 17}
        self.behavior = behavior
        self.log = [] if log is None else log
        self.calls = 0
        self.return_value = object()
        self._app = ForbiddenSDKProxy()

    def close(self):
        self.calls += 1
        self.log.append('app')
        if self.behavior == 'exit_zero':
            os._exit(0)
        if self.behavior == 'exit_seven':
            os._exit(7)
        if self.behavior == 'raise':
            raise RuntimeError('synthetic original App.close raised')
        if self.behavior == 'system_exit_zero':
            raise SystemExit(0)
        return self.return_value
