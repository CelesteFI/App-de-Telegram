/* juegos/ordenar.js — Línea de tiempo: ordena los pasos del método. */

import { escLatex, pintarMatematica } from '../dom.js';

export default {
  id: 'ordenar',

  crear({ ronda }) {
    let orden = ronda.pasos.map((_, i) => i);

    function pintar() {
      const caja = document.getElementById('ordenar');
      if (!caja) return;
      caja.innerHTML = `
        <div class="ordenar">
          <p class="tarjeta__nota">🧭 <b>${escLatex(ronda.pista || 'Pon los pasos en orden')}</b> · usa ▲ ▼</p>
          ${orden.map((pasoIdx, pos) => `
            <div class="ordenar__fila">
              <span class="ordenar__pos">${pos + 1}</span>
              <span class="ordenar__texto">${escLatex(ronda.pasos[pasoIdx])}</span>
              <span class="ordenar__botones">
                <button class="boton boton--plano" type="button" data-mover="arriba" data-indice="${pos}"
                        ${pos === 0 ? 'disabled' : ''} aria-label="subir">▲</button>
                <button class="boton boton--plano" type="button" data-mover="abajo" data-indice="${pos}"
                        ${pos === orden.length - 1 ? 'disabled' : ''} aria-label="bajar">▼</button>
              </span>
            </div>`).join('')}
        </div>`;
      pintarMatematica(caja);
    }

    function mover(pos, sentido) {
      const dest = pos + (sentido === 'arriba' ? -1 : 1);
      if (dest < 0 || dest >= orden.length) return;
      const copia = [...orden];
      [copia[pos], copia[dest]] = [copia[dest], copia[pos]];
      orden = copia;
      pintar();
      const filas = document.querySelectorAll('.ordenar__fila');
      filas[dest]?.animate?.(
        [{ transform: 'translateX(0)' }, { transform: 'translateX(8px)' }, { transform: 'translateX(0)' }],
        { duration: 220 });
    }

    return {
      auto: false,

      html() {
        return '<div id="ordenar"></div>';
      },

      montar() {
        pintar();
        document.getElementById('ordenar').addEventListener('click', (evento) => {
          const boton = evento.target.closest('button[data-mover]');
          if (!boton || boton.disabled) return;
          mover(Number(boton.dataset.indice), boton.dataset.mover);
        });
      },

      envio() {
        return orden;
      },
    };
  },
};
