// Tsunami chegando à costa: faixa de oceano ao longo de x (fundo fundo à esquerda, praia e cidade à direita).
// A superfície da água vem do Python como alturas amostradas ao longo de x (eta), a cena só posa.
// Estado: cam, alvo, fov, t, eta [NS alturas], x0, dx (amostragem), navio [x, y, rolagem], spray 0..1, sprayX.
import * as A from 'http://cena.local/ambiente.js';

const NS = 260, X0 = -2600, DX = 11.0, LARG = 700;

export function chao(x) {     // perfil do fundo e da terra (m)
  if (x < -1400) return -60;
  if (x < -120) return -60 + 58 * (x + 1400) / 1280;
  if (x < 60) return -2 + 5 * (x + 120) / 180;
  return 3 + Math.max(0, (x - 400) * 0.08);
}

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 6000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(61);
  S.ceu = A.ceu(T, cena, {sol: [0.3, 0.55, 0.75], neblina: 0xcbdbea, perto: 600, longe: 3500});
  A.nuvens(T, cena, {n: 30, y: [220, 320], x: [-3000, 1200], z: [-1200, -300], tam: [20, 36]});
  // fundo do mar e terra: malha ao longo de x com a altura de chao(x)
  const g = new T.PlaneGeometry(NS * DX + 1400, LARG, NS + 120, 8); g.rotateX(-Math.PI / 2); g.translate(0, 0, -LARG / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i) + (X0 + (NS * DX + 1400) / 2); p.setX(i, x); p.setY(i, chao(x)); }
  g.computeVertexNormals();
  const cores = [];
  for (let i = 0; i < p.count; i++) {
    const y = p.getY(i), x = p.getX(i);
    const c = y < -1 ? [0.55, 0.55, 0.42] : (x < 70 ? [0.93, 0.85, 0.62] : [0.42, 0.62, 0.32]);
    cores.push(...c);
  }
  g.setAttribute('color', new T.Float32BufferAttribute(cores, 3));
  cena.add(new T.Mesh(g, new T.MeshStandardMaterial({vertexColors: true, roughness: 1})));
  // cidade e árvores na terra
  for (let i = 0; i < 70; i++) {
    const x = 90 + A.aleat() * 500, z = -20 - A.aleat() * 500, h = 6 + A.aleat() * 18, w = 10 + A.aleat() * 10;
    const cor = [0xe8e2d4, 0xd9cbb0, 0xc9d3dc, 0xf0e6d8][i % 4];
    const b = new T.Mesh(new T.BoxGeometry(w, h, w), new T.MeshStandardMaterial({color: cor, roughness: 0.8}));
    b.position.set(x, chao(x) + h / 2, z); cena.add(b);
  }
  for (let i = 0; i < 50; i++) { const x = 70 + A.aleat() * 520; A.arvore(T, cena, x, -10 - A.aleat() * 600, {altura: 7 + A.aleat() * 4}); }
  // água
  const wg = new T.PlaneGeometry(NS * DX, LARG, NS - 1, 6); wg.rotateX(-Math.PI / 2); wg.translate(0, 0, -LARG / 2);
  S.wg = wg; S.wp = wg.attributes.position;
  for (let i = 0; i < S.wp.count; i++) S.wp.setX(i, S.wp.getX(i) + X0 + NS * DX / 2);
  S.agua = new T.Mesh(wg, new T.MeshStandardMaterial({color: 0x2a78a8, roughness: 0.2, metalness: 0.15, transparent: true, opacity: 0.92}));
  cena.add(S.agua);
  // corte (vista de aquário): face da água e face da terra no plano z = 0
  const cg = new T.PlaneGeometry(1, 1, NS - 1, 1);
  S.cg = cg;
  S.corte = new T.Mesh(cg, new T.MeshStandardMaterial({color: 0x2f86bb, transparent: true, opacity: 0.85, side: T.DoubleSide}));
  S.corte.frustumCulled = false; cena.add(S.corte);
  const tg = new T.PlaneGeometry(1, 1, NS + 119, 1);
  const tp = tg.attributes.position, nT = NS + 120;
  for (let i = 0; i < nT; i++) {
    const x = X0 + i * (NS * DX + 1400) / (nT - 1);
    tp.setXYZ(i, x, chao(x), 0.2); tp.setXYZ(i + nT, x, -90, 0.2);
  }
  tg.computeVertexNormals();
  cena.add(new T.Mesh(tg, new T.MeshStandardMaterial({color: 0x7a5a3a, roughness: 1, side: T.DoubleSide})));
  // navio
  S.navio = new T.Group(); cena.add(S.navio);
  const casco = new T.Mesh(new T.BoxGeometry(60, 8, 14), new T.MeshStandardMaterial({color: 0x30343c}));
  casco.position.y = 1; S.navio.add(casco);
  const ponte = new T.Mesh(new T.BoxGeometry(12, 9, 11), new T.MeshStandardMaterial({color: 0xf2f2f2})); ponte.position.set(-18, 9, 0); S.navio.add(ponte);
  for (let k = 0; k < 4; k++) {
    const c = new T.Mesh(new T.BoxGeometry(8, 5, 12), new T.MeshStandardMaterial({color: [0xd04030, 0x2f6fd8, 0xe8b030, 0x3aa060][k]}));
    c.position.set(-4 + k * 9, 7, 0); S.navio.add(c);
  }
  // espuma na crista
  const nE = 400; S.nE = nE;
  S.espuma = new T.InstancedMesh(new T.SphereGeometry(0.5, 6, 4), new T.MeshBasicMaterial({color: 0xf4fbff}), nE);
  S.espuma.frustumCulled = false; cena.add(S.espuma);
  S.eIni = []; for (let i = 0; i < nE; i++) S.eIni.push([A.aleat(), A.aleat(), A.aleat()]);
  S.m4 = new T.Matrix4(); S.q = new T.Quaternion(); S.v = new T.Vector3(); S.s = new T.Vector3();
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  const p = S.wp;
  for (let i = 0; i < p.count; i++) {
    const k = Math.min(NS - 1, Math.max(0, Math.round((p.getX(i) - X0) / DX)));
    p.setY(i, e.eta[k]);
  }
  p.needsUpdate = true; S.wg.computeVertexNormals();
  const cp = S.cg.attributes.position;
  for (let i = 0; i < NS; i++) {
    const x = X0 + i * DX;
    cp.setXYZ(i, x, e.eta[i], 0.3); cp.setXYZ(i + NS, x, Math.min(chao(x), e.eta[i]), 0.3);
  }
  cp.needsUpdate = true; S.cg.computeVertexNormals();
  S.navio.position.set(e.navio[0], e.navio[1], -60); S.navio.rotation.z = e.navio[2];
  for (let i = 0; i < S.nE; i++) {
    const [a, b, c] = S.eIni[i];
    if (e.spray < 0.02) { S.s.set(0.0001, 0.0001, 0.0001); S.v.set(0, -999, 0); }
    else {
      const x = e.sprayX + (a - 0.5) * 30;
      const k = Math.min(NS - 1, Math.max(0, Math.round((x - X0) / DX)));
      S.v.set(x, e.eta[k] + b * 4 * e.spray, -c * 500);
      const s = (0.6 + b) * e.spray * 2;
      S.s.set(s, s, s);
    }
    S.m4.compose(S.v, S.q, S.s); S.espuma.setMatrixAt(i, S.m4);
  }
  S.espuma.instanceMatrix.needsUpdate = true;
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
