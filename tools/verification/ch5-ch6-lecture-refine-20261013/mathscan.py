import re,sys,collections
from bs4 import BeautifulSoup, NavigableString
PAT=re.compile(r"[₀-₉ₐ-ₜᵢⱼₖₘₙₚ⁰-⁹ᵖᵀᴿⁿ]|[σβαλθρμεφτηγ]̂|[a-zA-Zσβαλθ]̂|‖|²|³|√|\^|\b(?:Cp|log\s?n|log\(n\))\b|R²|[σβαλθρμεφτηγΣΛ]|[≤≥≈→∞×−]|\b[a-zA-Z]\s?[<>=]\s?\d|\b\d+/[a-z]\b|\b[npdkKMBλ]\b")
def scan(path):
    s=BeautifulSoup(open(path).read(),'html.parser')
    for t in s(['script','style','code','pre']): t.decompose()
    for t in s.select('.pseudo-code,.deck-extra,.expected-out,.viz-source'): t.decompose()
    out=collections.Counter(); ex={}
    for node in s.find_all(string=True):
        if isinstance(node,NavigableString):
            txt=str(node)
            # strip $...$ and $$...$$ and \( \)
            stripped=re.sub(r'\$\$.*?\$\$','',txt,flags=re.S)
            stripped=re.sub(r'\$[^$]*\$','',stripped)
            for m in PAT.finditer(stripped):
                k=m.group(0); out[k]+=1
                ex.setdefault(k,[]).append(stripped[max(0,m.start()-25):m.end()+20].replace('\n',' '))
    return out,ex
for f in sys.argv[1:]:
    out,ex=scan(f); print('==',f,sum(out.values()))
    for k,v in out.most_common():
        print(repr(k),v,'|',ex[k][0])
