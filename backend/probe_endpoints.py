import json
import urllib.request
from urllib.error import URLError, HTTPError

with open('openapi.json','r',encoding='utf-8-sig') as f:
    spec=json.load(f)

base='http://127.0.0.1:8001'
lines=[]
for path, methods in spec.get('paths',{}).items():
    for method, info in methods.items():
        entry=f"{method} {path}"
        # skip if operation has requestBody
        if 'requestBody' in info:
            lines.append(f"{method} {path} => SKIP (requires body)")
            continue
        # prepare URL: replace path params with '1'
        url=base+path
        while '{' in url and '}' in url:
            start=url.find('{')
            end=url.find('}',start)
            url = url[:start] + '1' + url[end+1:]
        try:
            req=urllib.request.Request(url, method=method.upper())
            with urllib.request.urlopen(req, timeout=5) as r:
                status=r.getcode()
                lines.append(f"{method} {path} => {status}")
        except HTTPError as e:
            lines.append(f"{method} {path} => ERROR {e.code}")
        except URLError as e:
            lines.append(f"{method} {path} => ERR {e.reason}")
        except Exception as e:
            lines.append(f"{method} {path} => ERR {e}")

with open('endpoint_report.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Wrote backend/endpoint_report.txt')
