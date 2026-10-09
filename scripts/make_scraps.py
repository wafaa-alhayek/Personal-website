import sys,random,math
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import numpy as np
out=sys.argv[1]
def torn_mask(w,h,seed,amp=0.035):
    r=random.Random(seed);m=Image.new("L",(w,h),0);d=ImageDraw.Draw(m)
    def edge(n,base,a):
        # low-frequency wander + fine fibre jitter, kept inside +-a
        k=[r.uniform(-1,1) for _ in range(8)];pts=[]
        for i in range(n+1):
            t=i/n;lf=sum(k[j]*math.sin((j+1)*math.pi*t+k[(j+3)%8]*3)/(j+1) for j in range(8))*0.45
            pts.append(base+(lf+r.uniform(-.35,.35))*a)
        return pts
    n=320;ax=amp*min(w,h);ay=ax
    top=edge(n,ay*1.5,ay);bot=edge(n,h-ay*1.5,ay);lef=edge(n,ax*1.5,ax);rig=edge(n,w-ax*1.5,ax)
    X=lambda i:ax*1.5+(w-3*ax)*i/n; Y=lambda i:ay*1.5+(h-3*ay)*i/n
    poly=[(X(i),top[i]) for i in range(n+1)]+[(rig[i],Y(i)) for i in range(n+1)]+[(X(n-i),bot[n-i]) for i in range(n+1)]+[(lef[n-i],Y(n-i)) for i in range(n+1)]
    d.polygon(poly,fill=255);return m.filter(ImageFilter.GaussianBlur(0.8))
def paper(w,h,rgb,seed,fib=10):
    rs=np.random.RandomState(seed)
    base=np.ones((h,w,3))*np.array(rgb,float)
    n=rs.normal(0,1,(h//4+1,w//4+1));n=np.kron(n,np.ones((4,4)))[:h,:w]
    fine=rs.normal(0,1,(h,w))
    base+= (n*fib*0.6+fine*fib*0.4)[...,None]
    im=Image.fromarray(np.clip(base,0,255).astype("uint8"))
    return im
def fiber_rim(im,mask):
    # whitish torn fibre rim
    inner=mask.filter(ImageFilter.MinFilter(7))
    rim=ImageChops.subtract(mask,inner)
    white=Image.new("RGB",im.size,(240,236,226))
    im.paste(white,(0,0),rim.point(lambda v:int(v*.85)))
    return im
def save(im,mask,name):
    im=im.convert("RGBA");im.putalpha(mask);im.save(f"{out}/{name}.png",optimize=True)
# 1 aged paper scrap, tall
w,h=520,900;m=torn_mask(w,h,3,0.03);im=fiber_rim(paper(w,h,(222,212,190),3,12),m)
d=ImageDraw.Draw(im)
for y in range(140,h-120,34): d.line([(60,y),(w-60,y)],fill=(170,160,150),width=1)
d.line([(110,90),(110,h-90)],fill=(205,120,140),width=2)
save(im,m,"scrap-paper")
# 2 pink scrap, tall strip
w,h=360,980;m=torn_mask(w,h,7,0.045);im=fiber_rim(paper(w,h,(214,23,122),7,14),m);save(im,m,"scrap-pink")
# 3 newsprint scrap with halftone block
w,h=640,520;m=torn_mask(w,h,11,0.03);im=fiber_rim(paper(w,h,(206,200,186),11,10),m)
d=ImageDraw.Draw(im)
for col in (0,1):
    x0=60+col*(w-120)//2+col*10;x1=x0+(w-120)//2-10
    for y in range(80,h-70,15):
        rr=random.Random(y*7+col);x=x0
        while x<x1:
            L=rr.randint(6,30)
            d.rectangle([x,y,min(x+L,x1),y+4],fill=(92,86,88)); x+=L+rr.randint(4,7)
        if rr.random()<.12: y+=15
save(im,m,"scrap-newsprint")
# 4 masking tape
w,h=420,120;m=torn_mask(w,h,5,0.05);im=paper(w,h,(232,222,196),5,6);save(Image.blend(im,Image.new("RGB",(w,h),(240,230,205)),.3),m.point(lambda v:int(v*.88)),"tape")
print("done")
