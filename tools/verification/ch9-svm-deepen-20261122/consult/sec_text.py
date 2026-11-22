import re, sys, html
h=open(sys.argv[1],encoding='utf-8').read()
for sid in sys.argv[2:]:
    m=re.search(r'<section id="%s".*?</section>'%sid, h, re.S)
    t=m.group(0)
    t=re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>','',t,flags=re.S)
    t=re.sub(r'<(h[1-4]|summary)[^>]*>',r'\n### ',t)
    t=re.sub(r'<(p|li|tr|div|br)[^>]*>','\n',t)
    t=re.sub(r'<[^>]+>','',t); t=html.unescape(t)
    t=re.sub(r'\n\s*\n+','\n',t)
    print(f'\n################ SECTION {sid} ({len(t)} chars)\n{t}')
