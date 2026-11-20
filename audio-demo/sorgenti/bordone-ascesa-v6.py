import numpy as np, wave, sys
sr=44100; dur=25.0; N=int(sr*dur)
rng=np.random.default_rng(11)
L=np.zeros(N); R=np.zeros(N)
Sa=138.59  # C#3, tonic of the drone
def add(sig,start,pan,gain=1.0):
    i=int(start*sr); n=min(len(sig),N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*gain*np.cos(pan*np.pi/2); R[i:i+n]+=sig[:n]*gain*np.sin(pan*np.pi/2)
# --- tanpura, faster cycle (andante con moto) ---
def tanpura(f0, decay=5.0):
    n=int(6*sr); t=np.arange(n)/sr; s=np.zeros(n)
    for k in range(1,30):
        f=f0*k*(1+rng.normal(0,0.0004))
        if f>8000: break
        swell=1+2.2*(k/12)*np.exp(-((t-0.2-0.025*k)/0.5)**2)
        s+=k**-0.9*np.exp(-t/(decay/(1+0.06*k)))*swell*np.sin(2*np.pi*f*t+rng.uniform(0,6.28))
    return s*np.minimum(1,t/0.008)
cyc=[Sa*0.75,Sa,Sa,Sa*0.5]; t=0.3; i=0
while t<dur-4:
    add(tanpura(cyc[i%4]), t+rng.normal(0,0.015), [0.35,0.55,0.6,0.45][i%4], 0.2)
    t+=0.82; i+=1
# --- santoor-like struck strings: Bhupali (Sa Re Ga Pa Dha) ---
ratios=[1,9/8,5/4,3/2,5/3]
def note(deg):  # deg 0 = middle Sa (one octave above drone tonic)
    o,d=divmod(deg,5); return Sa*2*ratios[d]*2**o
def struck(f, length=2.6):
    n=int(length*sr); t=np.arange(n)/sr; s=np.zeros(n)
    for k,a in [(1,1),(2,0.7),(3,0.55),(4,0.42),(5,0.32),(6,0.25),(7,0.19),(8,0.14),(9,0.1),(10,0.07),(12,0.05)]:
        fk0=f*k*(1+0.0006*k*k)
        if fk0>12000: continue
        for det in (-0.6,0.6):   # paired strings, gentle chorus
            s+=a*np.exp(-t/(1.6/k**0.4))*np.sin(2*np.pi*(fk0+det)*t+rng.uniform(0,6.28))
    # bright hammer click: short high-passed noise burst
    m=int(0.012*sr); nz=rng.normal(0,1,m); nz=np.diff(nz,prepend=0)*np.exp(-np.arange(m)/(0.003*sr))
    s[:m]+=0.35*nz
    return s*np.minimum(1,t/0.002)
bpm=92; e=60/bpm/2       # eighth note
start=3.3; tcur=start
phr=[[0,1,2,3,2],[1,2,3,4,3],[2,3,4,5,4]]   # three rising phrases
for p,ph in enumerate(phr):
    g=0.6+0.05*p   # gentle crescendo as the line climbs
    for j,d in enumerate(ph):
        add(struck(note(d)), tcur+rng.normal(0,0.006), 0.3+0.4*(d%5)/4, g*(1.15 if j==0 else 1))
        tcur+=e
    tcur+=3*e
# final run upward in sixteenths, then the high Sa held
for rep,gr in enumerate([0.8,0.9,1.0]):   # the rising run, three times, in crescendo
    for d in range(5,10):
        add(struck(note(d),3.5), tcur+rng.normal(0,0.004), 0.4+0.05*(d-5), gr); tcur+=e/2
    if rep<2: tcur+=e*1.5
for d,g in [(10,1.15),(8,0.6),(5,0.5)]:   # Sa'' with Pa' and Sa' below
    add(struck(note(d),5.0), tcur, 0.5, g)
# singing bowl to seal the ascent
def bowl(f0,length):
    n=int(length*sr); t=np.arange(n)/sr; s=np.zeros(n)
    for r,a,dc in [(1,1,9),(2.71,0.5,6),(5.15,0.25,4),(8.17,0.12,2.5)]:
        for dt in (-0.35,0.35): s+=a*np.exp(-t/dc)*np.sin(2*np.pi*(f0*r+dt)*t)
    return s*np.minimum(1,t/0.004)
add(bowl(Sa*2, dur-tcur-0.4), tcur+0.4, 0.5, 0.5)
end_melody=tcur
# reverb
irn=int(2.4*sr); tt=np.arange(irn)/sr
def rev(x,seed):
    ir=np.random.default_rng(seed).normal(0,1,irn)*np.exp(-tt/0.75); ir[0]=0
    F=1<<int(np.ceil(np.log2(len(x)+irn)))
    y=np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]; return y/np.max(np.abs(y))
m=max(np.max(np.abs(L)),np.max(np.abs(R))); Lw=L/m; Rw=R/m
L2=0.8*Lw+0.3*rev(Lw,1)*np.max(np.abs(Lw)); R2=0.8*Rw+0.3*rev(Rw,2)*np.max(np.abs(Rw))
fade=np.ones(N); fi=int(2.5*sr); fo=int(4*sr)
fade[:fi]=np.linspace(0,1,fi)**2; fade[-fo:]=np.linspace(1,0,fo)**2
st=np.stack([L2*fade,R2*fade],1); st/=np.max(np.abs(st))*1.12
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((st*32767).astype('<i2').tobytes())
print("melody ends at %.2fs"%end_melody)
