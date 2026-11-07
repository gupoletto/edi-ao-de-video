// Raio atingindo um avião em cruzeiro (cena derivada de aviao.js): o raio entra pelo nariz, a corrente corre pela
// pele de alumínio até a cauda e sai; dentro (raio-x), os passageiros nem percebem: gaiola de Faraday.
// Estado extra: raio1, raio2 (0..1, brilho do raio de entrada e de saída), corrente 0..1 (quanto da pele já foi
// percorrida), brilhoCorr, raiox 0..1, descarga 0..1, flash 0..1.
// Base: Avião na aproximação final com o trem de pouso travado em cima: a hidráulica falha, o piloto puxa a alavanca de
// descida manual, as travas soltam e a gravidade derruba as rodas até travarem embaixo; depois o pouso na pista.
// Estado vindo do Python: cam, alvo, fov, t, pos [x,y,z], pitch (rad, + = nariz para cima), trem 0..1 (0 = recolhido,
// 1 = embaixo e travado; pode passar de 1 no "quique"), hidr 0..1 (brilho dos atuadores hidráulicos),
// falha 0..1 (atuadores ficam vermelhos), roda (rad, giro das rodas), fumaca (s desde o toque, <0 = não),
// trava 0..1 (ganchos das travas de cima abertos).
import * as A from 'http://cena.local/ambiente.js';

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 4000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 0.8;
  const S = {T};
  A.reiniciar(23);
  S.ceu = A.ceu(T, cena, {sol: [0.3, 0.25, 0.9], topo: [0.05, 0.06, 0.10], meio: [0.16, 0.18, 0.24], baixo: [0.30, 0.32, 0.38],
                          neblina: 0x3a3f4c, perto: 250, longe: 1500});
  const nuvMat = new T.MeshStandardMaterial({color: 0x5a6070, roughness: 1, emissive: 0x23283a, emissiveIntensity: 0.5});
  S.nuvMat = nuvMat;
  for (let i = 0; i < 70; i++) {   // nuvens de tempestade em volta da rota (o avião voa em y = 600)
    const x = -300 + A.aleat() * 2600, z = A.aleat() < 0.7 ? -(70 + A.aleat() * 500) : (170 + A.aleat() * 350);
    A.nuvem(T, cena, x, 560 + A.aleat() * 140, z, 18 + A.aleat() * 26, nuvMat);
  }
  for (let i = 0; i < 40; i++) A.nuvem(T, cena, -300 + A.aleat() * 2600, 480 + A.aleat() * 30, -600 + A.aleat() * 1200, 30 + A.aleat() * 30, nuvMat);
  for (let i = 0; i < 25; i++) A.nuvem(T, cena, -300 + A.aleat() * 2600, 760 + A.aleat() * 60, -600 + A.aleat() * 1200, 30 + A.aleat() * 30, nuvMat);
  S.relampago = new T.PointLight(0xcfe0ff, 0, 400, 1.2); cena.add(S.relampago);
  S.amb = new T.AmbientLight(0xbfd0ff, 0); cena.add(S.amb);

  // ---------- avião (bimotor de corredor único, ~38 m), eixo +x = nariz ----------
  S.av = new T.Group(); cena.add(S.av);
  const casco = new T.MeshStandardMaterial({color: 0xf4f6f8, metalness: 0.3, roughness: 0.35, transparent: true, opacity: 1});
  S.casco = casco;
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

  // ---------- raio, corrente na fuselagem, cabine (raio-x) e descarregadores ----------
  S.raioMat = new T.MeshBasicMaterial({color: 0xeaf2ff, transparent: true, opacity: 0, depthWrite: false});
  S.raioAura = new T.MeshBasicMaterial({color: 0x7fb2ff, transparent: true, opacity: 0, depthWrite: false});
  const zigue = (a, b, n, amp, semente) => {
    A.reiniciar(semente); const pts = [];
    for (let i = 0; i <= n; i++) {
      const k = i / n, p = a.clone().lerp(b, k);
      if (i > 0 && i < n) p.add(new T.Vector3((A.aleat() - 0.5) * amp, (A.aleat() - 0.5) * amp * 0.4, (A.aleat() - 0.5) * amp));
      pts.push(p);
    }
    return new T.CatmullRomCurve3(pts, false, 'catmullrom', 0.1);
  };
  const raio = (a, b, sem) => {
    const g = new T.Group();
    const c = zigue(a, b, 22, 14, sem);
    g.add(new T.Mesh(new T.TubeGeometry(c, 160, 0.6, 6), S.raioMat));
    g.add(new T.Mesh(new T.TubeGeometry(c, 160, 2.0, 6), S.raioAura));
    for (let r = 0; r < 4; r++) {   // galhos
      const k = 0.2 + 0.18 * r, p = c.getPoint(k);
      const q = p.clone().add(new T.Vector3((A.aleat() - 0.5) * 40, -10 - A.aleat() * 20, (A.aleat() - 0.5) * 30));
      g.add(new T.Mesh(new T.TubeGeometry(zigue(p, q, 8, 6, sem + r + 1), 40, 0.18, 5), S.raioMat));
    }
    return g;
  };
  // entrada: da nuvem de cima até o nariz; saída: da cauda para baixo (coordenadas do avião)
  S.raioEntra = raio(new T.Vector3(34, 24, -6), new T.Vector3(18.4, YC, 0), 101); S.av.add(S.raioEntra);
  S.raioSai = raio(new T.Vector3(-22.5, YC + 0.5, 0), new T.Vector3(-55, -50, 8), 202); S.av.add(S.raioSai);
  // caminho da corrente pela pele: do nariz à cauda, por cima e pelas laterais
  S.corrMat = new T.MeshBasicMaterial({color: 0x6fe6ff, transparent: true, opacity: 0.95, depthWrite: false});
  S.corr = [];
  for (const [dy, dz] of [[RF + 0.05, 0], [0.4, RF + 0.05], [0.4, -RF - 0.05], [-RF - 0.05, 0]]) {
    const pts = [];
    for (let i = 0; i <= 40; i++) {
      const x = 18.4 - i * (41 / 40);
      const enc = x < -14 ? Math.max(0.25, 1 - (-14 - x) / 9) : 1;   // a cauda afina
      pts.push(new T.Vector3(x, YC + dy * enc + (x < -14 ? (-14 - x) * 0.07 : 0), dz * enc + Math.sin(i * 1.7) * 0.15));
    }
    const m = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts), 120, 0.26, 6), S.corrMat);
    m.geometry.setDrawRange(0, 0); S.av.add(m); S.corr.push(m);
  }
  // cabine: poltronas e passageiros (aparecem no raio-x)
  S.cabine = new T.Group(); S.av.add(S.cabine);
  const banco = new T.MeshStandardMaterial({color: 0x2c4f8f}), pele = new T.MeshStandardMaterial({color: 0xe0b48a});
  for (let x = -10; x < 11; x += 1.6) for (const z of [-1.25, -0.75, 0.75, 1.25]) {
    const b = new T.Mesh(new T.BoxGeometry(0.5, 0.9, 0.45), banco); b.position.set(x, YC - 0.5, z); S.cabine.add(b);
    const cab = new T.Mesh(new T.SphereGeometry(0.2, 10, 8), pele); cab.position.set(x + 0.05, YC + 0.15, z); S.cabine.add(cab);
  }
  S.cabine.visible = false;
  S.faisca = new T.MeshBasicMaterial({color: 0xcfe6ff, transparent: true, opacity: 0, depthWrite: false});
  for (const z of [-1, 1]) {   // descarregadores de estática na ponta das asas
    const f = new T.Mesh(new T.SphereGeometry(0.5, 10, 8), S.faisca); f.position.set(-10.2, YC - 0.4, z * 16.4); S.av.add(f);
  }
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
  // raio e corrente
  S.raioMat.opacity = e.raio1 > 0 ? e.raio1 : e.raio2;
  S.raioAura.opacity = 0.35 * S.raioMat.opacity;
  S.raioEntra.visible = e.raio1 > 0.01; S.raioSai.visible = e.raio2 > 0.01;
  S.corr.forEach(m => { m.geometry.setDrawRange(0, Math.floor(e.corrente * m.geometry.index.count)); });
  S.corrMat.opacity = 0.95 * e.brilhoCorr;
  S.casco.opacity = 1 - 0.75 * e.raiox; S.casco.depthWrite = e.raiox < 0.05;
  S.cabine.visible = e.raiox > 0.02;
  S.faisca.opacity = e.descarga * (0.5 + 0.5 * Math.sin(e.t * 47));
  S.relampago.intensity = 1.2e5 * e.flash; S.relampago.position.set(e.pos[0] + 30, e.pos[1] + 60, 20);
  S.amb.intensity = 0.8 * e.flash;
  S.nuvMat.emissiveIntensity = 0.5 + 0.4 * e.flash;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);   // o domo do céu acompanha a câmera (o avião voa 1,6 km)
};
