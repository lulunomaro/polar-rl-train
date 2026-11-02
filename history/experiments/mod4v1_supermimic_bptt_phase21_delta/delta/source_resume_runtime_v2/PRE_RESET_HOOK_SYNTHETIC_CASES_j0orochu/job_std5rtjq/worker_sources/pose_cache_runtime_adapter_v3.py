calls = []
def install_pose_cache_runtime_adapter_v3(robot, *, receipt_callback):
    calls.append(robot)
    receipt_callback({'event': 'installed', 'synthetic_fixture_only': True})
    return {'synthetic_handle': True}
