/* juegos/intruso.js — Rueda de sospechosos: encuentra al que no encaja. */

import { escLatex, letras, mateEcuacion, pintarMatematica } from '../dom.js';

const AVATARES = ['🕵️', '👩‍🔬', '👨‍🔬', '🧙'];

export default {
  id: 'intruso',

  crear({ ronda }) {
    let elegido = -1;

    return {
      auto: false,

      html() {
        const tarjetas = ronda.tarjetas
          .map((carta, i) => `
            <button class="tarjeta intruso__carta ${elegido === i ? 'intruso__carta--elegida' : ''}" type="button" data-indice="${i}">
              <span class="tarjeta__fila">
                <span class="intruso__lupa" aria-hidden="true">${AVATARES[i % AVATARES.length]}</span>
                <span class="tarjeta__cuerpo">
                  <span class="opcion__letra">${letras(i)}</span>
                  <span class="intruso__tex">${mateEcuacion(carta.tex)}</span>
                </span>
                <span aria-hidden="true">${elegido === i ? '🚨' : '❔'}</span>
              </span>
            </button>`)
          .join('');
        return `
          <div class="intruso">
            <p class="intruso__pista">🔍 Caso: ${escLatex(ronda.pista)}</p>
            <div class="intruso__rejilla">${tarjetas}</div>
            <p class="tarjeta__nota">👆 Interroga a los 4 sospechosos y toca al <b>intruso</b>.</p>
          </div>`;
      },

      montar() {
        const zona = document.querySelector('.intruso');
        pintarMatematica(zona);
        zona.addEventListener('click', (evento) => {
          const carta = evento.target.closest('.intruso__carta');
          if (!carta) return;
          elegido = Number(carta.dataset.indice);
          zona.querySelectorAll('.intruso__carta').forEach((otra) => {
            const on = otra === carta;
            otra.classList.toggle('intruso__carta--elegida', on);
            otra.setAttribute('aria-disabled', on ? 'false' : 'true');
            const marca = otra.querySelector('[aria-hidden="true"]:last-child');
            if (marca) marca.textContent = on ? '🚨' : '❔';
          });
          carta.animate?.(
            [{ transform: 'rotate(0) scale(1)' }, { transform: 'rotate(-2deg) scale(1.04)' }, { transform: 'rotate(0) scale(1)' }],
            { duration: 300 });
        });
      },

      envio() {
        return elegido;
      },
    };
  },
};
