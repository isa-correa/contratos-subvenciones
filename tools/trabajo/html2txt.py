import re,sys,html
for a in sys.argv[1:]:
    s=open(a+'.html',encoding='utf8',errors='ignore').read()
    i=s.find('id="textoxslt"'); s=s[i:] if i>0 else s
    s=re.sub(r'(?is)<(script|style).*?</\1>','',s)
    s=re.sub(r'(?i)</(p|h\d|div|li|tr)>|<br\s*/?>','\n',s)
    s=html.unescape(re.sub(r'<[^>]+>','',s))
    s=re.sub(r'[ \t]+',' ',s); s=re.sub(r'\n\s*\n+','\n',s)
    open(a+'.txt','w',encoding='utf8').write(s)
    print(a,len(s),len(re.findall(r'(?m)^\s*Art[íi]culo\s+(\d+)',s)))
