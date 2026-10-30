// Motor de 4 tempos em corte: pistão, biela, virabrequim, válvulas, vela e o gás em cada fase.
// O estado vem do Python (tres.py): theta (ângulo do virabrequim, rad), lift_adm / lift_esc (0..1),
// gas_cor [r,g,b], gas_op (0..1), faisca (0..1), cam_ang (rad), cam_r, cam_y.
const R = 1.0, L = 3.2;              // raio da manivela e comprimento da biela
const TOPO = 5.6;                     // altura do cabeçote

window.montar = (THREE, cena, camera) => {
  const T = THREE;
  cena.background = new T.Color(0x141b2e);
  cena.add(new T.HemisphereLight(0xe8eeff, 0x2a3048, 2.0));
  cena.add(new T.AmbientLight(0xffffff, 0.35));
  const sol = new T.DirectionalLight(0xffffff, 3.2);
  sol.position.set(6, 10, 8);
  cena.add(sol);
  const contra = new T.DirectionalLight(0x8fb4ff, 1.0);
  contra.position.set(-8, 4, -6);
  cena.add(contra);

  const aco = new T.MeshStandardMaterial({color: 0xb9c0cc, metalness: 0.85, roughness: 0.32});
  const escuro = new T.MeshStandardMaterial({color: 0x3a4150, metalness: 0.7, roughness: 0.45});
  const latao = new T.MeshStandardMaterial({color: 0xc9a46a, metalness: 0.8, roughness: 0.35});
  const S = {};

  // cilindro de vidro (corte) com anéis de metal
  const vidro = new T.MeshStandardMaterial({color: 0x9fc4ff, transparent: true, opacity: 0.16, side: T.DoubleSide,
                                            metalness: 0.1, roughness: 0.05, depthWrite: false});
  const tubo = new T.Mesh(new T.CylinderGeometry(1.28, 1.28, TOPO - 1.9, 48, 1, true), vidro);
  tubo.position.y = (TOPO + 1.9) / 2;
  cena.add(tubo);
  for (const y of [1.95, TOPO - 0.05]) {
    const anel = new T.Mesh(new T.TorusGeometry(1.3, 0.06, 12, 48), escuro);
    anel.rotation.x = Math.PI / 2; anel.position.y = y; cena.add(anel);
  }
  // cabeçote
  const cab = new T.Mesh(new T.CylinderGeometry(1.45, 1.45, 0.5, 48), escuro);
  cab.position.y = TOPO + 0.25; cena.add(cab);
  // gás da câmara (volume entre o pistão e o cabeçote)
  S.gas = new T.Mesh(new T.CylinderGeometry(1.2, 1.2, 1, 40),
                     new T.MeshStandardMaterial({color: 0x5fa8ff, transparent: true, opacity: 0.3, emissive: 0x000000,
                                                 depthWrite: false}));
  cena.add(S.gas);
  // pistão
  S.pistao = new T.Group();
  const corpo = new T.Mesh(new T.CylinderGeometry(1.18, 1.18, 1.2, 48), aco);
  S.pistao.add(corpo);
  for (const dy of [0.35, 0.18]) {
    const ag = new T.Mesh(new T.TorusGeometry(1.185, 0.03, 8, 48), escuro);
    ag.rotation.x = Math.PI / 2; ag.position.y = dy; S.pistao.add(ag);
  }
  cena.add(S.pistao);
  // biela
  S.biela = new T.Mesh(new T.BoxGeometry(0.34, 1, 0.3), latao);
  cena.add(S.biela);
  // virabrequim: eixo, braços com contrapeso e o moente
  const eixo = new T.Mesh(new T.CylinderGeometry(0.32, 0.32, 3.4, 32), aco);
  eixo.rotation.x = Math.PI / 2; cena.add(eixo);
  S.vira = new T.Group();
  for (const z of [-0.45, 0.45]) {
    const braco = new T.Mesh(new T.BoxGeometry(0.7, 1.6, 0.22), escuro);
    braco.position.set(0, 0.35, z); S.vira.add(braco);
    const contrapeso = new T.Mesh(new T.CylinderGeometry(1.05, 1.05, 0.22, 40, 1, false, Math.PI * 0.75, Math.PI * 1.5),
                                  escuro);
    contrapeso.rotation.x = Math.PI / 2; contrapeso.position.z = z; S.vira.add(contrapeso);
  }
  const moente = new T.Mesh(new T.CylinderGeometry(0.26, 0.26, 1.1, 24), aco);
  moente.rotation.x = Math.PI / 2; moente.position.y = R; S.vira.add(moente);
  cena.add(S.vira);
  // volante atrás
  const volante = new T.Mesh(new T.CylinderGeometry(1.6, 1.6, 0.22, 64), aco);
  volante.rotation.x = Math.PI / 2; volante.position.z = -1.8; cena.add(volante);
  S.volante = volante;
  // válvulas (admissão azul à esquerda, escape vermelho à direita) e vela no meio
  const valvula = (x, cor) => {
    const g = new T.Group();
    const haste = new T.Mesh(new T.CylinderGeometry(0.07, 0.07, 1.9, 12), aco); haste.position.y = 0.95; g.add(haste);
    const cabeca = new T.Mesh(new T.CylinderGeometry(0.42, 0.18, 0.14, 32),
                              new T.MeshStandardMaterial({color: cor, metalness: 0.6, roughness: 0.35}));
    g.add(cabeca);
    for (let k = 0; k < 5; k++) {  // mola: anéis empilhados
      const espira = new T.Mesh(new T.TorusGeometry(0.2, 0.035, 8, 24), aco);
      espira.rotation.x = Math.PI / 2; espira.position.y = 1.1 + k * 0.13; g.add(espira);
    }
    g.position.set(x, TOPO, 0); cena.add(g);
    return g;
  };
  S.adm = valvula(-0.6, 0x3f8cff);
  S.esc = valvula(0.6, 0xff6a4a);
  const vela = new T.Mesh(new T.CylinderGeometry(0.12, 0.12, 1.2, 16), new T.MeshStandardMaterial({color: 0xf2efe6}));
  vela.position.set(0, TOPO + 0.8, 0); cena.add(vela);
  S.faisca = new T.Mesh(new T.SphereGeometry(0.22, 24, 16), new T.MeshBasicMaterial({color: 0xfff1b0, transparent: true, depthTest: false}));
  S.faisca.renderOrder = 10;
  S.faisca.position.set(0, TOPO - 0.15, 0); cena.add(S.faisca);
  S.luz = new T.PointLight(0xffa040, 0, 12); S.luz.position.set(0, TOPO - 0.6, 0); cena.add(S.luz);
  // chão sutil
  const chao = new T.Mesh(new T.CircleGeometry(9, 64), new T.MeshStandardMaterial({color: 0x121827, roughness: 1}));
  chao.rotation.x = -Math.PI / 2; chao.position.y = -2.6; cena.add(chao);
  window._S = S; window._cam = camera; window._T = T;
};

window.posar = (e) => {
  const S = window._S, T = window._T, cam = window._cam;
  const th = e.theta;
  const yp = R * Math.cos(th) + Math.sqrt(L * L - R * R * Math.sin(th) ** 2);  // pino do pistão
  S.pistao.position.y = yp + 0.45;
  S.vira.rotation.z = -th;
  S.volante.rotation.y = th;
  const px = R * Math.sin(th), py = R * Math.cos(th);  // moente
  const dx = 0 - px, dy = yp - py, comp = Math.hypot(dx, dy);
  S.biela.scale.y = comp;
  S.biela.position.set((px) / 2, (py + yp) / 2, 0);
  S.biela.rotation.z = Math.atan2(-dx, dy);
  S.adm.position.y = TOPO - 0.42 * e.lift_adm;
  S.esc.position.y = TOPO - 0.42 * e.lift_esc;
  const topoPistao = yp + 1.05;
  const alt = Math.max(0.05, TOPO - topoPistao);
  S.gas.scale.y = alt;
  S.gas.position.y = topoPistao + alt / 2;
  S.gas.material.color.setRGB(...e.gas_cor);
  S.gas.material.emissive.setRGB(...e.gas_cor.map(v => v * 1.1 * Math.min(1, e.faisca + e.brilho)));
  S.gas.material.opacity = e.gas_op;
  S.faisca.material.opacity = e.faisca;
  S.faisca.scale.setScalar(0.3 + 2.4 * e.faisca);
  S.luz.intensity = 40 * e.faisca;
  cam.position.set(Math.sin(e.cam_ang) * e.cam_r, e.cam_y, Math.cos(e.cam_ang) * e.cam_r);
  cam.lookAt(0, e.cam_alvo, 0);
};
