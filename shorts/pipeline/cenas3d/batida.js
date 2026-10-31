// Carro batendo numa árvore: estrada no campo, carro com zona de deformação (a frente amassa como sanfona),
// modo "raio-x" (carroceria translúcida) com boneco de crash test, cinto e airbag.
// Estado vindo do Python: cam, alvo, fov, t, carro [x,z], rumo (rad), amassa (m), boneco (m, deslocamento para a
// frente), airbag 0..1 (tamanho), raiox 0..1, roda (rad), balanco (rad, árvore), folhas (s desde a batida, <0 = não),
// arvore [x,z].
import * as A from 'http://cena.local/ambiente.js';

const COMP = 4.5, LARG = 1.8, ZONA = 1.05;   // carro: comprimento, largura, zona de deformação
const XF = COMP / 2, XS = COMP / 2 - ZONA;

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 1500; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(5);
  A.ceu(T, cena, {sol: [-0.45, 0.55, 0.7], neblina: 0xcfe0ee, perto: 90, longe: 600});
  A.nuvens(T, cena, {n: 22, y: [55, 90], x: [-500, 500], z: [-500, -120]});
  A.nuvens(T, cena, {n: 10, y: [55, 90], x: [-500, 500], z: [150, 400]});
  A.grama(T, cena);
  A.estrada(T, cena, {larg: 7});
  A.morros(T, cena, {n: 18, dist: 420});
  for (let i = 0; i < 26; i++) {  // árvores ao longo da estrada, longe do ponto da batida
    const x = -260 + i * 22 + A.aleat() * 8, lado = i % 2 ? 1 : -1;
    if (Math.abs(x) < 14) continue;
    A.arvore(T, cena, x, lado * (8 + A.aleat() * 10), {altura: 5 + A.aleat() * 3});
  }
  S.arv = A.arvore(T, cena, 0, -4.6, {altura: 10, copa: 3.0, tronco: 0.42});

  // ---------- carro: caixa subdividida moldada em forma de sedã ----------
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
  const corCarro = new T.Color(0xd8322f), vidro = new T.Color(0x18202c), friso = new T.Color(0x2a2e35);
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
  S.orig = Float32Array.from(p.array);
  S.corpoMat = new T.MeshStandardMaterial({vertexColors: true, metalness: 0.45, roughness: 0.32, transparent: true,
                                           opacity: 1, side: T.DoubleSide});
  S.corpo = new T.Mesh(g, S.corpoMat);
  S.carro = new T.Group(); S.carro.add(S.corpo); cena.add(S.carro);
  // faróis e lanternas
  for (const z of [-0.6, 0.6]) {
    const f = new T.Mesh(new T.SphereGeometry(0.13, 16, 8), new T.MeshStandardMaterial({color: 0xfff6d8, emissive: 0xfff2c0, emissiveIntensity: 0.6}));
    f.scale.set(0.5, 1, 1.4); f.position.set(XF - 0.08, 0.72, z); S.carro.add(f); f.userData.frente = true;
    const l = new T.Mesh(new T.BoxGeometry(0.06, 0.12, 0.4), new T.MeshStandardMaterial({color: 0xb01010, emissive: 0x800000}));
    l.position.set(-XF + 0.03, 0.82, z); S.carro.add(l);
  }
  S.farois = S.carro.children.filter(c => c.userData.frente);
  // rodas
  S.rodas = [];
  const pneu = new T.MeshStandardMaterial({color: 0x1b1d21, roughness: 0.9});
  const aro = new T.MeshStandardMaterial({color: 0xc9ced6, metalness: 0.9, roughness: 0.25});
  for (const [x, z] of [[1.45, 0.82], [1.45, -0.82], [-1.45, 0.82], [-1.45, -0.82]]) {
    const w = new T.Group();
    const t = new T.Mesh(new T.CylinderGeometry(0.34, 0.34, 0.24, 28), pneu); t.rotation.x = Math.PI / 2; w.add(t);
    const a = new T.Mesh(new T.CylinderGeometry(0.2, 0.2, 0.25, 6), aro); a.rotation.x = Math.PI / 2; w.add(a);
    w.position.set(x, 0.34, z); S.carro.add(w); S.rodas.push(w);
  }
  // ---------- interior (aparece no raio-x): banco, volante, boneco, cinto, airbag ----------
  const escuro = new T.MeshStandardMaterial({color: 0x30343c, roughness: 0.8});
  const banco = new T.Group();
  const assento = new T.Mesh(new T.BoxGeometry(0.55, 0.12, 0.5), escuro); assento.position.set(0, 0.55, 0); banco.add(assento);
  const encosto = new T.Mesh(new T.BoxGeometry(0.12, 0.7, 0.5), escuro); encosto.position.set(-0.3, 0.9, 0);
  encosto.rotation.z = -0.15; banco.add(encosto);
  banco.position.set(-0.25, 0, 0.42); S.carro.add(banco);
  const volante = new T.Mesh(new T.TorusGeometry(0.19, 0.03, 10, 32), escuro);
  volante.position.set(0.55, 1.0, 0.42); volante.rotation.y = Math.PI / 2; volante.rotation.x = 0; volante.rotation.z = 0.0;
  volante.rotation.set(0, Math.PI / 2, 0); volante.rotateX(-0.5); S.carro.add(volante);
  const coluna = new T.Mesh(new T.CylinderGeometry(0.03, 0.03, 0.5, 8), escuro);
  coluna.position.set(0.78, 0.9, 0.42); coluna.rotation.z = 1.05; S.carro.add(coluna);
  // boneco de teste: amarelo com marcas pretas (o "dummy" dos testes de colisão)
  const amarelo = new T.MeshStandardMaterial({color: 0xf2c230, roughness: 0.55});
  const preto = new T.MeshStandardMaterial({color: 0x15171b, roughness: 0.6});
  const marca = document.createElement('canvas'); marca.width = marca.height = 128;
  const mc = marca.getContext('2d'); mc.fillStyle = '#f2c230'; mc.fillRect(0, 0, 128, 128);
  mc.fillStyle = '#15171b'; mc.beginPath(); mc.moveTo(64, 64); mc.arc(64, 64, 64, 0, Math.PI / 2); mc.fill();
  mc.beginPath(); mc.moveTo(64, 64); mc.arc(64, 64, 64, Math.PI, Math.PI * 1.5); mc.fill();
  const cabecaMat = new T.MeshStandardMaterial({map: new T.CanvasTexture(marca), roughness: 0.5});
  S.boneco = new T.Group();  // pivô no quadril
  S.boneco.position.set(-0.35, 0.68, 0.42); S.carro.add(S.boneco);
  S.tronco = new T.Group(); S.boneco.add(S.tronco);
  const torso = new T.Mesh(new T.CapsuleGeometry(0.17, 0.32, 6, 12), amarelo); torso.position.y = 0.3; S.tronco.add(torso);
  const pescoco = new T.Mesh(new T.CylinderGeometry(0.05, 0.05, 0.1, 10), preto); pescoco.position.y = 0.58; S.tronco.add(pescoco);
  const cabeca = new T.Mesh(new T.SphereGeometry(0.13, 24, 16), cabecaMat); cabeca.position.y = 0.72;
  cabeca.rotation.y = Math.PI / 2; S.tronco.add(cabeca);
  for (const z of [-0.2, 0.2]) {  // braços indo ao volante
    const b = new T.Mesh(new T.CapsuleGeometry(0.05, 0.42, 4, 8), amarelo);
    b.position.set(0.22, 0.38, z); b.rotation.z = -1.0; S.tronco.add(b);
  }
  for (const z of [-0.1, 0.1]) {  // pernas
    const c = new T.Mesh(new T.CapsuleGeometry(0.07, 0.4, 4, 8), amarelo);
    c.position.set(0.28, -0.02, z); c.rotation.z = -1.4; S.boneco.add(c);
    const ca = new T.Mesh(new T.CapsuleGeometry(0.06, 0.38, 4, 8), amarelo);
    ca.position.set(0.55, -0.25, z); ca.rotation.z = -0.25; S.boneco.add(ca);
  }
  // cinto: faixa diagonal no peito (estica junto com o tronco)
  S.cinto = new T.Mesh(new T.BoxGeometry(0.03, 0.7, 0.07), new T.MeshStandardMaterial({color: 0x101216}));
  S.cinto.position.set(0.17, 0.32, 0); S.cinto.rotation.x = 0.75; S.tronco.add(S.cinto);
  // airbag
  S.airbag = new T.Mesh(new T.SphereGeometry(0.32, 32, 20),
                        new T.MeshStandardMaterial({color: 0xf4f4f0, roughness: 0.85, transparent: true, opacity: 0.95}));
  S.airbag.position.set(0.42, 1.05, 0.42); S.carro.add(S.airbag);
  S.interior = [banco, volante, coluna, S.boneco, S.airbag];
  // ---------- folhas caindo da árvore ----------
  const nF = 160; S.nF = nF;
  S.folhaPos = new Float32Array(nF * 3);
  const fg = new T.BufferGeometry(); fg.setAttribute('position', new T.BufferAttribute(S.folhaPos, 3));
  S.folhas = new T.Points(fg, new T.PointsMaterial({color: 0x4f8a33, size: 0.12})); S.folhas.frustumCulled = false;
  cena.add(S.folhas);
  S.folhaIni = []; for (let i = 0; i < nF; i++) S.folhaIni.push([A.aleat() - 0.5, A.aleat(), A.aleat() - 0.5, A.aleat()]);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  // carroceria: amassa a zona da frente (mais no centro, onde bate o tronco), capô dobra para cima
  const p = S.corpo.geometry.attributes.position, o = S.orig, c = e.amassa;
  for (let i = 0; i < p.count; i++) {
    const x = o[i * 3], y = o[i * 3 + 1], z = o[i * 3 + 2];
    if (x <= XS || c <= 0) { p.setXYZ(i, x, y, z); continue; }
    const f = (x - XS) / ZONA;                                    // 0 no começo da zona, 1 no para-choque
    const centro = 0.5 + 0.5 * Math.exp(-(z * z) / 0.18);          // o tronco é estreito: o meio afunda mais
    const ce = c * centro;
    const nx = x - ce * f;
    const ruga = Math.sin(f * 14) * 0.09 * (c / 0.6) * f;          // sanfona
    const dobra = y > 0.7 ? 0.45 * (c / 0.6) * Math.sin(Math.PI * Math.min(1, f * 1.15)) : 0;  // capô sobe e dobra
    const abre = 1 + 0.07 * (c / 0.6) * f;                         // laterais estufam
    p.setXYZ(i, nx, y + ruga + dobra, z * abre);
  }
  p.needsUpdate = true; S.corpo.geometry.computeVertexNormals();
  S.farois.forEach(f => { f.position.x = XF - 0.08 - c * 0.85; f.visible = c < 0.45; });
  S.carro.position.set(e.carro[0], 0, e.carro[1]);
  S.carro.rotation.y = e.rumo;
  S.rodas.forEach((w, i) => { w.rotation.z = -e.roda; if (i < 2) w.position.x = 1.45 - c * 0.35; });
  // raio-x
  S.corpoMat.opacity = 1 - 0.78 * e.raiox;
  S.corpoMat.depthWrite = e.raiox < 0.05;
  S.interior.forEach(m => m.visible = e.raiox > 0.02);
  // boneco: o tronco vai para a frente (gira no quadril) e a cabeça segue
  S.tronco.rotation.z = -Math.atan2(e.boneco, 0.55);
  S.boneco.position.x = -0.35 + e.boneco * 0.35;
  S.airbag.scale.setScalar(Math.max(0.001, e.airbag));
  S.airbag.position.x = 0.42 - 0.12 * e.airbag;
  // árvore balança e solta folhas
  S.arv.copa.rotation.z = e.balanco; S.arv.copa.rotation.x = e.balanco * 0.4;
  const P = S.folhaPos;
  for (let i = 0; i < S.nF; i++) {
    const [a, b, d, k] = S.folhaIni[i];
    if (e.folhas < 0) { P[i * 3 + 1] = -100; continue; }
    const tf = e.folhas * (0.6 + 0.6 * k);
    P[i * 3] = e.arvore[0] + a * 4 + Math.sin(tf * 2 + k * 6) * 0.5 + tf * 0.4;
    P[i * 3 + 1] = Math.max(0.05, 4.6 + b * 2.6 - tf * 1.1);
    P[i * 3 + 2] = e.arvore[1] + d * 4 + Math.cos(tf * 1.7 + k * 5) * 0.4;
  }
  S.folhas.geometry.attributes.position.needsUpdate = true;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
