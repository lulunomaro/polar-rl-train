"""Same authorized zstd session in memory; one new read-only target, old filters unchanged."""
from pathlib import Path
import importlib.util, runpy, sys

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]
ORIGINAL_WRAPPER = W / "MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py"

def main():
    target = Path(sys.argv[1]).resolve()
    assert target.parent == HERE
    assert target.name == "read_249_GPU_UUID_and_existing_SDK_metadata_finite_v1.py"
    spec = importlib.util.spec_from_file_location("existing_compressed_session_setup_only", ORIGINAL_WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    transport, previous = module.install()
    try:
        sys.argv = [str(target), *sys.argv[2:]]
        runpy.run_path(str(target), run_name="__main__")
    finally:
        transport.SESSION = previous

if __name__ == "__main__":
    main()
