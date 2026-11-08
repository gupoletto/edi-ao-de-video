// Terremoto: duas torres de 12 andares lado a lado sobre uma praça que treme. A da esquerda tem base fixa (balança
// em ressonância); a da direita fica sobre apoios de borracha (isolamento de base) e quase não se mexe.
// Estado vindo do Python: cam, alvo, fov, t, chao (deslocamento da praça, m), andN [offset de cada andar, torre
// normal], andI [idem, torre isolada], base (offset da laje sobre os apoios), estresse 0..1 (brilho vermelho nos
// pilares da torre normal), poeira 0..1.
import * as A from 'http://cena.local/ambiente.js';

const N = 12, HA = 3.5, L = 12;   // andares, altura do andar, largura da torre (m)
const XN = -11, XI = 11;          // centro das torres
const HB = 1.6;                   // altura dos apoios

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 3000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(31);
  S.ceu = A.ceu(T, cena, {sol: [0.5, 0.6, 0.6], neblina: 0xcfe0ee, perto: 250, longe: 1400});
  A.nuvens(T, cena, {n: 26, y: [140, 220], x: [-700, 700], z: [-700, -200]});
  A.grama(T, cena, {tam: 3000, cor: 0x6b9a46});
  A.morros(T, cena, {n: 22, dist: 900});
  for (let i = 0; i < 90; i++) {
    const x = -600 + A.aleat() * 1200, z = -500 + A.aleat() * 420;
    if (Math.abs(x) < 70 && z > -80) continue;
    A.arvore(T, cena, x, z, {altura: 6 + A.aleat() * 5, copa: 2.6 + A.aleat() * 1.5});
  }
  for (let i = 0; i < 26; i++) {   // prédios baixos ao fundo, para dar escala de cidade
    const x = -260 + i * 21 + A.aleat() * 6, z = -120 - A.aleat() * 140, h = 8 + A.aleat() * 30;
    const b = new T.Mesh(new T.BoxGeometry(14, h, 14), new T.MeshStandardMaterial({color: 0xb7bcc4, roughness: 0.8}));
    b.position.set(x, h / 2, z); cena.add(b);
  }
  // praça que treme
  S.praca = new T.Group(); cena.add(S.praca);
  const piso = new T.Mesh(new T.BoxGeometry(70, 1, 44), new T.MeshStandardMaterial({color: 0xa9a49b, roughness: 0.9}));
  piso.position.y = -0.45; S.praca.add(piso);
  for (let x = -34; x <= 34; x += 4) {
    const j = new T.Mesh(new T.BoxGeometry(0.08, 0.02, 44), new T.MeshStandardMaterial({color: 0x8d887f}));
    j.position.set(x, 0.06, 0); S.praca.add(j);
  }

  const vidro = new T.MeshStandardMaterial({color: 0x6f9cc4, metalness: 0.6, roughness: 0.15});
  const laje = new T.MeshStandardMaterial({color: 0xe9e6df, roughness: 0.7});
  S.pilarN = new T.MeshStandardMaterial({color: 0xd9d4ca, roughness: 0.7, emissive: 0xff2a1a, emissiveIntensity: 0});
  const torre = (x, pilarMat, cor) => {
    const andares = [];
    for (let k = 0; k < N; k++) {
      const g = new T.Group(); cena.add(g);
      const l = new T.Mesh(new T.BoxGeometry(L + 0.6, 0.45, L + 0.6), laje); l.position.y = 0.22; g.add(l);
      const v = new T.Mesh(new T.BoxGeometry(L - 0.4, HA - 0.45, L - 0.4), cor); v.position.y = 0.45 + (HA - 0.45) / 2; g.add(v);
      for (const dx of [-1, 1]) for (const dz of [-1, 1]) {
        const p = new T.Mesh(new T.BoxGeometry(0.6, HA - 0.45, 0.6), pilarMat);
        p.position.set(dx * (L / 2 - 0.1), 0.45 + (HA - 0.45) / 2, dz * (L / 2 - 0.1)); g.add(p);
      }
      andares.push(g);
    }
    const teto = new T.Mesh(new T.BoxGeometry(L + 0.6, 0.6, L + 0.6), laje); cena.add(teto);
    return {andares, teto, x};
  };
  S.tN = torre(XN, S.pilarN, vidro);
  S.tI = torre(XI, new T.MeshStandardMaterial({color: 0xd9d4ca, roughness: 0.7}),
               new T.MeshStandardMaterial({color: 0x7fb7a4, metalness: 0.6, roughness: 0.15}));
  // isolamento: fundação presa na praça, apoios de borracha, laje que desliza
  const fund = new T.Mesh(new T.BoxGeometry(L + 3, 0.8, L + 3), new T.MeshStandardMaterial({color: 0x8f8a82, roughness: 0.95}));
  fund.position.set(XI, 0.4, 0); S.praca.add(fund);
  S.apoios = [];
  const borracha = new T.MeshStandardMaterial({color: 0x1f2124, roughness: 0.9});
  const aco = new T.MeshStandardMaterial({color: 0xb8c0c8, metalness: 0.8, roughness: 0.3});
  for (const dx of [-1, 0, 1]) for (const dz of [-1, 0, 1]) {
    const g = new T.Group(); cena.add(g);
    const c = new T.Mesh(new T.CylinderGeometry(0.9, 0.9, HB, 24), borracha); c.position.y = HB / 2; g.add(c);
    for (let i = 1; i < 5; i++) {
      const a = new T.Mesh(new T.CylinderGeometry(0.93, 0.93, 0.07, 24), aco); a.position.y = i * HB / 5; g.add(a);
    }
    S.apoios.push({g, dx: dx * (L / 2 - 1.2), dz: dz * (L / 2 - 1.2)});
  }
  S.lajeI = new T.Mesh(new T.BoxGeometry(L + 2, 0.7, L + 2), new T.MeshStandardMaterial({color: 0x9b968e, roughness: 0.9}));
  cena.add(S.lajeI);
  S.baseN = new T.Mesh(new T.BoxGeometry(L + 2, 0.8 + HB + 0.7, L + 2), new T.MeshStandardMaterial({color: 0x8f8a82, roughness: 0.95}));
  S.baseN.position.set(XN, (0.8 + HB + 0.7) / 2, 0); S.praca.add(S.baseN);

  // poeira
  const nP = 300; S.nP = nP; S.pPos = new Float32Array(nP * 3);
  const pg = new T.BufferGeometry(); pg.setAttribute('position', new T.BufferAttribute(S.pPos, 3));
  S.poeira = new T.Points(pg, new T.PointsMaterial({color: 0xcbbd9e, size: 0.4, transparent: true, opacity: 0.6, depthWrite: false}));
  S.poeira.frustumCulled = false; cena.add(S.poeira);
  S.pIni = []; for (let i = 0; i < nP; i++) S.pIni.push([A.aleat(), A.aleat(), A.aleat()]);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  const y0 = 0.8 + HB + 0.7;   // térreo começa acima da fundação + apoios + laje
  S.praca.position.x = e.chao;
  S.baseN.position.x = XN;      // (filho da praça)
  const poe = (t, offs, x) => {
    for (let k = 0; k < N; k++) {
      const o = offs[k], o2 = offs[Math.min(N - 1, k + 1)];
      const g = t.andares[k];
      g.position.set(x + o, y0 + k * HA, 0);
      g.rotation.z = -Math.atan2(o2 - o, HA) * 0.6;   // o andar inclina com a diferença para o de cima
    }
    t.teto.position.set(x + offs[N - 1], y0 + N * HA + 0.3, 0);
  };
  poe(S.tN, e.andN, XN);
  poe(S.tI, e.andI, XI);
  // apoios: embaixo presos na praça, em cima na laje; inclinam com a diferença
  const d = e.base - e.chao;
  S.apoios.forEach(({g, dx, dz}) => {
    g.position.set(XI + dx + e.chao, 0.8, dz);
    g.rotation.z = -Math.atan2(d, HB);
    g.scale.y = Math.sqrt(1 + (d / HB) ** 2);
    g.position.x += d / 2 - Math.sin(Math.atan2(d, HB)) * HB / 2;
  });
  S.lajeI.position.set(XI + e.base, 0.8 + HB + 0.35, 0);
  S.pilarN.emissiveIntensity = 1.4 * e.estresse;
  const Q = S.pPos;
  for (let i = 0; i < S.nP; i++) {
    const [a, b, c] = S.pIni[i];
    if (e.poeira <= 0.01) { Q[i * 3 + 1] = -999; continue; }
    const ang = a * Math.PI * 2, rr = 4 + 30 * b;
    Q[i * 3] = Math.cos(ang) * rr * 1.4 + Math.sin(e.t * 0.7 + c * 9) * 1.5;
    Q[i * 3 + 1] = 0.2 + c * 3 * e.poeira + (e.t * 0.3 + c) % 1 * 0.8;
    Q[i * 3 + 2] = Math.sin(ang) * rr * 0.6;
  }
  S.poeira.geometry.attributes.position.needsUpdate = true;
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
