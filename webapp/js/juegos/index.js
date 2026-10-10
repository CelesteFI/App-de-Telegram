/* juegos/index.js — Registro de los diez modulos de minijuego. */

import clasificador from './clasificador.js';
import columnas from './columnas.js';
import completar from './completar.js';
import deslizador from './deslizador.js';
import globos from './globos.js';
import grafico from './grafico.js';
import intruso from './intruso.js';
import memoria from './memoria.js';
import ordenar from './ordenar.js';
import palabra from './palabra.js';

export const MODULOS = {
  clasificador,
  columnas,
  completar,
  deslizador,
  globos,
  grafico,
  intruso,
  memoria,
  ordenar,
  palabra,
};

export function moduloDe(juegoId) {
  return MODULOS[juegoId] || null;
}