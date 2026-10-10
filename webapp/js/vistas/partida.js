/* partida.js — Motor comun de los diez minijuegos. */

import { api } from '../api.js';
import { aviso } from '../avisos.js';
import { avisarMarco, el, pintarMatematica } from '../dom.js';
import { estado } from '../estado.js';
import * as nav from '../navegacion.js';
import { pintarReporte } from './reporte.js';
import { MODULOS } from '../juegos/index.js';

function barraProgreso(pos, total) {
  const ancho = el('div', { class: 'progreso__barra' });
  ancho.style.width = `${total ? (pos / total) * 100 : 0}%`;
  return el('div', { class: 'progreso' }, ancho);
}

export function vistaPartida(juegoId) {
  const modulo = MODULOS[juegoId] || null;

  return {
    titulo: () => estado.partida?.titulo || 'Partida',
    sub: () => (estado.partida ? `Ronda ${(estado.partida.pos || 0) + 1} de ${estado.partida.total}` : ''),
    marcador: () => {
      if (!estado.partida) return '';
      return `<span class="pildora">${estado.partida.puntos || 0} pts</span>`;
    },
    pie: () => 'La correccion la hace el servidor: aqui no hay respuestas guardadas.',

    async entrar(raiz) {
      const partida = estado.partida;
      if (!partida || partida.juego_id !== juegoId) {
        raiz.append(
          el('div', { class: 'vacio', texto: 'No hay ninguna partida en marcha.' }),
          el('button', {
            class: 'boton boton--ancho',
            type: 'button',
            texto: 'Ver los minijuegos',
            onclick: () => nav.ir('juegos'),
          }),
        );
        return null;
      }

      let actual = partida;
      let instancias = null;
      let temporizadores = [];

      function limpiar() {
        for (const id of temporizadores) { clearTimeout(id); clearInterval(id); }
        temporizadores = [];
        instancias?.limpiar?.();
        instancias = null;
      }

      // Ticks repetidos cada `ms` (los juegos de tiempo descuentan 1 s por
      // tick hasta llegar a cero). Se limpian en `limpiar()` al responder.
      function temporizador(fn, ms) {
        temporizadores.push(setInterval(fn, ms));
      }

      async function refrescar() {
        const datos = await api.get(`/api/minijuegos/estado?intento=${actual.intento}`);
        if (datos.terminado) {
          estado.partida = null;
          avisarMarco();
          pintarReporte(raiz, datos.reporte, 'Partida terminada', () => nav.ir('juegos'));
          return;
        }
        actual = datos;
        estado.partida = datos;
        dibujar();
      }

      async function responder(valor) {
        limpiar();
        const datos = await api.post('/api/minijuegos/responder', {
          intento: actual.intento,
          ronda: actual.pos,
          respuesta: valor,
        });
        actual = { ...actual, pos: datos.pos, puntos: datos.puntos };
        estado.partida = actual;
        avisarMarco();
        mostrarVeredicto(datos);
      }

      function mostrarVeredicto(datos) {
        const zona = document.getElementById('zona');
        if (!zona) return;
        zona.replaceChildren(
          el('p', {
            class: `explica explica--${datos.correcto ? 'bien' : 'mal'}`,
            html: datos.detalle || '',
          }),
          datos.ultima
            ? el('button', {
                class: 'boton boton--ancho',
                type: 'button',
                texto: 'Ver mi resultado',
                onclick: () => {
                  estado.partida = null;
                  avisarMarco();
                  pintarReporte(raiz, datos.reporte, 'Partida terminada',
                    () => nav.ir('juegos'));
                },
              })
            : el('button', {
                class: 'boton boton--ancho',
                type: 'button',
                texto: 'Siguiente ronda',
                onclick: async () => {
                  try {
                    await refrescar();
                  } catch (error) {
                    aviso(error.message, true);
                  }
                },
              }),
        );
        pintarMatematica(zona);
      }

      function dibujar() {
        limpiar();
        raiz.replaceChildren(barraProgreso(actual.pos, actual.total));

        const zona = el('div', { id: 'zona' });
        raiz.append(zona);

        const contexto = {
          ronda: actual.ronda,
          indice: actual.pos,
          total: actual.total,
          intento: actual.intento,
          responder,
          temporizador,
        };

        instancias = modulo.crear(contexto);
        zona.innerHTML = instancias.html();
        instancias.montar();
        pintarMatematica(zona);

        if (!instancias.auto) {
          zona.append(el('div', { class: 'seccion' }), el('button', {
            class: 'boton boton--ancho',
            type: 'button',
            texto: 'Comprobar',
            onclick: async (evento) => {
              evento.currentTarget.disabled = true;
              try {
                await responder(instancias.envio());
              } catch (error) {
                aviso(error.message, true);
                evento.currentTarget.disabled = false;
              }
            },
          }));
        }
      }

      dibujar();
      return limpiar;
    },
  };
}