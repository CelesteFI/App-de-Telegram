/* juegos.js — Catálogo unificado: Quiz + los diez minijuegos. */

import { el, plural } from '../dom.js';
import { cargarJuegos, cargarMaterias, estado } from '../estado.js';
import * as nav from '../navegacion.js';

const NOMBRES_NIVEL = { facil: 'Fácil', medio: 'Normal', dificil: 'Difícil' };

const COLORES = [
  'linear-gradient(135deg,#0284c7,#22d3ee)',
  'linear-gradient(135deg,#7c3aed,#db2777)',
  'linear-gradient(135deg,#16a34a,#84cc16)',
  'linear-gradient(135deg,#ea580c,#facc15)',
  'linear-gradient(135deg,#db2777,#f97316)',
  'linear-gradient(135deg,#059669,#22d3ee)',
  'linear-gradient(135deg,#4c1d95,#ec4899)',
  'linear-gradient(135deg,#b45309,#ef4444)',
  'linear-gradient(135deg,#0d9488,#84cc16)',
  'linear-gradient(135deg,#1d4ed8,#a855f7)',
];

function tarjetaJuego(juego, record, i) {
  const niveles = (juego.niveles || []).map((n) => NOMBRES_NIVEL[n] || n).join(' · ');
  const marca = record?.pct !== undefined ? `🏆 mejor ${Math.round(record.pct)}%` : niveles;
  return el('button', {
    class: 'hub__card',
    type: 'button',
    onclick: () => nav.ir(`juego/${juego.id}`),
  }, [
    el('span', { class: 'hub__emoji', texto: juego.icono || '🎲' }),
    el('span', { class: 'hub__titulo', texto: juego.titulo }),
    el('span', { class: 'hub__nota', texto: `${juego.resumen || ''} · ${marca}` }),
  ]);
}

export function vistaJuegos() {
  return {
    titulo: () => 'Practicar',
    sub: () => 'Quiz + minijuegos de teoría',
    pie: () => 'Todo se califica en el servidor y guarda tu mejor marca.',

    async entrar(raiz) {
      raiz.append(el('div', { class: 'cargando' }, [
        el('div', { class: 'cargando__punto' }),
        el('p', { texto: 'Armando tu sala de juegos…' }),
      ]));
      try {
        await Promise.all([cargarJuegos(), cargarMaterias().catch(() => {})]);
      } catch (error) {
        raiz.replaceChildren(el('div', { class: 'vacio', texto: error.message }));
        return null;
      }
      raiz.replaceChildren();

      // ---- 1) Quiz como un juego más ----
      const temas = [];
      for (const materia of estado.materias || []) {
        for (const tema of materia.temas || []) temas.push({ materia, tema });
      }
      raiz.append(el('h2', { class: 'seccion', texto: `📝 Quiz por tema (${temas.length})` }));
      const gridQuiz = el('div', { class: 'hub__grid' });
      temas.forEach(({ materia, tema }, i) => {
        const record = estado.recordsQuiz?.[tema.id];
        const card = el('button', {
          class: 'hub__card',
          type: 'button',
          onclick: () => { if (tema.disponible) nav.ir(`tema/${materia.id}/${tema.id}`); },
        }, [
          el('span', { class: 'hub__emoji', texto: '📝' }),
          el('span', { class: 'hub__titulo', texto: tema.nombre }),
          el('span', {
            class: 'hub__nota',
            texto: record?.pct !== undefined
              ? `🏆 mejor ${Math.round(record.pct)}% · ${plural(tema.total || 0, 'pregunta', 'preguntas')}`
              : (tema.resumen || plural(tema.total || 0, 'pregunta', 'preguntas')),
          }),
        ]);
        card.style.background = 'linear-gradient(135deg,#1e1b4b,#7c3aed 60%,#db2777)';
        void i;
        gridQuiz.append(card);
      });
      if (!temas.length) gridQuiz.append(el('div', { class: 'vacio', texto: 'Sin temas por ahora.' }));
      raiz.append(gridQuiz);

      // ---- 2) Minijuegos ----
      raiz.append(el('h2', { class: 'seccion', texto: `🎮 Minijuegos (${plural(estado.juegos.length, 'juego', 'juegos')})` }));
      const grid = el('div', { class: 'hub__grid' });
      estado.juegos.forEach((juego, i) => {
        const card = tarjetaJuego(juego, estado.recordsJuego?.[juego.id], i);
        card.style.background = COLORES[i % COLORES.length];
        grid.append(card);
      });
      raiz.append(grid);

      const historial = estado.historialJuego || [];
      if (historial.length) {
        raiz.append(el('h2', { class: 'seccion', texto: 'Tus últimas partidas' }));
        for (const fila of historial.slice(0, 5)) {
          raiz.append(el('div', { class: 'tarjeta' }, [
            el('span', { class: 'tarjeta__fila' }, [
              el('span', { class: 'tarjeta__cuerpo' }, [
                el('span', { class: 'tarjeta__titulo', texto: fila.titulo || fila.juego_id }),
                el('span', {
                  class: 'tarjeta__nota',
                  texto: `${fila.puntos}/${fila.max} · ${fila.fecha || ''}`,
                }),
              ]),
              el('span', {
                class: `pildora ${fila.pct >= 70 ? 'pildora--bien' : 'pildora--mal'}`,
                texto: `${Math.round(fila.pct || 0)}%`,
              }),
            ]),
          ]));
        }
      }
      return null;
    },
  };
}
