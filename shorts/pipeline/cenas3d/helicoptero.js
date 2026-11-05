// Helicóptero perdendo o motor: autorrotação. Campo aberto, o helicóptero em voo nivelado, o motor apaga, a roda-livre
// desacopla, o ar passa a subir pelo rotor (como num cata-vento), a descida, o "flare" perto do chão e o pouso.
// Estado vindo do Python: cam, alvo, fov, t, pos [x,y,z], pitch (rad, + = nariz para cima), rotor (rad), cauda (rad),
// motor 0..1 (1 = ligado), eixoMotor (rad, eixo do lado do motor), roda 0..1 (1 = roda-livre desacoplada),
// passo (rad, ângulo das pás), fluxo (-1 = ar descendo / +1 = ar subindo / 0 = nada), raiox 0..1, fumaça (s desde a
// pane, <0 = não), poeira (s desde o toque, <0 = não), luzAlerta 0..1.
import * as A from 'http://cena.local/ambiente.js';

const R = 5.5;   // raio do rotor principal (m)

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 2000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(9);
  A.ceu(T, cena, {sol: [0.4, 0.55, 0.75], neblina: 0xcfe0ee, perto: 200, longe: 900});
  A.nuvens(T, cena, {n: 26, y: [140, 220], x: [-700, 900], z: [-700, -150]});
  A.nuvens(T, cena, {n: 10, y: [140, 220], x: [-700, 900], z: [200, 500]});
  A.grama(T, cena, {tam: 2400, cor: 0x6b9a46});
  A.morros(T, cena, {n: 22, dist: 700});
  for (let i = 0; i < 70; i++) {  // árvores espalhadas, longe da área de pouso
    const x = -500 + A.aleat() * 1300, z = -260 + A.aleat() * 420;
    if (Math.abs(x - 520) < 60 && Math.abs(z) < 50) continue;
    A.arvore(T, cena, x, z, {altura: 6 + A.aleat() * 5, copa: 2.6 + A.aleat() * 1.5});
  }
  // área de pouso: grama mais clara e uma estrada de terra
  const campo = new T.Mesh(new T.CircleGeometry(30, 48), new T.MeshStandardMaterial({color: 0x8fb85e, roughness: 1}));
  campo.rotation.x = -Math.PI / 2; campo.position.set(520, 0.02, 0); cena.add(campo);
  const terra = new T.Mesh(new T.PlaneGeometry(1600, 6), new T.MeshStandardMaterial({color: 0xa58a62, roughness: 1}));
  terra.rotation.x = -Math.PI / 2; terra.position.set(300, 0.03, 40); cena.add(terra);

  // ---------- helicóptero ----------
  S.heli = new T.Group(); cena.add(S.heli);
  const corpoMat = new T.MeshStandardMaterial({color: 0xd23b2f, metalness: 0.4, roughness: 0.35, transparent: true, opacity: 1});
  const escuro = new T.MeshStandardMaterial({color: 0x23262c, metalness: 0.5, roughness: 0.5});
  const metal = new T.MeshStandardMaterial({color: 0xb9c0c9, metalness: 0.85, roughness: 0.3});
  S.mats = [corpoMat];
  const corpo = new T.Mesh(new T.SphereGeometry(1, 40, 24), corpoMat);   // cabine: elipsoide
  corpo.scale.set(2.6, 1.35, 1.25); corpo.position.set(0.4, 1.7, 0); S.heli.add(corpo);
  const vidroMat = new T.MeshStandardMaterial({color: 0x23415c, metalness: 0.2, roughness: 0.05, transparent: true, opacity: 0.85});
  const vidro = new T.Mesh(new T.SphereGeometry(1, 32, 20, 0, Math.PI * 2, 0, Math.PI * 0.55), vidroMat);
  vidro.scale.set(1.5, 1.1, 1.15); vidro.rotation.z = -1.1; vidro.position.set(1.9, 1.95, 0); S.heli.add(vidro);
  S.mats.push(vidroMat);
  const capo = new T.Mesh(new T.BoxGeometry(2.4, 0.7, 1.3), corpoMat); capo.position.set(-0.6, 2.95, 0); S.heli.add(capo);
  const cone = new T.Mesh(new T.CylinderGeometry(0.22, 0.55, 6.2, 18), corpoMat);   // cone de cauda
  cone.rotation.z = Math.PI / 2; cone.position.set(-4.6, 2.1, 0); S.heli.add(cone);
  const deriva = new T.Mesh(new T.BoxGeometry(0.9, 1.6, 0.12), corpoMat); deriva.position.set(-7.5, 2.8, 0);
  deriva.rotation.z = 0.35; S.heli.add(deriva);
  const estab = new T.Mesh(new T.BoxGeometry(0.7, 0.08, 2.0), corpoMat); estab.position.set(-6.6, 2.1, 0); S.heli.add(estab);
  for (const z of [-1.0, 1.0]) {   // esquis
    const esqui = new T.Mesh(new T.CylinderGeometry(0.07, 0.07, 4.4, 10), escuro);
    esqui.rotation.z = Math.PI / 2; esqui.position.set(0.4, 0.08, z); S.heli.add(esqui);
    const ponta = new T.Mesh(new T.TorusGeometry(0.25, 0.07, 8, 16, Math.PI / 2), escuro);
    ponta.position.set(2.6, 0.33, z); ponta.rotation.z = -Math.PI / 2; S.heli.add(ponta);
    for (const x of [-0.7, 1.4]) {
      const perna = new T.Mesh(new T.CylinderGeometry(0.06, 0.06, 0.95, 8), escuro);
      perna.position.set(x, 0.55, z * 0.85); perna.rotation.x = -z * 0.25; S.heli.add(perna);
    }
  }
  // mastro e rotor principal
  const mastro = new T.Mesh(new T.CylinderGeometry(0.12, 0.14, 0.9, 12), metal); mastro.position.set(-0.3, 3.7, 0); S.heli.add(mastro);
  S.rotor = new T.Group(); S.rotor.position.set(-0.3, 4.15, 0); S.heli.add(S.rotor);
  const cubo = new T.Mesh(new T.CylinderGeometry(0.32, 0.32, 0.22, 16), escuro); S.rotor.add(cubo);
  S.pas = [];
  for (let i = 0; i < 4; i++) {
    const g = new T.Group(); g.rotation.y = i * Math.PI / 2; S.rotor.add(g);
    const pa = new T.Mesh(new T.BoxGeometry(R - 0.3, 0.06, 0.32), escuro); pa.position.x = R / 2 + 0.1; g.add(pa);
    S.pas.push(pa);
  }
  S.disco = new T.Mesh(new T.CircleGeometry(R, 64), new T.MeshBasicMaterial({color: 0x101216, transparent: true, opacity: 0.12, depthWrite: false, side: T.DoubleSide}));
  S.disco.rotation.x = -Math.PI / 2; S.rotor.add(S.disco);
  // rotor de cauda
  S.cauda = new T.Group(); S.cauda.position.set(-7.6, 3.1, 0.25); S.heli.add(S.cauda);
  for (let i = 0; i < 2; i++) {
    const pa = new T.Mesh(new T.BoxGeometry(0.12, 1.5, 0.04), escuro); pa.rotation.z = i * Math.PI / 2; S.cauda.add(pa);
  }
  // ---------- por dentro (raio-x): motor, eixo, roda-livre, transmissão ----------
  S.dentro = new T.Group(); S.heli.add(S.dentro);
  S.motorMat = new T.MeshStandardMaterial({color: 0x8a8f99, metalness: 0.6, roughness: 0.4, emissive: 0xff6a20, emissiveIntensity: 0.6});
  const motor = new T.Mesh(new T.CylinderGeometry(0.42, 0.42, 1.6, 20), S.motorMat);
  motor.rotation.z = Math.PI / 2; motor.position.set(-1.35, 3.0, 0); S.dentro.add(motor);
  S.eixoM = new T.Mesh(new T.CylinderGeometry(0.09, 0.09, 0.55, 12), new T.MeshStandardMaterial({color: 0xffd34d, metalness: 0.7}));
  S.eixoM.rotation.z = Math.PI / 2; S.eixoM.position.set(-0.35, 3.0, 0); S.dentro.add(S.eixoM);
  S.rodaMat = new T.MeshStandardMaterial({color: 0x30d060, emissive: 0x30d060, emissiveIntensity: 0.6});
  S.roda = new T.Mesh(new T.TorusGeometry(0.2, 0.07, 10, 24), S.rodaMat); S.roda.rotation.y = Math.PI / 2;
  S.roda.position.set(-0.05, 3.0, 0); S.dentro.add(S.roda);
  const caixa = new T.Mesh(new T.CylinderGeometry(0.38, 0.45, 0.6, 18), metal); caixa.position.set(-0.3, 3.25, 0); S.dentro.add(caixa);
  // listras nos eixos para ver se giram
  S.listra = new T.Mesh(new T.BoxGeometry(0.5, 0.03, 0.2), escuro); S.listra.position.y = 0.05; S.eixoM.add(S.listra);
  S.dentro.visible = false;
  // luz de alerta no painel
  S.alerta = new T.Mesh(new T.SphereGeometry(0.12, 12, 8), new T.MeshStandardMaterial({color: 0x400000, emissive: 0xff1010, emissiveIntensity: 0}));
  S.alerta.position.set(2.2, 1.9, 0.5); S.heli.add(S.alerta);

  // ---------- partículas: fluxo de ar pelo rotor, fumaça e poeira ----------
  const nA = 140; S.nA = nA;   // setas de ar (cones) atravessando o disco do rotor
  S.arMat = new T.MeshBasicMaterial({color: 0x9fd8ff, transparent: true, opacity: 0.85, depthWrite: false});
  S.ar = new T.InstancedMesh(new T.ConeGeometry(0.13, 0.55, 8), S.arMat, nA); S.ar.frustumCulled = false;
  S.heli.add(S.ar);
  S.arIni = []; for (let i = 0; i < nA; i++) S.arIni.push([A.aleat(), A.aleat(), A.aleat()]);
  S.m4 = new T.Matrix4(); S.q = new T.Quaternion(); S.v = new T.Vector3(); S.esc = new T.Vector3();
  const nF = 160; S.nF = nF; S.fPos = new Float32Array(nF * 3);
  const fg = new T.BufferGeometry(); fg.setAttribute('position', new T.BufferAttribute(S.fPos, 3));
  S.fumaca = new T.Points(fg, new T.PointsMaterial({color: 0x5a5a5a, size: 0.5, transparent: true, opacity: 0.6, depthWrite: false}));
  S.fumaca.frustumCulled = false; cena.add(S.fumaca);
  S.fIni = []; for (let i = 0; i < nF; i++) S.fIni.push([A.aleat(), A.aleat(), A.aleat()]);
  const nP = 260; S.nP = nP; S.pPos = new Float32Array(nP * 3);
  const pg = new T.BufferGeometry(); pg.setAttribute('position', new T.BufferAttribute(S.pPos, 3));
  S.poeira = new T.Points(pg, new T.PointsMaterial({color: 0xc9b48a, size: 0.35, transparent: true, opacity: 0.7, depthWrite: false}));
  S.poeira.frustumCulled = false; cena.add(S.poeira);
  S.pIni = []; for (let i = 0; i < nP; i++) S.pIni.push([A.aleat(), A.aleat(), A.aleat()]);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam, T = S.T;
  S.heli.position.set(...e.pos);
  S.heli.rotation.set(0, 0, e.pitch);
  S.rotor.rotation.y = e.rotor;
  S.pas.forEach(p => { p.rotation.x = e.passo; });
  S.cauda.rotation.z = e.cauda;
  // raio-x
  S.mats.forEach(m => { m.opacity = 1 - 0.8 * e.raiox; m.depthWrite = e.raiox < 0.05; });
  S.dentro.visible = e.raiox > 0.02;
  S.motorMat.emissiveIntensity = 0.6 * e.motor;
  S.eixoM.rotation.x = e.eixoMotor;
  S.rodaMat.color.setRGB(0.19 + 0.8 * e.roda, 0.82 - 0.7 * e.roda, 0.38 - 0.3 * e.roda);
  S.rodaMat.emissive.copy(S.rodaMat.color);
  S.alerta.material.emissiveIntensity = 2.5 * e.luzAlerta;
  // fluxo de ar pelo disco (coordenadas do helicóptero): desce com motor, sobe na autorrotação
  const f = e.fluxo;
  S.ar.visible = Math.abs(f) > 0.02;
  if (S.ar.visible) {
    const cima = f > 0;
    S.q.setFromAxisAngle(new T.Vector3(1, 0, 0), cima ? 0 : Math.PI);   // cone aponta para onde o ar vai
    for (let i = 0; i < S.nA; i++) {
      const [a, b, c] = S.arIni[i];
      const ang = a * Math.PI * 2, rr = R * Math.sqrt(b) * 0.92;
      const fase = (e.t * 0.8 + c) % 1;
      const y = 4.15 + (cima ? (-3.5 + 7 * fase) : (3.5 - 7 * fase));
      const k = Math.sin(Math.PI * fase) * Math.min(1, Math.abs(f));   // nasce e some suave
      S.v.set(-0.3 + Math.cos(ang) * rr, y, Math.sin(ang) * rr);
      S.esc.set(k, k, k);
      S.m4.compose(S.v, S.q, S.esc);
      S.ar.setMatrixAt(i, S.m4);
    }
    S.ar.instanceMatrix.needsUpdate = true;
    S.arMat.color.setHex(cima ? 0xffb15a : 0x9fd8ff);
  }
  // fumaça do motor (fica no ar, no mundo)
  const F = S.fPos;
  for (let i = 0; i < S.nF; i++) {
    const [a, b, c] = S.fIni[i];
    const ts = e.fumaca - c * 2.5;
    if (e.fumaca < 0 || ts < 0 || ts > 4) { F[i * 3 + 1] = -999; continue; }
    F[i * 3] = e.fumacaX[0] - ts * 1.5 + (a - 0.5) * ts;
    F[i * 3 + 1] = e.fumacaX[1] + ts * 0.8 + (b - 0.5) * ts;
    F[i * 3 + 2] = e.fumacaX[2] + (a - 0.5) * ts * 1.2;
  }
  S.fumaca.geometry.attributes.position.needsUpdate = true;
  // poeira do pouso
  const Q = S.pPos;
  for (let i = 0; i < S.nP; i++) {
    const [a, b, c] = S.pIni[i];
    if (e.poeira < 0 || e.poeira > 5) { Q[i * 3 + 1] = -999; continue; }
    const ang = a * Math.PI * 2, d = (2 + 9 * b) * Math.min(1, e.poeira / 1.5) * (0.6 + 0.4 * c);
    Q[i * 3] = e.pos[0] + Math.cos(ang) * d; Q[i * 3 + 1] = 0.2 + c * 1.2 * Math.exp(-e.poeira * 0.6);
    Q[i * 3 + 2] = e.pos[2] + Math.sin(ang) * d;
  }
  S.poeira.geometry.attributes.position.needsUpdate = true;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
