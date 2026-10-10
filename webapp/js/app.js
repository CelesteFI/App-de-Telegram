/* app.js — Arranque: tema de Telegram, rutas y montaje de la vista activa. */

import { api, usuario } from './api.js';
import { cargarConfig, estado } from './estado.js';
import * as nav from './navegacion.js';
import { alPintar, vaciar } from './dom.js';
import { vistaInicio } from './vistas/inicio.js';
import { vistaTema } from './vistas/tema.js';
import { vistaQuiz } from './vistas/quiz.js';
import { vistaJuegos } from './vistas/juegos.js';
import { vistaJuego } from './vistas/juego.js';
import { vistaPartida } from './vistas/partida.js';
import { aviso } from './avisos.js';

const app = document.getElementById('app');
const barra = {
  volver: document.getElementById('volver'),
  titulo: document.getElementById('titulo'),
  sub: document.getElementById('subtitulo'),
  marcador: document.getElementById('marcador'),
  pie: document.getElementById('pie'),
  textoPie: document.getElementById('pieTexto'),
};

let limpiarVista = null;

// Deja una pantalla de error con boton para recargar la app entera.
// Recargar es a proposito: vuelve a montar rutas y oyentes desde cero, sin
// duplicarlos como pasaria si solo reintentara el fetch.
function detallesConexion(error) {
  const tg = window.Telegram?.WebApp;
  return [
    `mensaje: ${error?.message || error}`,
    `codigo: ${error?.codigo ?? 'n/a'}`,
    `origen: ${location.origin}`,
    `ruta: ${location.pathname + location.search + location.hash}`,
    `telegram: ${tg ? 'si' : 'no'}`,
    `initData: ${tg?.initData ? `${tg.initData.length} caracteres` : 'vacio'}`,
    `online: ${navigator.onLine}`,
    `userAgent: ${navigator.userAgent}`,
  ].join('\n');
}

function pantallaError(mensaje, error) {
  vaciar(app);
  const caja = document.createElement('div');
  caja.className = 'vacio';
  const texto = document.createElement('p');
  texto.textContent = mensaje || 'No se pudo cargar la app.';
  caja.append(texto);

  const boton = document.createElement('button');
  boton.type = 'button';
  boton.className = 'boton boton--ancho';
  boton.textContent = 'Reintentar';
  boton.addEventListener('click', () => location.reload());
  caja.append(boton);

  const detalles = detallesConexion(error);
  const copiar = document.createElement('button');
  copiar.type = 'button';
  copiar.className = 'boton boton--ancho';
  copiar.style.marginTop = '8px';
  copiar.textContent = 'Copiar detalles';
  copiar.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(detalles);
      copiar.textContent = 'Copiado';
    } catch {
      window.prompt('Copia este texto:', detalles);
    }
  });
  caja.append(copiar);

  const pre = document.createElement('pre');
  pre.className = 'vacio__detalle';
  pre.textContent = detalles;
  caja.append(pre);

  app.append(caja);
}

function pintarMarco(actual) {
  const vista = actual.vista;
  const titulo = vista ? vista.titulo() : estado.config?.app || 'Repaso';
  barra.titulo.textContent = titulo;
  barra.sub.textContent = vista ? (vista.sub?.() || '') : '';
  barra.marcador.innerHTML = vista?.marcador?.() || '';
  barra.marcador.hidden = !barra.marcador.innerHTML;
  barra.volver.hidden = nav.nivel() <= 1;
  const pie = vista?.pie?.() || '';
  barra.pie.hidden = !pie;
  barra.textoPie.textContent = pie;
}

async function montar(actual) {  try {
    limpiarVista?.();
  } catch {
    /* la vista anterior fallo al salir; seguimos */
  }
  limpiarVista = null;
  pintarMarco(actual);
  vaciar(app);

  if (!actual.vista) {
    app.append(Object.assign(document.createElement('div'), {
      className: 'vacio',
      textContent: 'Esa pantalla no existe.',
    }));
    nav.reemplazar('inicio');
    return;
  }

  try {
    limpiarVista = await actual.vista.entrar(app);
    alPintar(app);
  } catch (error) {
    vaciar(app);
    app.append(Object.assign(document.createElement('div'), {
      className: 'vacio',
      textContent: error.message || 'No se pudo cargar esta pantalla.',
    }));
    aviso(error.message || 'Algo fallo', true);
  }
}

function aplicarTelegram() {
  const tg = window.Telegram?.WebApp;
  if (!tg) return;
  tg.ready?.();
  tg.expand?.();
  try {
    tg.setHeaderColor?.('secondary_bg_color');
    tg.disableVerticalSwipes?.();
  } catch {
    /* versiones antiguas de Telegram WebApp */
  }
  document.body.style.background = tg.themeParams?.bg_color || '';
}

async function arrancar() {
  // Marca para el respaldo de index.html: si el modulo no llega a ejecutarse,
  // ese script muestra solo un aviso con boton de reintentar.
  window.__repasoArranco = true;
  aplicarTelegram();
  barra.volver.addEventListener('click', () => nav.atras());

  nav.definirRutas([
    { re: /^inicio$/, vista: () => vistaInicio() },
    { re: /^tema\/[^/]+\/[^/]+$/, vista: (p) => vistaTema(p[0], p[1]) },
    { re: /^quiz$/, vista: () => vistaQuiz() },
    { re: /^juegos$/, vista: () => vistaJuegos() },
    { re: /^juego\/[^/]+$/, vista: (p) => vistaJuego(p[0]) },
    { re: /^partida\/[^/]+$/, vista: (p) => vistaPartida(p[0]) },
  ]);

  nav.alCambiar(montar);

  try {
    await cargarConfig();
  } catch (error) {
    pantallaError(error.message || 'No se pudo contactar al servidor.', error);
    barra.sub.textContent = 'Sin conexion con el servidor';
    return;
  }

  const quien = estado.config.usuario;
  // Con modo dev el backend ya responde con un usuario de prueba, asi que no
  // hace falta initData valido: se puede entrar y jugar normal.
  const entra = Boolean(quien) || Boolean(estado.config.dev);
  barra.sub.textContent = quien?.nombre
    ? `Hola, ${quien.nombre}`
    : (estado.config.dev ? 'Modo de pruebas: tu progreso se guarda como Invitado' : 'Abrir desde Telegram para registrar tu progreso');
  nav.iniciar();

  if (!entra) {
    vaciar(app);
    app.append(Object.assign(document.createElement('div'), {
      className: 'vacio',
      textContent: 'Abre esta app desde el bot de Telegram para poder repasar.',
    }));
  }
}

window.addEventListener('marca:cambio', () => pintarMarco(nav.rutaActual()));

window.addEventListener('error', (evento) => {
  aviso(evento.message || 'Error inesperado', true);
});

window.addEventListener('unhandledrejection', (evento) => {
  aviso(String(evento.reason?.message || evento.reason || 'Error inesperado'), true);
});

arrancar();

export { api, usuario };