/* juego.js — Configuracion de una partida: nivel, cantidad y tema. */

import { api } from '../api.js';
import { aviso } from '../avisos.js';
import { el } from '../dom.js';
import { estado, juego as buscarJuego, usuarioActual } from '../estado.js';
import * as nav from '../navegacion.js';

const NOMBRES_NIVEL = { facil: 'Facil', medio: 'Normal', dificil: 'Dificil' };

const ELECCIONES = new Map();

function eleccionDe(juegoId) {
  if (!ELECCIONES.has(juegoId)) ELECCIONES.set(juegoId, { nivel: '', cantidad: 0, tema: '' });
  return ELECCIONES.get(juegoId);
}

function botones(valores, etiquetas, elegido, alElegir) {
  return el('div', { class: 'fila' }, valores.map((valor, indice) =>
    el('button', {
      class: `boton ${elegido === valor ? '' : 'boton--plano'}`,
      type: 'button',
      texto: etiquetas[indice],
      onclick: () => alElegir(valor),
    })));
}

export function vistaJuego(juegoId) {
  const encontrado = buscarJuego(juegoId) || { id: juegoId, titulo: juegoId };
  const guardado = eleccionDe(juegoId);
  const niveles = encontrado.niveles || ['medio'];
  const datos = {
    nivel: guardado.nivel && niveles.includes(guardado.nivel)
      ? guardado.nivel
      : (niveles.includes('medio') ? 'medio' : niveles[0]),
    cantidad: guardado.cantidad || 8,
    tema: guardado.tema || '',
  };

  return {
    titulo: () => encontrado.titulo,
    sub: () => encontrado.resumen || '',
    pie: () => encontrado.mecanica || '',

    async entrar(raiz) {
      raiz.append(el('div', { class: 'cargando' }, [
        el('div', { class: 'cargando__punto' }),
        el('p', { texto: 'Preparando el juego…' }),
      ]));

      let temas = [];
      try {
        temas = (await api.get('/api/temas')).temas || [];
      } catch {
        temas = [];
      }

      const record = estado.recordsJuego?.[encontrado.id];
      raiz.replaceChildren();

      if (record?.pct !== undefined) {
        raiz.append(el('p', { class: 'tarjeta__nota',
          texto: `Tu mejor marca: ${Math.round(record.pct)}% (${record.nivel || ''})` }));
      }

      raiz.append(el('h2', { class: 'seccion', texto: 'Nivel' }));
      raiz.append(botones(niveles,
        niveles.map((n) => NOMBRES_NIVEL[n] || n),
        datos.nivel,
        (valor) => {
          datos.nivel = valor;
          guardado.nivel = valor;
          nav.reemplazar(`juego/${juegoId}`);
        }));

      const cantidades = estado.cantidadesJuego || [5, 8, 10, 15];
      raiz.append(el('h2', { class: 'seccion', texto: 'Cuantas rondas' }));
      raiz.append(botones(cantidades, cantidades.map(String), datos.cantidad,
        (valor) => {
          datos.cantidad = valor;
          guardado.cantidad = valor;
          nav.reemplazar(`juego/${juegoId}`);
        }));

      if (temas.length > 1) {
        raiz.append(el('h2', { class: 'seccion', texto: 'Enfocar en un tema (opcional)' }));
        raiz.append(botones(['', ...temas.map((t) => t.tema)],
          ['Todos', ...temas.map((t) => t.tema_nombre)],
          datos.tema,
          (valor) => {
            datos.tema = valor;
            guardado.tema = valor;
            nav.reemplazar(`juego/${juegoId}`);
          }));
      }

      const empezar = el('button', {
        class: 'boton boton--ancho',
        type: 'button',
        texto: 'Jugar',
        onclick: async () => {
          empezar.disabled = true;
          empezar.textContent = 'Armando las rondas…';
          try {
            estado.partida = await api.post('/api/minijuegos/iniciar', {
              juego: encontrado.id,
              nivel: datos.nivel,
              cantidad: datos.cantidad,
              tema: datos.tema || null,
            });
            estado.partida.usuario = usuarioActual();
            nav.ir(`partida/${encontrado.id}`);
          } catch (error) {
            aviso(error.message, true);
            empezar.disabled = false;
            empezar.textContent = 'Jugar';
          }
        },
      });

      raiz.append(el('div', { class: 'seccion' }), empezar);
      return null;
    },
  };
}