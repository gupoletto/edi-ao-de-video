// Peças de cenário reaproveitáveis nas cenas 3D (importe com: import * as A from 'http://cena.local/ambiente.js').
// Tudo procedural: céu em gradiente com sol, nuvens de esferas, chão de grama, estrada, árvores, morros.

let semente = 11;
export const aleat = () => { semente = (semente * 16807) % 2147483647; return semente / 2147483647; };
export const reiniciar = (s) => { semente = s; };

export function ceu(T, cena, {sol = [0.55, 0.35, -0.75], topo = [0.10, 0.32, 0.72], meio = [0.42, 0.66, 0.93],
                              baixo = [0.82, 0.90, 0.98], neblina = 0xbfd8f2, perto = 120, longe = 700} = {}) {
  const s = new T.Vector3(...sol).normalize();
  const m = new T.Mesh(new T.SphereGeometry(900, 48, 24), new T.ShaderMaterial({
    side: T.BackSide, depthWrite: false, fog: false,
    uniforms: {sol: {value: s}, topo: {value: new T.Vector3(...topo)}, meio: {value: new T.Vector3(...meio)},
               baixo: {value: new T.Vector3(...baixo)}},
    vertexShader: 'varying vec3 v; void main(){ v = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `varying vec3 v; uniform vec3 sol, topo, meio, baixo;
      void main(){
        float h = clamp(v.y * 0.5 + 0.5, 0.0, 1.0);
        vec3 c = h > 0.5 ? mix(meio, topo, (h - 0.5) * 2.0) : mix(baixo, meio, h * 2.0);
        float d = max(dot(normalize(v), sol), 0.0);
        c += vec3(1.0, 0.92, 0.75) * (pow(d, 600.0) * 3.0 + pow(d, 12.0) * 0.25);
        gl_FragColor = vec4(c, 1.0);
      }`}));
  cena.add(m);
  cena.fog = new T.Fog(neblina, perto, longe);
  cena.add(new T.HemisphereLight(0xdfeaff, 0x7d8f6a, 1.5));
  const luz = new T.DirectionalLight(0xfff3dd, 3.2);
  luz.position.copy(s.clone().multiplyScalar(100));
  cena.add(luz);
  const preenche = new T.DirectionalLight(0xbfd6ff, 0.9);
  preenche.position.set(-s.x * 60, 30, -s.z * 60);
  cena.add(preenche);
  return {ceu: m, luz};
}

export function nuvem(T, cena, x, y, z, tam, mat) {
  const bola = new T.SphereGeometry(1, 16, 12);
  const g = new T.Group();
  const n = 7 + Math.floor(aleat() * 6);
  for (let i = 0; i < n; i++) {
    const m = new T.Mesh(bola, mat);
    const rr = tam * (0.45 + aleat() * 0.55);
    m.scale.set(rr * 1.3, rr * 0.8, rr);
    m.position.set((aleat() - 0.5) * tam * 3.2, (aleat() - 0.2) * tam * 0.7, (aleat() - 0.5) * tam * 1.8);
    g.add(m);
  }
  g.position.set(x, y, z);
  cena.add(g);
  return g;
}

export function nuvens(T, cena, {n = 20, y = [40, 70], x = [-400, 400], z = [-400, -150], tam = [8, 16]} = {}) {
  const mat = new T.MeshStandardMaterial({color: 0xffffff, roughness: 1, emissive: 0x9fb4c8, emissiveIntensity: 0.3});
  const lista = [];
  for (let i = 0; i < n; i++) {
    lista.push(nuvem(T, cena, x[0] + aleat() * (x[1] - x[0]), y[0] + aleat() * (y[1] - y[0]),
                     z[0] + aleat() * (z[1] - z[0]), tam[0] + aleat() * (tam[1] - tam[0]), mat));
  }
  return lista;
}

export function grama(T, cena, {tam = 1200, cor = 0x5f8f3a, y = 0} = {}) {
  // chão com variação de cor por vértice (manchas), para não ficar chapado
  const g = new T.PlaneGeometry(tam, tam, 120, 120);
  g.rotateX(-Math.PI / 2);
  const c = new T.Color(cor), cores = [];
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), z = p.getZ(i);
    const k = 0.85 + 0.15 * Math.sin(x * 0.07) * Math.cos(z * 0.05) + 0.08 * (aleat() - 0.5);
    cores.push(c.r * k, c.g * k, c.b * k);
  }
  g.setAttribute('color', new T.Float32BufferAttribute(cores, 3));
  const m = new T.Mesh(g, new T.MeshStandardMaterial({vertexColors: true, roughness: 1}));
  m.position.y = y;
  cena.add(m);
  return m;
}

export function estrada(T, cena, {comp = 1200, larg = 7, y = 0.01} = {}) {
  // ao longo de x; faixa central tracejada e linhas brancas laterais
  const asfalto = new T.Mesh(new T.PlaneGeometry(comp, larg), new T.MeshStandardMaterial({color: 0x34373d, roughness: 0.9}));
  asfalto.rotation.x = -Math.PI / 2; asfalto.position.y = y; cena.add(asfalto);
  const branco = new T.MeshStandardMaterial({color: 0xf2f2ea, roughness: 0.6});
  const amarelo = new T.MeshStandardMaterial({color: 0xf2c230, roughness: 0.6});
  for (const z of [-larg / 2 + 0.25, larg / 2 - 0.25]) {
    const l = new T.Mesh(new T.PlaneGeometry(comp, 0.15), branco);
    l.rotation.x = -Math.PI / 2; l.position.set(0, y + 0.005, z); cena.add(l);
  }
  for (let x = -comp / 2; x < comp / 2; x += 6) {
    const t = new T.Mesh(new T.PlaneGeometry(3, 0.15), amarelo);
    t.rotation.x = -Math.PI / 2; t.position.set(x, y + 0.005, 0); cena.add(t);
  }
  return asfalto;
}

export function arvore(T, cena, x, z, {altura = 6, copa = 2.6, tronco = 0.35, cor = 0x3f7a2e} = {}) {
  // tronco com casca irregular + copa de esferas; devolve {grupo, copa} para animar (balançar)
  const g = new T.Group();
  const tg = new T.CylinderGeometry(tronco * 0.8, tronco * 1.15, altura * 0.55, 14, 8);
  const p = tg.attributes.position;
  for (let i = 0; i < p.count; i++) {  // casca: pequenas irregularidades
    const k = 1 + 0.08 * Math.sin(p.getY(i) * 9 + Math.atan2(p.getZ(i), p.getX(i)) * 5);
    p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k);
  }
  tg.computeVertexNormals();
  const t = new T.Mesh(tg, new T.MeshStandardMaterial({color: 0x6b4a32, roughness: 0.95}));
  t.position.y = altura * 0.275; g.add(t);
  const copaG = new T.Group(); copaG.position.y = altura * 0.62;
  const folha = new T.MeshStandardMaterial({color: cor, roughness: 0.9, flatShading: true});
  const bola = new T.IcosahedronGeometry(1, 1);
  for (let i = 0; i < 9; i++) {
    const m = new T.Mesh(bola, folha);
    const r = copa * (0.45 + aleat() * 0.35);
    m.scale.setScalar(r);
    m.position.set((aleat() - 0.5) * copa * 1.3, (aleat() - 0.2) * copa * 0.9, (aleat() - 0.5) * copa * 1.3);
    copaG.add(m);
  }
  g.add(copaG);
  g.position.set(x, 0, z);
  cena.add(g);
  return {grupo: g, copa: copaG, tronco: t};
}

export function morros(T, cena, {n = 14, dist = 380, cor = 0x7fa86a} = {}) {
  const mat = new T.MeshStandardMaterial({color: cor, roughness: 1, flatShading: true});
  for (let i = 0; i < n; i++) {
    const a = -Math.PI * 0.95 + aleat() * Math.PI * 0.9;
    const r = 60 + aleat() * 70;
    const m = new T.Mesh(new T.SphereGeometry(1, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2), mat);
    m.scale.set(r, 20 + aleat() * 40, r * 0.7);
    m.position.set(Math.cos(a) * dist, 0, Math.sin(a) * dist);
    cena.add(m);
  }
}
