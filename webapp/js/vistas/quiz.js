/* quiz.js — Show de concurso: pregunta, respuesta inmediata y explicación. */

import { api } from '../api.js';
import { aviso } from '../avisos.js';
import { alPintar, avisarMarco, el, escLatex, letras, pintarMatematica } from '../dom.js';
import { estado } from '../estado.js';
import * as nav from '../navegacion.js';
import { pintarReporte } from './reporte.js';

let acertados = 0;

function barraProgreso(pos, total) {
  const ancho = el('div', { class: 'progreso__barra' });
  ancho.style.width = `${total ? (pos / total) * 100 : 0}%`;
  return el('div', { class: 'progreso' }, ancho);
}

function pintarPregunta(raiz, vista, responder) {
  raiz.replaceChildren();
  raiz.append(barraProgreso(vista.pos, vista.total));

  if (vista.terminado) {
    estado.quiz = null;
    pintarReporte(raiz, vista.reporte, 'Quiz terminado', () => nav.ir('juegos'));
    return;
  }

  const show = el('div', { class: 'quizshow' });
  show.append(el('div', { class: 'quizshow__focos', texto: '✨ 📝 ✨' }));
  show.append(el('div', { class: 'quizshow__pregunta', html: `🎙️ ${escLatex(vista.pregunta.p)}` }));
  if (vista.pregunta.f) {
    show.append(el('div', { class: 'quizshow__formula', html: escLatex(vista.pregunta.f) }));
  }

  const lista = el('div', { class: 'quizshow__opciones' });
  const botones = vista.pregunta.opciones.map((_, indice) =>
    el('button', {
      class: 'quizshow__opcion',
      type: 'button',
      onclick: () => responder(indice, lista, show),
    }, [
      el('span', { class: 'quizshow__letra', texto: letras(indice) }),
      el('span', { html: escLatex(vista.pregunta.opciones[indice]) }),
    ]));
  lista.append(...botones);
  show.append(lista);
  raiz.append(show);

  const saltar = el('button', {
    class: 'boton boton--plano boton--ancho',
    type: 'button',
    texto: '⏭️ No la sé, pasar',
    onclick: async () => {
      saltar.disabled = true;
      await responder(-1, lista, show);
    },
  });
  raiz.append(el('div', { class: 'seccion' }), saltar);
  pintarMatematica(raiz);
}

function mostrarResultado(acierto, texto) {
  return el('p', {
    class: `explica explica--${acierto ? 'bien' : 'mal'}`,
    html: `${acierto ? '🎉 ¡Correcto!' : '💥 No era esa.'} ${escLatex(texto || '')}`,
  });
}

export function vistaQuiz() {
  return {
    titulo: () => estado.quiz?.titulo || 'Quiz',
    sub: () => (estado.quiz ? `${estado.quiz.materia} · ${estado.quiz.tema}` : ''),
    marcador: () => {
      if (!estado.quiz || estado.quiz.terminado) return '';
      const pos = estado.quiz.pos || 0;
      const total = estado.quiz.total || 1;
      return `<span class="pildora">${pos + 1}/${total}</span>` +
             `<span class="pildora pildora--bien">⭐ ${acertados}</span>`;
    },
    pie: () => 'El quiz vive dentro de Practicar, como un minijuego más.',

    async entrar(raiz) {
      if (!estado.quiz) {
        raiz.append(
          el('div', { class: 'vacio', texto: 'No hay ningún quiz en marcha.' }),
          el('button', {
            class: 'boton boton--ancho',
            type: 'button',
            texto: '🎮 Ir a Practicar',
            onclick: () => nav.ir('juegos'),
          }),
        );
        return null;
      }

      let datos = estado.quiz;
      if (datos.pos === 0) acertados = 0;

      async function refrescar() {
        datos = await api.get(`/api/quiz/estado?intento=${datos.intento}`);
        estado.quiz = datos.terminado ? null : datos;
        pintarPregunta(raiz, datos, responder);
      }

      async function responder(elegida, lista, show) {
        const botones = [...lista.querySelectorAll('button')];
        for (const boton of botones) boton.disabled = true;

        let veredicto;
        try {
          veredicto = elegida < 0
            ? await api.post('/api/quiz/saltar', { intento: datos.intento, pos: datos.pos })
            : await api.post('/api/quiz/responder',
                { intento: datos.intento, pos: datos.pos, opcion: elegida });
        } catch (error) {
          aviso(error.message, true);
          await refrescar();
          return;
        }

        if (elegida >= 0 && veredicto.acierto) acertados += 1;
        if (elegida >= 0 && botones[elegida]) botones[elegida].classList.add('quizshow__opcion--mal');
        if (veredicto.correcta !== undefined && botones[veredicto.correcta]) {
          botones[veredicto.correcta].classList.add('quizshow__opcion--bien');
        }
        show.after(mostrarResultado(elegida >= 0 && veredicto.acierto,
          veredicto.explicacion));
        pintarMatematica(raiz);
        avisarMarco();
        void alPintar;

        const siguiente = el('button', {
          class: 'boton boton--ancho',
          type: 'button',
          texto: veredicto.ultima ? '🏁 Ver mi resultado' : '➡️ Siguiente pregunta',
          onclick: async () => {
            if (veredicto.ultima) {
              estado.quiz = null;
              pintarReporte(raiz, veredicto.reporte, 'Quiz terminado',
                () => nav.ir('juegos'));
              return;
            }
            try {
              await refrescar();
            } catch (error) {
              aviso(error.message, true);
            }
          },
        });
        raiz.querySelector('.boton--plano')?.replaceWith(siguiente);
      }

      pintarPregunta(raiz, datos, responder);
      return null;
    },
  };
}
