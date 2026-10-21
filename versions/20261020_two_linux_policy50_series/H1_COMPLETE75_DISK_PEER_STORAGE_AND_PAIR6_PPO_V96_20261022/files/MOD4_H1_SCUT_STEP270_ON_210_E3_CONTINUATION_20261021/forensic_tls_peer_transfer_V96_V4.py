"""Finite storage-only peer transfer: pinned TLS, memory-only HMAC, full SHA.

This module never imports CUDA, Torch, SDK training, or a budget writer.
"""
from pathlib import Path
import fcntl,hashlib,hmac,json,os,re,secrets,socket,ssl,struct,subprocess,sys,threading,time,traceback
import psutil

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def exact(s,n):
    out=bytearray()
    while len(out)<n:
        x=s.recv(n-len(out))
        if not x:raise EOFError('Incomplete authenticated storage stream')
        out.extend(x)
    return bytes(out)
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def send(s,v,key):
    data=encoded(dict(data=v,mac=hmac.new(bytes.fromhex(key),encoded(v),hashlib.sha256).hexdigest()))
    assert len(data)<1024**2;s.sendall(struct.pack('!I',len(data))+data)
def recv(s,key):
    n=struct.unpack('!I',exact(s,4))[0];assert 0<n<1024**2
    v=json.loads(exact(s,n));assert hmac.compare_digest(v['mac'],hmac.new(bytes.fromhex(key),encoded(v['data']),hashlib.sha256).hexdigest()),'Storage authentication rejected'
    return v['data']
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def identity():
    p=psutil.Process();return dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline())
def server_context():
    key=os.memfd_create('mod4-storage-key',0);cert=os.memfd_create('mod4-storage-cert',0)
    try:
        p=subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=MOD4-storage-in-memory','-keyout','/proc/self/fd/'+str(key),'-out','/proc/self/fd/'+str(cert)],pass_fds=(key,cert),capture_output=True,timeout=20)
        assert p.returncode==0,'In-memory TLS certificate generation failed'
        os.lseek(cert,0,0);pem=os.read(cert,65536).decode();fingerprint=hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest()
        ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.minimum_version=ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain('/proc/self/fd/'+str(cert),'/proc/self/fd/'+str(key))
        return ctx,fingerprint
    finally:os.close(key);os.close(cert)
def client(addr,port,pin):
    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT);ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE;ctx.minimum_version=ssl.TLSVersion.TLSv1_2
    raw=socket.create_connection((addr,port),timeout=12);s=ctx.wrap_socket(raw,server_hostname='MOD4-storage-in-memory');s.settimeout(60)
    assert hmac.compare_digest(hashlib.sha256(s.getpeercert(binary_form=True)).hexdigest(),pin),'Exact SSH-delivered TLS certificate pin rejected'
    return s
def cpu_test():
    ctx,pin=server_context();token=secrets.token_hex(32);payload=b'MOD4-storage-CPU-fixture\0'*45000;sha=hashlib.sha256(payload).hexdigest();result={}
    listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(10)
    def server():
        try:
            raw,_=listener.accept()
            with ctx.wrap_socket(raw,server_side=True) as s:
                s.settimeout(10);v=recv(s,token);assert v==dict(bytes=len(payload),SHA=sha)
                assert hashlib.sha256(exact(s,len(payload))).hexdigest()==sha;send(s,dict(SHA=sha,complete=True),token)
                try:recv(s,token)
                except AssertionError:result['wrong_HMAC_rejected']=True
                else:raise AssertionError('Wrong HMAC was accepted')
                result['full_SHA_passed']=True
        except BaseException:result['error']=traceback.format_exc()
        finally:listener.close()
    thread=threading.Thread(target=server);thread.start()
    with client('127.0.0.1',listener.getsockname()[1],pin) as s:
        send(s,dict(bytes=len(payload),SHA=sha),token);s.sendall(payload);assert recv(s,token)==dict(SHA=sha,complete=True)
        bad=encoded(dict(data=dict(untrusted=True),mac='0'*64));s.sendall(struct.pack('!I',len(bad))+bad)
    thread.join(15);assert not thread.is_alive() and result==dict(wrong_HMAC_rejected=True,full_SHA_passed=True),result
    return dict(epoch=time.time(),passed=True,TLS_pin_HMAC_and_actual_stream_SHA_CPU=True,synthetic_bytes=len(payload),wrong_HMAC_rejected=True,private_key_memfd_only_closed=True,openssl_child_waited=True,no_GPU_or_training=True)

def receiver(cfg):
    root=Path(cfg['controller_root']);target=Path(cfg['target']);assert target.is_dir() and target.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals').resolve())
    files={Path(r['path']).name:r for r in cfg['files']};assert len(files)==len(cfg['files'])
    for name,r in files.items():assert re.fullmatch(r'control_prefix_\d+\.npz',name) and 0<r['bytes']<1024**3 and re.fullmatch('[0-9a-f]{64}',r['SHA'])
    import shutil
    assert shutil.disk_usage(target).free>sum(r['bytes'] for r in files.values())+25*1024**3
    ctx,pin=server_context();listener=socket.socket();listener.bind(('0.0.0.0',0));listener.listen(1);listener.settimeout(90)
    receipts=[];ready=dict(epoch=time.time(),identity=identity(),port=listener.getsockname()[1],TLS_certificate_SHA=pin,target=str(target),finite_accept_seconds=90)
    put(root/'RECEIVER_READY_ACTUAL.json',ready);print(json.dumps(ready),flush=True)
    try:
        raw,peer=listener.accept()
        with ctx.wrap_socket(raw,server_side=True) as s:
            s.settimeout(60);hello=recv(s,cfg['token']);assert hello['kind']=='begin' and hello['manifest_SHA']==cfg['manifest_SHA']
            nonce=hello['nonce'];send(s,dict(kind='ready',nonce=nonce),cfg['token']);start=time.monotonic()
            while True:
                assert time.monotonic()-start<1200
                msg=recv(s,cfg['token'])
                if msg['kind']=='end':break
                assert msg['kind']=='file' and msg['name'] in files;row=files[msg['name']]
                assert (msg['bytes'],msg['SHA'])==(row['bytes'],row['SHA']) and msg['name'] not in {r['name'] for r in receipts}
                p=target/msg['name'];assert p.resolve().is_relative_to(target.resolve()) and not p.is_symlink()
                existing=p.exists() and p.stat().st_size==row['bytes'] and digest(p)==row['SHA']
                if existing:send(s,dict(kind='already_complete',name=p.name,SHA=row['SHA']),cfg['token'])
                else:
                    if p.exists():p.rename(p.with_name(p.name+'.preserved_SFTP_prefix_'+str(time.time_ns())))
                    part=p.with_name(p.name+'.direct_partial_'+str(time.time_ns()));send(s,dict(kind='send_data',name=p.name),cfg['token']);h=hashlib.sha256();remaining=row['bytes']
                    with part.open('xb') as f:
                        while remaining:
                            block=exact(s,min(8*1024**2,remaining));f.write(block);h.update(block);remaining-=len(block)
                        f.flush();os.fsync(f.fileno())
                    assert h.hexdigest()==row['SHA'];part.replace(p)
                receipt=dict(name=p.name,path=row['path'],target_path=str(p),bytes=row['bytes'],SHA=row['SHA'],target_full_SHA_verified=True,existing_complete_no_retransfer=existing)
                put(root/('FILE_'+p.name+'.json'),receipt);receipts.append(receipt);send(s,dict(kind='complete',receipt=receipt,nonce=nonce),cfg['token'])
            assert len(receipts)==len(files)
            result=dict(epoch=time.time(),passed=True,files=receipts,peer_IP=peer[0],TLS_pin_HMAC_and_full_SHA=True,all_private_key_and_HMAC_memory_only=True)
            put(root/'RECEIVER_COMPLETE_ACTUAL.json',result);send(s,dict(kind='all_complete',files=len(receipts),manifest_SHA=cfg['manifest_SHA']),cfg['token'])
    except BaseException:
        put(root/'RECEIVER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),verified_prefix=receipts,no_source_deletion_by_receiver=True));raise
    finally:
        listener.close();put(root/'RECEIVER_EXIT_ACTUAL.json',dict(epoch=time.time(),identity=identity(),all_network_sockets_closed=True,no_children_after_waited_openssl=True))

def sender(cfg):
    root=Path(cfg['controller_root']);old=Path(cfg['source_root']);base=old/'job0/production/control_prefix_raw';owner=Path(cfg['owner_root'])
    C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();budget=json.loads(canonical)
    assert budget['active_segment'] is None and budget['authorized_training_seconds']==1548000 and len(budget['budget_extensions'])==8 and budget['remaining_training_seconds']==cfg['remaining']
    assert json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'] and json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
    for q in (old,owner):assert not any(p.pid!=os.getpid() and any(a.startswith(str(q)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
    def guard():
        assert C.read_bytes()==canonical
        for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(cfg['private_lock'])):
            with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
    guard();out=[];import shutil
    before=shutil.disk_usage(old).free
    try:
        with client(cfg['address'],cfg['port'],cfg['TLS_certificate_SHA']) as s:
            nonce=secrets.token_hex(32);send(s,dict(kind='begin',nonce=nonce,manifest_SHA=cfg['manifest_SHA']),cfg['token']);assert recv(s,cfg['token'])==dict(kind='ready',nonce=nonce)
            started=time.monotonic()
            for row in cfg['files']:
                assert time.monotonic()-started<1200
                p=Path(row['path']);assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
                stat=p.stat();assert (stat.st_size,stat.st_mtime_ns,stat.st_ino,stat.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)
                send(s,dict(kind='file',name=p.name,bytes=row['bytes'],SHA=row['SHA']),cfg['token']);response=recv(s,cfg['token'])
                if response['kind']=='send_data':
                    h=hashlib.sha256()
                    with p.open('rb') as f:
                        for block in iter(lambda:f.read(8*1024**2),b''):s.sendall(block);h.update(block)
                    assert h.hexdigest()==row['SHA']
                else:assert response==dict(kind='already_complete',name=p.name,SHA=row['SHA'])
                ack=recv(s,cfg['token']);r=ack['receipt'];assert ack['kind']=='complete' and ack['nonce']==nonce and r['path']==str(p) and r['SHA']==row['SHA'] and r['bytes']==row['bytes'] and r['target_full_SHA_verified']
                guard();stat2=p.stat();assert (stat2.st_size,stat2.st_mtime_ns,stat2.st_ino,stat2.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)
                p.unlink();out.append(r);put(root/('SOURCE_RELEASED_'+p.name+'.json'),dict(epoch=time.time(),receipt=r,canonical_bytes_unchanged=True))
            send(s,dict(kind='end'),cfg['token']);assert recv(s,cfg['token'])==dict(kind='all_complete',files=len(out),manifest_SHA=cfg['manifest_SHA'])
        guard();result=dict(epoch=time.time(),passed=True,identity=identity(),files=out,source_free_before=before,source_free_after=shutil.disk_usage(old).free,bytes=sum(r['bytes'] for r in out),canonical_bytes_unchanged=True,only_target_full_SHA_verified_NPZ_duplicates_removed=True,no_FINAL_model_source_text_or_error_touched=True)
        put(root/'SENDER_COMPLETE_ACTUAL.json',result);return result
    except BaseException:
        put(root/'SENDER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),verified_and_released_prefix=out,all_other_sources_retained=True));raise
    finally:put(root/'SENDER_EXIT_ACTUAL.json',dict(epoch=time.time(),identity=identity(),no_network_or_child_left=True))

def main(cfg):
    if cfg['role']=='CPU':print(json.dumps(cpu_test()))
    elif cfg['role']=='receiver':receiver(cfg)
    elif cfg['role']=='sender':print(json.dumps(sender(cfg)))
    else:raise ValueError('Unknown storage role')
if __name__=='__main__':main(globals().get('CFG') or json.loads(sys.stdin.buffer.readline()))
