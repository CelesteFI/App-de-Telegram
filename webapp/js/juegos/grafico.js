/* juegos/grafico.js — Laboratorio de campos: toca la región correcta. */

import { mateEcuacion } from '../dom.js';

const ETIQUETAS = {
  bandas_y: '🌊 Bandas horizontales',
  verticales_x: '🎋 Trazados verticales',
  circular: '🌀 Trayectorias circulares',
  recta: '📏 Rectas',
  ninguna: '🌫️ Sin campo claro',
};

export default {
  id: 'grafico',

  crear({ ronda }) {
    let elegido = -1;

    return {
      auto: false,

      html() {
        const pistas = ronda.tipos
          .map((tipo, i) => `<li data-i="${i}" class="${elegido === i ? 'elegida' : ''}">${i + 1}. ${ETIQUETAS[tipo] || tipo}</li>`)
          .join('');
        return `
          <div class="grafico">
            <p class="pregunta">🔭 ¿Qué campo corresponde a ${mateEcuacion(ronda.ecuacion)}?</p>
            <div class="grafico__marco">
              <canvas class="grafico__lienzo" id="grafico-lienzo" width="640" height="420"
                      role="img" aria-label="Plano de fases por tocar"></canvas>
              <ol class="grafico__pistas">${pistas}</ol>
            </div>
            <p class="tarjeta__nota">👆 Toca la <b>región del dibujo</b> que creas correcta: arriba, abajo-izq o abajo-der.</p>
          </div>`;
      },

      montar() {
        const lienzo = document.getElementById('grafico-lienzo');
        const ctx = lienzo.getContext('2d');
        const regiones = dibujarPlano(ctx, lienzo, elegido);

        const marcar = (i) => {
          if (i < 0) return;
          elegido = i;
          dibujarPlano(ctx, lienzo, elegido);
          document.querySelectorAll('.grafico__pistas li').forEach((li) => {
            li.classList.toggle('elegida', Number(li.dataset.i) === i);
          });
          lienzo.animate?.([{ transform: 'scale(1)' }, { transform: 'scale(1.015)' }, { transform: 'scale(1)' }], { duration: 250 });
        };

        const toPos = (evento) => {
          const caja = lienzo.getBoundingClientRect();
          const cx = (evento.clientX ?? (evento.touches?.[0]?.clientX || 0));
          const cy = (evento.clientY ?? (evento.touches?.[0]?.clientY || 0));
          const x = ((cx - caja.left) / caja.width) * lienzo.width;
          const y = ((cy - caja.top) / caja.height) * lienzo.height;
          for (const r of regiones) {
            if (x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1) return r.indice;
          }
          return -1;
        };

        lienzo.addEventListener('click', (e) => marcar(toPos(e)));
        document.querySelectorAll('.grafico__pistas li').forEach((li) => {
          li.style.cursor = 'pointer';
          li.addEventListener('click', () => marcar(Number(li.dataset.i)));
        });
      },

      envio() {
        return elegido;
      },
    };
  },
};

function dibujarPlano(ctx, lienzo, elegido = -1) {
  const w = lienzo.width;
  const h = lienzo.height;
  const x0 = 40;
  const x1 = w - 40;
  const y0 = 30;
  const y1 = h - 30;
  const medio = (x0 + x1) / 2;

  const grad = ctx.createLinearGradient(0, 0, w, h);
  grad.addColorStop(0, '#0f172a');
  grad.addColorStop(0.55, '#1e1b4b');
  grad.addColorStop(1, '#500f28');
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // estrellas decorativas
  ctx.fillStyle = 'rgba(255,255,255,.5)';
  for (let s = 0; s < 24; s += 1) {
    const sx = (s * 173) % w;
    const sy = (s * 97) % h;
    ctx.fillRect(sx, sy, 2, 2);
  }

  const regiones = [
    { indice: 0, x0, x1, y0, y1: y0 + (y1 - y0) / 2, color: '#22d3ee' },
    { indice: 1, x0, x1: medio, y0: y0 + (y1 - y0) / 2, y1, color: '#a3e635' },
    { indice: 2, x0: medio, x1, y0: y0 + (y1 - y0) / 2, y1, color: '#fb7185' },
  ];

  ctx.lineWidth = 2;
  ctx.strokeStyle = '#e2e8f0';
  ctx.beginPath();
  ctx.moveTo(x0, y1);
  ctx.lineTo(x1, y1);
  ctx.moveTo(x0, y1);
  ctx.lineTo(x0, y0);
  ctx.stroke();

  ctx.beginPath();
  ctx.setLineDash([6, 6]);
  ctx.strokeStyle = 'rgba(226,232,240,.5)';
  ctx.moveTo(x0, (y0 + y1) / 2);
  ctx.lineTo(x1, (y0 + y1) / 2);
  ctx.moveTo(medio, y0);
  ctx.lineTo(medio, y1);
  ctx.stroke();
  ctx.setLineDash([]);

  for (const r of regiones) {
    const activo = elegido === r.indice;
    ctx.fillStyle = activo ? `${r.color}55` : 'rgba(255,255,255,.06)';
    ctx.fillRect(r.x0, r.y0, r.x1 - r.x0, r.y1 - r.y0);
    ctx.strokeStyle = activo ? '#facc15' : r.color;
    ctx.lineWidth = activo ? 4 : 2;
    ctx.strokeRect(r.x0, r.y0, r.x1 - r.x0, r.y1 - r.y0);
    if (activo) {
      ctx.font = '900 30px system-ui, sans-serif';
      ctx.textAlign = 'right';
      ctx.fillStyle = '#facc15';
      ctx.fillText('✔', r.x1 - 12, r.y0 + 34);
    }
  }

  const flecha = (ax, ay, bx, by, color) => {
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(bx, by);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(bx, by);
    ctx.lineTo(bx - 9, by - 5);
    ctx.lineTo(bx - 9, by + 5);
    ctx.closePath();
    ctx.fill();
  };

  const titulo = (texto, x, y, color) => {
    ctx.font = '700 21px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = color;
    ctx.fillText(texto, x, y);
  };

  for (let k = 1; k <= 3; k += 1) {
    const y = y0 + ((y1 - y0) / 4) * k;
    flecha(x0 + 20, y, x1 - 20, y, '#22d3ee');
  }
  titulo('🌊 1. Bandas horizontales', (x0 + x1) / 2, y0 + 34, '#a5f3fc');

  ctx.setLineDash([10, 8]);
  for (let k = 1; k <= 3; k += 1) {
    const x = x0 + ((x1 - x0) / 4) * k;
    flecha(x, y1 - 20, x, y0 + 20, '#a3e635');
  }
  ctx.setLineDash([]);
  titulo('🎋 2. Verticales', (x0 + medio) / 2, y1 - 30, '#d9f99d');

  for (const centro of [[x0 + (x1 - x0) * 0.25, y0 + (y1 - y0) * 0.75], [x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.75]]) {
    ctx.strokeStyle = '#fb7185';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(centro[0], centro[1], 34, 0, Math.PI * 2);
    ctx.stroke();
    flecha(centro[0] + 34, centro[1], centro[0] - 20, centro[1] - 24, '#fb7185');
  }
  titulo('🌀 3. Circulares', (medio + x1) / 2, y1 - 30, '#fecdd3');

  ctx.font = '700 26px system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillStyle = '#e2e8f0';
  ctx.fillText('y', x0 - 22, y0 + 14);
  ctx.fillText('x', x1 + 24, y1 + 6);
  return regiones;
}
