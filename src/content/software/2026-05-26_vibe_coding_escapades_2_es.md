Title: Aventuras en vibe coding: pelican-copy-code
Date: 2026-05-26
Lang: es
Category: Software
Tags: blog,ia,pelican,programación,python
Slug: vibe-coding-escapades-pelican-copy-code
Series: Aventuras en vibe coding

## El problema

Me di cuenta que este blog usa muchísimos bloques de código, pero no es fácil copiarlos porque falta un botón de *Copiar* en cada bloque.

Busqué un plugin para [Pelican](https://getpelican.com/) que lo hiciese, convencido de que habría alguno ya hecho, ¡pero me sorprendí al no encontrar nada!

Me pareció un proyecto ideal para resolver rápidamente con IA.
Podía solventar mi problema y crear un proyecto útil para la comunidad.

## Ejecución

Mi objetivo era crear un nuevo proyecto publicable a PyPI, con estos requisitos:

- Compatible con Pelican estable.
- Instalable con `pip` y con autodescubrimiento. O sea debe ser un plugin Pelican de nueva generación, no necesita añadirse en la configuración de Pelican (`pelicanconf.py`), se instala con `pip` y a correr.
- Ficheros estáticos de Javascript y CSS, sin `npm` ni similar.
- Sin dependencias externas de Javascript ni CSS, sólo APIs estándar.
- No debe necesitar cambios en las plantillas. Una vez activado el plugin inserta el botón automáticamente en todos los bloques.
- Sin manipulación del DOM, el botón se inserta al generar el sitio Pelican.
- Configurable.

Usé OpenCode (aislado, [lo describo en este otro artículo]({filename}/software/2026-05-14_how_i_sandbox_ai_agents_es.md)), inicialmente con Kimi 2.6, después con Deepseek V4 Pro, y más adelante con Claude Opus 4.7.
Comentaré los detalles en la sección de *Lecciones*.

El desarrollo fue a ratos en una tarde.
Mientras hacía otras cosas iba al ordenador, le pedía el siguiente cambio en el modo de planificación, luego volvía, revisaba rápidamente y le daba el visto bueno para implementar.

Los cambios los iba probando en local en este blog.
Simplemente instalé el plugin con `uv` en modo editable: `uv add --editable ~/Code/pelican-copy-code`

Es un proyecto muy pequeño así que no me molesté en generar ni mantener tests, *linting*, ni acciones de Github.

## Resultados

El plugin es `pelican-copy-code`, publicado en [Github](https://github.com/haplo/pelican-copy-code) y [PyPI](https://pypi.org/project/pelican-copy-code/).

Es instalable directamente como se pretendía, está a un `pip install pelican-copy-code` de distancia.

Mejor que una captura de pantalla dejo este bloque de código con el que experimentarlo en vivo, sólo pasa el cursor por encima y haz click en "Copiar":

```python
def swallow_airspeed(laden=False):
   return 24 if not laden else RuntimeError("African or European?")

class BlackKnight:
   def __init__(self):
       self.flesh_wounds = ["'Tis but a scratch!"]
   def is_defeated(self):
       return len(self.flesh_wounds) >= 4

print(swallow_airspeed(laden="coconut"))
```

## Lecciones

Inicialmente usé Kimi 2.6 porque es mi modelo por defecto en [Venice.ai](https://venice.ai/).
Es barato, rápido y privado (Venice.ai no guarda registros de las conversaciones en sus propios modelos).

Probé a cambiar a Deepseek V4 Pro porque era novedoso y decían que algo mejor para programar, comparable a Claude Opus 4.5.
No noté demasiado cambio, para un proyecto tan pequeño probablemente cualquiera de los dos habría dado buenos resultados.

Sí es verdad que Kimi 2.6 cometió algunos errores en su implementación inicial, como por ejemplo algunos de los ajustes de configuración que le pedí incluir no tenían efecto, o sea el código no los usaba nunca.
Fue algo fácil de corregir en sesiones separadas, pero me hizo abrir los ojos sobre lo importante que es la fase de pruebas.

También acabé haciendo algunas refactorizaciones a mano que probablemente me podría haber evitado si hubiese sido más específico en las instrucciones en `AGENTS.md`.
Por ejemplo mantener las variables de configuración en orden alfabético, debería haber sido un requisito de estilo en `AGENTS.md`.
También el agente puso algunas variables de configuración fuera del diccionario.
Un error de estilo que un humano probablemente no habría cometido.

Cuando llegó la hora de probar el plugin por primera vez resultó que no funcionaba, daba un error por mal uso de [las señales y los generadores](https://github.com/haplo/pelican-copy-code/blob/f0a625b85caa3ff134ab85bfdf006abad4bd505c/pelican/plugins/copy_code/__init__.py#L8).
Se lo puse a Deepseek V4 Pro pero no lo consiguó arreglar.
Ahí fue cuando cambié a Claude Opus 4.7, que al primer intento encontró el problema y lo arregló correctamente.
Cobró sentido los consejos que había leído por ahí de usar a Opus como planificador y a otro modelo más barato para ejecutar los cambios.
Se nota que es el modelo más avanzado, pero también mucho más caro que Kimi o Deepseek.

Cuando implementé el [soporte de traducciones](https://github.com/haplo/pelican-copy-code/commit/b76cff671550231135ced60dbd598993a160ebcf) lo hice con Deepseek V4 Pro, y funcionó bien.
Sin embargo duplicó código (las cadenas "Copy" y "Copied!" estaban duplicadas en dos ficheros distintos).
Le pedí refactorizar para eliminar la duplicación, pero la propuesta no era nada buena, eliminaba la duplicación pero añadía más código con mal estilo.
Una vez más cambié a Opus 4.7 que planteó una solución mucho mejor que realmente simplificaba el código.
