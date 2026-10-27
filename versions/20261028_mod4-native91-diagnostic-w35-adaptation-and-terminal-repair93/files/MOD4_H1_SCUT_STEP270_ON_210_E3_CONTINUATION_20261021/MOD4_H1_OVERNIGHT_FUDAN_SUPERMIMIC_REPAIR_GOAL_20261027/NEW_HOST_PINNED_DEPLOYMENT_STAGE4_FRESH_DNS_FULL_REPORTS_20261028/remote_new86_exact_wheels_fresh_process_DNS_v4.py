import pathlib,os,sys,json,time,subprocess,signal,traceback,hashlib
R=pathlib.Path('/data/robemo/polar-rl-train');S1=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';RUN=R/'setup_runs/W35_PINNED_ENV_STAGE4_FRESH_DNS_20261028_V4';DEADLINE=time.time()+600 # Bounded after actual auth/upload; no stale absolute deadline.
PINS={'torch':'2.10.0+cu128','torchvision':'0.25.0+cu128','isaacsim':'6.0.1.0','rsl-rl-lib':'5.0.1','numpy':'2.5.2','warp-lang':'1.13.0','tensordict':'0.14.1','scipy':'1.17.0','gymnasium':'1.2.1'}
assert R.resolve()==R and json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
assert (RUN/'SETUP_RUN_OWNER.json').is_file()
env=os.environ.copy()
for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/mpl','PYTHONUSERBASE':'home/.local'}.items():
 p=RUN/rel;assert p.resolve().is_relative_to(R);p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
(RUN/'logs').mkdir();env.update(CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
def emit(stage,**v):print(json.dumps(dict(stage=stage,epoch=time.time(),**v)),flush=True)
def command(label,args):
 assert time.time()<DEADLINE-15,'finite_deadline_before_'+label
 log=RUN/'logs'/str(label+'.log')
 with log.open('xb') as f:
  p=subprocess.Popen(args,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);last=0;timed=False
  emit('OWN_DNS_SHIM_INSTALLER_STARTED',label=label,pid=p.pid,argv=args)
  while p.poll() is None:
   if time.time()>DEADLINE-12:
    timed=True;os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(5)
    break
   if time.time()-last>25:emit('OWN_DNS_SHIM_INSTALLER_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size,remaining_s=round(DEADLINE-time.time(),1));last=time.time()
   time.sleep(1)
  rc=p.wait();emit('OWN_DNS_SHIM_INSTALLER_WAITED',label=label,returncode=rc,deadline_terminated=timed,log_tail=log.read_text(errors='replace')[-4000:])
 if timed:raise TimeoutError('owned_installer_waited_at_deadline')
 if rc:raise RuntimeError('owned_installer_failed_'+label+'_'+str(rc))
# Only this exact official host is resolved by actual publicDNS answers. No URL/TLS hostname alteration.
bootstrap=r"""import socket,runpy,sys,json,time,datetime,ipaddress
from pathlib import Path
responses=json.loads(Path(sys.argv[1]).read_bytes());row=next(r for r in responses if r['server']=='1.1.1.1');answers=row['answers'];ips=[a['IPAddress'] for a in answers if a['Type']==1];ttl=min(a['TTL'] for a in answers if a['Type'] in (1,5));epoch=datetime.datetime.fromisoformat(row['actual_UTC'].replace('Z','+00:00')).timestamp();original=socket.getaddrinfo
assert ips and ttl>0 and all(ipaddress.ip_address(ip).version==4 for ip in ips)
def resolve(host,port,*a,**kw):
 h=host.decode() if isinstance(host,bytes) else host
 if isinstance(h,str) and h.rstrip('.').lower()=='download-r2.pytorch.org':
  global epoch,ttl,ips
  if time.time()>epoch+ttl:
   # Fresh primary DNS query for only the official hostname, to the already audited public resolver's standard DNS service.
   import struct,os,base64
   ident=int.from_bytes(os.urandom(2),'big');name='download-r2.pytorch.org';q=struct.pack('!6H',ident,0x0100,1,0,0,0)+b''.join(bytes([len(x)])+x.encode() for x in name.split('.'))+bytes([0])+struct.pack('!HH',1,1)
   with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as ds:
    ds.settimeout(5);ds.sendto(q,('1.1.1.1',53));raw,peer=ds.recvfrom(4096)
   rid,flags,nq,na,_,_=struct.unpack('!6H',raw[:12]);assert peer[0]=='1.1.1.1' and rid==ident and flags&0x8000 and flags&15==0 and not flags&0x0200
   def dn(pos):
    labels=[];end=None;seen=set()
    while True:
     assert pos not in seen;seen.add(pos);n=raw[pos]
     if n&0xc0==0xc0:
      if end is None:end=pos+2
      pos=((n&63)<<8)|raw[pos+1];continue
     pos+=1
     if n==0:return '.'.join(labels),end if end is not None else pos
     labels.append(raw[pos:pos+n].decode().lower());pos+=n
   pos=12
   for _ in range(nq):qn,pos=dn(pos);assert qn==name;pos+=4
   chain={name};newips=[];ttls=[];records=[]
   for _ in range(na):
    rn,pos=dn(pos);rt,rc,life,sz=struct.unpack('!HHIH',raw[pos:pos+10]);pos+=10;end=pos+sz
    if rn in chain and rc==1:
     if rt==5:cn,_=dn(pos);chain.add(cn);ttls.append(life);records.append({'name':rn,'type':5,'TTL':life,'cname':cn})
     elif rt==1 and sz==4:
      ip=socket.inet_ntoa(raw[pos:end]);assert ipaddress.ip_address(ip).is_global;newips.append(ip);ttls.append(life);records.append({'name':rn,'type':1,'TTL':life,'IP':ip})
    pos=end
   assert newips and min(ttls)>0;ips=newips;ttl=min(ttls);epoch=time.time()
   record={'primary_public_resolver':'1.1.1.1:53','exact_query':name,'epoch':epoch,'TTL':ttl,'answer_records':records,'raw_primary_DNS_base64':base64.b64encode(raw).decode(),'TLS_hostname_and_publishedSHA_unchanged':True}
   Path(sys.argv[1]).parent.joinpath('DNS_FRESH_PRIMARY_'+str(time.time_ns())+'.json').write_text(json.dumps(record,indent=2))
  rows=[]
  for ip in ips:
   try:rows.extend(original(ip,port,*a,**kw))
   except socket.gaierror:pass
  if not rows:raise socket.gaierror('no published address matches requested socket family')
  return rows
 return original(host,port,*a,**kw)
socket.getaddrinfo=resolve
if sys.argv[2]=='DOWNLOAD_EXACT_WHEEL':
 import urllib.request,hashlib,os
 url,destination,expected=sys.argv[3:6];part=Path(destination+'.part');h=hashlib.sha256();total=0;last=time.time()
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 with opener.open(url,timeout=20) as response,part.open('xb') as out:
  assert response.url.startswith('https://download-r2.pytorch.org/')
  while True:
   b=response.read(1024*1024)
   if not b:break
   out.write(b);h.update(b);total+=len(b)
   if time.time()-last>=20:print(json.dumps({'downloaded_bytes':total,'official_URL':url,'TLS_verified':True}),flush=True);last=time.time()
  out.flush();os.fsync(out.fileno())
 assert h.hexdigest()==expected,'published wheel fullSHA mismatch; partial kept'
 assert not Path(destination).exists();part.replace(destination)
 print(json.dumps({'official_URL':url,'bytes':total,'SHA':h.hexdigest(),'TLS_verified':True,'local_wheel':destination}),flush=True)
 raise SystemExit(0)
sys.argv=['pip',*sys.argv[2:]]
runpy.run_module('pip',run_name='__main__')
"""
try:
 emit('STAGE4_ENTERED',deadline_epoch=DEADLINE,process_only_DNS_host='download-r2.pytorch.org',TLS_certificate_and_hostname_validation_unchanged=True,published_wheel_fullSHA_unchanged=True)
 pins=RUN/'EXACT_CRITICAL72_CONSTRAINTS.txt';pins.write_text(''.join(k+'=='+v+chr(10) for k,v in PINS.items()))
 python=str(S1/'venv/bin/python3');pip=[python,'-B','-c',bootstrap,str(RUN/'PUBLIC_DNS_PRIMARY_A_TTL_SOURCE.json'),'--isolated','--disable-pip-version-check','--cache-dir',str(S1/'cache/pip'),'install','--no-clean','--no-input','--retries','0','--timeout','20','-c',str(pins)]
 torch='https://download-r2.pytorch.org/whl/cu128/torch-2.10.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl#sha256=628e89bd5110ced7debee2a57c69959725b7fbc64eab81a39dd70e46c7e28ba5';vision='https://download-r2.pytorch.org/whl/cu128/torchvision-0.25.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl#sha256=1255a0ca2bf987acf9f103b96c5c4cfe3415fc4a1eef17fa08af527a04a4f573'
 wheelhouse=RUN/'wheelhouse';wheelhouse.mkdir()
 torchfile=wheelhouse/'torch-2.10.0+cu128-cp312-cp312-manylinux_2_28_x86_64.whl';visionfile=wheelhouse/'torchvision-0.25.0+cu128-cp312-cp312-manylinux_2_28_x86_64.whl'
 command('download_official_Torch_exact_DNS_TLS_SHA',[python,'-B','-c',bootstrap,str(RUN/'PUBLIC_DNS_PRIMARY_A_TTL_SOURCE.json'),'DOWNLOAD_EXACT_WHEEL',torch.split('#')[0],str(torchfile),torch.split('sha256=')[1]])
 command('download_official_vision_exact_DNS_TLS_SHA',[python,'-B','-c',bootstrap,str(RUN/'PUBLIC_DNS_PRIMARY_A_TTL_SOURCE.json'),'DOWNLOAD_EXACT_WHEEL',vision.split('#')[0],str(visionfile),vision.split('sha256=')[1]])
 command('Torch_exact_local_verified_wheels',pip+['--index-url','https://pypi.org/simple',str(torchfile),str(visionfile)])
 command('Sim_RSL_exact',pip+['--extra-index-url','https://pypi.nvidia.com','isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.5.2','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1'])
 command('Lab_exact72_source',pip+['--no-build-isolation','--extra-index-url','https://pypi.nvidia.com','-e',str(S1/'sdk/source/isaaclab'),'-e',str(S1/'sdk/source/isaaclab_rl')])
 code="import importlib.metadata as m,json;v={k:m.version(k) for k in "+repr(list(PINS))+"};assert v=="+repr(PINS)+";print(json.dumps(v))";command('Final_package_metadata_only',[python,'-B','-c',code])
 (RUN/'STAGE4_PACKAGE_INSTALL_PASSED_ACTUAL.json').write_text(json.dumps(dict(passed=True,actual_SDK_CUDA_model_PPO_pending=True,no_GPU_or_GO=True),indent=2));emit('PINNED_PACKAGE_INSTALL_PASSED',actual_SDK_CUDA_model_PPO_pending=True)
except BaseException as e:
 value=dict(passed=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),partial_preserved=True,no_wrongversion_or_system_DNS_change=True)
 (RUN/'STAGE4_ORIGINAL_ERROR_ACTUAL.json').write_text(json.dumps(value,indent=2));emit('STAGE4_ORIGINAL_ERROR',**value);sys.exit(2)
finally:emit('STAGE4_FINITE_RETURNING',no_GPU_GO_ledger_or_system_DNS_write=True)
