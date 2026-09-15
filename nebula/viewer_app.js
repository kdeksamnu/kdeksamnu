(function(){
'use strict';
const N = window.NEBULA, E = window.NEBULA_SPLAT_EMIT;
const $ = id => document.getElementById(id);
const fail = m => { const e=$('err'); if(e){e.style.display='grid'; e.textContent=m;} throw new Error(m); };
if(!N) fail('core.js failed to load');
if(!E) fail('splat_emit.js failed to load');

/* ---------------------------------------------------------------- state */
let world=null, splat=null, mat=null;
let styleCode=new Float32Array(N.STYLE_DIM);
styleCode.set(N.STYLE_PRESETS.vanilla);
let styleName='vanilla';
let W=128, H=80;

/* How far out the quad extends, in sigmas. At 3 sigma the gaussian alpha is
   exp(-4.5) = 1.1%, so truncating there costs nothing visible. The previous
   viewer used a 1.6x radius heuristic against an isotropic disc, which both
   clipped tails and ignored the emitted anisotropy entirely. */
const SIGMA_SUPPORT = 3.0;
const FOV_DEG = 48;
const FOV = FOV_DEG * Math.PI / 180, NEAR = 0.1, FAR = 5000;

/* ------------------------------------------------------------- WebGL2 */
const cv = $('gl');
const gl = cv.getContext('webgl2', {antialias:true, alpha:false, premultipliedAlpha:false});
if(!gl) fail('WebGL2 is not available in this browser. Chrome, Edge, Safari 15+ or Firefox 128+ required.');

/* The vertex shader is a line-by-line transcription of E.splatBasis /
   E.shade / E.quatToMat3 in splat_emit.js, which test_splat.js asserts
   against (73 assertions). There is no GL toolchain in this environment, so
   the reference implementation is the test and the shader is the mirror.
   If you edit one, edit the other. */
const VS = `#version 300 es
precision highp float;

layout(location=0) in vec2 a_corner;   // static unit quad, [-1,1]^2
layout(location=1) in vec3 a_center;   // instance: world position
layout(location=2) in vec3 a_scale;    // instance: gaussian semi-axes, metres
layout(location=3) in vec4 a_rot;      // instance: quaternion (w,x,y,z)
layout(location=4) in vec4 a_color;    // instance: styled rgb + opacity
layout(location=5) in vec3 a_normal;   // instance: baked surface normal

uniform mat4 u_viewProj;
uniform vec3 u_viewRot0, u_viewRot1, u_viewRot2;  // world -> camera rotation
uniform vec3 u_camPos;
uniform vec2 u_viewport;
uniform float u_focal;        // (viewport.y * 0.5) / tan(fov/2), device pixels
uniform float u_sizeScale;
uniform float u_support;      // quad half-extent in sigmas

uniform vec3  u_sunDir, u_sunColor;
uniform vec3  u_moonDir, u_moonColor;
uniform float u_sunInt, u_moonInt, u_ambient;
uniform float u_unlit;

out vec2 v_local;   // fragment position in sigma units
out vec4 v_color;

mat3 quatMat3(vec4 q){
  float l = length(q);
  if(l < 1e-8) return mat3(1.0);
  vec4 n = q / l;
  float w=n.x, x=n.y, y=n.z, z=n.w;
  // row-major, matching E.quatToMat3 - q v q*, NOT its transpose
  return mat3(
    1.0-2.0*(y*y+z*z), 2.0*(x*y-w*z),     2.0*(x*z+w*y),
    2.0*(x*y+w*z),     1.0-2.0*(x*x+z*z), 2.0*(y*z-w*x),
    2.0*(x*z-w*y),     2.0*(y*z+w*x),     1.0-2.0*(x*x+y*y)
  );
}

void main(){
  vec4 clip = u_viewProj * vec4(a_center, 1.0);
  float pw  = max(abs(clip.w), 1e-4);

  // world -> camera (rotation only; translation cancels in the Jacobian)
  mat3 Wm = mat3(u_viewRot0, u_viewRot1, u_viewRot2);
  // Jacobian of the perspective divide at this splat. With
  // p = viewProj * world and ndc = p.xy / p.w,
  //   d(ndc)/d(view) = (1/pw) * [[1,0,-ndc.x],[0,1,-ndc.y]]
  vec2 ndc = clip.xy / pw;
  float ipw = 1.0 / pw;
  mat3x2 Jt = mat3x2(
    ipw, 0.0,
    0.0, ipw,
    -ndc.x * ipw, -ndc.y * ipw
  );
  mat2x3 J = transpose(Jt);

  // M = R * S; its columns are the gaussian's world-space semi-axes
  mat3 R = quatMat3(a_rot);
  mat3 M = mat3(R[0]*a_scale.x, R[1]*a_scale.y, R[2]*a_scale.z);

  // P = J * (W * M), a 2x3 of projected axes
  mat2x3 P = J * (Wm * M);

  // 2D covariance Sigma' = P P^T, then its eigen-decomposition
  float A = dot(P[0], P[0]);
  float B = dot(P[0], P[1]);
  float D = dot(P[1], P[1]);
  float tr = A + D;
  float disc = tr*tr*0.25 - (A*D - B*B);
  disc = max(disc, 0.0);
  float sq = sqrt(disc);
  float l1 = max(tr*0.5 + sq, 1e-12);
  float l2 = max(tr*0.5 - sq, 1e-12);

  vec2 axis;
  float eps = 1e-9 * max(1.0, abs(A) + abs(D));
  if(abs(B) > eps)      axis = normalize(vec2(l1 - D, B));
  else if(A >= D)       axis = vec2(1.0, 0.0);
  else                  axis = vec2(0.0, 1.0);
  vec2 perp = vec2(-axis.y, axis.x);

  // NDC -> device pixels, then into clip space
  vec2 e0 = axis * sqrt(l1) * u_focal * u_sizeScale * u_support;
  vec2 e1 = perp * sqrt(l2) * u_focal * u_sizeScale * u_support;
  vec2 offPx = a_corner.x * e0 + a_corner.y * e1;
  clip.xy += (offPx * 2.0 / u_viewport) * clip.w;
  gl_Position = clip;

  // fragment position in sigma units: e0 has length support*sigma along the
  // major axis, so dividing by support recovers sigmas for the falloff
  v_local = a_corner * u_support;

  vec3 nrm = normalize(a_normal);
  float ndlS = max(dot(nrm, normalize(u_sunDir)),  0.0);
  float ndlM = max(dot(nrm, normalize(u_moonDir)), 0.0);
  vec3 lit = vec3(u_ambient)
           + u_sunInt  * ndlS * u_sunColor
           + u_moonInt * ndlM * u_moonColor;
  lit = mix(lit, vec3(1.0), u_unlit);
  v_color = vec4(a_color.rgb * lit, a_color.a);
}`;

const FS = `#version 300 es
precision highp float;
in vec2 v_local;
in vec4 v_color;
uniform float u_exposure;
out vec4 frag;
void main(){
  float r2 = dot(v_local, v_local);
  if(r2 > 9.0) discard;             // outside the 3-sigma support
  float a = v_color.a * exp(-0.5 * r2);
  if(a < 1.0/255.0) discard;
  frag = vec4(v_color.rgb * u_exposure, a);
}`;

function compile(type, src){
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if(!gl.getShaderParameter(s, gl.COMPILE_STATUS))
    fail('shader compile failed: ' + gl.getShaderInfoLog(s));
  return s;
}
const prog = gl.createProgram();
gl.attachShader(prog, compile(gl.VERTEX_SHADER, VS));
gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FS));
gl.linkProgram(prog);
if(!gl.getProgramParameter(prog, gl.LINK_STATUS)) fail('link failed: ' + gl.getProgramInfoLog(prog));
gl.useProgram(prog);
const U = {};
['u_viewProj','u_viewRot0','u_viewRot1','u_viewRot2','u_camPos','u_viewport','u_focal',
 'u_sizeScale','u_support','u_exposure','u_unlit',
 'u_sunDir','u_sunColor','u_moonDir','u_moonColor','u_sunInt','u_moonInt','u_ambient'
].forEach(n=>{ U[n]=gl.getUniformLocation(prog,n); if(U[n]===null) console.warn('uniform not found:',n); });

/* ---------------------------------------------------------------- buffers
   Attribute 0 is a static unit quad; 1-5 are per-instance with divisor 1 and
   drawn with drawArraysInstanced(TRIANGLE_STRIP, 0, 4, count). The previous
   lit viewer used gl.POINTS, which cannot be anisotropic at all - so the
   rotation and scale that emit() produced and toSplatBytes() packed were both
   discarded, and every splat was a disc sized by max(scale.x, scale.z)*1.6. */
const vao = gl.createVertexArray();
gl.bindVertexArray(vao);

const quadBuf = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
gl.enableVertexAttribArray(0);
gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
gl.vertexAttribDivisor(0, 0);

const instBufs = {};
function makeInst(loc, size, key){
  const b = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, b);
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
  gl.vertexAttribDivisor(loc, 1);        // PER INSTANCE - the old code said 0
  instBufs[key] = b;
  return b;
}
makeInst(1,3,'center'); makeInst(2,3,'scale'); makeInst(3,4,'rot');
makeInst(4,4,'color');  makeInst(5,3,'normal');
gl.bindVertexArray(null);

gl.enable(gl.BLEND);
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
gl.enable(gl.DEPTH_TEST);
gl.depthFunc(gl.LEQUAL);
gl.depthMask(false);              // splats are transparent; do not write depth

/* ------------------------------------------------------- GPU-side arrays
   All of these were previously either undeclared (depths, sortKeys, sortTmp -
   a ReferenceError on the first sorted frame, so the viewer drew nothing) or
   declared and never assigned (scaleArr). */
let gpuCount = 0;
let centerArr=null, scaleArr=null, rotArr=null, colorArr=null, normalArr=null;
let order=null, depths=null, depthKeys=null, sortKeys=null, sortTmp=null, sortOrderB=null;

function upload(g){
  const n = g.count;
  gpuCount = n;
  centerArr = new Float32Array(n*3);
  scaleArr  = new Float32Array(n*3);
  rotArr    = new Float32Array(n*4);
  colorArr  = new Float32Array(n*4);
  normalArr = new Float32Array(n*3);
  order     = new Int32Array(n);
  depths    = new Float32Array(n);
  depthKeys = new Uint32Array(n);
  sortKeys  = new Uint32Array(n);
  sortTmp   = new Uint32Array(n);
  sortOrderB= new Int32Array(n);
  for(let i=0;i<n;i++) order[i]=i;
  recolor(g);
  reorderGeometry(g);
  bindBuffers(true);
}

/** Style the gaussians. Independent of depth order, so a style swap does not
 *  have to touch the geometry buffers. */
function recolor(g){
  const n=g.count;
  const mode = $('appear') ? $('appear').value : 'analytic';
  const fin = new Float32Array(N.MAT_IN);
  const outHi = new Float32Array(N.MAT_OUT);
  const outLo = new Float32Array(N.MAT_OUT);
  const useNeural = (mode === 'neural') && mat && mat.trained;
  const t0 = performance.now();

  for(let i=0;i<n;i++){
    const o = order[i];
    let r, gg, b;
    if(g.feat){
      // exact core path: the emitted features are the same 9 slots
      // featuresAt() produces, so styledTarget() here is the SAME function the
      // materializer was trained against. The old applyStyle() claimed to
      // mirror it but dropped the per-cell grain term n and replaced it with a
      // flat global tint - losing the largest single source of surface detail.
      fin.set(g.feat.subarray(o*9, o*9+9), 0);
      fin.set(styleCode, 9);
      if(useNeural){
        mat.decode(fin, outHi);
        r=outHi[0]; gg=outHi[1]; b=outHi[2];
      } else {
        N.styledTarget(fin, styleCode, outLo);
        r=outLo[0]; gg=outLo[1]; b=outLo[2];
      }
      if(g.tint){ r*=g.tint[o*3]; gg*=g.tint[o*3+1]; b*=g.tint[o*3+2]; }
    } else {
      // a loaded .splat has no features: fall back to its stored colour
      r=g.color[o*3]; gg=g.color[o*3+1]; b=g.color[o*3+2];
    }
    colorArr[i*4]  =r<0?0:r>1?1:r;
    colorArr[i*4+1]=gg<0?0:gg>1?1:gg;
    colorArr[i*4+2]=b<0?0:b>1?1:b;
    colorArr[i*4+3]=g.opacity[o];
  }
  lastColorMs = performance.now()-t0;
  lastColorMode = useNeural ? 'neural' : 'analytic';
  bindBuffers(false);
}
let lastColorMs=0, lastColorMode='analytic';

/** Rewrite the geometry buffers in the current depth order. */
function reorderGeometry(g){
  const n=g.count;
  for(let i=0;i<n;i++){
    const o=order[i];
    centerArr[i*3]=g.pos[o*3]; centerArr[i*3+1]=g.pos[o*3+1]; centerArr[i*3+2]=g.pos[o*3+2];
    scaleArr[i*3] =g.scale[o*3]; scaleArr[i*3+1]=g.scale[o*3+2-1]; scaleArr[i*3+2]=g.scale[o*3+2];
    rotArr[i*4]   =g.rot[o*4]; rotArr[i*4+1]=g.rot[o*4+1]; rotArr[i*4+2]=g.rot[o*4+2]; rotArr[i*4+3]=g.rot[o*4+3];
    if(g.normal){ normalArr[i*3]=g.normal[o*3]; normalArr[i*3+1]=g.normal[o*3+1]; normalArr[i*3+2]=g.normal[o*3+2]; }
    else { normalArr[i*3]=0; normalArr[i*3+1]=1; normalArr[i*3+2]=0; }
  }
}

function bindBuffers(all){
  gl.bindVertexArray(vao);
  const put=(key,arr)=>{ gl.bindBuffer(gl.ARRAY_BUFFER, instBufs[key]); gl.bufferData(gl.ARRAY_BUFFER, arr, gl.DYNAMIC_DRAW); };
  if(all!==false){ put('center',centerArr); put('scale',scaleArr); put('rot',rotArr); put('normal',normalArr); }
  put('color',colorArr);
  gl.bindVertexArray(null);
}

/* -------------------------------------------------- radix sort by depth
   4 passes of 8 bits over the float-as-uint monotonic transform. O(n), which
   matters: at 100k+ gaussians Array.sort on a comparator costs more per frame
   than the draw call does. */
function radixSortIndices(n){
  // sort descending depth (far first) so back-to-front blending is correct
  const keys = sortKeys, tmp = sortTmp;
  const idxA = order, idxB = sortOrderB;
  for(let i=0;i<n;i++) keys[i] = 0xFFFFFFFF - depthKeys[i];
  let src = idxA, dst = idxB;
  for(let pass=0; pass<4; pass++){
    const shift = pass*8;
    const hist = new Uint32Array(256);
    for(let i=0;i<n;i++) hist[(keys[i]>>>shift)&0xFF]++;
    let acc=0;
    for(let i=0;i<256;i++){ const c=hist[i]; hist[i]=acc; acc+=c; }
    for(let i=0;i<n;i++){ const id=src[i]; const k=(keys[id]>>>shift)&0xFF; dst[hist[k]++]=id; }
    const t=src; src=dst; dst=t;
  }
  if(src!==order) order.set(src);
}

/* ------------------------------------------------------------- camera
   Verified by cam_test.js (14 assertions): perspective maps the optical axis to
   NDC 0, near/far land on -1/+1, lookAt centres the target, +Y stays up, the
   rotation is orthonormal, and the degenerate up-parallel case cannot produce
   NaN. Column-major for uniformMatrix4fv. */
const camPos = new Float32Array(3);
const vpMat = new Float32Array(16);
const _p = new Float32Array(16), _v = new Float32Array(16);

function m4Perspective(out, aspect) {
  const f = 1 / Math.tan(FOV / 2), nf = 1 / (NEAR - FAR);
  out.fill(0);
  out[0] = f / aspect; out[5] = f;
  out[10] = (FAR + NEAR) * nf; out[11] = -1; out[14] = 2 * FAR * NEAR * nf;
  return out;
}
function m4LookAt(out, eye, cx, cy, cz) {
  let zx = eye[0] - cx, zy = eye[1] - cy, zz = eye[2] - cz;
  let l = Math.hypot(zx, zy, zz);
  if (l === 0) { zx = 0; zy = 0; zz = 1; l = 1; }
  zx /= l; zy /= l; zz /= l;
  // x = normalize(cross(up=(0,1,0), z))
  let xx = zz, xy = 0, xz = -zx;
  l = Math.hypot(xx, xy, xz);
  if (l < 1e-6) { xx = 1; xy = 0; xz = 0; l = 1; }   // looking straight down
  xx /= l; xy /= l; xz /= l;
  const yx = zy * xz - zz * xy, yy = zz * xx - zx * xz, yz = zx * xy - zy * xx;
  out[0]=xx; out[1]=yx; out[2]=zx; out[3]=0;
  out[4]=xy; out[5]=yy; out[6]=zy; out[7]=0;
  out[8]=xz; out[9]=yz; out[10]=zz; out[11]=0;
  out[12]=-(xx*eye[0]+xy*eye[1]+xz*eye[2]);
  out[13]=-(yx*eye[0]+yy*eye[1]+yz*eye[2]);
  out[14]=-(zx*eye[0]+zy*eye[1]+zz*eye[2]);
  out[15]=1;
  return out;
}
function m4Mul(out, a, b) {
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
    let s2 = 0;
    for (let k = 0; k < 4; k++) s2 += a[k * 4 + r] * b[c * 4 + k];
    out[c * 4 + r] = s2;
  }
  return out;
}
const cam = { yaw: 0.6, pitch: 0.26, dist: 150, tx: 64, ty: 14, tz: 40 };
function viewProj(out, aspect) {
  const cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
  const ex = cam.tx + cam.dist * cp * Math.sin(cam.yaw);
  const ey = cam.ty + cam.dist * sp;
  const ez = cam.tz + cam.dist * cp * Math.cos(cam.yaw);
  camPos[0] = ex; camPos[1] = ey; camPos[2] = ez;
  m4LookAt(_v, camPos, cam.tx, cam.ty, cam.tz);
  m4Perspective(_p, aspect);
  return m4Mul(out, _p, _v);
}
/** Rows of the view rotation, for the shader's covariance projection.
 *  m4LookAt is column-major, so row r of the rotation is _v[r], _v[4+r], _v[8+r]. */
const viewRot = [new Float32Array(3), new Float32Array(3), new Float32Array(3)];
function extractViewRot(){
  for(let r=0;r<3;r++){ viewRot[r][0]=_v[r]; viewRot[r][1]=_v[4+r]; viewRot[r][2]=_v[8+r]; }
}

/* ---------------------------------------------------------- interaction */
let dragging=false, lx=0, ly=0;
cv.addEventListener('pointerdown',e=>{dragging=true;lx=e.clientX;ly=e.clientY;cv.setPointerCapture(e.pointerId);});
cv.addEventListener('pointermove',e=>{
  if(!dragging)return;
  cam.yaw -= (e.clientX-lx)*0.006;
  cam.pitch = Math.max(0.05, Math.min(1.5, cam.pitch + (e.clientY-ly)*0.005));
  lx=e.clientX; ly=e.clientY; needsSort=true;
});
['pointerup','pointercancel','pointerleave'].forEach(ev=>cv.addEventListener(ev,()=>dragging=false));
cv.addEventListener('wheel',e=>{
  e.preventDefault();
  cam.dist = Math.max(20, Math.min(600, cam.dist * (1 + Math.sign(e.deltaY)*0.09)));
  needsSort=true;
},{passive:false});

/* --------------------------------------------------------------- UI */
function bindRange(id,fmt){
  const el=$(id); if(!el) return;
  const o=$(id+'O');
  const up=()=>{ if(o) o.textContent=fmt(+el.value); };
  el.oninput=up; up();
}
const hhmm = m => `${String(Math.floor(m/60)%24).padStart(2,'0')}:${String(m%60).padStart(2,'0')}`;
bindRange('seed',v=>v);
bindRange('dens',v=>v);
bindRange('veg',v=>(v/100).toFixed(2).replace('0.','.'));
bindRange('jit',v=>(v/100).toFixed(2).replace('0.','.'));
bindRange('height',v=>(v/100).toFixed(2));
bindRange('tod',hhmm);
bindRange('sunaz',v=>v);
bindRange('sunel',v=>v);
bindRange('moonInt',v=>(v/100).toFixed(2).replace('0.','.'));
bindRange('nightAmb',v=>(v/100).toFixed(2).replace('0.','.'));
bindRange('ambient',v=>(v/100).toFixed(2).replace('0.','.'));
bindRange('psize',v=>(v/100).toFixed(2));
bindRange('expo',v=>(v/100).toFixed(2));

const sel=$('style');
if(sel){
  Object.keys(N.STYLE_PRESETS).forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent=k;sel.appendChild(o);});
  sel.onchange=()=>{
    styleName=sel.value;
    styleCode.set(N.STYLE_PRESETS[sel.value]);
    if(splat){ recolor(splat); msg(`weights swapped to "${sel.value}" — world truth unchanged`); }
  };
}

['dens','veg','jit','height','showVeg','showWater'].forEach(id=>{ const el=$(id); if(el) el.addEventListener('input',()=>rebuild()); });
if($('seed')) $('seed').addEventListener('change',()=>rebuild());
if($('size')) $('size').addEventListener('change',()=>{const v=$('size').value.split(',');W=+v[0];H=+v[1];rebuild();});
if($('regen')) $('regen').onclick=()=>rebuild();
if($('sortOn')) $('sortOn').addEventListener('change',()=>{needsSort=true;});
if($('appear')) $('appear').onchange=()=>{ if(splat) recolor(splat); msg(`appearance: ${$('appear').value}`); };

if($('dlSplat')) $('dlSplat').onclick=()=>{
  if(!splat)return;
  const buf=E.toSplatBytes(splat);
  const blob=new Blob([buf],{type:'application/octet-stream'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob); a.download='nebula_chunk.splat'; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),4000);
  msg(`downloaded ${splat.count.toLocaleString()} gaussians, ${(buf.byteLength/1024).toFixed(0)} KB`);
};
if($('loadSplat')) $('loadSplat').onclick=()=>$('fileIn').click();
if($('fileIn')) $('fileIn').onchange=async ev=>{
  const f=ev.target.files[0]; if(!f)return;
  const buf=await f.arrayBuffer();
  if(buf.byteLength%32!==0){msg('not a 32-byte-per-gaussian .splat file');return;}
  splat=E.fromSplatBytes(buf);
  // The 32-byte format has no field for kind, normals or features, so a loaded
  // file comes back unlit and every gaussian as terrain. Say so rather than
  // implying the render path is identical.
  splatLoaded=true;
  upload(splat);
  needsSort=true;
  msg(`loaded ${splat.count.toLocaleString()} gaussians — no normals or features in the .splat format, so shading and style fall back to stored colour`);
};
let splatLoaded=false;

/* --------------------------------------------------------------- rebuild */
function rebuild(){
  const t0=performance.now();
  world = new N.World(W,H,+$('seed').value);
  // a few simulation ticks so the terrain has settled and erosion has run
  for(let i=0;i<40;i++) world.microStep(1);
  const agent = new N.SettlerAgent(1,{cooldown:6,seed:3});
  for(let i=0;i<12;i++) world.macroStep([agent]);
  const hs = +$('height').value/100;
  splat = E.emit(world,{
    density:+$('dens').value,
    vegDensity:+$('veg').value/100,
    jitter:+$('jit').value/100,
    heightScale:hs,
    includeVeg:$('showVeg').checked,
    includeWater:$('showWater').checked,
    seed:+$('seed').value
  });
  const emitMs=performance.now()-t0;

  // Train the materializer against THIS world so the neural appearance path is
  // a real comparison rather than a network trained on different terrain.
  // This is the offline bake; it is paid once per rebuild, never per frame.
  const t1=performance.now();
  mat = new N.Materializer(42);
  const loss = mat.train(world, 2600);
  const trainMs=performance.now()-t1;

  splatLoaded=false;
  upload(splat);
  needsSort=true;
  cam.tx=W*E.CELL_METRES/2; cam.tz=H*E.CELL_METRES/2; cam.ty=6*hs;
  cam.dist=Math.max(W,H)*0.75;
  if($('sEmit')) $('sEmit').textContent=emitMs.toFixed(0)+' ms';
  msg(`emitted ${splat.count.toLocaleString()} gaussians in ${emitMs.toFixed(0)} ms · materializer baked in ${(trainMs/1000).toFixed(1)} s (loss ${loss.toFixed(5)})`);
}

/* --------------------------------------------------------------- loop */
let needsSort=true, lastSortMs=0, lastDrawMs=0;
let fpsAcc=0, fpsN=0, lastT=performance.now();
let todMinutes = 13*60;

function resize(){
  const r=cv.getBoundingClientRect();
  const dpr=Math.min(2, window.devicePixelRatio||1);
  const w=Math.max(1,Math.floor(r.width*dpr)), h=Math.max(1,Math.floor(r.height*dpr));
  if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h;}
}

function frame(now){
  requestAnimationFrame(frame);
  const dt=now-lastT; lastT=now;
  fpsAcc+=dt; fpsN++;
  resize();
  if(!splat) return;

  if($('autoSpin').checked){ cam.yaw += dt*0.00022; needsSort=true; }
  if($('playTime') && $('playTime').checked){
    todMinutes = (todMinutes + dt*0.0025*60/1000*60) % 1440;   // ~0.4 s per minute
    const el=$('tod'); if(el){ el.value=String(Math.round(todMinutes)%1440); hhmmOut(); }
  } else {
    todMinutes = +($('tod') ? $('tod').value : 780);
  }

  const aspect = cv.width/cv.height;
  viewProj(vpMat, aspect);
  extractViewRot();

  if($('sortOn').checked && needsSort){
    const t0=performance.now();
    const ex=camPos[0],ey=camPos[1],ez=camPos[2];
    for(let i=0;i<gpuCount;i++){
      const dx=splat.pos[i*3]-ex, dy=splat.pos[i*3+1]-ey, dz=splat.pos[i*3+2]-ez;
      depths[i]=dx*dx+dy*dy+dz*dz;
    }
    // monotonic float->uint so a radix sort on the bits sorts by value
    const ubuf=new Uint32Array(depths.buffer);
    for(let i=0;i<gpuCount;i++){
      const b=ubuf[i];
      depthKeys[i]=(b&0x80000000)? ~b : (b|0x80000000);
    }
    radixSortIndices(gpuCount);
    reorderGeometry(splat);
    bindBuffers(true);
    lastSortMs=performance.now()-t0;
    needsSort=false;
  }

  // ---- sky state: one clock, two bodies -------------------------------
  const cel = E.celestial(todMinutes/60, {
    sunAzimuth: +$('sunaz').value,
    tilt:       +$('sunel').value,
    moonIntensity: +$('moonInt').value/100,
    nightAmbient:  +$('nightAmb').value/100,
    dayAmbient:    +$('ambient').value/100
  });
  gl.clearColor(cel.sky[0], cel.sky[1], cel.sky[2], 1);

  const t1=performance.now();
  gl.viewport(0,0,cv.width,cv.height);
  gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  gl.useProgram(prog);
  gl.uniformMatrix4fv(U.u_viewProj,false,vpMat);
  gl.uniform3fv(U.u_viewRot0, viewRot[0]);
  gl.uniform3fv(U.u_viewRot1, viewRot[1]);
  gl.uniform3fv(U.u_viewRot2, viewRot[2]);
  gl.uniform3fv(U.u_camPos, camPos);
  gl.uniform2f(U.u_viewport,cv.width,cv.height);
  gl.uniform1f(U.u_focal,(cv.height*0.5)/Math.tan(FOV/2));
  gl.uniform1f(U.u_sizeScale,+$('psize').value/100);
  gl.uniform1f(U.u_support,SIGMA_SUPPORT);
  gl.uniform1f(U.u_exposure,+$('expo').value/100);
  gl.uniform1f(U.u_unlit, ($('showAlbedo')&&$('showAlbedo').checked) ? 1 : 0);
  gl.uniform3fv(U.u_sunDir,  Float32Array.from(cel.sunDir));
  gl.uniform3fv(U.u_sunColor,Float32Array.from(cel.sunColor));
  gl.uniform3fv(U.u_moonDir, Float32Array.from(cel.moonDir));
  gl.uniform3fv(U.u_moonColor,Float32Array.from(cel.moonColor));
  gl.uniform1f(U.u_sunInt,  cel.sunIntensity);
  gl.uniform1f(U.u_moonInt, cel.moonIntensity);
  gl.uniform1f(U.u_ambient, cel.ambient);
  gl.bindVertexArray(vao);
  gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, gpuCount);
  gl.bindVertexArray(null);
  lastDrawMs=performance.now()-t1;
  lastCel = cel;
}
let lastCel=null;

function hhmmOut(){ const o=$('todO'); if(o) o.textContent=hhmm(+($('tod')?$('tod').value:0)); }

function updateHud(){
  if(!splat)return;
  if($('sCount')) $('sCount').textContent=splat.count.toLocaleString();
  if($('sBytes')) $('sBytes').textContent=(splat.bytes/1024).toFixed(0)+' KB';
  // zstd-3 measured at 3.85x on real splat bytes (§5d)
  if($('sComp')) $('sComp').textContent=(splat.bytes/1024/3.85).toFixed(0)+' KB @3.85x';
  if(lastCel){
    const c=lastCel;
    const phase = c.day>0.85?'day' : c.day>0.15?(c.dusk>0.02?'dusk':'twilight') : 'night';
    const n=$('skyNote');
    if(n) n.innerHTML =
      `<b>${hhmm(Math.round(c.t*60))}</b> &mdash; ${phase}. `+
      `sun ${c.sunEl>=0?'+':''}${c.sunEl.toFixed(0)}&deg; az ${c.sunAz.toFixed(0)}&deg;, `+
      `moon ${c.moonEl>=0?'+':''}${c.moonEl.toFixed(0)}&deg;. `+
      `ambient ${c.ambient.toFixed(2)}, sun ${c.sunIntensity.toFixed(2)}, moon ${c.moonIntensity.toFixed(2)}. `+
      `Appearance: <b>${lastColorMode}</b>, ${lastColorMs.toFixed(0)} ms for ${splat.count.toLocaleString()} gaussians.`;
  }
}
setInterval(updateHud,400);

let msgT=0;
function msg(s){ const el=$('sMsg'); if(!el)return; el.textContent=s; clearTimeout(msgT); msgT=setTimeout(()=>{el.textContent='';},6000); }

rebuild();
requestAnimationFrame(frame);
msg('drag to orbit · scroll to zoom · scrub time to move the sun and moon');
})();