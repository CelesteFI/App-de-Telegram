/* reporte.js — Pantalla de resultados, compartida por quiz y minijuegos. */

import { el, escLatex, letras, pintarMatematica, segundos } from '../dom.js';

function valor(nota) {
  if (nota >= 90) return 'pildora--bien';
  if (nota >= 60) return '';
  return 'pildora--mal';
}

function detalleQuiz(reporte) {
  return el('div', { class: 'detalle' }, (reporte.detalle || []).map((fila) => el('div', {
    class: 'detalle__fila',
  }, [
    el('span', {
      class: `detalle__marca ${fila.ok ? 'detalle__marca--ok' : 'detalle__marca--no'}`,
      texto: fila.ok ? '✓' : (fila.saltada ? '–' : '✗'),
    }),
    el('span', { class: 'detalle__cuerpo' }, [
      el('div', { html: escLatex(fila.p) }),
      el('div', {
        class: 'detalle__texto',
        html: `Tu respuesta: ${fila.saltada ? 'saltada'
          : escLatex(fila.opciones?.[fila.elige] ?? '—')} · ` +
          `Correcta: ${letras(fila.correcta)}`,
      }),
      fila.explicacion
        ? el('div', { class: 'detalle__texto', html: escLatex(fila.explicacion) })
        : null,
    ]),
  ])));
}

function detalleJuego(reporte) {
  return el('div', { class: 'detalle' }, (reporte.detalle || []).map((fila) => el('div', {
    class: 'detalle__fila',
  }, [
    el('span', {
      class: `detalle__marca ${fila.correcto ? 'detalle__marca--ok' : 'detalle__marca--no'}`,
      texto: fila.correcto ? '✓' : '✗',
    }),
    el('span', { class: 'detalle__cuerpo' }, [
      el('div', { texto: `Ronda ${fila.pos + 1} · ${fila.puntaje} puntos` }),
      el('div', { class: 'detalle__texto', html: escLatex(fila.detalle || '') }),
    ]),
  ])));
}

export function pintarReporte(raiz, reporte, titulo = 'Resultado', alVolver = null) {
  if (!reporte) {
    raiz.replaceChildren(el('div', { class: 'vacio', texto: 'No hay resultado que mostrar.' }));
    return;
  }
  const esQuiz = typeof reporte.aciertos === 'number';
  const nota = Number(reporte.pct) || 0;

  const acciones = [];
  if (alVolver) {
    acciones.push(el('button', {
      class: 'boton',
      type: 'button',
      texto: 'Volver al inicio',
      onclick: alVolver,
    }));
  }
  const repetir = el('button', {
    class: 'boton boton--plano',
    type: 'button',
    texto: 'Repetir',
    onclick: () => location.reload(),
  });
  acciones.push(repetir);

  raiz.replaceChildren(
    el('div', { class: 'cifra' }, [
      el('div', { class: 'cifra__valor', texto: `${Math.round(nota)}%` }),
      el('div', {
        class: 'cifra__nota',
        texto: esQuiz
          ? `${reporte.aciertos} de ${reporte.n_preguntas} · ${segundos(reporte.duracion)}`
          : `${reporte.puntos} de ${reporte.max} puntos · ${reporte.n_rondas} rondas`,
      }),
    ]),
    el('div', { class: 'fila' }, [
      el('span', { class: `pildora ${valor(nota)}`, texto: titulo }),
      reporte.record
        ? el('span', { class: 'pildora', texto: `Mejor marca ${Math.round(reporte.record.pct)}%` })
        : null,
    ]),
    el('h2', { class: 'seccion', texto: 'Como te fue pregunta por pregunta' }),
    esQuiz ? detalleQuiz(reporte) : detalleJuego(reporte),
    el('div', { class: 'seccion' }),
    el('div', { class: 'fila' }, acciones),
  );
  pintarMatematica(raiz);
}