/* estado.js — Lo que esta pasando ahora: config del servidor y partidas en curso. */

import { api, activarModoDev, usuario } from './api.js';

export const estado = {
  config: null,
  materias: [],
  juegos: [],
  quiz: null,
  partida: null,
};

export async function cargarConfig() {
  // Reintenta solo: el primer envio por el tunel puede tardar o fallar de
  // forma transitoria (arranque en frio). Asi no hace falta tocar Reintentar.
  let ultimoError;
  for (let intento = 0; intento < 3; intento += 1) {
    try {
      const datos = await api.get('/api/config');
      estado.config = datos;
      activarModoDev(Boolean(datos.dev) && !datos.usuario);
      return datos;
    } catch (error) {
      ultimoError = error;
      if (intento < 2) await new Promise((r) => setTimeout(r, 1500));
    }
  }
  throw ultimoError;
}

export function usuarioActual() {
  const delServer = estado.config?.usuario;
  if (delServer) return delServer;
  return { uid: usuario.uid || '1', nombre: usuario.nombre || 'Invitado' };
}

export async function cargarMaterias() {
  const datos = await api.get('/api/materias');
  estado.materias = datos.materias || [];
  estado.recordsQuiz = datos.records || {};
  estado.historialQuiz = datos.historial || [];
  return datos;
}

export async function cargarJuegos() {
  const datos = await api.get('/api/minijuegos');
  estado.juegos = datos.juegos || [];
  estado.cantidadesJuego = datos.cantidades || [5, 8, 10, 15];
  estado.recordsJuego = datos.records || {};
  try {
    const extra = await api.get('/api/minijuegos/historial');
    estado.historialJuego = extra.historial || datos.historial || [];
  } catch {
    estado.historialJuego = datos.historial || [];
  }
  return datos;
}

export function tema(materiaId, temaId) {
  for (const materia of estado.materias) {
    if (materia.id !== materiaId) continue;
    for (const tema of materia.temas || []) {
      if (tema.id === temaId) return { materia, tema };
    }
  }
  return null;
}

export function juego(juegoId) {
  return estado.juegos.find((j) => j.id === juegoId) || null;
}