// Bake the published simulator into a script-free SVG for GitHub's image renderer.
// Run: node scripts/generate_car_soccer.mjs [--source path/to/index.html]
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const REVISION = '826012a86ed75470bd702c2a6b55dcb1b46a2900';
const SOURCE_URL = `https://raw.githubusercontent.com/pedrogieler/car-soccer-autoplay/${REVISION}/index.html`;
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const option = name => args.includes(name) ? args[args.indexOf(name) + 1] : undefined;
const sourcePath = option('--source');
const output = resolve(option('--output') || resolve(ROOT, 'assets/car-soccer.svg'));
const seed = Number(option('--seed') || 20261022);
const FPS = 24;
const PHYSICS_HZ = 240;
const xml = value => String(value).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const number = value => {
  if (!Number.isFinite(value)) throw new Error(`Non-finite coordinate: ${value}`);
  return String(Number(value.toFixed(2)));
};
const decode = value => value.replace(/&(#x[\da-f]+|#\d+|quot|apos|lt|gt|amp);/gi, (_, entity) => {
  if (entity.startsWith('#x')) return String.fromCodePoint(parseInt(entity.slice(2), 16));
  if (entity.startsWith('#')) return String.fromCodePoint(Number(entity.slice(1)));
  return ({ quot: '"', apos: "'", lt: '<', gt: '>', amp: '&' })[entity.toLowerCase()];
});

let source;
if (sourcePath) source = await readFile(sourcePath, 'utf8');
else {
  const response = await fetch(SOURCE_URL);
  if (!response.ok) throw new Error(`Game source: HTTP ${response.status}`);
  source = await response.text();
}
const embedded = source.match(/<iframe\b[^>]*\bdata-srcdoc="([^"]*)"/i);
if (embedded) source = decode(embedded[1]);
const arena = source.match(/<svg\b[^>]*\bid="aq-arena"[\s\S]*?<\/svg>/i)?.[0];
let script = [...source.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]
  .find(match => match[1].includes('window.__aquadomeSoccerPreview='))?.[1];
if (!script) {
  const scriptPath = source.match(/<script\b[^>]*\bsrc=["']([^"']+)["'][^>]*><\/script>/i)?.[1];
  if (scriptPath) {
    if (sourcePath) script = await readFile(resolve(dirname(resolve(sourcePath)), scriptPath), 'utf8');
    else {
      const response = await fetch(new URL(scriptPath, SOURCE_URL));
      if (!response.ok) throw new Error(`Game script: HTTP ${response.status}`);
      script = await response.text();
    }
  }
}
if (!arena || !script) throw new Error('Published simulator markup was not found.');

// This small document adapter records the renderer's output; no browser is used.
const elements = new Map();
const element = id => {
  if (!elements.has(id)) elements.set(id, { innerHTML: '', textContent: '', hidden: false });
  return elements.get(id);
};
const root = { querySelector: selector => element(selector.slice(1)) };
const deterministicMath = Object.create(Math);
deterministicMath.random = () => seed / 4294967296;
const context = {
  document: { getElementById: id => id === 'aquadome-futebol-preview' ? root : null },
  window: {}, Math: deterministicMath, matchMedia: () => ({ matches: false }),
  requestAnimationFrame: () => {},
};
vm.runInNewContext(script, context, { timeout: 5000, filename: 'published-car-soccer.js' });
const api = context.window.__aquadomeSoccerPreview;
if (!api?.game) throw new Error('Simulation did not initialize.');
const game = api.game;
const initialAction = element('aq-action').innerHTML;
const ballStart = initialAction.indexOf('<circle r="25"');
if (ballStart < 0) throw new Error('Ball artwork was not found.');
const ballArtwork = initialAction.slice(ballStart).replace(/<\/g>$/, '');

const frames = [];
let finalState;
for (let frame = 0; frame < FPS * 200; frame++) {
  const s = game.state;
  if (s.round > 1) break;
  const seconds = Math.max(0, Math.ceil(s.remaining));
  const message = s.phase === 'kickoff' ? ['SAÍDA DE BOLA', 'Prontos para acelerar']
    : s.phase === 'goal' ? [`GOL ${s.goalTeam === 0 ? 'AZUL' : 'LARANJA'}!`, '+1 no placar']
    : s.phase === 'finished' ? [s.scores[0] === s.scores[1] ? 'EMPATE' : s.scores[0] > s.scores[1] ? 'AZUL VENCEU' : 'LARANJA VENCEU', 'Nova partida em instantes']
    : null;
  frames.push({
    ball: { ...s.ball }, cars: s.cars.map(c => ({ ...c })),
    trails: s.trails.map(p => ({ ...p })), scores: [...s.scores],
    clock: `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`,
    round: s.overtime ? 'PRORROGAÇÃO' : 'PARTIDA 01', message,
  });
  finalState = { phase: s.phase, scores: [...s.scores], stats: { ...s.stats } };
  for (let tick = 0; tick < PHYSICS_HZ / FPS; tick++) game.step(1 / PHYSICS_HZ);
}
if (game.state.round !== 2 || finalState.phase !== 'finished') throw new Error('Recording did not include a complete match.');
const duration = frames.length / FPS;
const dur = `${duration.toFixed(6)}s`;

function animation(attribute, values, transformType) {
  if (values.every(value => value === values[0])) return '';
  const tag = transformType ? 'animateTransform' : 'animate';
  const type = transformType ? ` type="${transformType}"` : '';
  // Sparse discrete tracks compress long pauses and keep the first and last frames exact.
  const changes = [0];
  for (let i = 1; i < values.length; i++) if (values[i] !== values[i - 1]) changes.push(i);
  if (changes.length < values.length * 0.45) {
    const times = changes.map(i => (i / values.length).toFixed(7));
    times.push('1');
    const sparse = changes.map(i => values[i]);
    sparse.push(values[values.length - 1]);
    return `<${tag} attributeName="${attribute}"${type} dur="${dur}" repeatCount="indefinite" calcMode="discrete" keyTimes="${times.join(';')}" values="${xml(sparse.join(';'))}"/>`;
  }
  return `<${tag} attributeName="${attribute}"${type} dur="${dur}" repeatCount="indefinite" calcMode="discrete" values="${xml(values.join(';'))}"/>`;
}
const track = (attribute, values) => `${attribute}="${xml(values[0])}">${animation(attribute, values)}`;
const transformed = (type, values, contents, extra = '') => `<g transform="${type}(${xml(values[0])})"${extra}>${animation('transform', values, type)}${contents}</g>`;
const FLOOR = api.constants.FLOOR;
const scale = api.constants.CAR_SCALE;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const dynamic = [];

for (let i = 0; i < 4; i++) {
  const point = frames.map(frame => frame.trails[i]);
  dynamic.push(`<circle r="${number(2 + i * 1.3)}" fill="#d6edfa" opacity="${number(i * .035)}" cx="${number(point[0]?.x || 0)}" cy="${number(FLOOR - (point[0]?.y || 0))}">${animation('cx', point.map(p => number(p?.x || 0)))}${animation('cy', point.map(p => number(FLOOR - (p?.y || 0))))}</circle>`);
}
dynamic.push(`<ellipse cy="${FLOOR}" ry="3.5" fill="#020d18" cx="${number(frames[0].ball.x)}" rx="${number(12 + frames[0].ball.y * .025)}" opacity=".3">${animation('cx', frames.map(f => number(f.ball.x)))}${animation('rx', frames.map(f => number(12 + f.ball.y * .025)))}${animation('opacity', frames.map(f => number(clamp(.3 - f.ball.y * .0004, .1, .3))))}</ellipse>`);

for (let team = 0; team < 2; team++) {
  const cars = frames.map(frame => frame.cars[team]);
  const color = team === 0 ? '#43b4f4' : '#ffac4f';
  dynamic.push(`<ellipse cy="${FLOOR}" rx="${number(34 * scale)}" ry="${number(4 * scale)}" fill="#010c18" cx="${number(cars[0].x)}" opacity=".3">${animation('cx', cars.map(c => number(c.x)))}${animation('opacity', cars.map(c => number(clamp(.3 - c.y * .00055, .08, .3))))}</ellipse>`);
  const lengths = cars.map(c => clamp(28 + Math.hypot(c.vx, c.vy) * .045, 28, 57) * Math.sqrt(c.boostPower || 1));
  const flame = lengths.map(len => `M-37-3Q-${number(44 + len * .3)}-13 -${number(43 + len)} 2Q-${number(45 + len * .3)} 16 -37 8Z`);
  const core = lengths.map(len => `M-37-1Q-60-5 -${number(47 + len * .5)} 2Q-58 9 -37 6Z`);
  let body = `<g opacity="${cars[0].boosting ? 1 : 0}">${animation('opacity', cars.map(c => c.boosting ? '1' : '0'))}<path fill="#ffab4c" opacity=".85" ${track('d', flame)}</path><path fill="#fff2ba" ${track('d', core)}</path></g>`;
  body += '<use href="#aq-car-body" xlink:href="#aq-car-body"/>';
  body += `<path d="M-26 19H26" fill="none" stroke="#f5fff9" stroke-width="4" stroke-linecap="round" opacity="${number(cars[0].resetGlow / .24)}">${animation('opacity', cars.map(c => number(c.resetGlow / .24)))}</path>`;
  for (const x of [-23, 23]) {
    const wheel = cars.map(c => `${number(c.x * 2.6 * c.face)} ${x} 11`);
    body += `<path d="M${x - 5} 11H${x + 5}M${x} 6V16" stroke="#dcebf4" stroke-width="1.4" opacity=".65" transform="rotate(${wheel[0]})">${animation('transform', wheel, 'rotate')}</path>`;
  }
  body = transformed('scale', cars.map(c => `${number(c.face * scale)} ${scale}`), body, ` color="${color}"`);
  body = transformed('rotate', cars.map(c => number(-c.a * 180 / Math.PI)), body);
  body = transformed('translate', cars.map(c => `${number(c.x)} ${number(FLOOR - c.y)}`), body, ` id="car-${team}"`);
  dynamic.push(body);
}
let ball = transformed('rotate', frames.map(f => number(-f.ball.a * 180 / Math.PI)), ballArtwork);
ball = transformed('translate', frames.map(f => `${number(f.ball.x)} ${number(FLOOR - f.ball.y)}`), ball, ' id="ball"');
dynamic.push(ball);

function textTimeline(values, x, y, attrs = '') {
  return [...new Set(values)].map(value => {
    const visibility = values.map(current => current === value ? '1' : '0');
    return `<text x="${x}" y="${y}" ${attrs} opacity="${visibility[0]}">${xml(value)}${animation('opacity', visibility)}</text>`;
  }).join('');
}
const board = `<rect x="0" y="0" width="1600" height="76" fill="#0b2636"/>
<g font-family="Consolas,monospace" text-anchor="middle">
<text x="620" y="45" fill="#66c8ff" font-size="16">AZUL</text>
<rect x="660" y="15" width="50" height="38" rx="3" fill="#1b6ab4"/>
${textTimeline(frames.map(f => String(f.scores[0])), 685, 44, 'fill="#eaf2fa" font-size="28"')}
${textTimeline(frames.map(f => f.clock), 800, 31, 'fill="#d9e5f2" font-size="17"')}
${textTimeline(frames.map(f => f.round), 800, 57, 'fill="#9aafc5" font-size="13" letter-spacing="1"')}
<rect x="890" y="15" width="50" height="38" rx="3" fill="#bb711e"/>
${textTimeline(frames.map(f => String(f.scores[1])), 915, 44, 'fill="#eaf2fa" font-size="28"')}
<text x="1000" y="45" fill="#ffb964" font-size="16">LARANJA</text></g>`;
const messageStates = frames.map(f => f.message ? f.message.join('|') : '');
const messages = [...new Set(messageStates)].filter(Boolean).map(value => {
  const [heading, caption] = value.split('|');
  const visible = messageStates.map(current => current === value ? '1' : '0');
  return `<g opacity="${visible[0]}" font-family="Consolas,monospace" text-anchor="middle">${animation('opacity', visible)}<rect x="568" y="382" width="464" height="112" rx="10" fill="#071420" fill-opacity=".91"/><text x="800" y="429" fill="#eaf2fa" font-size="27">${xml(heading)}</text><text x="800" y="465" fill="#bccddd" font-size="17">${xml(caption)}</text></g>`;
}).join('');

let scene = arena
  .replace(/<svg\b[^>]*>/, '<svg x="0" y="76" width="1600" height="930" viewBox="0 0 1600 930">')
  .replace('<g id="aq-action"></g>', `<g id="aq-action">${dynamic.join('')}</g>`)
  .replace(/\sclass="aq-jelly-drift(?: aq-jelly-drift-late)?"/g, '')
  .replace('</svg>', `${messages}</svg>`);
const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="1006" viewBox="0 0 1600 1006" role="img" aria-labelledby="soccer-title soccer-description">
<title id="soccer-title">Futebol de carros — partida automática</title>
<desc id="soccer-description">Uma partida completa em loop, gerada pela física e pelos bots do simulador, com carros azul e laranja, boost e gols elevados na arena submersa.</desc>
<!-- Generated from car-soccer-autoplay ${REVISION}; seed ${seed}; ${FPS} fps. -->
<defs><clipPath id="profile-arena-clip"><rect width="1600" height="1006" rx="16"/></clipPath></defs>
<g clip-path="url(#profile-arena-clip)"><rect width="1600" height="1006" fill="#0b1522"/>${board}${scene}</g></svg>\n`;
if (/<script\b|<foreignObject\b|\son\w+\s*=|(?:href|src)="https?:/i.test(svg)) throw new Error('SVG must be self-contained and script-free.');
await mkdir(dirname(output), { recursive: true });
await writeFile(output, svg);
console.log(JSON.stringify({ output, bytes: Buffer.byteLength(svg), duration, fps: FPS, frames: frames.length, seed, scores: finalState.scores, stats: finalState.stats }));

