// Submarino mergulhando: na superfície, as válvulas abrem e os tanques de lastro (em raio-x) enchem de água do mar,
// ele afunda, fica em equilíbrio (tanques de compensação) e depois o ar comprimido expulsa a água e ele sobe.
// Estado vindo do Python: cam, alvo, fov, t, pos [x,y,z], pitch (rad), raiox 0..1, lastro 0..1 (água nos tanques),
// bolhasVent 0..1 (ar saindo pelas válvulas de cima), bolhasSopro 0..1 (ar comprimido expulsando a água por baixo),
// helice (rad).
import * as A from 'http://cena.local/ambiente.js';

const L = 40, R = 3.2;   // comprimento e raio do casco (m)

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 3000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(41);
  S.ceu = A.ceu(T, cena, {sol: [0.4, 0.6, 0.6], neblina: 0xbfd6ea, perto: 300, longe: 1600});
  A.nuvens(T, cena, {n: 30, y: [160, 240], x: [-900, 900], z: [-900, -200], tam: [14, 26]});
  S.neblinaAr = cena.fog;
  S.neblinaAgua = new T.FogExp2(0x1b6a92, 0.009);
  S.luzAgua = new T.AmbientLight(0x9fd0ff, 0); cena.add(S.luzAgua);
  // superfície do mar (vista de cima e de baixo)
  const g = new T.PlaneGeometry(1600, 1600, 160, 160); g.rotateX(-Math.PI / 2);
  S.marGeo = g; S.marBase = Float32Array.from(g.attributes.position.array);
  S.mar = new T.Mesh(g, new T.MeshStandardMaterial({color: 0x1f6f9c, roughness: 0.25, metalness: 0.2, transparent: true,
                                                     opacity: 0.88, side: T.DoubleSide}));
  cena.add(S.mar);
  const fundo = new T.Mesh(new T.PlaneGeometry(1600, 1600), new T.MeshStandardMaterial({color: 0x3c6e66, roughness: 1}));
  fundo.rotation.x = -Math.PI / 2; fundo.position.y = -90; cena.add(fundo);
  for (let i = 0; i < 60; i++) {   // rochas no fundo para dar referência de profundidade
    const rr = 2 + A.aleat() * 6;
    const m = new T.Mesh(new T.DodecahedronGeometry(rr), new T.MeshStandardMaterial({color: 0x4f6b63, roughness: 1}));
    m.position.set(-300 + A.aleat() * 600, -90 + rr * 0.4, -120 + A.aleat() * 200); cena.add(m);
  }
  // ---------- submarino ----------
  S.sub = new T.Group(); cena.add(S.sub);
  S.casco = new T.MeshStandardMaterial({color: 0x23272d, metalness: 0.4, roughness: 0.5, transparent: true, opacity: 1});
  const corpo = new T.Mesh(new T.CapsuleGeometry(R, L - 2 * R, 16, 48), S.casco); corpo.rotation.z = Math.PI / 2;
  corpo.scale.set(1, 1, 1); S.sub.add(corpo);
  const vela = new T.Mesh(new T.BoxGeometry(7, 5.5, 1.6), S.casco); vela.position.set(6, R + 2.4, 0); S.sub.add(vela);
  for (const z of [-1, 1]) {
    const a = new T.Mesh(new T.BoxGeometry(2.6, 0.3, 3.4), S.casco); a.position.set(6, R + 2.6, z * 2.4); S.sub.add(a);
    const e = new T.Mesh(new T.BoxGeometry(3, 0.3, 3.6), S.casco); e.position.set(-L / 2 + 2, 0, z * 3.2); S.sub.add(e);
  }
  const leme = new T.Mesh(new T.BoxGeometry(3, 6, 0.3), S.casco); leme.position.set(-L / 2 + 2, 0, 0); S.sub.add(leme);
  S.helice = new T.Group(); S.helice.position.set(-L / 2 - 0.4, 0, 0); S.sub.add(S.helice);
  for (let i = 0; i < 7; i++) {
    const p = new T.Mesh(new T.BoxGeometry(0.2, 2.2, 0.6), new T.MeshStandardMaterial({color: 0x8a6b3a, metalness: 0.8, roughness: 0.3}));
    p.position.y = 1.1; const gg = new T.Group(); gg.rotation.x = i * Math.PI * 2 / 7; gg.add(p); S.helice.add(gg);
  }
  // tanques de lastro (raio-x): na frente e atrás, entre o casco interno e o externo
  S.tanques = [];
  S.dentro = new T.Group(); S.sub.add(S.dentro);
  const interno = new T.Mesh(new T.CylinderGeometry(R * 0.72, R * 0.72, L * 0.48, 32), new T.MeshStandardMaterial({color: 0x9aa4ae, metalness: 0.6, roughness: 0.4}));
  interno.rotation.z = Math.PI / 2; S.dentro.add(interno);
  const tqMat = new T.MeshStandardMaterial({color: 0xdfe8ef, transparent: true, opacity: 0.35, depthWrite: false});
  S.aguaTq = new T.MeshStandardMaterial({color: 0x2f8fd0, transparent: true, opacity: 0.85});
  for (const x of [L * 0.36, -L * 0.36]) {
    const tq = new T.Mesh(new T.BoxGeometry(8, R * 1.6, R * 1.6), tqMat); tq.position.set(x, 0, 0); S.dentro.add(tq);
    const ag = new T.Mesh(new T.BoxGeometry(7.8, 1, R * 1.55), S.aguaTq); S.dentro.add(ag);
    S.tanques.push({x, ag});
  }
  S.dentro.visible = false;
  // bolhas
  const nB = 160; S.nB = nB;
  S.bolhas = new T.InstancedMesh(new T.SphereGeometry(0.25, 8, 6), new T.MeshBasicMaterial({color: 0xeaf6ff, transparent: true, opacity: 0.8}), nB);
  S.bolhas.frustumCulled = false; cena.add(S.bolhas);
  S.bIni = []; for (let i = 0; i < nB; i++) S.bIni.push([A.aleat(), A.aleat(), A.aleat()]);
  S.m4 = new T.Matrix4(); S.q = new T.Quaternion(); S.v = new T.Vector3(); S.e = new T.Vector3();
  window._S = S; window._cam = camera; window._cena = cena;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam, cena = window._cena;
  // ondas
  const p = S.marGeo.attributes.position, b = S.marBase;
  for (let i = 0; i < p.count; i++) {
    const x = b[i * 3], z = b[i * 3 + 2];
    p.setY(i, 0.45 * Math.sin(x * 0.05 + e.t * 1.3) + 0.3 * Math.cos(z * 0.07 + e.t * 0.9));
  }
  p.needsUpdate = true; S.marGeo.computeVertexNormals();
  S.sub.position.set(...e.pos); S.sub.rotation.set(0, 0, e.pitch);
  S.casco.opacity = 1 - 0.75 * e.raiox; S.casco.depthWrite = e.raiox < 0.05;
  S.dentro.visible = e.raiox > 0.02;
  const hT = R * 1.5 * Math.max(0.01, e.lastro);
  S.tanques.forEach(({x, ag}) => { ag.scale.y = hT; ag.position.set(x, -R * 0.75 + hT / 2, 0); });
  S.helice.rotation.x = e.helice;
  // bolhas: das válvulas de cima (ar saindo quando enche) ou de baixo (sopro)
  for (let i = 0; i < S.nB; i++) {
    const [a, c, d] = S.bIni[i];
    const ph = (e.t * 0.8 + d) % 1;
    const tx = (i % 2 ? 1 : -1) * L * 0.36 + (a - 0.5) * 6;
    let vis = 0;
    if (e.bolhasVent > 0.02) { S.v.set(e.pos[0] + tx, e.pos[1] + R + ph * 14, (c - 0.5) * 3); vis = e.bolhasVent; }
    else if (e.bolhasSopro > 0.02) { S.v.set(e.pos[0] + tx + (c - 0.5) * 4, e.pos[1] - R + ph * 6 + ph * ph * 10, (a - 0.5) * 5); vis = e.bolhasSopro; }
    if (S.v.y > -0.2) vis = 0;   // não mostra bolhas acima da superfície
    const s = vis > 0 ? (0.6 + c) * vis : 0.0001;
    S.e.set(s, s, s); S.m4.compose(S.v, S.q, S.e); S.bolhas.setMatrixAt(i, S.m4);
  }
  S.bolhas.instanceMatrix.needsUpdate = true;
  const sob = e.cam[1] < 0;
  cena.fog = sob ? S.neblinaAgua : S.neblinaAr;
  S.ceu.ceu.visible = !sob;
  cena.background = sob ? new S.T.Color(0x1b6a92) : null;
  S.luzAgua.intensity = sob ? 1.4 : 0;
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
