// Onda de pêndulos: 15 pêndulos de comprimentos ligeiramente diferentes pendurados numa barra. Os ângulos vêm do
// Python (solução exata do pêndulo de pequena amplitude). Estado: cam, alvo, fov, t, ang [15], rastro 0..1.
import * as A from 'http://cena.local/ambiente.js';

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 200; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.0;
  const S = {T};
  cena.background = new T.Color(0x0d1018);
  cena.add(new T.HemisphereLight(0xdfe8ff, 0x202230, 1.4));
  const luz = new T.DirectionalLight(0xffffff, 2.4); luz.position.set(3, 6, 5); cena.add(luz);
  const piso = new T.Mesh(new T.PlaneGeometry(40, 40), new T.MeshStandardMaterial({color: 0x161a24, roughness: 0.6, metalness: 0.2}));
  piso.rotation.x = -Math.PI / 2; piso.position.y = -0.2; cena.add(piso);
  const madeira = new T.MeshStandardMaterial({color: 0x8a5a32, roughness: 0.6});
  const barra = new T.Mesh(new T.BoxGeometry(0.12, 0.12, 3.3), madeira); barra.position.set(0, 2.6, 0); cena.add(barra);
  for (const z of [-1.6, 1.6]) {
    const p = new T.Mesh(new T.BoxGeometry(0.12, 2.8, 0.12), madeira); p.position.set(0, 1.2, z); cena.add(p);
  }
  S.pend = [];
  const fio = new T.MeshBasicMaterial({color: 0xcfd6e0});
  window._L = null;
  window.montarPendulos = (Ls) => {
    Ls.forEach((L, i) => {
      const z = -1.4 + i * 2.8 / (Ls.length - 1);
      const g = new T.Group(); g.position.set(0, 2.54, z); cena.add(g);
      const f = new T.Mesh(new T.CylinderGeometry(0.004, 0.004, L, 6), fio); f.position.y = -L / 2; g.add(f);
      const cor = new T.Color().setHSL(i / Ls.length, 0.75, 0.55);
      const b = new T.Mesh(new T.SphereGeometry(0.075, 24, 16), new T.MeshStandardMaterial({color: cor, roughness: 0.25, metalness: 0.3,
        emissive: cor, emissiveIntensity: 0.25}));
      b.position.y = -L; g.add(b);
      S.pend.push(g);
    });
  };
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  if (!S.pend.length) window.montarPendulos(e.L);
  S.pend.forEach((g, i) => { g.rotation.z = e.ang[i]; });
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
