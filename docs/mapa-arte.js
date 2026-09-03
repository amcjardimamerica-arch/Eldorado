/* Arte do «Mappa das Oportunidades» — gravura renascentista a traço.
   Tudo é desenhado em SVG puro sobre fundo transparente. Convenções:
   tinta #3B2A14 · ouro #B8912E · sombra por hachura · traço fino variável.
   Cada função devolve um <g> posicionado (x,y) e escalado (s). */
window.MAPA_ARTE = (function () {
  const INK = "#3B2A14", GOLD = "#B8912E", GOLD2 = "#E2C36E", SEA = "#4E6E8E";
  const g = (x, y, s, inner, cls = "") =>
    `<g class="arte ${cls}" transform="translate(${x},${y}) scale(${s})" pointer-events="none">${inner}</g>`;
  const hatch = (d, n = 4, dx = 2.2) => // hachura paralela dentro de uma forma (clip)
    `<g stroke="${INK}" stroke-width=".45" opacity=".55">${[...Array(n)].map((_, i) => `<path d="${d}" transform="translate(${i * dx},0)"/>`).join("")}</g>`;

  /* ---------- cartela em fita (título) ---------- */
  function fita(texto, sub) {
    return `<g class="arte fita" pointer-events="none">
      <path d="M40 26 C60 14 120 10 190 12 C260 14 310 8 350 14 C380 18 400 30 396 42 C392 54 372 58 350 56 C300 52 260 60 190 58 C120 56 60 58 40 46 C28 40 28 33 40 26 Z"
            fill="#FBF3E3" stroke="${INK}" stroke-width="1.1"/>
      <path d="M40 26 C60 14 120 10 190 12 C260 14 310 8 350 14 C380 18 400 30 396 42" fill="none" stroke="${INK}" stroke-width=".4" transform="translate(0,3)" opacity=".7"/>
      <path d="M40 46 C30 50 22 58 26 66 C36 60 44 56 48 52 Z M396 42 C404 46 412 52 408 62 C398 56 392 52 388 50 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/>
      <path d="M52 20 q-6 8 0 16 M384 22 q6 8 0 16" fill="none" stroke="${INK}" stroke-width=".6"/>
      <text x="218" y="33" text-anchor="middle" font-family="Georgia,'Times New Roman',serif" font-size="14" font-weight="700" letter-spacing="3" fill="${INK}">${texto}</text>
      <text x="218" y="47" text-anchor="middle" font-family="Georgia,serif" font-size="8" font-style="italic" letter-spacing="1.2" fill="${GOLD}">${sub}</text>
    </g>`;
  }

  /* ---------- rosa dos ventos sem círculo ---------- */
  function rosa() {
    const pt = (r1, r2, a, fill) => { // ponta com meia-face
      const ca = Math.cos(a), sa = Math.sin(a), cb = Math.cos(a + Math.PI / 2), sb = Math.sin(a + Math.PI / 2);
      const tip = [r1 * ca, r1 * sa], base = [r2 * ca, r2 * sa], l = [r2 * ca + 6 * cb, r2 * sa + 6 * sb], r = [r2 * ca - 6 * cb, r2 * sa - 6 * sb];
      return `<path d="M0 0 L${l} L${tip} Z" fill="${fill}" stroke="${INK}" stroke-width=".55"/><path d="M0 0 L${r} L${tip} Z" fill="#FBF3E3" stroke="${INK}" stroke-width=".55"/>`;
    };
    let s = "";
    for (let i = 0; i < 16; i++) if (i % 2) s += pt(30, 10, i * Math.PI / 8 - Math.PI / 2, "#6B4E16");
    for (let i = 0; i < 8; i++) if (i % 2) s += pt(48, 14, i * Math.PI / 4 - Math.PI / 2, GOLD);
    for (let i = 0; i < 8; i++) if (!(i % 2)) s += pt(70, 16, i * Math.PI / 4 - Math.PI / 2, i === 0 ? "#8A2E2E" : INK);
    // flor-de-lis no norte e círculos finos abertos
    s += `<g transform="translate(0,-78) scale(.85)" fill="#8A2E2E" stroke="${INK}" stroke-width=".4"><path d="M0-9 C4-4 4 1 0 4 C-4 1 -4-4 0-9z"/><path d="M0 4 C5 1 10 3 11 8 C7 8 3 6 0 4z"/><path d="M0 4 C-5 1 -10 3 -11 8 C-7 8 -3 6 0 4z"/><rect x="-1.4" y="4" width="2.8" height="6"/></g>`;
    s += `<circle r="16" fill="none" stroke="${INK}" stroke-width=".45" stroke-dasharray="1 2"/><circle r="3" fill="#FBF3E3" stroke="${INK}" stroke-width=".7"/><circle r="1.1" fill="#8A2E2E"/>`;
    s += `<g font-family="Georgia,serif" font-size="9" font-weight="700" fill="${INK}" text-anchor="middle"><text y="-90">N</text><text y="86">S</text><text x="82" y="3">L</text><text x="-82" y="3">O</text></g>`;
    return s;
  }

  /* ---------- marcos geográficos (gravura) ---------- */
  const paoDeAcucar = `<path d="M-22 14 C-20 2 -12 -8 -4 -12 C4 -8 10 2 12 14 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/>
    <path d="M-14 12 C-13 4 -8 -2 -4 -5 M-8 13 C-7 6 -4 1 -1 -2 M2 13 C3 6 4 2 5 -1" fill="none" stroke="${INK}" stroke-width=".4"/>
    <path d="M12 14 C14 8 18 4 22 2 C26 4 28 9 29 14 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".8"/>
    <path d="M-30 14 h62" stroke="${INK}" stroke-width=".9"/><path d="M-4 -12 v-8 M-9 -16 h10" stroke="${INK}" stroke-width="1.1" stroke-linecap="round"/>
    <path d="M-4 -20 a1.6 1.6 0 1 1 0.01 0" fill="${INK}"/>`;
  const cataratas = `<path d="M-24 -6 h48 v3 h-48z" fill="#E9D6A8" stroke="${INK}" stroke-width=".7"/>
    <g stroke="${SEA}" stroke-width=".8" fill="none" opacity=".9">${[...Array(9)].map((_, i) => `<path d="M${-20 + i * 5} -3 C${-20 + i * 5} 4 ${-19 + i * 5} 8 ${-21 + i * 5} 14"/>`).join("")}</g>
    <path d="M-26 15 q6 -3 12 0 t12 0 t12 0 t12 0" fill="none" stroke="${SEA}" stroke-width=".7"/><path d="M-24 -6 C-20 -12 -10 -14 -4 -12 M6 -12 C12 -14 20 -12 24 -6" fill="none" stroke="${INK}" stroke-width=".6"/>`;
  const igreja = `<path d="M-14 12 v-16 h28 v16z" fill="#FBF3E3" stroke="${INK}" stroke-width=".9"/><path d="M-14 -4 L0 -14 L14 -4" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/>
    <path d="M-12 -4 v-12 h6 v12 M6 -4 v-12 h6 v12" fill="#FBF3E3" stroke="${INK}" stroke-width=".8"/><path d="M-9 -16 q0 -5 3 -6 q3 1 3 6 M6 -16 q0 -5 3 -6 q3 1 3 6" fill="none" stroke="${INK}" stroke-width=".7"/>
    <path d="M0 -22 v-6 M-2.5 -25 h5" stroke="${INK}" stroke-width=".9"/><rect x="-3" y="2" width="6" height="10" fill="${INK}" opacity=".85"/><circle cx="-8" cy="4" r="1.6" fill="none" stroke="${INK}" stroke-width=".6"/><circle cx="8" cy="4" r="1.6" fill="none" stroke="${INK}" stroke-width=".6"/>`;
  const dunas = `<path d="M-30 10 C-22 -2 -12 -4 -2 4 C6 -6 18 -6 30 8 Z" fill="#FBF3E3" stroke="${INK}" stroke-width=".8"/>
    <path d="M-26 8 C-20 2 -12 0 -4 5 M0 2 C8 -4 18 -4 26 6" fill="none" stroke="${INK}" stroke-width=".4"/><ellipse cx="-8" cy="9" rx="6" ry="1.6" fill="${SEA}" opacity=".45"/><ellipse cx="12" cy="10" rx="5" ry="1.3" fill="${SEA}" opacity=".45"/>`;
  const jacare = `<path d="M-22 4 C-16 -2 -6 -4 4 -3 C10 -3 16 -1 24 2 L20 5 C12 3 4 2 -4 4 C-10 5 -16 6 -22 4 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".8"/>
    <path d="M-14 0 l1 -3 M-8 -1 l1 -3 M-2 -2 l1 -3 M4 -2 l1 -3" stroke="${INK}" stroke-width=".7"/><circle cx="18" cy="0" r=".9" fill="${INK}"/><path d="M24 2 l-4 3" stroke="${INK}" stroke-width=".6"/>
    <path d="M-30 8 q8 -3 16 0 t16 0 t16 0 t16 0" fill="none" stroke="${SEA}" stroke-width=".6" opacity=".8"/>`;
  const araucaria = `<path d="M0 16 V-10" stroke="${INK}" stroke-width="1.2"/>
    <path d="M-16 -4 C-10 -12 -4 -14 0 -12 C4 -14 10 -12 16 -4 M-13 2 C-8 -4 -3 -6 0 -5 C3 -6 8 -4 13 2 M-9 8 C-5 3 -2 2 0 2 C2 2 5 3 9 8" fill="none" stroke="${INK}" stroke-width=".9" stroke-linecap="round"/>
    <path d="M-16 -4 q2 -3 5 -4 M16 -4 q-2 -3 -5 -4 M-13 2 q2 -2 4 -3 M13 2 q-2 -2 -4 -3" fill="none" stroke="${INK}" stroke-width=".5"/>`;
  const mata = `<path d="M0 14 V-4" stroke="${INK}" stroke-width="1"/><path d="M0 -4 C-8 -3 -13 2 -14 9 C-8 7 -3 3 0 -2 C3 3 8 7 14 9 C13 2 8 -3 0 -4z" fill="#E9D6A8" stroke="${INK}" stroke-width=".8"/>
    <path d="M0 -2 C-3 -8 -3 -12 0 -16 C3 -12 3 -8 0 -2z" fill="#E9D6A8" stroke="${INK}" stroke-width=".7"/><path d="M-3 4 C-6 1 -9 1 -12 3 M3 4 C6 1 9 1 12 3" fill="none" stroke="${INK}" stroke-width=".4"/>
    <g transform="translate(18,4)"><path d="M0 10 V-2" stroke="${INK}" stroke-width=".9"/><path d="M0 -2 C-6 -1 -9 3 -10 8 C-5 6 -2 3 0 0 C2 3 5 6 10 8 C9 3 6 -1 0 -2z" fill="#E9D6A8" stroke="${INK}" stroke-width=".7"/></g>`;
  const rioAmazonas = `<path d="M-120 -8 C-90 -14 -60 -6 -30 -10 C0 -14 30 -4 60 -8 C80 -11 96 -6 112 -2" fill="none" stroke="${SEA}" stroke-width="2.2" opacity=".55"/>
    <path d="M-120 -8 C-90 -14 -60 -6 -30 -10 C0 -14 30 -4 60 -8 C80 -11 96 -6 112 -2" fill="none" stroke="${SEA}" stroke-width=".6" opacity=".9"/>
    <path d="M-80 -9 C-72 -18 -60 -20 -50 -16 M-10 -12 C0 -22 12 -24 22 -18 M40 -7 C48 -16 60 -18 70 -14" fill="none" stroke="${SEA}" stroke-width=".5" opacity=".7"/>`;

  /* Eldorado — cidade de ouro sobre a chapada, em Goiás */
  const eldorado = `<path d="M-40 20 C-30 8 -14 4 0 6 C14 4 30 8 40 20 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/>
    ${hatch("M-36 19 C-28 11 -16 7 -4 8", 5, 4)}
    <g fill="${GOLD2}" stroke="${INK}" stroke-width=".7">
      <rect x="-22" y="-2" width="10" height="10"/><rect x="-10" y="-10" width="8" height="18"/><rect x="0" y="-6" width="9" height="14"/><rect x="11" y="-1" width="10" height="9"/>
      <path d="M-22 -2 l5 -7 5 7 M-10 -10 l4 -7 4 7 M0 -6 l4.5 -8 4.5 8 M11 -1 l5 -6 5 6"/>
      <path d="M-6 -17 v-8 M-6 -24 l5 2 -5 2" fill="${GOLD}"/></g>
    <g fill="${INK}"><rect x="-19" y="2" width="2" height="3"/><rect x="-8" y="-5" width="2" height="3"/><rect x="-8" y="1" width="2" height="3"/><rect x="3" y="-2" width="2" height="3"/><rect x="14" y="2" width="2" height="3"/></g>
    <g stroke="${GOLD}" stroke-width=".5" fill="none" opacity=".9"><path d="M-30 -14 q4 -3 8 0 M22 -16 q4 -3 8 0 M-2 -30 l2 -4 2 4 M-36 -2 l3 -1"/></g>
    <text y="27" text-anchor="middle" font-family="Georgia,serif" font-size="7.5" font-style="italic" letter-spacing="1.5" fill="${INK}">ELDORADO</text>`;

  /* Farol de Alexandria — na costa do Nordeste, sobre o mar */
  const farol = `<path d="M-30 24 q7 -3 14 0 t14 0 t14 0 t14 0" fill="none" stroke="${SEA}" stroke-width=".7"/><path d="M-26 28 q6 -2.5 12 0 t12 0 t12 0" fill="none" stroke="${SEA}" stroke-width=".5" opacity=".7"/>
    <path d="M-14 22 h28 l-2 -6 h-24z" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/>
    <path d="M-9 16 v-18 h18 v18" fill="#FBF3E3" stroke="${INK}" stroke-width=".9"/>${hatch("M-8 15 v-16", 3, 2.4)}
    <path d="M-7 -2 v-12 h14 v12" fill="#FBF3E3" stroke="${INK}" stroke-width=".8"/><path d="M-5 -14 v-10 h10 v10" fill="#FBF3E3" stroke="${INK}" stroke-width=".8"/>
    <path d="M-4 -24 L0 -34 L4 -24" fill="${GOLD2}" stroke="${INK}" stroke-width=".7"/>
    <g stroke="${GOLD}" stroke-width=".6" fill="none"><path d="M4 -28 l14 -4 M4 -26 l16 2 M-4 -28 l-14 -4 M-4 -26 l-16 2"/></g>
    <circle cx="0" cy="-27" r="1.4" fill="${GOLD}"/><text y="38" text-anchor="middle" font-family="Georgia,serif" font-size="6.5" font-style="italic" letter-spacing="1" fill="${INK}">FAROL DE ALEXANDRIA</text>`;

  /* ---------- criaturas ---------- */
  const serpente = `<path d="M-60 0 C-50 -18 -38 -18 -28 0 C-18 18 -6 18 4 0 C14 -18 26 -18 36 0 C42 10 50 12 58 6" fill="none" stroke="${INK}" stroke-width="3.6" stroke-linecap="round"/>
    <path d="M-60 0 C-50 -18 -38 -18 -28 0 C-18 18 -6 18 4 0 C14 -18 26 -18 36 0 C42 10 50 12 58 6" fill="none" stroke="#E9D6A8" stroke-width="2" stroke-linecap="round"/>
    <path d="M-52 -9 l-3 -6 M-44 -12 l0 -7 M-36 -9 l3 -6 M-20 9 l-3 6 M-12 12 l0 7 M-4 9 l3 6 M12 -9 l-3 -6 M20 -12 l0 -7 M28 -9 l3 -6" stroke="${INK}" stroke-width=".7"/>
    <path d="M58 6 C64 2 70 4 72 9 C70 12 65 13 61 11 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/><circle cx="66" cy="8" r=".9" fill="${INK}"/><path d="M72 9 l6 -2 -5 4" fill="none" stroke="${INK}" stroke-width=".7"/>
    <path d="M-60 0 l-8 -6 l3 8 l-7 4z" fill="#E9D6A8" stroke="${INK}" stroke-width=".8"/>
    <path d="M-70 16 q8 -3 16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="${SEA}" stroke-width=".6" opacity=".8"/>`;
  const iara = `<path d="M0 -4 C-3 -8 -2 -14 2 -16 C6 -14 6 -8 3 -4 Z" fill="#FBF3E3" stroke="${INK}" stroke-width=".8"/>
    <path d="M-1 -16 C-6 -14 -8 -6 -6 2 C-3 -2 -1 -6 0 -10 M3 -16 C8 -14 9 -8 7 -1 C5 -4 4 -8 3 -10" fill="none" stroke="${INK}" stroke-width=".7"/>
    <path d="M-3 -4 C-6 4 -8 10 -4 16 C2 18 8 14 14 12 C10 10 6 10 2 12 C0 6 2 0 4 -4z" fill="#E9D6A8" stroke="${INK}" stroke-width=".8"/>${hatch("M-3 6 C-4 10 -3 13 0 15", 3, 2)}
    <path d="M14 12 C20 8 24 8 28 12 C24 12 20 14 18 18 C17 15 15 13 14 12z" fill="#E9D6A8" stroke="${INK}" stroke-width=".8"/>
    <path d="M-6 0 l-8 -6 M4 -2 l8 -6" stroke="${INK}" stroke-width=".8" stroke-linecap="round"/>
    <path d="M-20 20 q6 -3 12 0 t12 0 t12 0 t12 0" fill="none" stroke="${SEA}" stroke-width=".6" opacity=".8"/>`;
  const caravela = `<path d="M-18 8 C-12 10 12 10 18 8 L14 14 H-14 Z" fill="#E9D6A8" stroke="${INK}" stroke-width=".9"/><path d="M-16 9 h32" stroke="${INK}" stroke-width=".4"/>
    <path d="M0 8 V-18 M-8 4 V-8" stroke="${INK}" stroke-width="1"/>
    <path d="M0 -17 C8 -14 11 -8 11 -1 H0 Z" fill="#FBF3E3" stroke="${INK}" stroke-width=".8"/>${hatch("M2 -12 C6 -10 8 -6 9 -2", 3, 2)}
    <path d="M-8 -7 C-3 -5 -2 -1 -2 3 H-8 Z" fill="#FBF3E3" stroke="${INK}" stroke-width=".7"/><path d="M0 -18 l6 2 -6 2" fill="#8A2E2E" stroke="${INK}" stroke-width=".4"/>
    <path d="M-26 14 q6 -3 12 0 t12 0 t12 0 t12 0" fill="none" stroke="${SEA}" stroke-width=".6" opacity=".8"/>`;

  /* ---------- montagem: posições sobre o viewBox 0 0 613 639 ---------- */
  function ilustracoes() {
    return [
      g(150, 104, 1, rioAmazonas, "rio"), g(190, 150, 1, mata),
      g(470, 128, 1, dunas), g(604, 262, 1, farol, "farol"),
      g(392, 292, .95, eldorado, "eldorado"),
      g(470, 372, .9, igreja), g(505, 448, .9, paoDeAcucar),
      g(315, 430, 1, jacare), g(330, 528, .95, cataratas), g(345, 585, 1, araucaria),
      g(560, 560, 1, serpente, "criatura"), g(610, 340, 1, iara, "criatura"),
      g(80, 500, 1, caravela), g(590, 120, .8, caravela),
    ].join("");
  }
  return { fita, rosa, ilustracoes, INK, GOLD, SEA };
})();
