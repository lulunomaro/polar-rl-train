"""Source captured after the initial inline tool execution; retained only, never rerun."""
import socket, json, time
from concurrent.futures import ThreadPoolExecutor

def probe(endpoint):
 host,port=endpoint;out={'host':host,'port':port,'started_epoch':time.time()}
 try:
  with socket.create_connection((host,port),timeout=6) as s:
   out['tcp_connected']=True
   s.settimeout(4)
   try:out['banner']=s.recv(256).decode('utf-8',errors='replace')
   except socket.timeout:out['banner_read_timeout']=True
 except Exception as e:out.update(tcp_connected=False,error_type=type(e).__name__,error=str(e))
 out['finished_epoch']=time.time();return out
with ThreadPoolExecutor(max_workers=1) as ex:
 for row in ex.map(probe,[('10.24.5.27',4090)]):print(json.dumps(row,ensure_ascii=False))
