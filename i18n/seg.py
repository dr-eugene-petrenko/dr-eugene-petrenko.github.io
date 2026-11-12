import re,json,pathlib,sys
CYR=re.compile(r'[А-Яа-яЄєІіЇїҐґ]')
def split(h):
    """yield (kind, start, end) segments of translatable text"""
    segs=[]
    for m in re.finditer(r'<(style|script)\b[^>]*>(.*?)</\1>',h,re.S):
        if m.group(1)=='script':
            body_start=m.start(2)
            for s in re.finditer(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\]|\\.)*)`",m.group(2)):
                g=next(i for i in (1,2,3) if s.group(i) is not None)
                if CYR.search(s.group(g)): segs.append(('js',body_start+s.start(g),body_start+s.end(g)))
    mask=re.sub(r'<(style|script)\b[^>]*>.*?</\1>',lambda m:' '*len(m.group(0)),h,flags=re.S)
    for m in re.finditer(r'>([^<]+)<',mask):
        t=m.group(1)
        if CYR.search(t):
            l=len(t)-len(t.lstrip());r=len(t.rstrip())
            segs.append(('t',m.start(1)+l,m.start(1)+r))
    for m in re.finditer(r'''\b(alt|title|placeholder|aria-label|content|data-[\w-]+|value)=("([^"]*)"|'([^']*)')''',mask):
        v=m.group(3) if m.group(3) is not None else m.group(4)
        if v and CYR.search(v):
            st=m.start(3) if m.group(3) is not None else m.start(4)
            segs.append(('a',st,st+len(v)))
    segs.sort(key=lambda x:x[1])
    return segs
if __name__=='__main__':
    out={}
    for f in sorted(pathlib.Path('src/pages').glob('*.html')):
        if f.name.endswith('.head.html'): continue
        h=f.read_text('utf-8');seen=[];ss=set()
        for k,a,b in split(h):
            s=h[a:b]
            if s not in ss: ss.add(s);seen.append(s)
        out[f.stem]=seen
    json.dump(out,open(pathlib.Path(__file__).parent/'uk.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    for k,v in out.items(): print(k,len(v),sum(map(len,v)))
