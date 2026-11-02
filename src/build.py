#!/usr/bin/env python3
"""inline assets/ into src/rhw_template.html -> dist/index.html (LEVEE JAW build contract: /*__ASSET:name__*/ -> data: URI;
   a key 'x.png' also accepts assets/x.webp; a missing file -> empty string, the page falls back)"""
import base64, os, re
R = '/workspace/rhw'
s = open(f'{R}/src/rhw_template.html', encoding='utf-8').read()
MIME = {'.png': 'image/png', '.webp': 'image/webp', '.woff2': 'font/woff2', '.mp3': 'audio/mpeg', '.bin': 'application/octet-stream', '.jpg': 'image/jpeg'}
miss = []
def sub(m):
    n = m.group(1); p = f'{R}/assets/{n}'
    if not os.path.exists(p): p = os.path.splitext(p)[0] + '.webp'
    if not os.path.exists(p): miss.append(n); return ''
    return f'data:{MIME[os.path.splitext(p)[1]]};base64,' + base64.b64encode(open(p, 'rb').read()).decode()
s = re.sub(r'/\*__ASSET:([^_*]+?)__\*/', sub, s)
os.makedirs(f'{R}/dist', exist_ok=True)
open(f'{R}/dist/index.html', 'w', encoding='utf-8').write(s)
open(f'{R}/dist/.nojekyll', 'w').close()
print('dist/index.html', round(os.path.getsize(f'{R}/dist/index.html') / 1e6, 2), 'MB; missing (fallback):', miss)
