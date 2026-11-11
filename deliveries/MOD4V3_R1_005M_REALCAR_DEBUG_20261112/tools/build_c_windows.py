"""Build the reference DLL/CLI using installed MSVC. No hardware access."""
from pathlib import Path
import os,subprocess,shutil,json
B=Path(__file__).resolve().parents[1];dest=B/'bin/windows-x64';dest.mkdir(parents=True,exist_ok=True)
result=subprocess.run(['cmd','/d','/c',r'D:\VS2022\VC\Auxiliary\Build\vcvars64.bat >nul && set'],capture_output=True,encoding='utf-8',errors='replace',check=True);env=dict(os.environ)
for line in result.stdout.splitlines():
 if '=' in line:
  k,v=line.split('=',1)
  if k.upper() in ('PATH','INCLUDE','LIB','LIBPATH'):env[k]=v
cc=shutil.which('cl.exe',path=env.get('Path',env.get('PATH','')));assert cc
commands=[[cc,'/nologo','/O2','/fp:precise','/std:c11','/LD',str(B/'firmware/mod4_runtime.c'),'/link','/OUT:'+str(dest/'mod4_runtime.dll')],[cc,'/nologo','/O2','/fp:precise','/std:c11',str(B/'firmware/mod4_runtime.c'),str(B/'firmware/stdio_example.c'),'/Fe:'+str(dest/'mod4_stdio.exe')]];logs=[]
for cmd in commands:
 p=subprocess.run(cmd,cwd=dest,env=env,capture_output=True,encoding='utf-8',errors='replace');logs.append(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,(p.stdout,p.stderr)
(B/'evidence/C_BUILD.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('C_REFERENCE_COMPILED',flush=True)
