"""Read-only HTML link selection from the already-fetched official Keil TOC, no network/code execution."""
from pathlib import Path
import re,html,json,hashlib,urllib.parse
O=Path(__file__).resolve().parent
p=Path(r'C:\Users\lulu\AppData\Local\Temp\dsh-spill-N99Hsy\session-de481967f16c\47eb8e86fb36-web_fetch.txt')
b=p.read_bytes();assert len(b)<1048576
s=b.decode('utf-8');out=[]
for href,body in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',s,re.I|re.S):
 t=html.unescape(re.sub(r'<[^>]*>',' ',body)).strip()
 if any(w in t for w in ['--apcs','--cpu','--fpu','PRESERVE8','REQUIRE8']):
  url=urllib.parse.urljoin('https://www.keil.com/support/man/docs/ARMASM/default.htm',html.unescape(href));assert urllib.parse.urlparse(url).hostname=='www.keil.com';out.append(dict(text=t,URL=url))
r=dict(source_URL='https://www.keil.com/support/man/docs/ARMASM/default.htm',formatted_web_fetch_path=str(p),formatted_web_fetch_bytes=len(b),formatted_web_fetch_SHA=hashlib.sha256(b).hexdigest(),not_raw_HTTP_body_or_commit_SHA=True,selected_links=out)
with (O/'PRIMARY_OPTION_LINKS_01.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(r,ensure_ascii=False))
