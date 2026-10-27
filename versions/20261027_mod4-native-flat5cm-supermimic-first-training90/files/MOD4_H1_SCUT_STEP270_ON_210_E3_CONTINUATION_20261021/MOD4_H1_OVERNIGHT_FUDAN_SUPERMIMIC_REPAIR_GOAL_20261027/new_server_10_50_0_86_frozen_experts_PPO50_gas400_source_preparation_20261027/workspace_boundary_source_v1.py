"""New-host filesystem contract only. Import performs no host or file operation."""
from pathlib import Path,PurePosixPath
ROOT='/data/robemo/polar-rl-train'
MARKER='.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json'
def relative_path(value):
 if not isinstance(value,str) or not value or '\\' in value or '\x00' in value:raise ValueError('explicit POSIX relative path required')
 p=PurePosixPath(value)
 if p.is_absolute() or p==PurePosixPath('.') or '..' in p.parts:raise ValueError('path leaves new workspace')
 return p
def resolve_fresh_target(relative):
 """Future target-host call only; does not mkdir/open/write/rename anything."""
 base=Path(ROOT).resolve(strict=True)
 if base!=Path(ROOT):raise ValueError('literal authorized root resolves elsewhere')
 p=base.joinpath(*relative_path(relative).parts)
 resolved=p.resolve(strict=False)
 if resolved==base or not resolved.is_relative_to(base):raise ValueError('resolved target leaves authorized root')
 if p.exists() or p.is_symlink():raise FileExistsError('new paths only; preserve existing files, including partials')
 return p
def filesystem_environment(selected_GPU_UUID=None):
 """Process-only locations; caller first proves root ownership/resolved boundary.

 No profile/system environment, package installation or directory is changed.
 SDK-specific extra write locations still need actual target source admission.
 """
 gpu='' if selected_GPU_UUID is None else selected_GPU_UUID
 if not isinstance(gpu,str) or gpu and not gpu.startswith('GPU-'):raise ValueError('actual selected UUID, never an index/all-devices default')
 return dict(HOME=ROOT+'/home',TMPDIR=ROOT+'/tmp',TMP=ROOT+'/tmp',TEMP=ROOT+'/tmp',
  XDG_CACHE_HOME=ROOT+'/cache/xdg',XDG_CONFIG_HOME=ROOT+'/config',XDG_DATA_HOME=ROOT+'/data',XDG_STATE_HOME=ROOT+'/state',
  PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=ROOT+'/cache/pycache',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',
  PIP_CACHE_DIR=ROOT+'/cache/pip',CONDA_PKGS_DIRS=ROOT+'/cache/conda_packages',TORCH_HOME=ROOT+'/cache/torch',
  CUDA_CACHE_PATH=ROOT+'/cache/cuda',TRITON_CACHE_DIR=ROOT+'/cache/triton',HF_HOME=ROOT+'/cache/huggingface',
  MPLCONFIGDIR=ROOT+'/config/matplotlib',WANDB_DIR=ROOT+'/logs/wandb',WANDB_CACHE_DIR=ROOT+'/cache/wandb',
  CUDA_VISIBLE_DEVICES=gpu)
def classify_root_metadata(probe,expected_marker):
 """Read an actual probe receipt, not the filesystem. Never admit a GPU job."""
 if probe['host']!='10.50.0.86' or probe['username']!='robemo':raise ValueError('wrong authorized host/account')
 if probe['requested_root']!=ROOT or probe['resolved_root']!=ROOT:raise ValueError('scope/path mismatch')
 if probe['exists_before']:
  if probe.get('existing_our_marker')!=expected_marker:raise ValueError('existing root not owned by this manifest; no overwrite')
  return 'existing_our_workspace_metadata_only'
 if probe.get('created_now') is not True or probe.get('exists_after') is not True:raise ValueError('new mkdir result not established')
 return 'new_root_created_by_current_authorized_probe_metadata_only'
