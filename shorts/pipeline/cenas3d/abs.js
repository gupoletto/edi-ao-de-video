// Freada no molhado: dois carros iguais, um sem ABS (rodas travam, desliza reto e derruba os cones) e um com ABS
// (as rodas continuam girando e ele desvia). Corpo do carro igual ao de batida.js.
// Estado vindo do Python: cam, alvo, fov, t, verm [x,z,rumo,giroRoda,esterco], azul [idem], freioV/freioA 0..1
// (brilho do disco), marcas (m de marca de pneu atrás do vermelho), cones [[x,z,tomb,rumo]...], spray 0..1.
import * as A from 'http://cena.local/ambiente.js';

const COMP = 4.5, LARG = 1.8;
const XF = COMP / 2;
const fazCarro = (T, cena, cor) => {
  const g = new T.BoxGeometry(COMP, 1, LARG, 90, 24, 22);
  const p = g.attributes.position;
  const altura = (x) => {  // altura do teto/capô ao longo do comprimento
    if (x > 1.05) return 0.9 - 0.2 * Math.pow((x - 1.05) / 1.2, 2);         // capô, caindo na frente
    if (x > 0.35) return 0.9 + 0.5 * Math.pow((1.05 - x) / 0.7, 0.8);       // para-brisa inclinado
    if (x > -0.75) return 1.4 - 0.03 * Math.pow((x + 0.2) / 0.55, 2);        // teto levemente curvo
    if (x > -1.55) return 1.4 - 0.45 * Math.pow((-0.75 - x) / 0.8, 1.2);     // vidro traseiro
    return 0.95 - 0.08 * Math.pow((-1.55 - x) / 0.7, 2);                     // porta-malas
  };
  const cores = [];
  const corCarro = new T.Color(cor), vidro = new T.Color(0x18202c), friso = new T.Color(0x2a2e35);
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), v = p.getY(i) + 0.5, z = p.getZ(i);
    const h = altura(x), base = 0.28;
    const y = base + v * (h - base);
    const estreita = 1 - 0.13 * Math.pow(Math.max(0, (y - 0.95) / 0.5), 1.5);            // teto mais estreito
    const pontas = 1 - 0.1 * Math.pow(Math.max(0, (Math.abs(x) - 1.7) / 0.55), 2);         // frente/traseira arredondadas
    p.setXYZ(i, x, y, z * estreita * pontas);
    let c = corCarro;
    const lado = Math.abs(z) > LARG * 0.42, cima = v > 0.98;
    if (y > 0.97 && y < 1.33 && x > -1.4 && x < 0.95 && (lado || !cima)) c = vidro;          // janelas laterais
    if (cima && ((x > 0.42 && x < 0.98) || (x < -0.8 && x > -1.45))) c = vidro;            // para-brisa e vidro traseiro
    if (y < 0.42) c = friso;                                                                 // saia
    cores.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new T.Float32BufferAttribute(cores, 3));
  g.computeVertexNormals();
    const corpoMat = new T.MeshStandardMaterial({vertexColors: true, metalness: 0.45, roughness: 0.32, transparent: true,
                                           opacity: 1, side: T.DoubleSide});
  const corpo = new T.Mesh(g, corpoMat);
  const carro = new T.Group(); carro.add(corpo); cena.add(carro);
  // faróis e lanternas
  for (const z of [-0.6, 0.6]) {
    const f = new T.Mesh(new T.SphereGeometry(0.13, 16, 8), new T.MeshStandardMaterial({color: 0xfff6d8, emissive: 0xfff2c0, emissiveIntensity: 0.6}));
    f.scale.set(0.5, 1, 1.4); f.position.set(XF - 0.08, 0.72, z); carro.add(f); f.userData.frente = true;
    const l = new T.Mesh(new T.BoxGeometry(0.06, 0.12, 0.4), new T.MeshStandardMaterial({color: 0xb01010, emissive: 0x800000}));
    l.position.set(-XF + 0.03, 0.82, z); carro.add(l);
  }
  
  // rodas
  const rodas = [];
  const pneu = new T.MeshStandardMaterial({color: 0x1b1d21, roughness: 0.9});
  const aro = new T.MeshStandardMaterial({color: 0xc9ced6, metalness: 0.9, roughness: 0.25});
  for (const [x, z] of [[1.45, 0.82], [1.45, -0.82], [-1.45, 0.82], [-1.45, -0.82]]) {
    const w = new T.Group(); const ws = new T.Group(); w.add(ws);
    const t = new T.Mesh(new T.CylinderGeometry(0.34, 0.34, 0.24, 28), pneu); t.rotation.x = Math.PI / 2; ws.add(t);
    const a = new T.Mesh(new T.CylinderGeometry(0.2, 0.2, 0.25, 6), aro); a.rotation.x = Math.PI / 2; ws.add(a);
    const raio = new T.Mesh(new T.BoxGeometry(0.36, 0.05, 0.26), aro); ws.add(raio);
    w.position.set(x, 0.34, z); carro.add(w); rodas.push({w, ws});
  }
  return {carro, rodas};
};

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 1500; camera.updateProjectionMatrix();
  r.toneMappingExposure = 0.9;
  const S = {T};
  A.reiniciar(7);
  S.ceu = A.ceu(T, cena, {sol: [-0.4, 0.5, 0.7], topo: [0.30, 0.36, 0.45], meio: [0.55, 0.60, 0.66], baixo: [0.75, 0.78, 0.82],
                          neblina: 0xb4bcc6, perto: 80, longe: 500});
  A.nuvens(T, cena, {n: 30, y: [45, 70], x: [-500, 500], z: [-500, -100], tam: [12, 22]});
  A.grama(T, cena, {cor: 0x55804a});
  A.morros(T, cena, {n: 18, dist: 420});
  for (let i = 0; i < 40; i++) {
    const x = -300 + i * 16 + A.aleat() * 8, lado = i % 2 ? 1 : -1;
    A.arvore(T, cena, x, lado * (20 + A.aleat() * 12), {altura: 5 + A.aleat() * 3});
  }
  // pista larga e molhada (asfalto escuro, brilhante), faixas
  const asf = new T.Mesh(new T.PlaneGeometry(900, 26), new T.MeshStandardMaterial({color: 0x26292e, roughness: 0.22, metalness: 0.35}));
  asf.rotation.x = -Math.PI / 2; asf.position.y = 0.01; cena.add(asf);
  const branco = new T.MeshStandardMaterial({color: 0xe8e8e8, roughness: 0.5});
  for (let x = -440; x < 440; x += 12) for (const z of [0]) {
    const f = new T.Mesh(new T.PlaneGeometry(6, 0.25), branco); f.rotation.x = -Math.PI / 2; f.position.set(x, 0.02, z); cena.add(f);
  }
  for (const z of [-12.6, 12.6]) {
    const f = new T.Mesh(new T.PlaneGeometry(900, 0.3), branco); f.rotation.x = -Math.PI / 2; f.position.set(0, 0.02, z); cena.add(f);
  }
  S.v = fazCarro(T, cena, 0xd8322f);
  S.a = fazCarro(T, cena, 0x2f6fd8);
  // discos de freio (brilham quando freia)
  S.discoV = new T.MeshStandardMaterial({color: 0x555a60, emissive: 0xff3010, emissiveIntensity: 0});
  S.discoA = new T.MeshStandardMaterial({color: 0x555a60, emissive: 0xff3010, emissiveIntensity: 0});
  for (const [c, m] of [[S.v, S.discoV], [S.a, S.discoA]]) c.rodas.forEach(({w}) => {
    const d = new T.Mesh(new T.CylinderGeometry(0.11, 0.11, 0.2, 20), m); d.rotation.x = Math.PI / 2; w.add(d);
  });
  // marca de pneu (faixas escuras que crescem atrás do carro vermelho)
  S.marcas = [];
  for (const z of [-0.82, 0.82]) {
    const m = new T.Mesh(new T.PlaneGeometry(1, 0.22), new T.MeshBasicMaterial({color: 0x0b0b0c, transparent: true, opacity: 0.8}));
    m.rotation.x = -Math.PI / 2; m.position.y = 0.025; cena.add(m); S.marcas.push({m, z});
  }
  // cones na faixa do vermelho e na do azul
  S.cones = [];
  const laranja = new T.MeshStandardMaterial({color: 0xff6a1a, roughness: 0.6});
  const listra = new T.MeshStandardMaterial({color: 0xf2f2f2, roughness: 0.6});
  for (let i = 0; i < 10; i++) {
    const g = new T.Group();
    const c = new T.Mesh(new T.ConeGeometry(0.28, 0.8, 16), laranja); c.position.y = 0.4; g.add(c);
    const l = new T.Mesh(new T.CylinderGeometry(0.19, 0.22, 0.12, 16), listra); l.position.y = 0.42; g.add(l);
    const b = new T.Mesh(new T.BoxGeometry(0.6, 0.06, 0.6), laranja); b.position.y = 0.03; g.add(b);
    cena.add(g); S.cones.push(g);
  }
  // spray de água atrás das rodas
  const nP = 260; S.nP = nP; S.pPos = new Float32Array(nP * 3);
  const pg = new T.BufferGeometry(); pg.setAttribute('position', new T.BufferAttribute(S.pPos, 3));
  S.spray = new T.Points(pg, new T.PointsMaterial({color: 0xdfe8f2, size: 0.12, transparent: true, opacity: 0.55, depthWrite: false}));
  S.spray.frustumCulled = false; cena.add(S.spray);
  S.pIni = []; for (let i = 0; i < nP; i++) S.pIni.push([A.aleat(), A.aleat(), A.aleat()]);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  for (const [c, st] of [[S.v, e.verm], [S.a, e.azul]]) {
    c.carro.position.set(st[0], 0, st[1]); c.carro.rotation.y = st[2];
    c.rodas.forEach(({w, ws}, i) => { ws.rotation.z = -st[3]; if (i < 2) w.rotation.y = st[4]; });
  }
  S.discoV.emissiveIntensity = 0.7 * e.freioV; S.discoA.emissiveIntensity = 0.7 * e.freioA;
  S.marcas.forEach(({m, z}) => {
    const L = Math.max(0.01, e.marcas);
    m.scale.x = L; m.position.set(e.marcaX - L / 2, 0.025, e.marcaZ + z);
  });
  e.cones.forEach((c, i) => {
    const g = S.cones[i]; g.position.set(c[0], 0, c[1]); g.rotation.set(0, c[3], c[2]);
  });
  const Q = S.pPos, ativo = e.sprayDe;
  for (let i = 0; i < S.nP; i++) {
    const [a, b, d] = S.pIni[i];
    if (!ativo || e.spray < 0.02) { Q[i * 3 + 1] = -99; continue; }
    const ph = (e.t * 1.7 + d) % 1;
    Q[i * 3] = ativo[0] - 2.4 - ph * 4 * e.spray;
    Q[i * 3 + 1] = 0.1 + Math.sin(ph * Math.PI) * 0.7 * e.spray * (0.5 + b);
    Q[i * 3 + 2] = ativo[1] + (a < 0.5 ? -0.85 : 0.85) + (a - 0.5) * 0.6 * ph;
  }
  S.spray.geometry.attributes.position.needsUpdate = true;
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
