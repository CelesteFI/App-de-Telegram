/* juegos/deslizador.js — Tinder de ED con sellos animados. */

import { escLatex, mateEcuacion, pintarMatematica } from '../dom.js';

export default {
  id: 'deslizador',

  crear({ ronda }) {
    let posicion = 0.5;
    const id = `deslizador-${ronda.id}`;

    // Regla oficial del juego (app/minijuegos/deslizador.py + mecanica):
    // DERECHA = Verdadero, IZQUIERDA = Falso. El slider va de 0 (izq) a 1 (der).
    const esVerdadero = () => posicion >= 0.66;
    const esFalso = () => posicion <= 0.34;

    return {
      auto: false,

      html() {
        return `
          <div class="deslizador">
            <div class="deslizador__zona" id="${id}-zona">
              <span class="deslizador__sello deslizador__sello--si" id="${id}-si">✔ CIERTO</span>
              <span class="deslizador__sello deslizador__sello--no" id="${id}-no">✘ FALSO</span>
              <div class="deslizador__formula" id="${id}-tarjeta">${mateEcuacion(ronda.formula)}</div>
              <p class="deslizador__afirmacion">❓ ${escLatex(ronda.attr)}</p>
            </div>
            <input class="deslizador__pista" id="${id}" type="range" min="0" max="100" value="50"
                   aria-label="Desliza: izquierda falso, derecha verdadero">
            <div class="deslizador__extremos">
              <span data-lado="f">✘ Falso</span>
              <span data-lado="v">✔ Verdadero</span>
            </div>
            <p class="deslizador__ayuda">⬅️ Izquierda = Falso · Derecha = Verdadero ➡️. Desliza el control hasta el extremo: el sello confirma tu voto.</p>
          </div>`;
      },

      montar() {
        pintarMatematica(document.getElementById(`${id}-zona`));
        const pista = document.getElementById(id);
        const tarjeta = document.getElementById(`${id}-tarjeta`);
        const selloSi = document.getElementById(`${id}-si`);
        const selloNo = document.getElementById(`${id}-no`);

        const reflejar = () => {
          const gira = (posicion - 0.5) * 24;
          const dx = (posicion - 0.5) * 160;
          if (tarjeta) tarjeta.style.transform = `translateX(${dx}px) rotate(${gira}deg)`;
          const votoSi = esVerdadero();
          const votoNo = esFalso();
          if (selloSi) selloSi.style.opacity = votoSi ? '1' : '0';
          if (selloNo) selloNo.style.opacity = votoNo ? '1' : '0';
          pista.dataset.lado = votoSi ? 'v' : (votoNo ? 'f' : 'm');
        };

        pista.addEventListener('input', () => {
          posicion = Number(pista.value) / 100;
          reflejar();
        });
        reflejar();
      },

      envio() {
        return esVerdadero();
      },
    };
  },
};
