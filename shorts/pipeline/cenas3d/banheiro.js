// Descarga do vaso sanitário em corte (raio-x): a caixa despeja a água na bacia, a água passa por cima da curva do
// sifão, o sifão puxa a bacia inteira para o esgoto, o ar entra (o "gorgolejo") e a caixa enche de novo, deixando o
// selo d'água. Coordenadas em metros; o vaso fica na origem, com o sifão no plano x-y (visto de lado, de +z).
// Estado vindo do Python: cam, alvo, fov, t, raiox 0..1, caixa 0..1 (nível na caixa), bacia (altura da água, m),
// alavanca 0..1, flapper 0..1 (aberto), fluxoCaixa 0..1 (água da caixa para a bacia), fluxoSifao 0..1, sifao 0..1
// (quanto do cano está cheio), bolhas 0..1.

const SIFAO = [  // da saída no fundo da bacia, sobe por trás até a curva e desce até o ralo no piso
  [0.02, 0.19, 0], [-0.07, 0.17, 0], [-0.11, 0.24, 0], [-0.13, 0.33, 0], [-0.17, 0.37, 0], [-0.21, 0.32, 0],
  [-0.22, 0.2, 0], [-0.21, 0.08, 0], [-0.2, -0.04, 0]];

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.near = 0.02; camera.far = 50; camera.updateProjectionMatrix();
  r.toneMappingExposure = 1.05;
  const S = {T};
  cena.background = new T.Color(0xdfe6ec);
  cena.add(new T.HemisphereLight(0xffffff, 0xb8c2cc, 1.6));
  const luz = new T.DirectionalLight(0xffffff, 2.2); luz.position.set(2, 3, 2.5); cena.add(luz);
  const luz2 = new T.DirectionalLight(0xdfe9ff, 0.8); luz2.position.set(-2, 1.5, 1); cena.add(luz2);
  // piso de ladrilhos e parede
  const lad = document.createElement('canvas'); lad.width = lad.height = 256;
  const lc = lad.getContext('2d'); lc.fillStyle = '#c9d3dc'; lc.fillRect(0, 0, 256, 256);
  lc.fillStyle = '#f2f5f8'; for (const [x, y] of [[4, 4], [132, 4], [4, 132], [132, 132]]) lc.fillRect(x, y, 120, 120);
  const texP = new T.CanvasTexture(lad); texP.wrapS = texP.wrapT = T.RepeatWrapping; texP.repeat.set(12, 12);
  const piso = new T.Mesh(new T.PlaneGeometry(6, 6), new T.MeshStandardMaterial({map: texP, roughness: 0.4}));
  piso.rotation.x = -Math.PI / 2; cena.add(piso);
  const texW = texP.clone(); texW.needsUpdate = true; texW.repeat.set(12, 6);
  const parede = new T.Mesh(new T.PlaneGeometry(6, 3), new T.MeshStandardMaterial({map: texW, roughness: 0.5, color: 0xe8f0f6}));
  parede.position.set(0, 1.5, -0.42); cena.add(parede);

  // ---------- vaso: louça translúcida no raio-x ----------
  S.louca = new T.MeshStandardMaterial({color: 0xf8f8f6, roughness: 0.18, metalness: 0.05, transparent: true, opacity: 1,
                                        side: T.DoubleSide});
  const perfil = [];   // bacia (torno): raio x altura
  for (const [rr, y] of [[0.02, 0.18], [0.07, 0.19], [0.12, 0.24], [0.16, 0.31], [0.19, 0.37], [0.2, 0.4], [0.205, 0.42]])
    perfil.push(new T.Vector2(rr, y));
  const bacia = new T.Mesh(new T.LatheGeometry(perfil, 48), S.louca); bacia.scale.set(1.15, 1, 0.85); bacia.position.x = 0.04;
  cena.add(bacia);
  const aro = new T.Mesh(new T.TorusGeometry(0.205, 0.025, 12, 48), S.louca); aro.rotation.x = Math.PI / 2;
  aro.scale.set(1.15, 0.85, 1); aro.position.set(0.04, 0.42, 0); cena.add(aro);
  const pe = new T.Mesh(new T.CylinderGeometry(0.11, 0.14, 0.2, 32), S.louca); pe.scale.z = 0.8; pe.position.set(-0.04, 0.1, 0);
  cena.add(pe);
  // caixa acoplada
  const caixa = new T.Mesh(new T.BoxGeometry(0.2, 0.36, 0.42), S.louca); caixa.position.set(-0.3, 0.62, 0); cena.add(caixa);
  const tampa = new T.Mesh(new T.BoxGeometry(0.22, 0.03, 0.44), S.louca); tampa.position.set(-0.3, 0.815, 0); cena.add(tampa);
  S.alavanca = new T.Group(); S.alavanca.position.set(-0.19, 0.74, 0.16); cena.add(S.alavanca);
  const cabo = new T.Mesh(new T.BoxGeometry(0.07, 0.015, 0.02), new T.MeshStandardMaterial({color: 0xc0c6cc, metalness: 0.9, roughness: 0.2}));
  cabo.position.x = 0.03; S.alavanca.add(cabo);
  // água
  S.aguaMat = new T.MeshStandardMaterial({color: 0x4aa8e8, transparent: true, opacity: 0.8, roughness: 0.1, metalness: 0.1});
  S.aguaCaixa = new T.Mesh(new T.BoxGeometry(0.18, 1, 0.4), S.aguaMat); cena.add(S.aguaCaixa);
  S.aguaBacia = new T.Mesh(new T.CircleGeometry(1, 40), S.aguaMat); S.aguaBacia.rotation.x = -Math.PI / 2; cena.add(S.aguaBacia);
  S.aguaBaciaCorpo = new T.Mesh(new T.SphereGeometry(1, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), S.aguaMat);
  cena.add(S.aguaBaciaCorpo);
  // válvula (flapper) no fundo da caixa
  S.flapper = new T.Group(); S.flapper.position.set(-0.24, 0.45, 0); cena.add(S.flapper);
  const fl = new T.Mesh(new T.CylinderGeometry(0.035, 0.035, 0.012, 24), new T.MeshStandardMaterial({color: 0xd23a3a, roughness: 0.6}));
  fl.position.x = -0.035; S.flapper.add(fl);
  // sifão
  const curva = new T.CatmullRomCurve3(SIFAO.map(p => new T.Vector3(...p)));
  S.curva = curva;
  S.canoMat = new T.MeshStandardMaterial({color: 0xf0f0ee, transparent: true, opacity: 0.0, roughness: 0.2, depthWrite: false});
  cena.add(new T.Mesh(new T.TubeGeometry(curva, 120, 0.032, 16), S.canoMat));
  S.aguaSifao = new T.Mesh(new T.TubeGeometry(curva, 120, 0.026, 12), S.aguaMat); cena.add(S.aguaSifao);
  S.nIdx = S.aguaSifao.geometry.index.count;
  // partículas de água (correnteza) e bolhas
  const n = 90; S.n = n;
  S.gotas = new T.InstancedMesh(new T.SphereGeometry(0.009, 8, 6), new T.MeshBasicMaterial({color: 0xd8f0ff}), n);
  S.gotas.frustumCulled = false; cena.add(S.gotas);
  S.bolhas = new T.InstancedMesh(new T.SphereGeometry(0.012, 8, 6), new T.MeshBasicMaterial({color: 0xffffff, transparent: true, opacity: 0.85}), 30);
  S.bolhas.frustumCulled = false; cena.add(S.bolhas);
  S.m4 = new T.Matrix4(); S.q = new T.Quaternion(); S.v = new T.Vector3(); S.e = new T.Vector3();
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam, T = S.T;
  S.louca.opacity = 1 - 0.72 * e.raiox; S.louca.depthWrite = e.raiox < 0.05;
  S.canoMat.opacity = 0.35 * e.raiox;
  S.alavanca.rotation.z = -0.5 * e.alavanca;
  S.flapper.rotation.z = 1.1 * e.flapper;
  const hc = Math.max(0.002, 0.3 * e.caixa);
  S.aguaCaixa.scale.y = hc; S.aguaCaixa.position.set(-0.3, 0.455 + hc / 2, 0);
  // água da bacia: superfície elíptica cujo raio acompanha o perfil da louça na altura do nível
  const y = e.bacia, rr = Math.max(0.02, Math.min(0.2, 0.02 + (y - 0.18) * 0.85));
  S.aguaBacia.position.set(0.04, y, 0); S.aguaBacia.scale.set(rr * 1.15, rr * 0.85, 1);
  S.aguaBaciaCorpo.position.set(0.04, y, 0); S.aguaBaciaCorpo.scale.set(rr * 1.15, Math.max(0.001, y - 0.18), rr * 0.85);
  S.aguaBacia.visible = S.aguaBaciaCorpo.visible = y > 0.185;
  S.aguaSifao.geometry.setDrawRange(0, Math.floor(e.sifao * S.nIdx / 3) * 3);
  // gotas: da caixa pelo canal até a borda e caindo na bacia; e pelo sifão até o ralo
  for (let i = 0; i < S.n; i++) {
    const f = ((e.t * 1.6) + i / S.n) % 1;
    let vis = false;
    if (i % 2 === 0 && e.fluxoCaixa > 0.05) {
      const a = (i * 2.4) % (Math.PI * 2);
      if (f < 0.4) S.v.set(-0.24 + f * 0.6, 0.45 - f * 0.05, Math.sin(a) * 0.05);
      else { const k = (f - 0.4) / 0.6; S.v.set(0.04 + Math.cos(a) * 0.2 * (1 - k * 0.5) * 1.15, 0.42 - k * 0.18, Math.sin(a) * 0.17 * (1 - k * 0.5)); }
      vis = true;
    } else if (i % 2 === 1 && e.fluxoSifao > 0.05) {
      S.curva.getPoint(f, S.v); vis = true;
    }
    const s = vis ? 1 : 0.0001;
    S.e.set(s, s, s); S.m4.compose(S.v, S.q, S.e); S.gotas.setMatrixAt(i, S.m4);
  }
  S.gotas.instanceMatrix.needsUpdate = true;
  for (let i = 0; i < 30; i++) {
    const f = ((e.t * 0.9) + i / 30) % 1;
    S.curva.getPoint(0.15 + 0.5 * f, S.v); S.v.y += 0.01 * Math.sin(i * 7 + e.t * 10);
    const s = e.bolhas > 0.05 ? e.bolhas : 0.0001;
    S.e.set(s, s, s); S.m4.compose(S.v, S.q, S.e); S.bolhas.setMatrixAt(i, S.m4);
  }
  S.bolhas.instanceMatrix.needsUpdate = true;
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
