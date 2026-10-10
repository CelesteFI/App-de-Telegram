/* navegacion.js — Rutas por hash y pila de vistas. */

const rutas = [];
const oyentes = [];
let actual = null;

export function definirRutas(lista) {
  rutas.length = 0;
  for (const ruta of lista) rutas.push(ruta);
}

export function alCambiar(fn) {
  oyentes.push(fn);
}

export function rutaActual() {
  return actual || { camino: 'inicio', partes: [], vista: null };
}

export function nivel() {
  return (location.hash || '').replace(/^#\//, '').split('/').filter(Boolean).length;
}

export function ir(ruta) {
  const destino = ruta.startsWith('#') ? ruta : `#/${ruta}`;
  if (location.hash === destino) resolver();
  else location.hash = destino;
}

export function reemplazar(ruta) {
  const destino = ruta.startsWith('#') ? ruta : `#/${ruta}`;
  history.replaceState(null, '', destino);
  resolver();
}

export function atras() {
  if (nivel() > 1) history.back();
  else ir('inicio');
}

function resolver() {
  const camino = (location.hash || '#/inicio').replace(/^#\//, '');
  const trozos = camino.split('/').filter(Boolean);
  for (const ruta of rutas) {
    if (!ruta.re.test(camino)) continue;
    actual = { camino, partes: trozos.slice(1), vista: ruta.vista(trozos.slice(1)) };
    break;
  }
  if (!actual || actual.camino !== camino) {
    actual = { camino, partes: trozos.slice(1), vista: null };
  }
  for (const fn of oyentes) fn(actual);
}

export function iniciar() {
  window.addEventListener('hashchange', resolver);
  if (!location.hash) reemplazar('inicio');
  else resolver();
}