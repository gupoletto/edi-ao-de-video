// Quarto de Ames: construído deformando um quarto retangular "aparente" ao longo dos raios que saem do olho do
// observador O. Cada vértice P vira O + s(x) (P - O), com s maior à esquerda: o canto esquerdo fica quase 2x mais
// longe, mas do ponto O o quarto parece um retângulo perfeito. As duas pessoas têm a mesma altura real.
// Estado: cam, alvo, fov, t, pA [x,z], pB [x,z] (posições aparentes no chão), passoA, passoB (fase da caminhada).
const O = [0, 1.6, 8];
const XL = -3, XR = 3, ZF = 0, ZB = -6, HT = 3;
const sDe = (x) => 1 + 0.9 * (XR - x) / (XR - XL);
export function real(x, y, z) {
  const s = sDe(x);
  return [O[0] + s * (x - O[0]), O[1] + s * (y - O[1]), O[2] + s * (z - O[2])];
}

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 400; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.05;
  const S = {T};
  cena.background = new T.Color(0x1a1d26);
  cena.add(new T.HemisphereLight(0xffffff, 0x404858, 1.8));
  const luz = new T.DirectionalLight(0xffffff, 1.6); luz.position.set(4, 12, 10); cena.add(luz);
  // superfície deformada: grade aparente (u, v) -> ponto aparente -> ponto real
  const sup = (n, m, f, cor) => {
    const g = new T.PlaneGeometry(1, 1, n, m), p = g.attributes.position, cores = [];
    for (let i = 0; i < p.count; i++) {
      const u = p.getX(i) + 0.5, v = p.getY(i) + 0.5;
      const [x, y, z] = f(u, v);
      const [rx, ry, rz] = real(x, y, z);
      p.setXYZ(i, rx, ry, rz);
      cores.push(...cor(u, v));
    }
    g.setAttribute('color', new T.Float32BufferAttribute(cores, 3));
    g.computeVertexNormals();
    const malha = new T.Mesh(g, new T.MeshStandardMaterial({vertexColors: true, roughness: 0.8, side: T.DoubleSide}));
    cena.add(malha);
    return malha;
  };
  const xadrez = (u, v) => ((Math.floor(u * 8) + Math.floor(v * 8)) % 2 ? [0.95, 0.93, 0.88] : [0.12, 0.12, 0.14]);
  sup(64, 64, (u, v) => [XL + u * (XR - XL), 0, ZB + v * (ZF - ZB)], xadrez);                       // piso
  sup(32, 32, (u, v) => [XL + u * (XR - XL), v * HT, ZB], (u, v) => {                                 // fundo
    const jan = (Math.abs(u - 0.27) < 0.1 || Math.abs(u - 0.73) < 0.1) && v > 0.42 && v < 0.82;
    return jan ? [0.55, 0.78, 0.95] : [0.86, 0.72, 0.55];
  });
  sup(32, 32, (u, v) => [XL, v * HT, ZB + u * (ZF - ZB)], () => [0.80, 0.66, 0.50]);                   // esquerda
  sup(32, 32, (u, v) => [XR, v * HT, ZB + u * (ZF - ZB)], () => [0.80, 0.66, 0.50]);                   // direita
  // sem teto: na vista de cima ele esconderia o formato (do buraco, o alto do quarto fica escuro)
  // olho / buraco na frente
  const olho = new T.Mesh(new T.TorusGeometry(0.12, 0.03, 8, 24), new T.MeshStandardMaterial({color: 0xffc23a, emissive: 0x996600}));
  olho.position.set(...O); cena.add(olho); S.olho = olho;
  // pessoas (mesma altura real: 1,7 m)
  const pessoa = (cor) => {
    const g = new T.Group();
    const pele = new T.MeshStandardMaterial({color: 0xe0b48a}), roupa = new T.MeshStandardMaterial({color: cor}),
          calca = new T.MeshStandardMaterial({color: 0x2a2f3a});
    const corpo = new T.Mesh(new T.CapsuleGeometry(0.2, 0.55, 8, 16), roupa); corpo.position.y = 1.15; g.add(corpo);
    const cab = new T.Mesh(new T.SphereGeometry(0.14, 20, 14), pele); cab.position.y = 1.58; g.add(cab);
    const pernas = [];
    for (const dz of [-0.09, 0.09]) {
      const p = new T.Group(); p.position.set(0, 0.8, dz); g.add(p);
      const m = new T.Mesh(new T.CapsuleGeometry(0.07, 0.62, 6, 10), calca); m.position.y = -0.38; p.add(m);
      pernas.push(p);
    }
    cena.add(g);
    return {g, pernas};
  };
  S.A = pessoa(0xd23a3a); S.B = pessoa(0x2f6fd8);
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam;
  for (const [P, p, f] of [[S.A, e.pA, e.passoA], [S.B, e.pB, e.passoB]]) {
    const [x, , z] = real(p[0], 0, p[1]);
    P.g.position.set(x, 0, z);
    P.g.rotation.y = e.virar || 0;
    P.pernas[0].rotation.z = 0.5 * Math.sin(f); P.pernas[1].rotation.z = -0.5 * Math.sin(f);
  }
  S.olho.visible = e.olho > 0.5;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
