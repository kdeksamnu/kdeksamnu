import numpy as np, time
f32=np.float32

print("="*78); print("CLAIM: 32 bytes per gaussian, quaternion as (q+1)*127.5 in uint8"); print("="*78)
layout=[("position",3,4),("log-scale",3,4),("rgba",4,1),("quat",4,1)]
tot=sum(n*b for _,n,b in layout)
print(f"  {'field':<12}{'n':>4}{'bytes':>7}{'subtotal':>10}")
for name,n,b in layout: print(f"  {name:<12}{n:>4}{b:>7}{n*b:>10}")
print(f"  {'TOTAL':<12}{'':>4}{'':>7}{tot:>10}   -> {'exactly 32' if tot==32 else 'NOT 32'}")
print(f"  107k gaussians: {107_000*tot/1e6:.2f} MB   (the '0.5 GB over budget' is not the splat data)")

print()
print("="*78); print("CLAIM: quaternion quantisation is free ('indifferent to your feelings')"); print("="*78)
rng=np.random.default_rng(0)
q=rng.normal(size=(200000,4)); q/=np.linalg.norm(q,axis=1,keepdims=True)
enc=np.clip(np.round((q+1.0)*127.5),0,255).astype(np.uint8)
dec=enc.astype(np.float64)/127.5-1.0
dec/=np.linalg.norm(dec,axis=1,keepdims=True)          # MUST renormalise after decode
dot=np.clip(np.abs(np.sum(q*dec,axis=1)),-1,1)
ang=2*np.degrees(np.arccos(dot))
print(f"  encode (q+1)*127.5 -> uint8 -> decode -> RENORMALISE")
print(f"  angular error: mean {ang.mean():.4f} deg   max {ang.max():.4f} deg   p99 {np.percentile(ang,99):.4f}")
print(f"  step size = 2/255 = {2/255:.5f} per component; worst-case angle = 2*asin(step/sqrt2) = "
      f"{2*np.degrees(np.arcsin((2/255)/np.sqrt(2))):.4f} deg")
d2=dec/np.maximum(np.linalg.norm(dec,axis=1,keepdims=True),1e-12)
Rerr=[]
for i in range(300):
    def rotm(v):
        w,x,y,z=v
        return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
                         [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
                         [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
    A,B=rotm(q[i]),rotm(d2[i]); Rerr.append(np.linalg.norm(A-B)/np.linalg.norm(A))
print(f"  relative rotation-matrix error: mean {np.mean(Rerr)*100:.4f}%   max {np.max(Rerr)*100:.4f}%")
print(f"  => at a 150 m sector viewed on a 1000 px viewport, {ang.mean():.3f} deg of orientation")
print(f"     error moves a splat edge by roughly {150*np.tan(np.radians(ang.mean()))*1000/150:.2f} px equivalent.")
print(f"     Fine for canopy. NOT fine for anything with straight architectural edges.")
qnr=enc.astype(np.float64)/127.5-1.0
nrm=np.linalg.norm(qnr,axis=1)
print(f"  skipping renormalisation: |q| in [{nrm.min():.4f}, {nrm.max():.4f}] (needs 1.0)")
