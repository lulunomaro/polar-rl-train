from pathlib import Path
import json,time,traceback
from windows4090_transport import connect,powershell
D=Path(__file__).resolve().parent
code=r'''
$OutputEncoding=[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new()
$os=Get-CimInstance Win32_OperatingSystem
$cpu=Get-CimInstance Win32_Processor
$volumes=@(Get-Volume | Select-Object DriveLetter,FileSystemLabel,FileSystem,Size,SizeRemaining,HealthStatus)
$disks=@(Get-Disk | Select-Object Number,FriendlyName,Size,PartitionStyle,OperationalStatus,IsOffline,IsReadOnly)
$partitions=@(Get-Partition | Select-Object DiskNumber,PartitionNumber,DriveLetter,Type,GptType,Size,AccessPaths)
$runtimeCommands=@(Get-Command python,python3,py,uv,conda,nvidia-smi -ErrorAction SilentlyContinue | Select-Object Name,Source)
$gpu=(nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version,utilization.gpu --format=csv,noheader,nounits | Out-String).Trim()
$processes=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|isaac|kit|wsl' } | Select-Object ProcessId,Name,ExecutablePath,CreationDate)
$roots=@{}
foreach($p in @('C:\Users\Win10','C:\Users\Win10\Documents\默认项目','C:\Users\Win10\AppData\Local\Programs','C:\Program Files','D:\','E:\','F:\')) { if(Test-Path -LiteralPath $p){$roots[$p]=@(Get-ChildItem -LiteralPath $p -Force -ErrorAction SilentlyContinue | Select-Object -First 35 Name,FullName,Mode)} }
$result=[ordered]@{timestamp=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();hostname=$env:COMPUTERNAME;username=$env:USERNAME;OS=$os.Caption;version=$os.Version;boot=$os.LastBootUpTime;RAMtotal=$os.TotalVisibleMemorySize*1024;RAMfree=$os.FreePhysicalMemory*1024;CPU=@($cpu | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors);GPU=$gpu;volumes=$volumes;disks=$disks;partitions=$partitions;runtime_commands=$runtimeCommands;actual_runtime_processes=$processes;root_inventory=$roots;read_only=$true;no_GPU_training_or_evaluation_launch=$true;no_Linux_partition_mount=$true}
$result | ConvertTo-Json -Depth 7 -Compress
'''
def main():
 c=connect()
 try:
  raw=powershell(c,code,60);a=json.loads(raw);p=D/'reports'/('WINDOWS4090_HOST_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(a,ensure_ascii=False))
 finally:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'reports'/('WINDOWS4090_READONLY_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_training_GPU_or_OS_mutation=True)),encoding='utf8');raise
