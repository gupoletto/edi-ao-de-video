// Corrente de dominós em que cada peça é 1,5 vez maior que a anterior: de 5 mm até a 29ª, da altura do Empire State.
// A queda de cada peça (ângulo) vem do Python; a cena só posa. Coordenadas em metros, as peças seguem o eixo +x.
// Estado: cam, alvo, fov, t, ang [ângulo de cada peça, rad], empire 0..1 (prédio de comparação aparecendo).
import * as A from 'http://cena.local/ambiente.js';

const N = 29, H0 = 0.005, F = 1.5;

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.near = 0.002; camera.far = 8000; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  A.reiniciar(55);
  S.ceu = A.ceu(T, cena, {sol: [0.5, 0.6, 0.55], neblina: 0xcfe0ee, perto: 900, longe: 5000});
  // chão: grama clara com ladrilhos de madeira perto do começo (para a escala de milímetros ler bem)
  A.grama(T, cena, {tam: 9000, cor: 0x6f9c4a});
  const mesa = new T.Mesh(new T.PlaneGeometry(1.2, 0.5), new T.MeshStandardMaterial({color: 0xb98a5a, roughness: 0.6}));
  mesa.rotation.x = -Math.PI / 2; mesa.position.set(0.45, 0.0015, 0); cena.add(mesa);
  for (let i = 0; i < 60; i++) {
    const x = 20 + A.aleat() * 1500, z = (A.aleat() < 0.5 ? -1 : 1) * (40 + A.aleat() * 600);
    A.arvore(T, cena, x, z, {altura: 7 + A.aleat() * 6, copa: 3 + A.aleat() * 2});
  }
  A.morros(T, cena, {n: 26, dist: 3000});
  // peças
  S.pecas = [];
  const cores = [0xf4f1ea, 0x1b1d22];
  let x = 0;
  S.xs = [];
  for (let i = 0; i < N; i++) {
    const h = H0 * Math.pow(F, i), e = h * 0.18, w = h * 0.5;
    const piv = new T.Group(); piv.position.set(x + e, 0, 0); cena.add(piv);   // gira na aresta da frente
    const m = new T.Mesh(new T.BoxGeometry(e, h, w), new T.MeshStandardMaterial({color: cores[i % 2], roughness: 0.35, metalness: 0.05}));
    m.position.set(-e / 2, h / 2, 0); piv.add(m);
    // pontos (pips) na face lateral, para parecer dominó
    const pip = new T.MeshStandardMaterial({color: cores[(i + 1) % 2]});
    for (const yy of [0.25, 0.75]) {
      const d = new T.Mesh(new T.CylinderGeometry(w * 0.08, w * 0.08, e * 1.02, 12), pip);
      d.rotation.z = Math.PI / 2; d.position.set(-e / 2, h * yy, 0); piv.add(d);
    }
    S.pecas.push(piv); S.xs.push(x);
    x += e + h * 0.5;    // distância entre peças: meia altura da peça
  }
  // Empire State para comparação, ao lado da última peça
  S.empire = new T.Group(); cena.add(S.empire);
  const cinza = new T.MeshStandardMaterial({color: 0xb9b3a6, roughness: 0.8});
  for (const [w, h0, h1] of [[60, 0, 180], [45, 180, 290], [32, 290, 350], [20, 350, 381]]) {
    const b = new T.Mesh(new T.BoxGeometry(w, h1 - h0, w), cinza); b.position.y = (h0 + h1) / 2; S.empire.add(b);
  }
  const ant = new T.Mesh(new T.CylinderGeometry(1, 3, 62, 8), cinza); ant.position.y = 412; S.empire.add(ant);
  S.empire.position.set(S.xs[N - 1] + 30, 0, -190);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  S.pecas.forEach((p, i) => { p.rotation.z = -e.ang[i]; });
  S.empire.scale.y = Math.max(0.001, e.empire);
  S.empire.visible = e.empire > 0.01;
  S.ceu.ceu.position.set(e.cam[0], 0, e.cam[2]);
  S.ceu.ceu.scale.setScalar(Math.max(1, Math.abs(e.cam[2]) / 300));
  cam.near = Math.max(0.0005, e.perto); cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
