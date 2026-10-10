/* inicio.js — Portada hub: todo vive en "Practicar" (quiz + minijuegos). */

import { el, plural } from '../dom.js';
import { cargarJuegos, cargarMaterias, estado, usuarioActual } from '../estado.js';
import * as nav from '../navegacion.js';

export function vistaInicio() {
  return {
    titulo: () => estado.config?.app || 'Repaso de Ecuaciones Diferenciales',
    sub: () => {
      const quien = usuarioActual();
      return quien?.nombre ? `Hola, ${quien.nombre}` : '';
    },
    pie: () => 'Todo el repaso vive en Practicar: quiz y minijuegos juntos.',

    async entrar(raiz) {
      raiz.append(el('div', { class: 'cargando' }, [
        el('div', { class: 'cargando__punto' }),
        el('p', { texto: 'Cargando tu sala de juegos…' }),
      ]));

      let nJuegos = 0;
      let nTemas = 0;
      try {
        await Promise.all([
          cargarMaterias().catch(() => {}),
          cargarJuegos().catch(() => {}),
        ]);
        nJuegos = estado.juegos.length;
        nTemas = estado.materias.reduce((a, m) => a + (m.temas || []).length, 0);
      } catch {
        /* seguimos con lo que haya */
      }
      raiz.replaceChildren();

      raiz.append(el('div', { class: 'hub' }, [
        el('div', { class: 'hub__hero' }, [
          el('h2', { texto: '🎪 ¡A repasar jugando!' }),
          el('p', { texto: `${nTemas} temas con quiz + ${nJuegos} minijuegos. Todo da puntos y guarda tu mejor marca.` }),
        ]),
        el('button', {
          class: 'boton boton--ancho',
          type: 'button',
          onclick: () => nav.ir('juegos'),
        }, [
          el('span', { texto: '🎮 Practicar: quiz + minijuegos' }),
        ]),
      ]));

      const historial = [...(estado.historialQuiz || []).slice(0, 3), ...(estado.historialJuego || []).slice(0, 3)];
      if (estado.historialQuiz?.length || estado.historialJuego?.length) {
        raiz.append(el('h2', { class: 'seccion', texto: 'Tus últimos repasos' }));
        for (const fila of (estado.historialJuego || []).slice(0, 3)) {
          raiz.append(el('div', { class: 'tarjeta' }, [
            el('span', { class: 'tarjeta__fila' }, [
              el('span', { class: 'tarjeta__icono', texto: '🎮' }),
              el('span', { class: 'tarjeta__cuerpo' }, [
                el('span', { class: 'tarjeta__titulo', texto: fila.titulo || fila.juego_id }),
                el('span', { class: 'tarjeta__nota', texto: `${fila.puntos}/${fila.max} · ${fila.fecha || ''}` }),
              ]),
              el('span', {
                class: `pildora ${fila.pct >= 70 ? 'pildora--bien' : 'pildora--mal'}`,
                texto: `${Math.round(fila.pct || 0)}%`,
              }),
            ]),
          ]));
        }
        for (const fila of (estado.historialQuiz || []).slice(0, 3)) {
          raiz.append(el('div', { class: 'tarjeta' }, [
            el('span', { class: 'tarjeta__fila' }, [
              el('span', { class: 'tarjeta__icono', texto: '📝' }),
              el('span', { class: 'tarjeta__cuerpo' }, [
                el('span', { class: 'tarjeta__titulo', texto: fila.titulo || fila.tema }),
                el('span', { class: 'tarjeta__nota', texto: `${fila.aciertos}/${fila.n_preguntas} · ${fila.fecha || ''}` }),
              ]),
              el('span', {
                class: `pildora ${fila.pct >= 70 ? 'pildora--bien' : 'pildora--mal'}`,
                texto: `${Math.round(fila.pct || 0)}%`,
              }),
            ]),
          ]));
        }
        void plural;
      }
      return null;
    },
  };
}
