from pathlib import Path
import subprocess,base64,json,time,traceback
import windows4090_native_transport as transport
D=Path(__file__).resolve().parent
CODE=r'''$r='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';$rows=@();foreach($f in @(Get-ChildItem -LiteralPath (Join-Path $r 'install_reports') -File -ErrorAction SilentlyContinue|Where-Object{$_.Name -match 'SUBPROCESS|COMPLETE|FAIL|OFFLINE|ENDED'}|Sort-Object LastWriteTimeUtc|Select-Object -Last 12)){$b=[IO.File]::ReadAllBytes($f.FullName);$txt=[Text.Encoding]::UTF8.GetString($b);try{$v=$txt|ConvertFrom-Json}catch{$v=$null};$rows+=@{name=$f.Name;bytes=$b.Length;content=$v}};[pscustomobject]@{epoch=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds();hostname=$env:COMPUTERNAME;username=$env:USERNAME;reports=$rows;Python_present=Test-Path -LiteralPath (Join-Path $r 'env/python.exe');no_mutation=$true}|ConvertTo-Json -Depth 9 -Compress'''
def main():
 transport.connect() # Validate saved Windows hostkey digest; no network call.
 stamp=str(time.time_ns());attempts=[];result=None
 enc=base64.b64encode(CODE.encode('utf-16-le')).decode()
 for host in ('10.24.4.210','172.27.131.74'):
  argv=[v.replace('ConnectTimeout=15','ConnectTimeout=6') for v in transport.base()]
  argv+=['-o','HostKeyAlias=10.24.4.210','Win10@'+host,'powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc]
  t=time.time()
  try:
   p=subprocess.run(argv,capture_output=True,timeout=30)
   row=dict(host=host,seconds=time.time()-t,exitcode=p.returncode,stderr=p.stderr.decode('utf8','replace'),pinned_to_existing_Windows_hostkey=True,no_retry_loop=True)
   attempts.append(row)
   if p.returncode==0:
    result=json.loads(p.stdout.decode('utf-8-sig').strip());assert result['hostname']=='DESKTOP-J17LAN1' and result['username'].lower()=='win10'
    row['authenticated_expected_Windows_host']=True;break
  except Exception as e:attempts.append(dict(host=host,seconds=time.time()-t,error=repr(e),no_retry_loop=True))
 out=dict(epoch=time.time(),attempts=attempts,actual=result,successful_host=attempts[-1]['host'] if result else None,no_GPU_or_service_or_network_setting_or_installer_mutation=True)
 path=D/'reports'/('WINDOWS4090_SINGLE_PINNED_LAN_ZT_READONLY_ACTUAL_'+stamp+'.json');path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
