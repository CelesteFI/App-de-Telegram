# Cómo probar la Mini App (guía rápida)

Guía para verificar en tu equipo los últimos cambios: deslizador de atributos,
memorama y renderizado de ecuaciones.

---

## 1. Arrancar todo

Desde la carpeta del proyecto:

```powershell
.\run.ps1
```

Deja esa ventana **abierta**. Salidas esperadas:

```
URL publica HTTPS (Cloudflare): https://xxxx.trycloudflare.com
URL publica verificada (HTTPS): https://xxxx.trycloudflare.com
Lanzando bot.py ... Ctrl+C para terminar.
```

La primera vez puede tardar un poco más: `run.ps1` descarga solo
`cloudflared.exe` (una única vez) para abrir el túnel sin pantalla de aviso.

## 2. Abrir en el navegador

1. Copia la URL publica HTTPS que imprime `run.ps1`.
2. Pegala en el navegador.
3. Con Cloudflare no hay ninguna pantalla de aviso: entra directo.
   (Si usas `-Tunel ngrok`, sí aparece el aviso del plan gratis: pulsa
   **Visit** una vez y queda guardado 7 dias.)
4. En la primera prueba, recarga con **Ctrl+Shift+R** para descartar lo que el
   navegador hubiera guardado antes. Despues ya no hace falta.

Tambien sirve `http://localhost:8081` para revisar rapido desde el mismo
navegador.

Si la app no carga, veras un aviso con botón **Reintentar** (ya no se queda
en "Cargando la app…" para siempre): revisa que la ventana de `run.ps1` siga
abierta y toca Reintentar.

## 3. Probar desde Telegram

1. Abre Telegram y busca tu bot.
2. Enviale `/start`.
3. Pulsa el **boton del mensaje nuevo** que acaba de aparecer. El bot de esta
   corrida apunta a la URL del tunel de esta corrida. El botón de menú
   **«Repaso ED»** también se actualiza solo al arrancar el bot.
4. No abras la app desde mensajes viejos: apuntaban a URLs anteriores que ya
   no existen.

## 4. Que revisar

### Deslizador de atributos (juego deslizador)

Regla oficial (documentada en `Minijuegos.md`):

| Posicion | Resultado |
|---|---|
| Derecha | **Verdadero** |
| Izquierda | **Falso** |

- [ ] Al soltar el control al extremo **derecho**, marca **Verdadero**.
- [ ] Al soltarlo al extremo **izquierdo**, marca **Falso**.
- [ ] **Ya no hay botones** de "Falso" ni "Verdadero" al lado del control.
- [ ] El sello verde (V) queda en el lado derecho.
- [ ] El sello de la derecha dice "Verdadero"; el de la izquierda, "Falso".

Si sigue invertido, **no sigas probando**: avisame, porque significa que el
navegador sirvio una version vieja y hay que limpiar la cache.

### Memorama

- [ ] **Todas las cartas tapadas muestran el mismo emoji** (estrella).
- [ ] Al voltear dos cartas se ven las caras con las ecuaciones renderizadas.
- [ ] Al emparejar todas, se muestra el resumen con las ecuaciones bien escritas.

### Ecuaciones (KaTeX)

Revisa que las ecuaciones aparezcan **dibujadas** (con fracciones, exponentes y
simbolos), no como texto plano como `x^2` o `\frac{1}{2}`.

- [ ] Memorama: las cartas y el resumen.
- [ ] Intruso y clasificador: las tarjetas.
- [ ] Completar: el enunciado y las opciones.
- [ ] Globos: las etiquetas de cada globo.
- [ ] Columnas: los textos de las columnas.
- [ ] Ordenar: los pasos.
- [ ] Grafico: la ecuacion de la recta.
- [ ] Deslizador: la formula de la ronda.

## 5. Problemas frecuentes

### Veo la version vieja (botones, emoji variados, texto plano)

El navegador guardo los modulos JS. Solucion:

- Recarga con **Ctrl+Shift+R**.
- Si sigue igual, abre una ventana de incógnito y prueba ahi.
- Si **tampoco** funciona en incógnito, cierra y vuelve a levantar `.\run.ps1`
  y escribe `/start` de nuevo en el bot.

### "La URL publica responde, pero no parece la app"

Ocurre cuando el tunel apunta a un puerto distinto al del servidor. Revisa que
el puerto que imprime `run.ps1` sea el mismo que usa el backend.

### La Mini App se queda cargando en Telegram

Ya no deberia pasar. Si ocurre:

- Comprueba que NO estés usando ngrok en plan gratis (`-Tunel ngrok`): su
  pantalla de aviso deja la Mini App colgada. Usa el modo por defecto
  (Cloudflare) o `-Tunel cloudflare`.
- Revisa que la ventana de `run.ps1` siga abierta y que la URL pública
  aparezca como **verificada** en la consola.
- Cierra y vuelve a levantar `.\run.ps1` y escribe `/start` de nuevo.

### El bot no responde

- `run.ps1` debe seguir corriendo en su ventana.
- Revisa que el token del bot sea valido.
- El script cierra bots/servidores/tuneles viejos al arrancar, asi que no hace
  falta matarlos a mano.
- Para detener todo: **Ctrl+C** en la ventana de `run.ps1`.

---

## 6. Volver a parar

**Ctrl+C** en la ventana de `run.ps1`. Eso detiene el servidor, el túnel y el bot.

La URL del túnel **cambia en cada corrida** (es aleatoria). Si quieres que sea
siempre la misma, hay que usar un dominio propio (Cloudflare nombrado o ngrok
de pago). Da igual: el bot actualiza sus botones y el de menú en cada arranque.