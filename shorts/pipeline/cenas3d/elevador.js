// Elevador panorâmico num prédio de vidro: os cabos arrebentam, o regulador de velocidade (governor) dispara no alto
// do poço e os freios de segurança (cunhas) agarram os trilhos.
// Estado vindo do Python: cam, alvo, fov, t, carro (y do piso da cabine, m), cabos 0..1 (0 = inteiros, >0 = tempo
// de recuo da ponta de cima após o rompimento, normalizado), quebra (y do rompimento), faisca (0..1, rompimento),
// gov (rad, ângulo do regulador), pesos 0..1 (abertura dos pesos), garra 0..1 (garra do regulador fechando),
// cunha 0..1 (cunhas subindo), atrito 0..1 (faíscas nos trilhos), raiox 0..1 (cabine translúcida), ts (s, tempo
// físico para animar faíscas).
import * as A from 'http://cena.local/ambiente.js';

const TOPO = 46;                 // y do eixo da polia de tração (casa de máquinas no telhado)
const RX = 1.15, ZC = 1.45;      // trilhos-guia em x = ±RX, centro do poço em z = ZC
const CW = 2.0, CD = 1.6, CH = 2.5;   // cabine: largura, profundidade, altura
const GX = -1.75, GZ = 2.05, GR = 0.36;   // regulador: centro (x, z) e raio; fica no alto do poço (y = TOPO - 1)
const NC = 6;                    // cabos de tração

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 1500; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.05;
  const S = {T};
  A.reiniciar(3);
  A.ceu(T, cena, {sol: [0.5, 0.6, 0.65], neblina: 0xcfe0ee, perto: 120, longe: 700});
  A.nuvens(T, cena, {n: 22, y: [70, 120], x: [-500, 500], z: [-500, -150]});
  A.nuvens(T, cena, {n: 10, y: [70, 120], x: [-500, 500], z: [150, 420]});
  A.grama(T, cena, {cor: 0x6a9a44});
  A.morros(T, cena, {n: 18, dist: 430});
  // praça em frente ao prédio
  const praca = new T.Mesh(new T.PlaneGeometry(60, 30), new T.MeshStandardMaterial({color: 0xb9b4aa, roughness: 0.95}));
  praca.rotation.x = -Math.PI / 2; praca.position.set(0, 0.01, 8); cena.add(praca);
  for (let i = 0; i < 10; i++) {
    const x = -26 + i * 5.8 + A.aleat() * 1.5;
    if (Math.abs(x) < 6) continue;
    A.arvore(T, cena, x, 14 + A.aleat() * 6, {altura: 5 + A.aleat() * 2});
  }
  // outros prédios ao fundo
  const cinzas = [0x8c96a3, 0xa9b1bb, 0x7c8796, 0xb7bcc4];
  for (let i = 0; i < 14; i++) {
    const h = 20 + A.aleat() * 50, w = 10 + A.aleat() * 12;
    const b = new T.Mesh(new T.BoxGeometry(w, h, 12), new T.MeshStandardMaterial({color: cinzas[i % 4], roughness: 0.7}));
    b.position.set(-120 + i * 19 + A.aleat() * 6, h / 2, -60 - A.aleat() * 60); cena.add(b);
  }

  // ---------- prédio principal: vidro azulado com grade de janelas (textura desenhada) ----------
  const tela = document.createElement('canvas'); tela.width = 512; tela.height = 1024;
  const g2 = tela.getContext('2d');
  g2.fillStyle = '#3d5a78'; g2.fillRect(0, 0, 512, 1024);
  for (let y = 0; y < 12; y++) for (let x = 0; x < 8; x++) {
    const k = 0.75 + 0.25 * Math.random();
    g2.fillStyle = `rgb(${Math.round(120 * k)},${Math.round(165 * k)},${Math.round(205 * k)})`;
    g2.fillRect(x * 64 + 5, y * 85 + 8, 54, 70);
  }
  const vidroTex = new T.CanvasTexture(tela); vidroTex.colorSpace = T.SRGBColorSpace;
  vidroTex.wrapS = vidroTex.wrapT = T.RepeatWrapping; vidroTex.repeat.set(2, 1);
  const predio = new T.Mesh(new T.BoxGeometry(18, 44, 14),
    new T.MeshStandardMaterial({map: vidroTex, metalness: 0.35, roughness: 0.25}));
  predio.position.set(0, 22, -7); cena.add(predio);
  const telhado = new T.Mesh(new T.BoxGeometry(18.4, 0.6, 14.4), new T.MeshStandardMaterial({color: 0xd9dde2}));
  telhado.position.set(0, 44.3, -7); cena.add(telhado);

  // ---------- poço de vidro na fachada ----------
  const aco = new T.MeshStandardMaterial({color: 0xd5dae1, metalness: 0.8, roughness: 0.3});
  const escuro = new T.MeshStandardMaterial({color: 0x2a2f37, metalness: 0.6, roughness: 0.45});
  const X0 = -2.45, X1 = 1.75, Z0 = 0.15, Z1 = 2.75;
  for (const [x, z] of [[X0, Z0], [X0, Z1], [X1, Z0], [X1, Z1]]) {
    const p = new T.Mesh(new T.BoxGeometry(0.16, TOPO + 1.5, 0.16), aco);
    p.position.set(x, (TOPO + 1.5) / 2, z); cena.add(p);
  }
  for (let y = 0; y <= TOPO; y += 3.6) {  // vigas a cada andar: dão a noção da queda
    for (const [w, d, x, z] of [[X1 - X0, 0.12, (X0 + X1) / 2, Z1], [X1 - X0, 0.12, (X0 + X1) / 2, Z0],
                                [0.12, Z1 - Z0, X0, (Z0 + Z1) / 2], [0.12, Z1 - Z0, X1, (Z0 + Z1) / 2]]) {
      const v = new T.Mesh(new T.BoxGeometry(w, 0.14, d), aco); v.position.set(x, y, z); cena.add(v);
    }
  }
  S.vidroPoco = new T.MeshStandardMaterial({color: 0xbfe3ff, metalness: 0.1, roughness: 0.05, transparent: true,
                                           opacity: 0.12, depthWrite: false, side: T.DoubleSide});
  const vp = new T.Mesh(new T.BoxGeometry(X1 - X0, TOPO + 1.5, Z1 - Z0), S.vidroPoco);
  vp.position.set((X0 + X1) / 2, (TOPO + 1.5) / 2, (Z0 + Z1) / 2); cena.add(vp);
  // trilhos-guia (perfil T)
  for (const s of [-1, 1]) {
    const alma = new T.Mesh(new T.BoxGeometry(0.1, TOPO, 0.03), aco);
    alma.position.set(s * RX, TOPO / 2, ZC); cena.add(alma);
    const aba = new T.Mesh(new T.BoxGeometry(0.03, TOPO, 0.14), aco);
    aba.position.set(s * (RX + 0.05), TOPO / 2, ZC); cena.add(aba);
  }
  // casa de máquinas no topo do poço e polia de tração
  const casa = new T.Mesh(new T.BoxGeometry(X1 - X0 + 0.3, 1.6, Z1 - Z0 + 0.3), escuro);
  casa.position.set((X0 + X1) / 2, TOPO + 1.3, (Z0 + Z1) / 2); cena.add(casa);
  S.polia = new T.Mesh(new T.CylinderGeometry(0.42, 0.42, 0.5, 32), aco);
  S.polia.rotation.z = Math.PI / 2; S.polia.position.set(0, TOPO, ZC); cena.add(S.polia);
  // fosso: para-choques (molas) no chão
  for (const x of [-0.5, 0.5]) {
    const m = new T.Mesh(new T.CylinderGeometry(0.16, 0.16, 0.7, 16), new T.MeshStandardMaterial({color: 0xe0b020}));
    m.position.set(x, 0.35, ZC); cena.add(m);
  }

  // ---------- cabine panorâmica ----------
  S.cabine = new T.Group(); cena.add(S.cabine);
  const piso = new T.Mesh(new T.BoxGeometry(CW, 0.18, CD), escuro); piso.position.y = 0.09; S.cabine.add(piso);
  const teto = new T.Mesh(new T.BoxGeometry(CW, 0.16, CD), escuro); teto.position.y = CH; S.cabine.add(teto);
  const luz = new T.Mesh(new T.PlaneGeometry(CW * 0.7, CD * 0.6),
                         new T.MeshStandardMaterial({color: 0xffffff, emissive: 0xfff2d8, emissiveIntensity: 1.2}));
  luz.rotation.x = Math.PI / 2; luz.position.y = CH - 0.09; S.cabine.add(luz);
  for (const [x, z] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
    const p = new T.Mesh(new T.BoxGeometry(0.08, CH, 0.08), aco); p.position.set(x * CW / 2, CH / 2, z * CD / 2);
    S.cabine.add(p);
  }
  S.vidroCab = new T.MeshStandardMaterial({color: 0xcfeaff, metalness: 0.1, roughness: 0.05, transparent: true,
                                          opacity: 0.22, depthWrite: false, side: T.DoubleSide});
  for (const [w, d, x, z] of [[CW, 0.02, 0, CD / 2], [0.02, CD, -CW / 2, 0], [0.02, CD, CW / 2, 0]]) {
    const v = new T.Mesh(new T.BoxGeometry(w, CH - 0.2, d), S.vidroCab); v.position.set(x, CH / 2, z); S.cabine.add(v);
  }
  const fundo = new T.Mesh(new T.BoxGeometry(CW, CH - 0.2, 0.04), new T.MeshStandardMaterial({color: 0x9aa3ad, metalness: 0.7, roughness: 0.35}));
  fundo.position.set(0, CH / 2, -CD / 2); S.cabine.add(fundo);
  const corrimao = new T.Mesh(new T.BoxGeometry(CW - 0.2, 0.05, 0.05), aco);
  corrimao.position.set(0, 1.0, CD / 2 - 0.12); S.cabine.add(corrimao);
  // travessa superior com o engate dos cabos
  const trav = new T.Mesh(new T.BoxGeometry(CW + 0.5, 0.22, 0.24), escuro); trav.position.y = CH + 0.3; S.cabine.add(trav);
  for (const s of [-1, 1]) {
    const m = new T.Mesh(new T.BoxGeometry(0.16, 0.5, 0.2), escuro); m.position.set(s * (CW / 2 + 0.12), CH + 0.08, 0);
    S.cabine.add(m);
  }
  // guias deslizantes e freios de segurança (embaixo, um de cada lado, abraçando o trilho)
  S.cunhas = [];
  const vermelho = new T.MeshStandardMaterial({color: 0xd23a2a, metalness: 0.4, roughness: 0.4});
  S.cunhaMat = new T.MeshStandardMaterial({color: 0xe0402c, metalness: 0.5, roughness: 0.35, emissive: 0x000000});
  for (const s of [-1, 1]) {
    const placa = new T.Mesh(new T.BoxGeometry(0.05, 0.5, 0.42), escuro);  // suporte entre a cabine e o trilho
    placa.position.set(s * (CW / 2 + 0.03), 0.05, 0); S.cabine.add(placa);
    for (const lado of [-1, 1]) {
      const c = new T.Mesh(new T.BoxGeometry(0.12, 0.3, 0.07), S.cunhaMat);
      c.position.set(s * RX, 0.0, lado * 0.07); S.cabine.add(c); S.cunhas.push({m: c, lado});
    }
  }
  // haste que liga a cabine ao cabo do regulador (no topo, lado esquerdo)
  S.haste = new T.Mesh(new T.BoxGeometry(0.75, 0.08, 0.08), vermelho);
  S.haste.position.set(-CW / 2 - 0.1, CH + 0.3, GZ - ZC); S.cabine.add(S.haste);
  S.cabine.position.set(0, 20, ZC);
  S.vidros = [S.vidroCab];

  // ---------- cabos de tração ----------
  S.cabos = [];
  const caboMat = new T.MeshStandardMaterial({color: 0x9aa3ad, metalness: 0.9, roughness: 0.3});
  const cil = new T.CylinderGeometry(0.04, 0.04, 1, 10);
  for (let i = 0; i < NC; i++) {
    const x = (i % 3 - 1) * 0.2, z = ZC + (i < 3 ? -0.1 : 0.1);
    const baixo = new T.Mesh(cil, caboMat), cima = new T.Mesh(cil, caboMat);
    cena.add(baixo); cena.add(cima);
    S.cabos.push({x, z, baixo, cima, fase: A.aleat() * 6});
  }
  // ---------- regulador de velocidade (polia com pesos) e seu cabo ----------
  S.gov = new T.Group(); S.gov.position.set(GX, TOPO - 1.0, GZ); cena.add(S.gov);
  const disco = new T.Mesh(new T.CylinderGeometry(GR, GR, 0.08, 40), aco); disco.rotation.x = Math.PI / 2;
  S.govRoda = new T.Group(); S.gov.add(S.govRoda); S.govRoda.add(disco);
  const raio = new T.Mesh(new T.BoxGeometry(GR * 1.9, 0.05, 0.1), escuro); raio.position.z = 0.06; S.govRoda.add(raio);
  S.pesos = [];
  for (const s of [-1, 1]) {
    const piv = new T.Group(); piv.position.set(s * 0.08, 0, 0.1); S.govRoda.add(piv);
    const peso = new T.Mesh(new T.BoxGeometry(0.22, 0.09, 0.07), vermelho); peso.position.set(s * 0.12, 0, 0);
    piv.add(peso); S.pesos.push({piv, s});
  }
  const suporte = new T.Mesh(new T.BoxGeometry(0.12, 0.7, 0.1), escuro); suporte.position.set(0, 0.35, -0.1); S.gov.add(suporte);
  S.garra = new T.Mesh(new T.BoxGeometry(0.16, 0.22, 0.14), new T.MeshStandardMaterial({color: 0xf2c230}));
  S.gov.add(S.garra);
  S.govCabo = new T.Mesh(new T.CylinderGeometry(0.014, 0.014, 1, 6), new T.MeshStandardMaterial({color: 0xb8bec6, metalness: 0.7}));
  cena.add(S.govCabo);
  S.govCabo2 = new T.Mesh(new T.CylinderGeometry(0.014, 0.014, 1, 6), new T.MeshStandardMaterial({color: 0xb8bec6, metalness: 0.7}));
  cena.add(S.govCabo2);
  // ---------- faíscas (rompimento e atrito nas cunhas) ----------
  const nF = 260; S.nF = nF; S.fPos = new Float32Array(nF * 3);
  const fg = new T.BufferGeometry(); fg.setAttribute('position', new T.BufferAttribute(S.fPos, 3));
  S.faiscas = new T.Points(fg, new T.PointsMaterial({color: 0xffd27a, size: 0.035, transparent: true, opacity: 1}));
  S.faiscas.frustumCulled = false; cena.add(S.faiscas);
  S.fIni = []; for (let i = 0; i < nF; i++) S.fIni.push([A.aleat() - 0.5, A.aleat(), A.aleat() - 0.5, A.aleat()]);
  window._S = S; window._cam = camera;
};

function liga(m, a, b) {
  // cilindro unitário (eixo y) de a até b
  const T = window._S.T;
  const va = new T.Vector3(...a), vb = new T.Vector3(...b);
  const d = vb.clone().sub(va), L = d.length();
  m.visible = L > 0.01;
  m.position.copy(va.clone().add(vb).multiplyScalar(0.5));
  m.scale.set(1, Math.max(L, 0.001), 1);
  m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), d.normalize());
}

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  const yc = e.carro;
  S.cabine.position.y = yc;
  const engate = yc + CH + 0.4;
  // cabos: inteiros até a polia; depois do rompimento a parte de baixo cai junto com a cabine (chicoteando) e a de
  // cima recua para o alto
  S.cabos.forEach((c, i) => {
    if (e.cabos <= 0) {
      liga(c.baixo, [c.x, engate, c.z], [c.x, TOPO - 0.4, c.z]); c.cima.visible = false; return;
    }
    const q = e.cabos;
    const ponta = e.quebra - (e.carroIni - yc);              // a ponta de baixo desce com a cabine
    const chic = 0.35 * Math.sin(q * 9 + c.fase) * Math.min(1, q * 3);
    liga(c.baixo, [c.x, engate, c.z], [c.x + chic, ponta, c.z + chic * 0.4]);
    const recuo = 2.2 * (1 - Math.exp(-q * 2.5)) + 0.2 * (i % 3);
    const bal = 0.25 * Math.sin(q * 7 + c.fase) * Math.exp(-q);
    liga(c.cima, [c.x + bal, e.quebra + 0.15 + recuo, c.z], [c.x, TOPO - 0.4, c.z]);
  });
  // regulador
  S.govRoda.rotation.z = -e.gov;
  S.pesos.forEach(p => { p.piv.rotation.z = p.s * 0.9 * e.pesos; });
  S.garra.position.set(GR + 0.13 - 0.06 * e.garra, -0.05, 0.0);
  S.garra.material.emissive = new S.T.Color(e.garra > 0.9 ? 0x553300 : 0x000000);
  // cabo do regulador: desce do lado da cabine (preso na haste) e sobe do outro lado (vindo da polia do fosso)
  const xg = GX + GR, yg = TOPO - 1.0;
  liga(S.govCabo, [xg, yg, GZ], [xg, 0.6, GZ]);
  liga(S.govCabo2, [GX - GR, yg, GZ], [GX - GR, 0.6, GZ]);
  S.haste.rotation.z = 0.35 * e.cunha;
  // cunhas sobem e apertam o trilho
  S.cunhas.forEach(c => {
    c.m.position.y = 0.0 + 0.12 * e.cunha;
    c.m.position.z = c.lado * (0.075 - 0.025 * e.cunha);
  });
  S.cunhaMat.emissive.setRGB(0.9 * e.atrito, 0.35 * e.atrito, 0.05 * e.atrito);  // brasa do atrito
  // raio-x: vidro do poço some um pouco para ver os detalhes
  S.vidroPoco.opacity = 0.12 * (1 - e.raiox);
  // faíscas: no ponto de rompimento (faisca) ou nas cunhas (atrito)
  const P = S.fPos;
  for (let i = 0; i < S.nF; i++) {
    const [a, b, d, k] = S.fIni[i];
    let x = 0, y = -100, z = 0;
    if (e.faisca > 0 && i < 120) {
      const tf = e.faisca * (0.5 + k);
      x = a * 2.2 * tf; z = ZC + d * 2.2 * tf; y = e.quebra + b * 1.4 * tf - 2.5 * tf * tf;
      if (tf > 1.1) y = -100;
    } else if (e.atrito > 0 && i >= 120) {
      const lado = i % 2 ? 1 : -1, tf = ((e.ts * 3 + k) % 1);
      x = lado * (RX + 0.1 + Math.abs(a) * 0.9 * tf); z = ZC + d * 0.8 * tf;
      y = yc + 0.05 + b * 0.5 * tf - 1.2 * tf * tf;
      if (A.aleat() > e.atrito) y = -100;
    }
    P[i * 3] = x; P[i * 3 + 1] = y; P[i * 3 + 2] = z;
  }
  S.faiscas.geometry.attributes.position.needsUpdate = true;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
