from pathlib import Path
import hashlib,json,os,time,traceback,urllib.request,zipfile
D=Path(__file__).resolve().parent
OUT=D/'cpu_http_interface_wheels'
def main():
    assert not OUT.exists();OUT.mkdir();rows=[]
    for name,v in [('httpx','0.28.1'),('httpcore','1.0.9')]:
        url='https://pypi.org/pypi/'+name+'/'+v+'/json'
        with urllib.request.urlopen(url,timeout=20) as f:m=json.load(f)
        a=[x for x in m['urls'] if x['filename']==name+'-'+v+'-py3-none-any.whl'];assert len(a)==1
        row=a[0];assert row['size']<2_000_000 and row['url'].startswith('https://files.pythonhosted.org/')
        p=OUT/row['filename']
        with urllib.request.urlopen(row['url'],timeout=30) as src,p.open('xb') as f:f.write(src.read());f.flush();os.fsync(f.fileno())
        sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==row['digests']['sha256'] and p.stat().st_size==row['size']
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
        rows.append(dict(name=name,version=v,path=str(p),bytes=p.stat().st_size,sha256=sha,published_primary_metadata=url))
    result=dict(epoch=time.time(),passed=True,CPU_download_only=True,no_TLS_verification_disabled=True,no_installed_packages_or_GPU_changed=True,files=rows)
    (OUT/'OFFICIAL_TEST_WHEEL_MANIFEST.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('HTTP_TEST_LOCAL_DOWNLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_old_install_replay=True),indent=2),encoding='utf8')
        raise
