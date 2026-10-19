"""Read-only OS identity through the pre-existing strict Windows host pin; no key replacement."""
from pathlib import Path
import base64,hashlib,importlib.util,json,os,sys,time,traceback,paramiko
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not (R/'TRUSTED_WINDOWS_210_IDENTITY_READER_STARTED_ACTUAL.json').exists()
 pinned=Path.home()/'.ssh/known_hosts_mod4_4090_windows_20261013';keys=paramiko.HostKeys(str(pinned));key=keys.lookup('10.24.4.210')['ssh-ed25519'];observed='AAAAC3NzaC1lZDI1NTE5AAAAIARKX4W0a+cv2qT3VY8ksfIVujgjNp73n22S1nXh9a28';assert key.asbytes()==base64.b64decode(observed);fingerprint='SHA256:'+base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
 put('TRUSTED_WINDOWS_210_IDENTITY_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,pre_existing_same_host_Windows_pin_matches_observed_new_key=True,fingerprint=fingerprint,known_hosts_not_modified=True,actual_alive_only_exclusive_all_training_transport=True))
 path=W/'MOD4_4090_WINDOWS_REPAIR_20261013/windows4090_native_transport.py';sp=importlib.util.spec_from_file_location('existing_windows_pin_transport_readonly',path);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
 code="[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); $os = Get-CimInstance Win32_OperatingSystem; [ordered]@{epoch_utc=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();computer=$env:COMPUTERNAME;username=[Environment]::UserName;caption=$os.Caption;version=$os.Version;last_boot=$os.LastBootUpTime.ToString('o');gpu=((& nvidia-smi.exe --query-gpu=uuid,memory.free --format=csv,noheader,nounits) -join [Environment]::NewLine);wsl_running=((& wsl.exe --list --running --quiet 2>&1) -join [Environment]::NewLine)} | ConvertTo-Json -Depth 4"
 out=module.powershell(None,code,timeout=60);put('TRUSTED_WINDOWS_210_CURRENT_OS_IDENTITY_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,pre_existing_pin=fingerprint,actual=json.loads(out),raw_stdout=out,strict_host_key_checking_yes=True,original_Linux_knownhost_untouched=True,no_training_task_native_GPU_or_budget_write=True));print(out,flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('TRUSTED_WINDOWS_210_IDENTITY_READER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_hostkey_replacement_or_training_or_budget_write=True));raise
