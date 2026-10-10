/* api.js — Hablar con el backend, con la identidad de Telegram. */

const tg = window.Telegram?.WebApp;

function initData() {
  if (tg?.initData) return tg.initData;
  return new URLSearchParams(location.search).get('initData') || '';
}

export const usuario = {
  uid: tg?.initDataUnsafe?.user?.id ? String(tg.initDataUnsafe.user.id) : '',
  nombre: [tg?.initDataUnsafe?.user?.first_name, tg?.initDataUnsafe?.user?.last_name]
    .filter(Boolean).join(' ') || '',
};

let modoDev = false;

export function identidadEnQuery() {
  const params = new URLSearchParams();
  const init = initData();
  if (init) params.set('initData', init);
  if (modoDev) {
    params.set('dev_uid', usuario.uid || '1');
    if (usuario.nombre) params.set('dev_nombre', usuario.nombre);
  }
  const texto = params.toString();
  if (!texto) return '';
  return `?${texto}`;
}

/** Une la identidad de Telegram con lo que ya venga en la ruta. */
function conIdentidad(camino) {
  const sufijo = identidadEnQuery();
  if (!sufijo) return camino;
  const tieneConsulta = camino.includes('?');
  return tieneConsulta ? `${camino}&${sufijo.slice(1)}` : `${camino}${sufijo}`;
}

// Tope de espera por peticion: si el servidor o el tunel no responden,
// preferimos un error claro (con boton de reintentar) a un cuelgue eterno.
const TIEMPO_LIMITE = 15000;

async function pedir(metodo, camino, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (metodo === 'POST') {
    const datos = { ...(cuerpo || {}) };
    const init = initData();
    if (init) datos.initData = init;
    if (modoDev) datos.dev = { uid: usuario.uid || '1', nombre: usuario.nombre };
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(datos);
  }

  const control = new AbortController();
  const reloj = setTimeout(() => control.abort(), TIEMPO_LIMITE);
  let respuesta;
  try {
    respuesta = await fetch(camino, { ...opciones, signal: control.signal });
  } catch (error) {
    const abortado = error?.name === 'AbortError';
    const fallo = new Error(abortado
      ? 'El servidor tardo demasiado en responder.'
      : 'No se pudo contactar al servidor.');
    fallo.codigo = 0;
    throw fallo;
  } finally {
    clearTimeout(reloj);
  }

  let datos = {};
  try {
    datos = await respuesta.json();
  } catch {
    datos = { ok: false, error: 'el servidor no devolvio JSON' };
  }
  if (!respuesta.ok || datos.ok === false) {
    const error = new Error(datos.error || `error ${respuesta.status}`);
    error.codigo = respuesta.status;
    throw error;
  }
  return datos;
}

export const api = {
  get(camino) {
    return pedir('GET', conIdentidad(camino));
  },
  post(camino, cuerpo) {
    return pedir('POST', camino, cuerpo);
  },
};

export function activarModoDev(activo) {
  modoDev = Boolean(activo);
}

export function botonTelegram(texto, callback) {
  if (!tg?.showConfirm) return false;
  tg.showConfirm(texto, callback);
  return true;
}

export function cerrarTelegram() {
  tg?.close?.();
}