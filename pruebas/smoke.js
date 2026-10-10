/* smoke.js — Prueba de humo del frontend real contra el backend real.

Levanta el servidor de Python, monta `webapp/index.html` en jsdom, carga los
modulos ES tal cual los carga el navegador y recorre la app: portada, quiz
completo hasta el reporte, catalogo de minijuegos y dos partidas.

    npm install     (una vez, para tener jsdom)
    node pruebas/smoke.js

Termina con `todo correcto` y sale con codigo 0.
*/

import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const aqui = dirname(fileURLToPath(import.meta.url));
const raiz = join(aqui, '..');
const fallos = [];

function revisar(condicion, mensaje) {
  console.log(`  ${condicion ? '[ok ]' : '[FALLA]'} ${mensaje}`);
  if (!condicion) fallos.push(mensaje);
  return Boolean(condicion);
}

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

let estado = null;

async function hasta(condicion, ms = 8000, paso = 60) {
  const limite = Date.now() + ms;
  while (Date.now() < limite) {
    if (await condicion()) return true;
    await esperar(paso);
  }
  return false;
}

function puertoLibre() {
  return 8300 + Math.floor(Math.random() * 900);
}

async function arrancarServidor() {
  const resultados = mkdtempSync(join(tmpdir(), 'repaso-ed-prueba-'));
  for (let intento = 0; intento < 6; intento += 1) {
    const puerto = puertoLibre();
    const hijo = spawn(process.env.PYTHON || 'python',
      ['-m', 'app.nucleo.principal', '--puerto', String(puerto)],
      {
        cwd: raiz,
        env: {
          ...process.env,
          DEV_AUTHPASS: '1',
          PYTHONUNBUFFERED: '1',
          RESULTADOS_DIR: resultados,
        },
        stdio: 'ignore',
      });
    const responde = async () => {
      if (hijo.exitCode !== null) return false;
      try {
        const r = await fetch(`http://127.0.0.1:${puerto}/api/config`);
        return r.ok;
      } catch {
        return false;
      }
    };
    const vivo = await hasta(responde, 6000, 120);
    if (vivo) return { hijo, puerto, resultados };
    hijo.kill();
  }
  rmSync(resultados, { recursive: true, force: true });
  throw new Error('no se pudo arrancar el servidor de Python');
}

function instalarGlobales(dom, puerto) {
  const { window } = dom;
  globalThis.window = window;
  globalThis.document = window.document;
  globalThis.location = window.location;
  globalThis.history = window.history;
  Object.defineProperty(globalThis, 'navigator', {
    value: window.navigator, configurable: true, writable: true,
  });
  globalThis.Node = window.Node;
  globalThis.Element = window.Element;
  globalThis.HTMLElement = window.HTMLElement;
  globalThis.getComputedStyle = window.getComputedStyle.bind(window);
  globalThis.requestAnimationFrame = (fn) => setTimeout(() => fn(Date.now()), 0);
  globalThis.cancelAnimationFrame = (id) => clearTimeout(id);
  window.requestAnimationFrame = globalThis.requestAnimationFrame;
  window.cancelAnimationFrame = globalThis.cancelAnimationFrame;
  const nativo = globalThis.fetch.bind(globalThis);
  globalThis.fetch = (entrada, opciones) =>
    nativo(new URL(String(entrada), `http://127.0.0.1:${puerto}/`), opciones);
  window.fetch = globalThis.fetch;
  window.HTMLCanvasElement.prototype.getContext = () => ({
    clearRect() {}, fillRect() {}, strokeRect() {}, beginPath() {}, moveTo() {}, lineTo() {},
    arc() {}, closePath() {}, stroke() {}, fill() {}, setLineDash() {}, fillText() {},
    strokeStyle: '', fillStyle: '', lineWidth: 1, font: '', textAlign: '',
  });
}

const texto = () => document.body.textContent;
const nodos = (selector) => [...document.querySelectorAll(selector)];

function botonConTexto(selector, aguja) {
  return nodos(selector).find((n) => n.textContent.includes(aguja)) || null;
}

async function esperarYBuscar(selector, aguja, ms = 8000) {
  const ok = await hasta(() => botonConTexto(selector, aguja) !== null, ms);
  return ok ? botonConTexto(selector, aguja) : null;
}

async function probarPortada() {
  console.log('portada');
  await hasta(() => texto().includes('Clasificacion de ED'));
  const tarjetas = nodos('#app .tarjeta');
  revisar(tarjetas.length >= 8, `la portada lista los temas (${tarjetas.length} tarjetas)`);
  revisar(texto().includes('Series de Fourier y EDP'), 'incluye el ultimo tema del catalogo');
  revisar(texto().includes('Minijuegos'), 'ofrece la entrada a los minijuegos');
}

async function probarQuizCompleto() {
  console.log('quiz completo');
  const tema = botonConTexto('#app .tarjeta', 'ED exactas');
  if (!revisar(tema !== null, 'se encuentra la tarjeta del tema ED exactas')) return;
  tema.click();
  const empezar = await esperarYBuscar('#app .boton', 'Empezar');
  if (!revisar(empezar !== null, 'la pantalla de configuracion ofrece Empezar')) return;
  revisar(texto().includes('ED exactas'), 'la configuracion muestra el tema elegido');
  empezar.click();

  const ok = await hasta(() => nodos('#app .opcion').length >= 2, 8000);
  if (!revisar(ok, 'el quiz muestra la pregunta con sus opciones')) return;
  revisar(nodos('#app .opcion').length === 4, 'la pregunta llega con 4 opciones');
  revisar(texto().includes('1/'), 'el marcador avanza con la posicion de la pregunta');

  let vueltas = 0;
  while (vueltas < 12 && !document.querySelector('.cifra')) {
    const explicacion = document.querySelector('#app .explica');
    if (!explicacion) {
      const opciones = nodos('#app .opcion');
      if (!opciones.length) break;
      opciones[0].click();
      const respondida = await hasta(() => document.querySelector('#app .explica') !== null, 6000);
      if (!respondida) break;
      revisar(true, `pregunta ${vueltas + 1}: muestra explicacion al instante`);
    }
    const siguiente = botonConTexto('#app .boton', 'Siguiente pregunta')
      || botonConTexto('#app .boton', 'Ver mi resultado');
    if (!siguiente) break;
    siguiente.click();
    vueltas += 1;
    await esperar(120);
  }

  const hayCifra = await hasta(() => document.querySelector('.cifra') !== null, 8000);
  if (!hayCifra) {
    console.log(`    vueltas: ${vueltas}`);
    console.log(`    marcador: ${document.getElementById('marcador')?.textContent}`);
    console.log(`    app: ${document.getElementById('app')?.textContent.slice(0, 240)}`);
  }
  revisar(hayCifra, `el quiz llega al reporte (${vueltas} preguntas)`);
  revisar(texto().includes('Ver como te fue') || texto().includes('pregunta por pregunta'),
    'el reporte revisa pregunta por pregunta');
  revisar(nodos('#app .detalle__fila').length > 0, 'el detalle trae una fila por pregunta');
}

async function probarJuegos() {
  console.log('catalogo de minijuegos');
  location.hash = '#/juegos';
  const ok = await hasta(() => nodos('#app .tarjeta').length >= 10, 8000);
  revisar(ok, `el catalogo lista los 10 juegos (${nodos('#app .tarjeta').length})`);
  revisar(texto().includes('Clasificador Rapido'), 'incluye el clasificador');
  revisar(texto().includes('Tiro al Blanco Teorico'), 'incluye el tiro al blanco');
}

async function probarJuegoConBoton(id, titulo, selectorOpcion, etiquetaExito) {
  const tarjeta = botonConTexto('#app .tarjeta', titulo);
  if (!revisar(tarjeta !== null, `${id}: se encuentra la tarjeta`)) return;
  tarjeta.click();

  const jugar = await esperarYBuscar('#app .boton', 'Jugar');
  if (!revisar(jugar !== null, `${id}: la configuracion ofrece Jugar`)) return;
  jugar.click();

  const monto = await hasta(() => document.querySelector(selectorOpcion) !== null, 8000);
  if (!revisar(monto, `${id}: la partida monta su tablero`)) return;

  const objetivos = nodos(selectorOpcion);
  objetivos[0]?.click();
  const comprobar = botonConTexto('#app .boton', 'Comprobar');
  revisar(comprobar !== null, `${id}: hay boton Comprobar`);
  comprobar?.click();

  const hablo = await hasta(() => document.querySelector('#app .explica') !== null, 8000);
  revisar(hablo, `${id}: el servidor devuelve el veredicto (${etiquetaExito})`);
}

async function probarMemoria() {
  console.log('minijuego con auto-envio');
  location.hash = '#/juegos';
  await hasta(() => botonConTexto('#app .tarjeta', 'Memorama') !== null, 8000);
  const tarjeta = botonConTexto('#app .tarjeta', 'Memorama de Conceptos');
  if (!revisar(tarjeta !== null, 'memoria: se encuentra la tarjeta')) return;
  tarjeta.click();
  const jugar = await esperarYBuscar('#app .boton', 'Jugar');
  jugar?.click();

  const monto = await hasta(() => nodos('#app .memoria__carta').length > 0, 8000);
  if (!revisar(monto, `memoria: monta ${nodos('#app .memoria__carta').length} cartas`)) return;
  revisar(botonConTexto('#app .boton', 'Comprobar') === null,
    'memoria: no necesita boton Comprobar, se envia sola');

  const cartas = nodos('#app .memoria__carta');
  const partida = estado.partida;
  const pareja = await buscarPareja(cartas, partida);
  if (!revisar(pareja !== null, 'memoria: el servidor reconoce una pareja del tablero')) return;

  voltear(pareja[0].dataset.id);
  const primeraVista = await hasta(() => nodos('#app .memoria__carta--vista').length === 1, 3000);
  revisar(primeraVista, 'memoria: la primera carta se voltea al tocarla');
  voltear(pareja[1].dataset.id);

  const fijadas = await hasta(() => nodos('#app .memoria__carta--hecha').length === 2, 8000);
  revisar(fijadas, 'memoria: la pareja correcta queda fijada por el servidor');
  revisar(document.querySelector('#app .explica') === null,
    'memoria: no responde al servidor hasta completar todo el tablero');

  await jugarTableroEntero(partida);
}

/** El memorama se repinta en cada movimiento, asi que hay que buscar el nodo vivo. */
function voltear(id) {
  document.querySelector(`#app .memoria__carta[data-id="${id}"]`)?.click();
}

async function buscarPareja(cartas, partida) {
  for (const a of cartas) {
    for (const b of cartas) {
      if (a === b) continue;
      const r = await fetch('/api/minijuegos/pareja', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intento: partida.intento, ronda: partida.pos,
          a: a.dataset.id, b: b.dataset.id, dev: { uid: '1' },
        }),
      });
      if (r.ok && (await r.json()).pareja) return [a, b];
    }
  }
  return null;
}

/** Resuelve el resto del tablero usando al servidor como juez de cada pareja. */
async function jugarTableroEntero(partida) {
  for (let vuelta = 0; vuelta < 40; vuelta += 1) {
    if (document.querySelector('#app .explica')) break;
    const libres = nodos('#app .memoria__carta:not(.memoria__carta--hecha)');
    if (libres.length < 2) break;
    const pareja = await buscarPareja(libres, partida);
    if (!pareja) break;
    voltear(pareja[0].dataset.id);
    await hasta(() => nodos('#app .memoria__carta--vista').length >= 1, 2000);
    voltear(pareja[1].dataset.id);
    const completo = await hasta(() => document.querySelector('#app .explica') !== null
      || nodos('#app .memoria__carta--hecha').length >= 2, 4000);
    if (!completo) break;
    await esperar(120);
  }
  revisar(document.querySelector('#app .explica') !== null,
    'memoria: al llenar el tablero el servidor califica la ronda sola');
}

function rondasDeEjemplo() {
  return {
    deslizador: { id: 'd0', attr: 'Es autonoma', formula: "y' = -y + 3" },
    memoria: {
      id: 'r0', pares: 2,
      cartas: [
        { id: 'a', cara: 'concepto', texto: 'Ecuacion de Bernoulli' },
        { id: 'b', cara: 'mate', texto: "y' + P(x)\\,y = Q(x)\\,y^{n}" },
        { id: 'c', cara: 'concepto', texto: 'Ecuacion de Riccati' },
        { id: 'd', cara: 'mate', texto: "y' = a(x)y^{2} + b(x)y + c(x)" },
      ],
    },
    columnas: { id: 'c0', izquierda: ['uno', 'dos'], derecha: ['A', 'B'] },
    completar: { id: 'h0', enunciado: 'La ED $y\' = F(y/x)$ usa $y = ___\\,x$', opciones: ['v', 'w'] },
    intruso: {
      id: 'i0', pista: 'Tres son ED parciales',
      tarjetas: [{ id: 't0', tex: 'dy/dx = y' }, { id: 't1', tex: '\\partial u/\\partial t = u' }],
    },
    clasificador: {
      id: 'k0', segundos: 12,
      canastas: [{ clave: 'separable', nombre: 'Separable' }],
      items: [{ id: '0-0', tex: "y' = \\sin y" }],
    },
    ordenar: { id: 'o0', titulo: 't', total: 2, pista: '2 pasos.', pasos: ['uno', 'dos'] },
    grafico: { id: 'g0', ecuacion: "y' = -x/y", tipos: ['bandas_y', 'verticales_x', 'circular'] },
    palabra: {
      id: 'w0', pista: 'Una pista', longitud: 6,
      letras: ['A', 'C', 'E'], teclado: ['A', 'C', 'E', 'X'], intentos: 3,
    },
    globos: {
      id: 'b0', instruccion: 'Explota las soluciones', segundos: 10,
      globos: [{ id: 'g0', tex: 'e^{x}' }, { id: 'g1', tex: 'x' }],
    },
  };
}

async function probarModulos() {
  console.log('modulos de juego (sin servidor)');
  const { MODULOS } = await import(pathToFileURL(join(raiz, 'webapp/js/juegos/index.js')));
  const rondas = rondasDeEjemplo();
  revisar(Object.keys(MODULOS).length === 10, 'hay 10 modulos registrados');

  for (const [id, modulo] of Object.entries(MODULOS)) {
    const instancia = modulo.crear({
      ronda: rondas[id],
      indice: 0,
      total: 3,
      responder: () => {},
      temporizador: () => {},
    });
    const html = instancia.html();
    const envio = instancia.envio();
    revisar(typeof html === 'string' && html.length > 10, `${id}: html() construye su tablero`);
    revisar(envio !== undefined && envio !== null,
      `${id}: envio() responde en el formato que espera califica() (${formatoDe(envio)})`);
  }
}

function formatoDe(valor) {
  if (Array.isArray(valor)) return 'lista';
  if (valor && typeof valor === 'object') return 'objeto';
  return typeof valor;
}

async function main() {
  const { hijo, puerto, resultados } = await arrancarServidor();
  console.log(`servidor de Python en el puerto ${puerto}\n`);
  try {
    const html = readFileSync(join(raiz, 'webapp/index.html'), 'utf8');
    const { JSDOM } = await import('jsdom');
    const dom = new JSDOM(html, { url: `http://127.0.0.1:${puerto}/index.html`, pretendToBeVisual: true });
    instalarGlobales(dom, puerto);

    await import(pathToFileURL(join(raiz, 'webapp/js/app.js')).href);
    estado = (await import(pathToFileURL(join(raiz, 'webapp/js/estado.js')).href)).estado;

    const arranco = await hasta(() => texto().includes('Clasificacion de ED'), 10000);
    if (!arranco) {
      console.log(`    app vacio: ${nodos('#app > *').length} hijos`);
      console.log(`    subtitulo: ${document.getElementById('subtitulo')?.textContent}`);
      console.log(`    cuerpo: ${texto().slice(0, 300)}`);
    }
    if (!revisar(arranco, 'el modulo app.js monta la portada')) return;

    await probarPortada();
    await probarQuizCompleto();
    await probarJuegos();
    await probarJuegoConBoton('completar', 'Completa la Forma Estandar',
      '.completar__opcion', 'con opcion elegida');
    await probarMemoria();
    await probarModulos();
  } finally {
    hijo.kill();
    rmSync(resultados, { recursive: true, force: true });
  }

  console.log();
  if (fallos.length) {
    console.log(`${fallos.length} comprobaciones fallaron`);
    process.exitCode = 1;
    return;
  }
  console.log('todo correcto');
}

main().catch((error) => {
  console.error('\nla prueba se rompio:', error);
  process.exitCode = 1;
});