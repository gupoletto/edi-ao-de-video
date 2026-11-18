// Asteroide atingindo a Terra: globo com oceanos/continentes procedurais e atmosfera, o asteroide chegando, o clarão,
// a onda de choque (anel na superfície), a cratera brilhando e a nuvem de detritos subindo.
// Estado: cam, alvo, fov, t, ast [x,y,z] (centro do asteroide), astR, brilho 0..1 (reentrada), flash 0..1,
// onda (raio angular do anel, rad), cratera 0..1, poeira 0..1.
const R = 10;
const IMPACTO = [0.0, 0.42, 0.91];   // direção do ponto de impacto (normalizada no JS)

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 2000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.05;
  const S = {T};
  cena.background = new T.Color(0x02030a);
  const est = new T.BufferGeometry(), pos = [];
  for (let i = 0; i < 2500; i++) {
    const u = Math.random() * 2 - 1, a = Math.random() * Math.PI * 2, rr = 600;
    pos.push(rr * Math.sqrt(1 - u * u) * Math.cos(a), rr * u, rr * Math.sqrt(1 - u * u) * Math.sin(a));
  }
  est.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  cena.add(new T.Points(est, new T.PointsMaterial({color: 0xffffff, size: 1.6, sizeAttenuation: false})));
  cena.add(new T.AmbientLight(0x334455, 0.6));
  const sol = new T.DirectionalLight(0xfff4e0, 3.0); sol.position.set(30, 20, 40); cena.add(sol);
  // textura procedural: oceano + continentes por ruído simples
  const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 512;
  const c = cv.getContext('2d');
  c.fillStyle = '#1d4f9a'; c.fillRect(0, 0, 1024, 512);
  let sem = 7; const rnd = () => (sem = (sem * 16807) % 2147483647) / 2147483647;
  for (let k = 0; k < 14; k++) {
    const x = rnd() * 1024, y = 90 + rnd() * 330, w = 40 + rnd() * 140;
    for (let j = 0; j < 16; j++) {
      c.fillStyle = j % 3 ? '#3f7d3a' : '#8a7a4a';
      c.beginPath(); c.ellipse(x + (rnd() - 0.5) * w * 1.6, y + (rnd() - 0.5) * w, w * (0.3 + rnd() * 0.5), w * (0.2 + rnd() * 0.4), rnd() * 3, 0, 7); c.fill();
    }
  }
  c.fillStyle = '#f0f4f8'; c.fillRect(0, 0, 1024, 30); c.fillRect(0, 482, 1024, 30);
  S.tex = new T.CanvasTexture(cv); S.tex.colorSpace = T.SRGBColorSpace;
  S.terra = new T.Mesh(new T.SphereGeometry(R, 96, 64), new T.MeshStandardMaterial({map: S.tex, roughness: 0.8}));
  cena.add(S.terra);
  const atm = new T.Mesh(new T.SphereGeometry(R * 1.035, 64, 48), new T.MeshBasicMaterial({color: 0x6fb6ff, transparent: true,
    opacity: 0.10, side: T.BackSide})); cena.add(atm);
  // asteroide
  const ag = new T.IcosahedronGeometry(1, 3), ap = ag.attributes.position;
  for (let i = 0; i < ap.count; i++) { const f = 0.8 + 0.35 * Math.sin(ap.getX(i) * 5) * Math.cos(ap.getY(i) * 4); ap.setXYZ(i, ap.getX(i) * f, ap.getY(i) * f, ap.getZ(i) * f); }
  ag.computeVertexNormals();
  S.ast = new T.Mesh(ag, new T.MeshStandardMaterial({color: 0x5a5148, roughness: 1, emissive: 0xff5a10, emissiveIntensity: 0}));
  cena.add(S.ast);
  S.cauda = new T.Mesh(new T.ConeGeometry(1, 6, 24, 1, true), new T.MeshBasicMaterial({color: 0xffa040, transparent: true, opacity: 0, side: T.DoubleSide, depthWrite: false}));
  cena.add(S.cauda);
  // ponto de impacto
  S.n = new T.Vector3(...IMPACTO).normalize();
  S.flash = new T.Mesh(new T.SphereGeometry(1, 32, 16), new T.MeshBasicMaterial({color: 0xfff6d0, transparent: true, opacity: 0, depthWrite: false}));
  S.flash.position.copy(S.n.clone().multiplyScalar(R)); cena.add(S.flash);
  S.anel = new T.Mesh(new T.TorusGeometry(1, 0.08, 8, 96), new T.MeshBasicMaterial({color: 0xffe0a0, transparent: true, opacity: 0}));
  cena.add(S.anel);
  S.cratera = new T.Mesh(new T.CircleGeometry(1, 48), new T.MeshBasicMaterial({color: 0xff6a20, transparent: true, opacity: 0}));
  S.cratera.position.copy(S.n.clone().multiplyScalar(R * 1.002)); S.cratera.lookAt(S.n.clone().multiplyScalar(R * 3)); cena.add(S.cratera);
  S.poeira = new T.Mesh(new T.SphereGeometry(1, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), new T.MeshStandardMaterial({color: 0x8a7a6a, transparent: true, opacity: 0, roughness: 1}));
  S.poeira.position.copy(S.n.clone().multiplyScalar(R)); S.poeira.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), S.n); cena.add(S.poeira);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam, T = S.T;
  S.ast.position.set(...e.ast); S.ast.scale.setScalar(e.astR); S.ast.rotation.set(e.t * 0.7, e.t * 0.4, 0);
  S.ast.visible = e.flash < 0.05;
  S.ast.material.emissiveIntensity = 1.5 * e.brilho;
  const dir = S.n.clone().multiplyScalar(R).sub(S.ast.position).normalize();
  S.cauda.position.copy(S.ast.position).addScaledVector(dir, -3 * e.astR);
  S.cauda.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir.clone().negate());
  S.cauda.scale.set(e.astR * 0.9, e.astR, e.astR * 0.9);
  S.cauda.material.opacity = 0.7 * e.brilho * (S.ast.visible ? 1 : 0);
  S.flash.scale.setScalar(0.3 + 4 * e.flash); S.flash.material.opacity = e.flash;
  // anel da onda de choque: círculo de raio angular "onda" em volta do ponto de impacto
  const a = e.onda;
  S.anel.visible = a > 0.001;
  if (S.anel.visible) {
    S.anel.position.copy(S.n.clone().multiplyScalar(R * Math.cos(a) * 1.01));
    S.anel.scale.setScalar(R * Math.sin(a) * 1.01);
    S.anel.quaternion.setFromUnitVectors(new T.Vector3(0, 0, 1), S.n);
    S.anel.material.opacity = Math.max(0, 0.9 - a / 1.6);
  }
  S.cratera.scale.setScalar(0.2 + 0.9 * e.cratera); S.cratera.material.opacity = 0.9 * e.cratera;
  S.poeira.scale.set(0.4 + 2.2 * e.poeira, 0.2 + 1.4 * e.poeira, 0.4 + 2.2 * e.poeira);
  S.poeira.material.opacity = 0.75 * Math.min(1, e.poeira * 3) * (1 - 0.3 * e.poeira);
  S.terra.rotation.y = 0;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
