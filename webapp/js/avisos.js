/* avisos.js — Mensajes flotantes para errores y confirmaciones cortas. */

const contenedor = () => document.getElementById('avisos');

export function aviso(mensaje, esError = false, ms = 3200) {
  const caja = contenedor();
  if (!caja) return;
  const nodo = document.createElement('div');
  nodo.className = esError ? 'aviso aviso--error' : 'aviso';
  nodo.textContent = mensaje;
  caja.append(nodo);
  setTimeout(() => nodo.remove(), ms);
}

export function confirmar(texto, alAceptar) {
  const caja = contenedor();
  if (!caja) return;
  const fila = document.createElement('div');
  fila.className = 'aviso';
  const etiqueta = document.createElement('span');
  etiqueta.textContent = texto;
  const acciones = document.createElement('div');
  acciones.className = 'fila';
  acciones.style.marginTop = '8px';

  const no = document.createElement('button');
  no.className = 'boton boton--plano';
  no.textContent = 'Cancelar';
  const si = document.createElement('button');
  si.className = 'boton';
  si.textContent = 'Salir';
  si.onclick = () => {
    fila.remove();
    alAceptar();
  };
  no.onclick = () => fila.remove();

  acciones.append(no, si);
  fila.append(etiqueta, acciones);
  caja.append(fila);
}