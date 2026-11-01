// Foguete: lançamento na base (fumaça, chama, curva de gravidade) e, no espaço, a Terra com as trajetórias do
// "canhão de Newton" (subir e cair; ir de lado devagar e cair longe; ir de lado a 7,8 km/s = órbita).
// Estado do Python: fase (0 solo, 1 espaço), cam, alvo, fov, t, sobe (altura do foguete no solo, m),
// incl (inclinação, rad), chama 0..1, ignicao (s desde a ignição; <0 antes), tr [f0, f1, f2, f3] (fração desenhada de
// cada trajetória: subir-e-cair, lenta, média, órbita), marca (índice da trajetória com o foguetinho na ponta, -1 nenhum),
// giro (rad, rotação da Terra).
import * as A from 'http://cena.local/ambiente.js';

const R = 60, RO = 69, GM = 69;  // raio da Terra, raio da órbita (exagerado para aparecer), GM (v circular = 1 em RO)

function foguete(T, escala = 1) {
  const g = new T.Group();
  const branco = new T.MeshStandardMaterial({color: 0xf2f4f7, metalness: 0.3, roughness: 0.35});
  const preto = new T.MeshStandardMaterial({color: 0x1d2128, metalness: 0.4, roughness: 0.4});
  const azul = new T.MeshStandardMaterial({color: 0x2f8fe0, metalness: 0.3, roughness: 0.35});
  const add = (geo, mat, y) => { const m = new T.Mesh(geo, mat); m.position.y = y; g.add(m); return m; };
  add(new T.CylinderGeometry(1.8, 1.8, 22, 32), branco, 11);            // 1º estágio
  add(new T.CylinderGeometry(1.82, 1.82, 1.2, 32), preto, 22.6);         // interestágio
  add(new T.CylinderGeometry(1.8, 1.8, 7, 32), branco, 26.7);            // 2º estágio
  add(new T.CylinderGeometry(1.83, 1.83, 1.5, 32), azul, 6);             // faixa azul
  const ogiva = new T.LatheGeometry([[0, 4.8], [0.6, 4.5], [1.2, 3.6], [1.6, 2.2], [1.85, 0.6], [1.85, 0]]
    .map(([a, b]) => new T.Vector2(a, b)), 32);
  add(ogiva, branco, 30.2);
  for (let k = 0; k < 4; k++) {  // aletas
    const a = new T.Mesh(new T.BoxGeometry(0.2, 3.5, 2.2), preto);
    const ang = k * Math.PI / 2;
    a.position.set(Math.cos(ang) * 2.4, 1.8, Math.sin(ang) * 2.4);
    a.rotation.y = -ang;
    g.add(a);
  }
  for (let k = 0; k < 3; k++) {  // bocais dos motores
    const b = new T.Mesh(new T.CylinderGeometry(0.45, 0.75, 1.2, 16, 1, true), preto);
    const ang = k * Math.PI * 2 / 3;
    b.position.set(Math.cos(ang) * 0.8, -0.5, Math.sin(ang) * 0.8);
    g.add(b);
  }
  g.scale.setScalar(escala);
  return g;
}

function chama(T) {
  const g = new T.Group();
  const fora = new T.Mesh(new T.ConeGeometry(1.9, 12, 24, 1, true),
    new T.MeshBasicMaterial({color: 0xff8a2a, transparent: true, opacity: 0.85, blending: T.AdditiveBlending,
                             depthWrite: false, side: T.DoubleSide}));
  fora.rotation.x = Math.PI; fora.position.y = -7;
  const dentro = new T.Mesh(new T.ConeGeometry(1.0, 7, 24, 1, true),
    new T.MeshBasicMaterial({color: 0xfff1c0, transparent: true, opacity: 0.95, blending: T.AdditiveBlending,
                             depthWrite: false, side: T.DoubleSide}));
  dentro.rotation.x = Math.PI; dentro.position.y = -4.5;
  g.add(fora); g.add(dentro);
  return g;
}

function terraTextura(T) {
  const c = document.createElement('canvas'); c.width = 1024; c.height = 512;
  const x = c.getContext('2d');
  x.fillStyle = '#1d5fa8'; x.fillRect(0, 0, 1024, 512);
  A.reiniciar(21);
  for (let i = 0; i < 26; i++) {  // continentes: manchas
    const cx = A.aleat() * 1024, cy = 90 + A.aleat() * 330, r = 30 + A.aleat() * 90;
    x.fillStyle = ['#3f8a46', '#5b9a4a', '#a58a5a'][i % 3];
    x.beginPath();
    for (let k = 0; k <= 24; k++) {
      const a = k / 24 * Math.PI * 2, rr = r * (0.7 + 0.35 * Math.sin(a * 3 + i) + 0.15 * A.aleat());
      x.lineTo(cx + Math.cos(a) * rr * 1.4, cy + Math.sin(a) * rr);
    }
    x.fill();
  }
  x.fillStyle = 'rgba(255,255,255,0.55)';  // nuvens em faixas
  for (let i = 0; i < 70; i++) {
    const cx = A.aleat() * 1024, cy = A.aleat() * 512;
    x.beginPath(); x.ellipse(cx, cy, 30 + A.aleat() * 60, 6 + A.aleat() * 8, 0, 0, Math.PI * 2); x.fill();
  }
  x.fillStyle = '#eef3f7'; x.fillRect(0, 0, 1024, 26); x.fillRect(0, 486, 1024, 26);  // polos
  return new T.CanvasTexture(c);
}

function trajeto(vx, vy, x0, y0, maxPassos = 30000) {
  // integração (Verlet) no plano: devolve pontos até tocar o chão ou fechar uma volta
  const pts = [];
  let x = x0, y = y0, ux = vx, uy = vy, ang0 = Math.atan2(y0, x0), giro = 0, prev = ang0;
  const dt = 0.05;
  for (let i = 0; i < maxPassos; i++) {
    pts.push([x, y]);
    const r = Math.hypot(x, y), a = -GM / (r * r * r);
    ux += a * x * dt; uy += a * y * dt;
    x += ux * dt; y += uy * dt;
    const ang = Math.atan2(y, x);
    let d = ang - prev; if (d > Math.PI) d -= 2 * Math.PI; if (d < -Math.PI) d += 2 * Math.PI;
    giro += d; prev = ang;
    if (Math.hypot(x, y) < R) { pts.push([x * R / Math.hypot(x, y), y * R / Math.hypot(x, y)]); break; }
    if (Math.abs(giro) > Math.PI * 2) break;
  }
  return pts;
}

window.montar = (THREE, cena, camera, r) => {
  const T = THREE;
  camera.far = 3000; camera.updateProjectionMatrix();
  const S = {T};
  // ---------- solo ----------
  A.reiniciar(3);
  S.solo = new T.Group(); cena.add(S.solo);
  const amb = A.ceu(T, cena, {sol: [0.6, 0.35, 0.7], neblina: 0xcfe0ee, perto: 200, longe: 900});
  S.ceu = amb.ceu; S.neblina = cena.fog;
  const nuv = A.nuvens(T, cena, {n: 18, y: [120, 200], x: [-600, 600], z: [-600, -200], tam: [12, 24]});
  S.nuvensSolo = nuv;
  const chao = A.grama(T, cena, {cor: 0x6f8f4a});
  S.chao = chao;
  A.morros(T, S.solo, {n: 16, dist: 500});  // no grupo do solo: somem no espaço
  const concreto = new T.MeshStandardMaterial({color: 0x9aa0a8, roughness: 0.95});
  const base = new T.Mesh(new T.CylinderGeometry(16, 18, 2, 48), concreto); base.position.y = 1; S.solo.add(base);
  const vermelho = new T.MeshStandardMaterial({color: 0xb23a2f, roughness: 0.6, metalness: 0.4});
  for (let i = 0; i < 12; i++) {  // torre de serviço em treliça
    const y = 2 + i * 3;
    for (const [dx, dz] of [[-2, -2], [2, -2], [-2, 2], [2, 2]]) {
      const p = new T.Mesh(new T.BoxGeometry(0.35, 3, 0.35), vermelho); p.position.set(-7 + dx, y + 1.5, dz); S.solo.add(p);
    }
    const h = new T.Mesh(new T.BoxGeometry(4.4, 0.3, 4.4), vermelho); h.position.set(-7, y, 0); S.solo.add(h);
  }
  S.fog = foguete(T); S.fog.position.y = 2.6; cena.add(S.fog);
  S.chama = chama(T); S.fog.add(S.chama);
  S.luzChama = new T.PointLight(0xff9a40, 0, 80, 1.6); S.luzChama.position.y = -3; S.fog.add(S.luzChama);
  // fumaça: esferas que nascem no bocal e crescem
  S.fumaca = [];
  const bola = new T.SphereGeometry(1, 12, 8);
  for (let i = 0; i < 140; i++) {
    const m = new T.Mesh(bola, new T.MeshStandardMaterial({color: 0xeeeeee, roughness: 1, transparent: true, opacity: 0,
                                                           depthWrite: false}));
    m.userData = {nasce: i * 0.045, dir: A.aleat() * Math.PI * 2, vel: 3 + A.aleat() * 6, jit: A.aleat()};
    S.solo.add(m); S.fumaca.push(m);
  }
  // ---------- espaço ----------
  S.espaco = new T.Group(); S.espaco.visible = false; cena.add(S.espaco);
  const est = new T.BufferGeometry(), pe = [];
  for (let i = 0; i < 1500; i++) {
    const a = A.aleat() * Math.PI * 2, b = Math.acos(2 * A.aleat() - 1), d = 1500;
    pe.push(d * Math.sin(b) * Math.cos(a), d * Math.cos(b), d * Math.sin(b) * Math.sin(a));
  }
  est.setAttribute('position', new T.Float32BufferAttribute(pe, 3));
  S.espaco.add(new T.Points(est, new T.PointsMaterial({color: 0xffffff, size: 2.2, sizeAttenuation: false, fog: false})));
  S.terra = new T.Mesh(new T.SphereGeometry(R, 64, 48), new T.MeshStandardMaterial({map: terraTextura(T), roughness: 0.9}));
  S.espaco.add(S.terra);
  const atm = new T.Mesh(new T.SphereGeometry(R * 1.06, 64, 48), new T.ShaderMaterial({
    transparent: true, side: T.BackSide, depthWrite: false, blending: T.AdditiveBlending,
    vertexShader: 'varying vec3 n; void main(){ n = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: 'varying vec3 n; void main(){ float i = pow(0.75 - dot(n, vec3(0,0,1.0)), 3.0); gl_FragColor = vec4(0.35,0.65,1.0,1.0) * i; }'}));
  S.espaco.add(atm);
  S.solEsp = new T.DirectionalLight(0xffffff, 2.6); S.solEsp.position.set(150, 80, 200); S.espaco.add(S.solEsp);
  S.espaco.add(new T.AmbientLight(0x3a4a6a, 0.6));
  // trajetórias no plano z = 0: subir e cair (do chão), e três "canhões" do alto (lento, médio, órbita)
  const defs = [[0, 0.62, 0, R, 0xff5a5a], [0.62, 0, 0, RO, 0xffd23f], [0.82, 0, 0, RO, 0xffa040],
                [1.0, 0, 0, RO, 0x3ee8ff]];
  S.trs = defs.map(([vx, vy, x0, y0, cor]) => {
    const pts = trajeto(-vx, vy, x0, y0).map(([x, y]) => new T.Vector3(x, y, 0));
    const geo = new T.BufferGeometry().setFromPoints(pts);
    const lin = new T.Line(geo, new T.LineBasicMaterial({color: cor, linewidth: 2, transparent: true}));
    // linha grossa: um tubo fino segue a linha
    const tubo = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts.filter((_, i) => i % 6 === 0).concat([pts[pts.length - 1]])),
                                               400, 0.55, 8, false),
                            new T.MeshBasicMaterial({color: cor}));
    S.espaco.add(tubo);
    return {pts, tubo, n: tubo.geometry.index.count};
  });
  S.mini = foguete(T, 0.22); S.espaco.add(S.mini);
  S.amb = cena;
  window._S = S; window._cam = camera;
};

window.posar = (e) => {
  const S = window._S, cam = window._cam, T = S.T;
  const solo = e.fase < 0.5;
  S.solo.visible = solo; S.chao.visible = solo; S.ceu.visible = solo;
  S.nuvensSolo.forEach(n => n.visible = solo);
  S.espaco.visible = !solo;
  S.amb.fog = solo ? S.neblina : null;
  S.amb.background = solo ? null : new T.Color(0x02030a);
  if (solo) {
    S.fog.visible = true;
    S.fog.position.set(Math.sin(e.incl) * Math.max(0, e.sobe - 60) * 0.5, 2.6 + e.sobe, 0);
    S.fog.rotation.z = -e.incl;
    const f = 0.85 + 0.15 * Math.sin(e.t * 47) + 0.1 * Math.sin(e.t * 23);
    S.chama.visible = e.chama > 0.01;
    S.chama.scale.set(e.chama * f, e.chama * (0.8 + 0.4 * f), e.chama * f);
    S.luzChama.intensity = 120 * e.chama;
    for (const m of S.fumaca) {
      const u = m.userData, idade = e.ignicao - u.nasce;
      if (idade < 0 || e.ignicao < 0) { m.visible = false; continue; }
      m.visible = true;
      const k = Math.min(1, idade / 3.5);
      const raio = 1.2 + 4.5 * Math.pow(k, 0.6);
      const rodar = u.nasce < 2.5;  // a fumaça do começo espalha pelo chão
      const desloc = rodar ? u.vel * idade * (1 - k * 0.5) : idade * 2;
      const y0 = rodar ? 3 + raio * 0.5 : Math.max(3, 2.6 + (0.5 * 12 * u.nasce * u.nasce) - 2);
      m.position.set(Math.cos(u.dir) * desloc, y0 + idade * 1.5, Math.sin(u.dir) * desloc);
      m.scale.setScalar(raio);
      m.material.opacity = 0.7 * (1 - Math.pow(k, 2)) * Math.min(1, idade * 4);
      m.material.color.setScalar(0.85 + 0.15 * u.jit);
    }
  } else {
    S.fog.visible = false;
    S.terra.rotation.y = e.giro;
    S.trs.forEach((tr, i) => {
      const f = e.tr[i];
      tr.tubo.visible = f > 0.002;
      tr.tubo.geometry.setDrawRange(0, Math.floor(tr.n * f / 3) * 3);
    });
    if (e.marca >= 0) {
      const tr = S.trs[e.marca], f = e.pos >= 0 ? e.pos : e.tr[e.marca];
      const i = Math.min(tr.pts.length - 1, Math.floor((tr.pts.length - 1) * f));
      const p = tr.pts[i], q = tr.pts[Math.min(tr.pts.length - 1, i + 1)];
      S.mini.visible = true;
      S.mini.position.copy(p);
      const ang = Math.atan2(q.y - p.y, q.x - p.x);
      S.mini.rotation.set(0, 0, ang - Math.PI / 2);
    } else {
      S.mini.visible = false;
    }
  }
  cam.fov = e.fov; cam.updateProjectionMatrix();
  cam.position.set(...e.cam); cam.lookAt(...e.alvo);
};
