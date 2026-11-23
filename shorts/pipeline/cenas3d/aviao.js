// Avião na aproximação final com o trem de pouso travado em cima: a hidráulica falha, o piloto puxa a alavanca de
// descida manual, as travas soltam e a gravidade derruba as rodas até travarem embaixo; depois o pouso na pista.
// Estado vindo do Python: cam, alvo, fov, t, pos [x,y,z], pitch (rad, + = nariz para cima), trem 0..1 (0 = recolhido,
// 1 = embaixo e travado; pode passar de 1 no "quique"), hidr 0..1 (brilho dos atuadores hidráulicos),
// falha 0..1 (atuadores ficam vermelhos), roda (rad, giro das rodas), fumaca (s desde o toque, <0 = não),
// trava 0..1 (ganchos das travas de cima abertos).
import * as A from 'http://cena.local/ambiente.js';

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 4000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(17);
  S.ceu = A.ceu(T, cena, {sol: [0.5, 0.5, 0.7], neblina: 0xd6e4f0, perto: 400, longe: 2200});
  A.nuvens(T, cena, {n: 30, y: [220, 320], x: [-2500, 1500], z: [-900, -200], tam: [18, 34]});
  A.nuvens(T, cena, {n: 12, y: [220, 320], x: [-2500, 1500], z: [300, 700], tam: [18, 34]});
  A.grama(T, cena, {tam: 6000, cor: 0x6f9c4a});
  A.morros(T, cena, {n: 26, dist: 1600});
  for (let i = 0; i < 160; i++) {  // árvores longe da pista
    const x = -2600 + A.aleat() * 4200, z = -500 + A.aleat() * 1000;
    if (Math.abs(z) < 90) continue;
    A.arvore(T, cena, x, z, {altura: 7 + A.aleat() * 6, copa: 3 + A.aleat() * 2});
  }
  // pista: asfalto, faixa central tracejada, cabeceira listrada e marcas de toque
  const asf = new T.Mesh(new T.PlaneGeometry(3000, 45), new T.MeshStandardMaterial({color: 0x3b3e44, roughness: 0.95}));
  asf.rotation.x = -Math.PI / 2; asf.position.set(1300, 0.03, 0); cena.add(asf);
  const branco = new T.MeshStandardMaterial({color: 0xf2f2f2, roughness: 0.8});
  for (let x = -150; x < 2800; x += 50) {
    const f = new T.Mesh(new T.PlaneGeometry(30, 0.9), branco); f.rotation.x = -Math.PI / 2; f.position.set(x, 0.05, 0); cena.add(f);
  }
  for (let k = -7; k <= 7; k++) {
    if (k === 0) continue;
    const f = new T.Mesh(new T.PlaneGeometry(30, 1.8), branco); f.rotation.x = -Math.PI / 2;
    f.position.set(-180, 0.05, k * 2.8); cena.add(f);
  }
  for (const z of [-6, 6]) {
    const f = new T.Mesh(new T.PlaneGeometry(45, 4), branco); f.rotation.x = -Math.PI / 2; f.position.set(30, 0.05, z); cena.add(f);
  }
  for (let x = -195; x < 2800; x += 60) for (const z of [-23, 23]) {   // luzes de borda
    const l = new T.Mesh(new T.SphereGeometry(0.35, 8, 6), new T.MeshStandardMaterial({color: 0xfff3c0, emissive: 0xffe08a, emissiveIntensity: 1.2}));
    l.position.set(x, 0.3, z); cena.add(l);
  }

  // ---------- avião (bimotor de corredor único, ~38 m), eixo +x = nariz ----------
  S.av = new T.Group(); cena.add(S.av);
  const casco = new T.MeshStandardMaterial({color: 0xf4f6f8, metalness: 0.3, roughness: 0.35});
  const azul = new T.MeshStandardMaterial({color: 0x1f4fa8, metalness: 0.3, roughness: 0.4});
  const cinza = new T.MeshStandardMaterial({color: 0x9aa3ad, metalness: 0.7, roughness: 0.35});
  const escuro = new T.MeshStandardMaterial({color: 0x1d2026, metalness: 0.3, roughness: 0.7});
  const YC = 4.3, RF = 2.0;   // centro e raio da fuselagem
  const fus = new T.Mesh(new T.CylinderGeometry(RF, RF, 28, 40), casco); fus.rotation.z = Math.PI / 2;
  fus.position.set(0, YC, 0); S.av.add(fus);
  const nariz = new T.Mesh(new T.SphereGeometry(RF, 40, 24, 0, Math.PI * 2, 0, Math.PI / 2), casco);
  nariz.scale.set(1, 2.3, 1); nariz.rotation.z = -Math.PI / 2; nariz.position.set(14, YC, 0); S.av.add(nariz);
  const cauda = new T.Mesh(new T.CylinderGeometry(RF, 0.45, 9, 40), casco); cauda.rotation.z = Math.PI / 2;
  cauda.position.set(-18.5, YC + 0.6, 0); S.av.add(cauda);
  const faixa = new T.Mesh(new T.CylinderGeometry(RF + 0.02, RF + 0.02, 27, 40, 1, true, Math.PI * 0.42, Math.PI * 0.16), azul);
  faixa.rotation.z = Math.PI / 2; faixa.position.set(0, YC, 0); S.av.add(faixa);
  const vidros = new T.Mesh(new T.BoxGeometry(1.4, 0.45, 2.6), new T.MeshStandardMaterial({color: 0x1b2533, metalness: 0.4, roughness: 0.1}));
  vidros.position.set(15.4, YC + 1.15, 0); S.av.add(vidros);
  for (let x = -11; x < 12; x += 1.1) for (const z of [-1, 1]) {   // janelas
    const j = new T.Mesh(new T.BoxGeometry(0.35, 0.45, 0.05), escuro);
    j.position.set(x, YC + 0.7, z * (RF - 0.08) * 0.94 + z * 0.12); S.av.add(j);
  }
  for (const z of [-1, 1]) {   // asas (enflechadas) e motores
    const asa = new T.Mesh(new T.BoxGeometry(5.5, 0.35, 15), casco);
    asa.position.set(-1.5 - 3.0, YC - 1.3, z * 8.8); asa.rotation.y = -z * 0.42; asa.rotation.x = z * 0.07; S.av.add(asa);
    const ponta = new T.Mesh(new T.BoxGeometry(1.2, 2.0, 0.15), azul);
    ponta.position.set(-9.6, YC - 0.2, z * 16.2); ponta.rotation.z = 0.3; S.av.add(ponta);
    const mot = new T.Mesh(new T.CylinderGeometry(1.0, 0.85, 4.2, 28), cinza); mot.rotation.z = Math.PI / 2;
    mot.position.set(1.0, YC - 2.6, z * 5.4); S.av.add(mot);
    const boca = new T.Mesh(new T.CircleGeometry(0.85, 28), cinza); boca.rotation.y = Math.PI / 2;
    boca.position.set(3.12, YC - 2.6, z * 5.4); S.av.add(boca);
    const pilone = new T.Mesh(new T.BoxGeometry(3.0, 1.0, 0.3), casco); pilone.position.set(0.2, YC - 1.8, z * 5.4); S.av.add(pilone);
    const estab = new T.Mesh(new T.BoxGeometry(3.0, 0.2, 6.5), casco);
    estab.position.set(-20.5, YC + 0.9, z * 3.5); estab.rotation.y = -z * 0.45; S.av.add(estab);
  }
  const deriva = new T.Mesh(new T.BoxGeometry(4.2, 6.5, 0.3), azul); deriva.position.set(-20.5, YC + 4.6, 0);
  deriva.rotation.z = 0.5; S.av.add(deriva);
  // barriga: carenagem das asas
  const car = new T.Mesh(new T.SphereGeometry(1, 30, 16), casco); car.scale.set(6.5, 1.3, 2.3);
  car.position.set(-2.5, YC - 1.25, 0); S.av.add(car);

  // ---------- trem de pouso ----------
  const pneu = new T.MeshStandardMaterial({color: 0x15171a, roughness: 0.9});
  const roda = (raio, larg) => {
    const g = new T.Group();
    const p = new T.Mesh(new T.CylinderGeometry(raio, raio, larg, 24), pneu); p.rotation.x = Math.PI / 2; g.add(p);
    const c = new T.Mesh(new T.CylinderGeometry(raio * 0.55, raio * 0.55, larg + 0.02, 16), cinza); c.rotation.x = Math.PI / 2; g.add(c);
    const l = new T.Mesh(new T.BoxGeometry(raio * 1.05, 0.1, larg + 0.04), new T.MeshStandardMaterial({color: 0xffc23a})); g.add(l);
    return g;
  };
  S.rodas = [];
  S.atuMat = new T.MeshStandardMaterial({color: 0xffa23a, emissive: 0xff8a1a, emissiveIntensity: 0, metalness: 0.5, roughness: 0.4});
  S.travaMat = new T.MeshStandardMaterial({color: 0xff3030, emissive: 0xff2020, emissiveIntensity: 0.8});
  S.principais = [];
  S.travas = [];
  for (const z of [-1, 1]) {   // principais: articulam na raiz da asa e recolhem para dentro (em direção ao centro)
    const piv = new T.Group(); piv.position.set(-2.8, YC - 1.55, z * 3.6); S.av.add(piv);
    const perna = new T.Mesh(new T.CylinderGeometry(0.2, 0.2, 2.6, 12), cinza); perna.position.y = -1.3; piv.add(perna);
    const amort = new T.Mesh(new T.CylinderGeometry(0.13, 0.13, 0.9, 10), new T.MeshStandardMaterial({color: 0xe8edf2, metalness: 0.9, roughness: 0.15}));
    amort.position.y = -2.5; piv.add(amort);
    const eixo = new T.Group(); eixo.position.y = -2.75; piv.add(eixo);
    for (const dz of [-0.45, 0.45]) {
      const rr = roda(0.62, 0.42); rr.position.z = dz; eixo.add(rr); S.rodas.push(rr);
    }
    S.principais.push({piv, z});
    // atuador hidráulico: da fuselagem até o meio da perna (recalculado a cada quadro)
    const atu = new T.Mesh(new T.CylinderGeometry(0.12, 0.12, 1, 10), S.atuMat); S.av.add(atu);
    S.principais[S.principais.length - 1].atu = atu;
    // trava de cima: gancho vermelho na barriga
    const tr = new T.Mesh(new T.BoxGeometry(0.5, 0.25, 0.25), S.travaMat); tr.position.set(-2.8, YC - 1.75, z * 0.9);
    S.av.add(tr); S.travas.push({m: tr, z});
  }
  S.npiv = new T.Group(); S.npiv.position.set(11.5, YC - 1.6, 0); S.av.add(S.npiv);   // trem do nariz: recolhe para frente
  const np = new T.Mesh(new T.CylinderGeometry(0.15, 0.15, 2.9, 12), cinza); np.position.y = -1.45; S.npiv.add(np);
  const neixo = new T.Group(); neixo.position.y = -2.9; S.npiv.add(neixo);
  for (const dz of [-0.3, 0.3]) { const rr = roda(0.42, 0.3); rr.position.z = dz; neixo.add(rr); S.rodas.push(rr); }
  S.portas = [];
  for (const z of [-1, 1]) {   // portas do trem do nariz
    const pg = new T.Group(); pg.position.set(11.5, YC - 1.9, z * 0.55); S.av.add(pg);
    const p = new T.Mesh(new T.BoxGeometry(2.4, 0.06, 0.55), casco); p.position.z = -z * 0.27; pg.add(p);
    S.portas.push({pg, z});
  }

  // fumaça dos pneus no toque
  const nF = 220; S.nF = nF; S.fPos = new Float32Array(nF * 3);
  const fg = new T.BufferGeometry(); fg.setAttribute('position', new T.BufferAttribute(S.fPos, 3));
  S.fumaca = new T.Points(fg, new T.PointsMaterial({color: 0xd8d8d8, size: 0.7, transparent: true, opacity: 0.75, depthWrite: false}));
  S.fumaca.frustumCulled = false; cena.add(S.fumaca);
  S.fIni = []; for (let i = 0; i < nF; i++) S.fIni.push([A.aleat(), A.aleat(), A.aleat()]);
  S.v1 = new T.Vector3(); S.v2 = new T.Vector3(); S.up = new T.Vector3(0, 1, 0);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam, T = S.T;
  S.av.position.set(...e.pos);
  S.av.rotation.set(0, 0, e.pitch);
  const g = e.trem;
  const ang = (1 - g) * Math.PI / 2;   // 0 = embaixo, 90° = recolhido
  S.principais.forEach(({piv, z, atu}) => {
    piv.rotation.x = z * ang;   // a perna gira para dentro, em direção ao centro do avião
    // atuador: ponto fixo na barriga até o meio da perna
    S.v1.set(-2.8, 4.3 - 1.4, z * 1.2);
    S.v2.set(0, -1.2, 0); S.v2.applyEuler(piv.rotation); S.v2.add(piv.position);
    const d = S.v2.clone().sub(S.v1), L = d.length();
    atu.position.copy(S.v1).add(d.multiplyScalar(0.5)); atu.scale.set(1, L, 1);
    atu.quaternion.setFromUnitVectors(S.up, S.v2.clone().sub(S.v1).normalize());
  });
  S.npiv.rotation.z = ang;   // nariz: gira para frente
  S.portas.forEach(({pg, z}) => { pg.rotation.x = -z * Math.min(1, g * 2.5) * 1.4; });
  S.atuMat.emissiveIntensity = 1.6 * e.hidr;
  S.atuMat.color.setRGB(1, 0.64 - 0.45 * e.falha, 0.23 - 0.1 * e.falha);
  S.atuMat.emissive.setRGB(1, 0.54 - 0.5 * e.falha, 0.1);
  S.travas.forEach(({m, z}) => { m.rotation.x = z * e.trava * 1.2; });
  S.travaMat.color.setRGB(1 - 0.8 * e.trava, 0.19 + 0.6 * e.trava, 0.19 + 0.1 * e.trava);
  S.travaMat.emissive.copy(S.travaMat.color);
  S.rodas.forEach(rr => { rr.rotation.z = -e.roda; });
  const F = S.fPos;
  for (let i = 0; i < S.nF; i++) {
    const [a, b, c] = S.fIni[i];
    const ts = e.fumaca - c * 0.5;
    if (e.fumaca < 0 || ts < 0 || ts > 3) { F[i * 3 + 1] = -999; continue; }
    const lado = (i % 2 ? 1 : -1) * 3.6;
    F[i * 3] = e.toqueX - 2.8 + (a - 0.5) * 4 + ts * 6;   // a nuvem fica no lugar do toque e se espalha
    F[i * 3 + 1] = 0.3 + ts * (0.6 + b);
    F[i * 3 + 2] = lado + (b - 0.5) * (1 + ts * 3);
  }
  S.fumaca.geometry.attributes.position.needsUpdate = true;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);   // o domo do céu acompanha a câmera (o avião voa 1,6 km)
};
