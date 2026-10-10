/* juegos/clasificador.js — Encesta cada ecuacion en su canasta literal. */

import { escLatex, mateEcuacion, pintarMatematica } from '../dom.js';

const EMOJIS = ['🧺', '🧺', '🧺', '🧺'];

export default {
  id: 'clasificador',

  crear({ ronda, responder, temporizador }) {
    const asignado = new Map();
    let seleccionado = null;
    let segundos = ronda.segundos || 20;
    const reloj = { nodo: null };

    function conteoDe(clave) {
      return [...asignado.values()].filter((v) => v === clave).length;
    }

    function pintar() {
      const caja = document.getElementById('clasificador');
      if (!caja) return;
      caja.innerHTML = `
        <div class="clasificador">
          <p class="clasificador__reloj">⏳ Toca una tarjeta y luego su 🧺 cesta · <span id="clasificador-reloj">${segundos} s</span> · ${asignado.size}/${ronda.items.length}</p>
          <div class="clasificador__items">
            ${ronda.items.map((item) => `
              <button class="clasificador__item ${asignado.has(item.id) ? 'clasificador__item--puesto' : ''} ${seleccionado === item.id ? 'clasificador__item--elegido' : ''}"
                      type="button" data-id="${item.id}" ${asignado.has(item.id) ? 'disabled' : ''}>
                🃏 ${mateEcuacion(item.tex)}
              </button>`).join('')}
          </div>
          <div class="clasificador__canastas">
            ${ronda.canastas.map((canasta, i) => `
              <button class="clasificador__canasta" type="button" data-clave="${canasta.clave}" data-i="${i}">
                <span style="font-size:11px;opacity:.85">${EMOJIS[i % EMOJIS.length]} cesta</span>
                <span class="clasificador__canasta-titulo">${escLatex(canasta.nombre)}</span>
                <span class="clasificador__canasta-conteo">🍩 ${conteoDe(canasta.clave)} encestadas</span>
              </button>`).join('')}
          </div>
        </div>`;
      reloj.nodo = document.getElementById('clasificador-reloj');
      pintarMatematica(caja);
    }

    function volar(origenBtn, destinoBtn, alTerminar) {
      const o = origenBtn.getBoundingClientRect();
      const d = destinoBtn.getBoundingClientRect();
      const clon = origenBtn.cloneNode(true);
      clon.classList.add('clasificador__item--volando');
      Object.assign(clon.style, {
        left: `${o.left}px`, top: `${o.top}px`,
        width: `${o.width}px`, margin: '0',
      });
      document.body.appendChild(clon);
      requestAnimationFrame(() => {
        Object.assign(clon.style, {
          left: `${d.left + d.width / 2 - o.width / 2}px`,
          top: `${d.top + 10}px`,
          transform: 'scale(.4) rotate(18deg)',
          opacity: '.4',
        });
      });
      setTimeout(() => { clon.remove(); alTerminar(); }, 560);
    }

    function terminar() {
      responder(Object.fromEntries(asignado));
    }

    return {
      auto: true,

      html() {
        return '<div id="clasificador"></div>';
      },

      montar() {
        pintar();
        const caja = document.getElementById('clasificador');
        caja.addEventListener('click', (evento) => {
          const item = evento.target.closest('.clasificador__item');
          if (item && !item.disabled) {
            seleccionado = seleccionado === item.dataset.id ? null : item.dataset.id;
            pintar();
            return;
          }
          const canasta = evento.target.closest('.clasificador__canasta');
          if (!canasta) return;
          if (!seleccionado) {
            canasta.animate?.(
              [{ transform: 'rotate(0)' }, { transform: 'rotate(-4deg)' },
               { transform: 'rotate(4deg)' }, { transform: 'rotate(0)' }],
              { duration: 260 });
            return;
          }
          const idSel = seleccionado;
          const btnOrigen = caja.querySelector(`.clasificador__item[data-id="${idSel}"]`);
          seleccionado = null;
          volar(btnOrigen, canasta, () => {
            asignado.set(idSel, canasta.dataset.clave);
            pintar();
            const nueva = document.querySelector(`.clasificador__canasta[data-clave="${canasta.dataset.clave}"]`);
            nueva?.classList.add('clasificador__canasta--llena');
            setTimeout(() => nueva?.classList.remove('clasificador__canasta--llena'), 450);
            if (asignado.size === ronda.items.length) terminar();
          });
        });

        temporizador(() => {
          segundos = Math.max(0, segundos - 1);
          const relojFresco = document.getElementById('clasificador-reloj');
          if (relojFresco) relojFresco.textContent = `${segundos} s`;
          if (segundos === 0) terminar();
        }, 1000);
      },

      envio() {
        return Object.fromEntries(asignado);
      },
    };
  },
};
