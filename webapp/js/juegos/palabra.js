/* juegos/palabra.js — Concurso de la palabra oculta con teclado saltarín. */

import { escLatex, pintarMatematica } from '../dom.js';

export default {
  id: 'palabra',

  crear({ ronda }) {
    let palabra = '';

    function pintar(nueva = -1) {
      const caja = document.getElementById('palabra');
      if (!caja) return;
      const huecos = Array.from({ length: ronda.longitud }, (_, i) =>
        `<span class="palabra__hueco ${i === nueva ? 'palabra__hueco--nuevo' : ''}">${palabra[i] || '·'}</span>`).join('');
      caja.innerHTML = `
        <div class="palabra">
          <p class="palabra__pista">🎪 Pista: ${escLatex(ronda.pista)} <br><small>${palabra.length}/${ronda.longitud} letras</small></p>
          <div class="palabra__huecos">${huecos}</div>
          <div class="palabra__teclado">
            ${ronda.teclado.map((letra) => `
              <button class="palabra__tecla" type="button" data-letra="${letra}">${letra}</button>`).join('')}
          </div>
          <button class="boton boton--plano boton--ancho" type="button" id="palabra-borrar">⌫ Borrar letra</button>
        </div>`;
      pintarMatematica(caja);
    }

    return {
      auto: false,

      html() {
        return '<div id="palabra"></div>';
      },

      montar() {
        pintar();
        const caja = document.getElementById('palabra');
        caja.addEventListener('click', (evento) => {
          const tecla = evento.target.closest('[data-letra]');
          if (tecla) {
            if (palabra.length < ronda.longitud) {
              palabra += tecla.dataset.letra;
              tecla.animate?.([{ transform: 'scale(1)' }, { transform: 'scale(1.25) rotate(-6deg)' }, { transform: 'scale(1)' }], { duration: 220 });
              pintar(palabra.length - 1);
            }
            return;
          }
          if (evento.target.id === 'palabra-borrar' || evento.target.closest('#palabra-borrar')) {
            palabra = palabra.slice(0, -1);
            pintar();
          }
        });
      },

      envio() {
        return palabra;
      },
    };
  },
};
