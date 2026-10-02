"""Resumable, sha256-verified downloader for the NVIDIA extscache wheels.

uv/pip install these through a `wheel_stub` build backend that downloads the real wheel
from pypi.nvidia.com at build time; in this environment that download kept arriving
truncated ("Downloaded wheel and sha256 don't match").  Fetching them ourselves with HTTP
Range resume + an explicit sha256 check, then installing the local file, sidesteps it."""
import hashlib, os, re, subprocess, time, urllib.request

DEST = r"D:/tmp/nvwhl"
VENV_PY = r"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe"
UV = r"C:/Users/lulunomaro/.local/bin/uv.exe"
PKGS = ("isaacsim-extscache-kit", "isaacsim-extscache-kit-sdk", "isaacsim-extscache-physics")
os.makedirs(DEST, exist_ok=True)


def resolve():
    out = {}
    for pkg in PKGS:
        t = urllib.request.urlopen("https://pypi.nvidia.com/%s/" % pkg, timeout=120).read().decode("utf-8", "replace")
        for href in re.findall(r'href="([^"]+)"', t):
            base = href.split("/")[-1].split("#")[0]
            if "6.0.1.0" in base and "cp312" in base and "win_amd64" in base:
                url = href.split("#")[0]
                if not url.startswith("http"):
                    # PEP 503: hrefs are relative to the index page for THIS package name
                    url = "https://pypi.nvidia.com/%s/%s" % (pkg, url.split("/")[-1])
                sha = re.search(r"sha256=([0-9a-f]{64})", href)
                out[base] = (url, sha.group(1) if sha else None)
    return out


def fetch(url, path, size):
    pos = os.path.getsize(path) if os.path.exists(path) else 0
    for attempt in range(60):
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=%d-" % pos} if pos else {})
            with urllib.request.urlopen(req, timeout=300) as r, open(path, "ab" if pos else "wb") as fh:
                if pos and r.status != 206:
                    pos = 0
                    fh.seek(0)
                    fh.truncate(0)
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    fh.write(b)
                    pos += len(b)
                    if pos % (128 << 20) < (1 << 20):
                        print("   %s: %.0f/%.0f MB" % (os.path.basename(path), pos / 1e6, (size or 1) / 1e6), flush=True)
            if size and pos < size:
                raise IOError("short read %d/%d" % (pos, size))
            return True
        except Exception as e:
            print("   retry %d (%s) at %.0f MB" % (attempt, str(e)[:70], pos / 1e6), flush=True)
            time.sleep(3)
    return False


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


todo = resolve()
print("wheels found on the NVIDIA index:", len(todo), flush=True)
for fn, (url, sha) in sorted(todo.items()):
    p = os.path.join(DEST, fn)
    try:
        size = int(urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=90).headers.get("Content-Length", 0))
    except Exception:
        size = 0
    print("\n%s  %.2f GB" % (fn, size / 1e9), flush=True)
    if os.path.exists(p) and sha and sha256(p) == sha:
        print("   already verified", flush=True)
    else:
        if not fetch(url, p, size):
            print("   DOWNLOAD FAILED", flush=True)
            continue
        got = sha256(p)
        ok = (got == sha)
        print("   sha256 %s vs %s -> %s" % (got[:16], (sha or "")[:16], "MATCH" if ok else "MISMATCH"), flush=True)
        if not ok:
            os.remove(p)
            continue
    r = subprocess.run([UV, "pip", "install", "--python", VENV_PY, "--no-deps", p], capture_output=True, text=True)
    print("   install rc=%s %s" % (r.returncode, (r.stderr or r.stdout or "")[-200:]), flush=True)
print("\nDONE", flush=True)
