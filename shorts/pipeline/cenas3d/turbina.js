// Avião no céu + turbofan em corte (formato 3D cinematográfico).
// Mundo: o avião aponta para +x, com o "para cima" em +y. O motor do lado da câmera fica sob a asa em z > 0.
// Estado vindo do Python (tres.py) a cada quadro:
//   cam [x,y,z], alvo [x,y,z], fov, t (s), nuvem (deslocamento das nuvens), rolagem (rad),
//   fan / lp / hp (ângulos dos eixos), corte 0..1 (metade da carenagem some), fogo 0..1,
//   ate (x local até onde o fluxo já chegou, de +3.6 a -4), bypass 0..1, nucleo 0..1, destaque ("fan" | "comp" |
//   "comb" | "turb" | ""), pulso 0..1.
const MOTOR = [3.4, -2.55, 6.6];   // centro do motor do lado da câmera (mundo)
const ESC = 1.25;                    // escala do motor (unidades locais -> mundo)

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  r.localClippingEnabled = true;
  r.toneMappingExposure = 1.05;
  camera.far = 1500; camera.updateProjectionMatrix();
  const S = {T};

  // ---------- céu (gradiente + sol) e luz ----------
  const ceu = new T.Mesh(new T.SphereGeometry(900, 48, 24), new T.ShaderMaterial({
    side: T.BackSide, depthWrite: false,
    uniforms: {sol: {value: new T.Vector3(0.55, 0.35, -0.75).normalize()}},
    vertexShader: 'varying vec3 v; void main(){ v = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `varying vec3 v; uniform vec3 sol;
      void main(){
        float h = clamp(v.y * 0.5 + 0.5, 0.0, 1.0);
        vec3 topo = vec3(0.10, 0.32, 0.72), meio = vec3(0.42, 0.66, 0.93), baixo = vec3(0.82, 0.90, 0.98);
        vec3 c = h > 0.5 ? mix(meio, topo, (h - 0.5) * 2.0) : mix(baixo, meio, h * 2.0);
        float s = max(dot(normalize(v), sol), 0.0);
        c += vec3(1.0, 0.92, 0.75) * (pow(s, 600.0) * 3.0 + pow(s, 12.0) * 0.25);
        gl_FragColor = vec4(c, 1.0);
      }`}));
  cena.add(ceu);
  cena.fog = new T.Fog(0xbfd8f2, 120, 700);
  cena.add(new T.HemisphereLight(0xdfeaff, 0x8aa0b8, 1.6));
  const sol = new T.DirectionalLight(0xfff3dd, 3.4); sol.position.set(60, 40, -80); cena.add(sol);
  const preenche = new T.DirectionalLight(0xbfd6ff, 1.1); preenche.position.set(20, -10, 60); cena.add(preenche);

  // ---------- nuvens: blocos de esferas brancas (camada abaixo + algumas na altura do avião) ----------
  const branco = new T.MeshStandardMaterial({color: 0xffffff, roughness: 1, metalness: 0, emissive: 0x9fb4c8,
                                             emissiveIntensity: 0.25});
  const bola = new T.SphereGeometry(1, 16, 12);
  let semente = 7;
  const aleat = () => { semente = (semente * 16807) % 2147483647; return semente / 2147483647; };
  S.nuvens = [];
  const nuvem = (x, y, z, tam) => {
    const g = new T.Group();
    const n = 7 + Math.floor(aleat() * 6);
    for (let i = 0; i < n; i++) {
      const m = new T.Mesh(bola, branco);
      const rr = tam * (0.45 + aleat() * 0.55);
      m.scale.set(rr * 1.3, rr * 0.8, rr);
      m.position.set((aleat() - 0.5) * tam * 3.2, (aleat() - 0.2) * tam * 0.7, (aleat() - 0.5) * tam * 1.8);
      g.add(m);
    }
    g.position.set(x, y, z); g.userData.x0 = x; cena.add(g); S.nuvens.push(g);
  };
  for (let i = 0; i < 70; i++) nuvem(-700 + aleat() * 1400, -42 - aleat() * 20, -500 + aleat() * 900, 9 + aleat() * 12);
  for (let i = 0; i < 16; i++) nuvem(-500 + aleat() * 1000, -8 + aleat() * 26, -260 + aleat() * 180, 6 + aleat() * 7);
  for (let i = 0; i < 6; i++) nuvem(-300 + aleat() * 600, -6 + aleat() * 14, 70 + aleat() * 60, 4 + aleat() * 4);

  // ---------- avião ----------
  const pintura = new T.MeshStandardMaterial({color: 0xf3f5f8, metalness: 0.25, roughness: 0.35});
  const azul = new T.MeshStandardMaterial({color: 0x2f8fe0, metalness: 0.3, roughness: 0.35});
  const cinza = new T.MeshStandardMaterial({color: 0x9aa3ae, metalness: 0.6, roughness: 0.35});
  const vidroEsc = new T.MeshStandardMaterial({color: 0x1b2433, metalness: 0.5, roughness: 0.15});
  const aviao = new T.Group(); S.aviao = aviao; cena.add(aviao);
  const perfil = [[0, 16], [0.55, 15.7], [1.1, 14.9], [1.5, 13.4], [1.75, 11.5], [1.8, 9], [1.8, -7], [1.6, -10],
                  [1.15, -13], [0.55, -15.3], [0.15, -16]].map(([a, b]) => new T.Vector2(a, b));
  const fus = new T.LatheGeometry(perfil, 48); fus.rotateZ(-Math.PI / 2);
  aviao.add(new T.Mesh(fus, pintura));
  const faixa = new T.Mesh(new T.CylinderGeometry(1.815, 1.815, 22, 48, 1, true, Math.PI * 0.62, Math.PI * 0.18), azul);
  faixa.rotation.z = Math.PI / 2; faixa.position.x = -0.5; aviao.add(faixa);  // faixa azul na lateral
  for (const lado of [1, -1]) {
    for (let i = 0; i < 34; i++) {  // janelas
      const j = new T.Mesh(new T.BoxGeometry(0.28, 0.36, 0.1), vidroEsc);
      j.position.set(10.4 - i * 0.6, 0.55, lado * 1.76); aviao.add(j);
    }
  }
  const cabine = new T.Mesh(new T.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), vidroEsc);
  cabine.scale.set(1.2, 0.35, 1.05); cabine.position.set(14.0, 0.75, 0); aviao.add(cabine);
  const asa = (lado) => {
    const sh = new T.Shape();
    sh.moveTo(5, 1.5 * lado); sh.lineTo(-3.2, 1.5 * lado); sh.lineTo(-7.8, 17 * lado); sh.lineTo(-5.6, 17 * lado);
    sh.closePath();
    const g = new T.ExtrudeGeometry(sh, {depth: 0.32, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.08,
                                         bevelSegments: 2});
    g.rotateX(Math.PI / 2);
    const m = new T.Mesh(g, pintura); m.position.y = -0.7; m.rotation.x = lado * 0.07; return m;
  };
  aviao.add(asa(1)); aviao.add(asa(-1));
  for (const lado of [1, -1]) {  // pontas de asa (winglets) azuis
    const w = new T.Mesh(new T.BoxGeometry(1.3, 1.25, 0.08), azul);
    w.position.set(-6.9, 0.35, lado * 17.05); w.rotation.z = -0.35; aviao.add(w);
  }
  const estab = (lado) => {
    const sh = new T.Shape();
    sh.moveTo(-11.8, 0.8 * lado); sh.lineTo(-14.6, 0.8 * lado); sh.lineTo(-16.6, 6.2 * lado); sh.lineTo(-15.2, 6.2 * lado);
    sh.closePath();
    const g = new T.ExtrudeGeometry(sh, {depth: 0.18, bevelEnabled: false}); g.rotateX(Math.PI / 2);
    const m = new T.Mesh(g, pintura); m.position.y = 0.6; return m;
  };
  aviao.add(estab(1)); aviao.add(estab(-1));
  const leme = new T.Shape();
  leme.moveTo(-10.6, 1.2); leme.lineTo(-15.6, 1.2); leme.lineTo(-17.2, 7.8); leme.lineTo(-14.6, 7.8); leme.closePath();
  const lg = new T.ExtrudeGeometry(leme, {depth: 0.24, bevelEnabled: false}); lg.translate(0, 0, -0.12);
  aviao.add(new T.Mesh(lg, azul));

  // ---------- motores: carenagem (lathe) + pilone; o do lado da câmera tem o miolo detalhado ----------
  const corteNac = new T.Plane(new T.Vector3(0, 0, -1), 1e4);  // remove a metade z > constante
  const corteMiolo = new T.Plane(new T.Vector3(0, 0, -1), 1e4);
  S.cortes = [corteNac, corteMiolo];
  const nacMat = new T.MeshStandardMaterial({color: 0xe9edf2, metalness: 0.35, roughness: 0.3, side: T.DoubleSide,
                                             clippingPlanes: [corteNac], clipShadows: true});
  const nacPerfil = [[0.92, 2.05], [1.02, 2.0], [1.06, 1.6], [1.04, 0.2], [0.92, -1.4], [0.82, -1.85], [0.76, -1.85],
                     [0.86, -1.4], [0.97, 0.2], [0.99, 1.6], [0.95, 1.95]].map(([a, b]) => new T.Vector2(a, b));
  const motorEm = (pos, detalhado) => {
    const g = new T.Group(); g.position.set(...pos); g.scale.setScalar(ESC); aviao.add(g);
    const nacG = new T.LatheGeometry(nacPerfil, 64); nacG.rotateZ(-Math.PI / 2);
    g.add(new T.Mesh(nacG, detalhado ? nacMat : pintura));
    const pil = new T.Mesh(new T.BoxGeometry(2.6, 0.9, 0.25), pintura); pil.position.set(0.1, 1.15, 0); g.add(pil);
    const borda = new T.Mesh(new T.TorusGeometry(0.97, 0.06, 12, 64), cinza);
    borda.rotation.y = Math.PI / 2; borda.position.x = 2.02; g.add(borda);
    if (!detalhado) {  // motor do outro lado: só o fan escuro
      const f = new T.Mesh(new T.CircleGeometry(0.93, 40), new T.MeshStandardMaterial({color: 0x2a3038}));
      f.rotation.y = Math.PI / 2; f.position.x = 1.7; g.add(f);
    }
    return g;
  };
  motorEm([MOTOR[0], MOTOR[1], -MOTOR[2]], false);
  const M = motorEm(MOTOR, true); S.motor = M;

  // materiais do miolo (com corte) e brilho de destaque
  const mk = (cor, met, rug, extra = {}) => new T.MeshStandardMaterial(Object.assign(
    {color: cor, metalness: met, roughness: rug, clippingPlanes: [corteMiolo], side: T.DoubleSide}, extra));
  const titanio = mk(0xc5ccd6, 0.9, 0.25), ferro = mk(0x6c7480, 0.8, 0.4), quente = mk(0xb88a62, 0.8, 0.35);
  const fanMat = new T.MeshStandardMaterial({color: 0xd2d8e0, metalness: 0.9, roughness: 0.22, side: T.DoubleSide});
  const compMat = mk(0xc5ccd6, 0.9, 0.25);
  const carcaca = mk(0x8d96a3, 0.7, 0.4, {transparent: true, opacity: 0.55});
  S.destacaveis = {fan: [], comp: [], comb: [], turb: []};

  // eixo e cone de entrada (spinner)
  const eixo = new T.Mesh(new T.CylinderGeometry(0.07, 0.07, 4.2, 16), titanio); eixo.rotation.z = Math.PI / 2;
  eixo.position.x = -0.1; M.add(eixo);
  const spinnerG = new T.ConeGeometry(0.3, 0.6, 32); spinnerG.rotateZ(-Math.PI / 2);
  const spinner = new T.Mesh(spinnerG, mk(0x30363f, 0.6, 0.3)); spinner.position.x = 1.98; M.add(spinner);
  const espiral = new T.Mesh(new T.TorusGeometry(0.16, 0.025, 6, 24, Math.PI * 1.5), mk(0xffffff, 0.1, 0.6));
  espiral.rotation.y = Math.PI / 2; espiral.position.x = 2.12; M.add(espiral);

  // fan: pás largas e torcidas
  S.fan = new T.Group(); S.fan.position.x = 1.65; M.add(S.fan);
  const paFan = new T.BoxGeometry(0.06, 0.66, 0.24); paFan.translate(0, 0.6, 0);
  for (let i = 0; i < 22; i++) {
    const q = new T.Group(); q.rotation.x = (i / 22) * Math.PI * 2;
    const pa = new T.Mesh(paFan, fanMat); pa.rotation.y = 0.55; q.add(pa); S.fan.add(q);
    S.destacaveis.fan.push(pa);
  }
  const cubo = new T.Mesh(new T.CylinderGeometry(0.3, 0.3, 0.3, 32), ferro); cubo.rotation.z = Math.PI / 2;
  S.fan.add(cubo);

  // carcaça do núcleo (casca que separa o bypass do núcleo)
  const corePerfil = [[0.44, 1.25], [0.5, 1.0], [0.47, 0.0], [0.47, -0.6], [0.5, -1.4], [0.42, -2.05]]
    .map(([a, b]) => new T.Vector2(a, b));
  const coreG = new T.LatheGeometry(corePerfil, 48); coreG.rotateZ(-Math.PI / 2);
  M.add(new T.Mesh(coreG, carcaca));

  // estágios de pás (compressor e turbina): discos com pás pequenas
  const estagio = (x, rIn, rOut, n, mat, lista, ang) => {
    const g = new T.Group(); g.position.x = x;
    const disco = new T.Mesh(new T.CylinderGeometry(rIn, rIn, 0.06, 32), mat); disco.rotation.z = Math.PI / 2; g.add(disco);
    const pg = new T.BoxGeometry(0.035, rOut - rIn, 0.07); pg.translate(0, (rIn + rOut) / 2, 0);
    for (let i = 0; i < n; i++) {
      const q = new T.Group(); q.rotation.x = (i / n) * Math.PI * 2;
      const pa = new T.Mesh(pg, mat); pa.rotation.y = ang; q.add(pa); g.add(q);
    }
    lista.push(disco); g.children.forEach(c => c.children && c.children.forEach(m => lista.push(m)));
    M.add(g); return g;
  };
  S.comp = []; S.turb = [];
  for (let k = 0; k < 9; k++) {  // compressor: 9 estágios, cada vez menores
    const x = 1.05 - k * 0.12, rOut = 0.44 - k * 0.018;
    S.comp.push(estagio(x, 0.17 + k * 0.012, rOut, 28, compMat, S.destacaveis.comp, 0.4));
  }
  // câmara de combustão: anel que brilha
  S.chamaMat = mk(0x9a8f86, 0.7, 0.35, {emissive: 0xff6a1a, emissiveIntensity: 0});
  const camara = new T.Mesh(new T.TorusGeometry(0.33, 0.06, 16, 48), S.chamaMat);
  camara.rotation.y = Math.PI / 2; camara.scale.set(1, 1, 3.2); camara.position.x = -0.22; M.add(camara);
  S.destacaveis.comb.push(camara);
  S.luzFogo = new T.PointLight(0xff7a2a, 0, 4, 1.5); S.luzFogo.position.set(-0.22, 0, 0); M.add(S.luzFogo);
  for (let k = 0; k < 6; k++) {  // turbina: 2 de alta + 4 de baixa, cada vez maiores
    const x = -0.62 - k * 0.14, rOut = 0.36 + k * 0.016;
    S.turb.push(estagio(x, 0.2, rOut, 32, quente, S.destacaveis.turb, -0.45));
  }
  const coneEsc = new T.ConeGeometry(0.22, 0.9, 32); coneEsc.rotateZ(Math.PI / 2);
  const cone = new T.Mesh(coneEsc, ferro); cone.position.x = -1.95; M.add(cone);

  // ---------- fluxo de ar: partículas ----------
  const N = 2600;
  S.N = N;
  const geo = new T.BufferGeometry();
  S.pos = new Float32Array(N * 3); S.cor = new Float32Array(N * 3);
  geo.setAttribute('position', new T.BufferAttribute(S.pos, 3));
  geo.setAttribute('color', new T.BufferAttribute(S.cor, 3));
  const ponto = document.createElement('canvas'); ponto.width = ponto.height = 64;
  const pc = ponto.getContext('2d'); const gr = pc.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.4, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  pc.fillStyle = gr; pc.fillRect(0, 0, 64, 64);
  S.pontoMat = new T.PointsMaterial({size: 0.2, vertexColors: true, transparent: true, depthWrite: false,
    opacity: 0.95, map: new T.CanvasTexture(ponto), clippingPlanes: [corteMiolo]});
  S.pontos = new T.Points(geo, S.pontoMat); S.pontos.frustumCulled = false; M.add(S.pontos);
  S.part = [];
  for (let i = 0; i < N; i++) S.part.push({nucleo: aleat() < 0.32, fase: aleat(), ang: aleat() * Math.PI * 2, rr: aleat()});

  window._S = S; window._cam = camera;
};

// raio do caminho do ar em x (coordenadas locais do motor): bypass (fora do núcleo) e núcleo
const raioBypass = (x, u) => x > 1.8 ? 0.55 + 0.4 * u : 0.56 + 0.38 * u;
const raioNucleo = (x, u) => {
  if (x > 1.25) return 0.2 + 0.6 * u * Math.min(1, (x - 1.25) / 1.2);
  if (x > 0.0) return 0.2 + (0.22 - 0.06 * (1.25 - x) / 1.25) * u;      // compressor: aperta
  if (x > -0.5) return 0.26 + 0.12 * u;                                   // combustão
  if (x > -1.5) return 0.22 + 0.16 * u;                                    // turbina
  return Math.max(0.06, 0.24 + 0.1 * u - (-1.5 - x) * 0.12);               // bocal
};
// velocidade relativa ao longo do caminho (o ar desacelera no compressor = mais denso; acelera na saída)
const xDoNucleo = (s) => {
  // s 0..1 -> x de +3.6 a -4.2; o trecho do compressor ocupa mais "s" (fica mais lento, mais denso)
  const nos = [[0, 3.6], [0.18, 1.3], [0.52, 0.0], [0.64, -0.5], [0.76, -1.5], [1, -4.2]];
  for (let i = 1; i < nos.length; i++) if (s <= nos[i][0]) {
    const [s0, x0] = nos[i - 1], [s1, x1] = nos[i]; return x0 + (x1 - x0) * (s - s0) / (s1 - s0);
  }
  return -4.2;
};
const corNucleo = (x) => {
  if (x > 1.25) return [0.2, 0.62, 1.0];
  if (x > 0.0) { const q = (1.25 - x) / 1.25; return [0.2 + 0.8 * q, 0.62 + 0.38 * q, 1.0]; }
  if (x > -0.5) return [1.0, 0.55, 0.12];
  if (x > -1.5) return [1.0, 0.38, 0.1];
  return [0.9, 0.45, 0.25];
};

window.posar = (e) => {
  const S = window._S, T = S.T, cam = window._cam;
  // nuvens passando (o avião voa para +x: o mundo anda para -x)
  for (const n of S.nuvens) {
    let x = n.userData.x0 - e.nuvem;
    x = ((x + 700) % 1400 + 1400) % 1400 - 700;
    n.position.x = x;
  }
  S.aviao.rotation.x = e.rolagem;
  S.aviao.position.y = 0.25 * Math.sin(e.t * 0.7);
  // corte: a constante sobe de "longe" até o centro do motor
  const zc = MOTOR[2] + (1 - e.corte) * 8;
  S.cortes[0].constant = zc; S.cortes[1].constant = e.corte > 0.01 ? MOTOR[2] + 0.02 : 1e4;
  S.fan.rotation.x = e.fan;
  S.comp.forEach((g, i) => g.rotation.x = (i < 3 ? e.lp : e.hp) * (1 + i * 0.02));
  S.turb.forEach((g, i) => g.rotation.x = (i < 2 ? e.hp : e.lp));
  S.chamaMat.emissiveIntensity = 2.6 * e.fogo * (0.85 + 0.15 * Math.sin(e.t * 31));
  S.luzFogo.intensity = 6 * e.fogo;
  // destaque: pulso emissivo na parte que está sendo explicada
  const cores = {fan: 0x5cc7fa, comp: 0xffffff, comb: 0xff7a2a, turb: 0xff4a3a};
  for (const k of ['fan', 'comp', 'turb']) {
    const mat = S.destacaveis[k][0].material;
    mat.emissive = mat.emissive || new T.Color();
    mat.emissive.setHex(cores[k]);
    mat.emissiveIntensity = e.destaque === k ? 0.35 * e.pulso : 0;
  }
  // partículas
  const P = S.pos, C = S.cor;
  for (let i = 0; i < S.N; i++) {
    const p = S.part[i];
    let x, rad, cor, vis;
    if (p.nucleo) {
      const s = (p.fase + e.t * 0.22) % 1;
      x = xDoNucleo(s); rad = raioNucleo(x, p.rr); cor = corNucleo(x); vis = e.nucleo;
      if (x < -0.05 && x > -0.5) cor = cor.map(v => v * (0.4 + 0.8 * e.fogo));
    } else {
      const s = (p.fase + e.t * 0.3) % 1;
      x = 3.6 - s * 7.8; rad = raioBypass(x, p.rr); cor = [0.2, 0.62, 1.0]; vis = e.bypass;
    }
    if (x < e.ate || vis < 0.02) { P[i * 3] = 0; P[i * 3 + 1] = 1e4; P[i * 3 + 2] = 0; continue; }
    const ang = p.ang + (x < 1.65 ? 0.15 * (1.65 - x) : 0);  // o ar gira um pouco depois do fan
    P[i * 3] = x; P[i * 3 + 1] = Math.cos(ang) * rad; P[i * 3 + 2] = Math.sin(ang) * rad;
    C[i * 3] = cor[0] * vis; C[i * 3 + 1] = cor[1] * vis; C[i * 3 + 2] = cor[2] * vis;
  }
  S.pontos.geometry.attributes.position.needsUpdate = true;
  S.pontos.geometry.attributes.color.needsUpdate = true;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
