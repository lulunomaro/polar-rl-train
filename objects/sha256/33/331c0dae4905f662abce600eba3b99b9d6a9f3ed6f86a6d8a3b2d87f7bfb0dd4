import io,os,shutil,subprocess,sys
ROOT=r"D:\claude2\fangzhen"
src=io.open(os.path.join(ROOT,"scripts","build_cc.py"),encoding="utf-8").read()
buggy=src.replace('            fine_f = os.path.join(FINE, "meshes", s["obj"])',
                  '            fine_f = os.path.join(FINE, "meshes", obj)')
assert buggy!=src, "negative-test anchor missed"
dst=os.path.join(ROOT,"scripts","_neg_build.py")
io.open(dst,"w",encoding="utf-8").write(buggy)
env=dict(os.environ); env["TMP"]=env["TEMP"]=env["TMPDIR"]=r"D:\tmp"; env["PYTHONIOENCODING"]="utf-8"
r=subprocess.run([sys.executable,dst],capture_output=True,text=True,env=env,cwd=ROOT)
tail=(r.stdout or "").strip().splitlines()[-3:] + (r.stderr or "").strip().splitlines()[-4:]
print("returncode",r.returncode)
for l in tail: print("   ",l[:150])
assert r.returncode!=0 and "COARSE id" in (r.stderr or ""), "GUARD DID NOT FIRE"
print("NEGATIVE TEST PASSED: the guard rejects the old FINE-via-COARSE-id bug")