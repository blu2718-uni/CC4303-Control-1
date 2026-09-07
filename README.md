
# Control 1 - CC4303 Redes
Link del repositorio en GitHub: [Repositorio](https://github.com/blu2718-uni/CC4303-Control-1.git)

## Integrantes:
* **Oscar Conejeros Bruce**
* **Julio Yáñez**

## Actividad 1

### Declaración de uso de IA

**En esta actividad, se utilizó el modelo GLM 5.3 Flash en OpenCode para generar la página web que devuelve el proxy al intentar ingresar a una página prohibida**

### Ejecución

Para ejecutar el código de esta actividad, corra el archivo dentro del directorio en el que se encuentra `server.py`:

```
python3 server.py <ip-servidor> [(<nombre-json> | <nombre-json> <ruta-relativa-json>)]
```

El programa no depende de ninguna librería externa.

### Decisiones de implementación

#### Diseño

El servidor puede recibir mensajes extensos con un buffer relativamete pequeño ya que lee continuamente trozos del mensaje que se le envia, para construir el mensaje completo. El servidor sabe cuando acaba el mensaje, ya que es capar de detectar cuando el trozo que recibe es menor que el buffer (lo que indica implícitamente que no queda mas mensaje).

Se separaron las funciones de parseo y creación de mensajes HTTP en archivos distintos, esto se hizo al inicio de la actividad, para encapsular estas funcionalidades. Para parsear y construir mensajes usamos **diccionarios**, Almacenamos cada pieza del mensaje como **strings**. 

La respuesta del servidor al intentar ingresar a una página prohibida es flexible, en castellano, el servidor puede responder un HTML cualquiera. El mensaje HTTP asociado a este HTML arbitrario se construye dinámicamente.

Para el manejo de las peticiones de imágenes, se definió una función capaz de generar un mensaje HTTP para responder la petición para una imagen cualquiera. Esta se invoca solo cuando la petición solicita un tipo de dato `image/`.

Se separó la recepción de mensajes en dos, una que se dedica únicamente a capturar el HEAD, asegurando lo mejor posible que se recibe el HEAD completo, y otra que captura todo el mensaje que logre recibir.

La implementación del archivo de configuración asume, en primera instancia, que el nombre del archivo es `json_nombre.json` y que está ubicado en el mismo directorio que `server.py`. Es posible elegir un nombre de archivo arbitrario y una dirección relativa para ese nombre de archivo, para ello se le entregan argumentos a `server-py`. El servidor intentará abrir ese archivo, no se implementó un manejo de error para estos argumentos, se asume que los argumentos son válidos.

El servidor solo responde si el mensaje que recibe es de tipo GET. Primero revisa si es una imagen, luego determina el host y la ruta de la petición. Con toda esa información, se revisa si es una dirección prohibida, luego se revisa si existen palabras prohibidas, por último, revisa si se trata de una imagen. El servidor responde según corresponda.

El servidor va _printeando_ lo que hace constantemente. Indica lo que ha hecho, lo que ha recibido, lo que _proxeará_ y si es que se cierra algún proxy.

El servidor asume que los sitios _forbidden_ están escritos de esta forma: `<host> | <host>/<ruta>`, **sin** anteponer `http://`. Notar que el servidor busca matches exactos entre lo que pide el cliente y las direcciones prohibidas.

#### Funcionamiento

El mensaje es capaz de garantizar la recepción completa del HEAD con `receive_full_head()`, ya que se asegura que el mensaje recibido contiene el salto de linea `\r\n\r\n`, que separa el HEAD del BODY. La recepción del HEAD con el BODY, usando `recieve_full_message()` es mas fragil. Al no haber un caracter que indique el fin del BODY, el servidor solo se dedica a leer hasta que no haya mas que leer.

`gen_image_response()` toma como argumento la ubicación de una imagen, la lee **en bytes** y retorna un mensaje HTTP en la forma parseada que definimos en el diseño (como diccionario).

Ejecutar `python3 server.py` tomará el archivo de configuración que existe por defecto, pero podemos entregarle otro archivo de esta manera: `python3 server.py [nombre-archivo] [ruta-relativa-al-archivo]`. El servidor asume, de recbir solo el nombre, que el archivo está en la misma ruta que `server.py`. El servidor solo tira error si le entregamos más argumentos de lo esperado.

Para ver si hay que bloquear la página usamos un _flag_, `block`. Para manejar peticiones de imágenes, usamos una lista, donde el primer elemento es un _flag_ y el otro es un string con la ruta de la imagen (de existir).

La búsqueda del host, la deficición de la ruta, el censurado de palabras prohibidas y la determinación de que una petición sea o no para una imagen se hizo enteramente con manejo de strings. Tras parsear la respuesta que hayamos recibido del cliente.

Notar que verificar si la petición era para una imagen es el último paso. Ya que si en efecto, era una petición por una imagen, lo que retorna el servidor ignora todo el trabajo previo y corresponde a la generación de la respuesta de imagen.

### Observaciones al experimentar

A la hora de servir la página de La Negra al intentar acceder una página prohibida, se hacen multiples llamadas HTTP. Una para recibir el propio HTML y luego una llamada por cada imagen incrustada en el HTML. Naturalmente, el request de cada uno pide y espera un tipo de dato distinto.

Al intentar acceder a `http://cc4303.bachmann.cl/secret`, el proxy envia al usuario la página construida en `html_response.html` junto al código 403 en el respose header. Acceder a la página `http://cc4303.bachmann.cl/` muestra el nombre Oscar, tal como se especifica en `json_nombre.json`, además, hay palabras que fueron reemplazadas por `[REDACTED]`, `[FORBIDDEN]` y `[???]`. El resto del texto no parece haber sido alterado.

Se probó el proxy con distintos tamaños del buffer, no se vió una diferencia entre los distintos valores probados.

## Actividad 2

### Declaración de (no) uso de IA

**En esta actividad no se utilizó la inteligencia artificial.**


### Sobre la actividad

En esta actividad, se pidió construir un resolver DNS, el cual tenga una memoria caché. Para esto, asumiremos que todas las consultas que se harán del cliente al resolver serán de tipo A, es decir, preguntarán por la dirección IPv4 del dominio consultado.


### Cómo ejecutar el servidor DNS

Para ejecutar en el servidor, hay que ejecutar el programa python **resolver.py**, que se encuentra en la misma carpeta actividad_2.

```
python3 resolver.py <ip-servidor> [(-d | --debug)]
```

Para esta actividad, el único prerrequisito es tener la librería dnslib de Python. Esta se instala con el siguiente código en un entorno virtual:
```
pip3 install dnslib
```
O desde el repositorio de GitHub de dnslib: https://github.com/paulc/dnslib

Luego, para hacer consultas al servidor, se usa el comando dig en la terminal de la siguiente manera:
```
dig -p8000 @[IP_SERVIDOR_DNS] [dominio_a_consultar]
```

### Decisiones de implementación

#### Diseño

En esta actividad, tal como se mencionó en la materia de DNS, se usaron sockets no orientados a conexión, para asegurar una respuesta lo más rápida posible al servidor DNS.

Además, como se optó por utilizar la librería dnslib, se dio uso al parser ya incluido por esta librería, el cual otorgaba una estructura de datos ya adecuada para el manejo correcto de los mensajes DNS.
Por último, en la memoria caché, se decidió usar como estructura de datos un diccionario, el cual tiene como llaves los dominios consultados y como valores la lista de Resource Records de la respuesta, para entregar un mensaje DNS con este listado más fácilmente en una respuesta futura. Ver función **gen_new_cache(last)**, ya que esta es la que se encarga de crear la memoria caché.

El resto del programa sigue las instrucciones dadas en el enunciado de la actividad.

Es importante recalcar que una limitación de ignorar cualquier otro tipo de respuestas no consideradas en el paso 4 es, por ejemplo, que no podemos leer registros de tipo AAAA, es decir, no podremos obtener direcciones IP de 128 bits.

#### Funcionamiento

El programa consiste en 3 funciones, **gen_new_cache(last: List)**, **resolver(mensaje_consulta: bytes, ip_addr="198.41.0.4": str)** y el programa principal, que se ejecuta automáticamente.

* **gen_new_cache(last: List)**: Esta función recibe una lista con tuplas correspondientes al dominio consultado y la sección de respuesta del mensaje DNS recibido. Se encarga de generar una memoria caché para el resolver y actualizarla luego de cada consulta al servidor.
* **resolver(mensaje_consulta: bytes, ip_addr="198.41.0.4": str)**: La función sigue los pasos detallados en la parte 4 del enunciado de la actividad y finalmente, si no se cumple ninguna de las condiciones indicadas en los pasos, retorna el último mensaje recibido, junto a un mensaje indicando que la respuesta no es soportada por el resolver.
* **Programa principal**: Este es el que maneja toda la lógica, recibe los mensajes del cliente, llama a la función resolver, entrega la respuesta al cliente y actualiza el listado de las últimas consultas y la memoria caché.

### Resultados de la experimentación

Al momento de realizar la consulta:
```
dig -p8000 @[IP_SERVIDOR_DNS] eol.uchile.cl
```
se recibieron 12 respuestas, una de tipo CNAME con rdata oeol-c.uchile.cl y todas las demás con una IP de la forma 146.83.63.XX.

Luego, realizando la misma consulta, se logra obtener las mismas respuestas, pero esta vez desde la memoria caché (mensaje debug: (debug) se utilizó el caché).

El comando:
```
dig -p8000 @[IP_SERVIDOR_DNS] www.uchile.cl
```
resuelve a 200.89.76.36, mientras que el comando:
```
dig -p8000 @[IP_SERVIDOR_DNS] cc4303.bachmann.cl
```
resuelve a 104.248.65.245.

Siguiendo con los experimentos de la actividad, podemos ver que al realizar la consulta:
```
dig -p8000 @[IP_SERVIDOR_DNS] www.webofscience.com
```
se resuelve correctamente, obteniendo 4 respuestas: 2 de tipo CNAME y 2 de tipo A.
Las respuestas de tipo CNAME tienen un rdata www-us.webofscience.com. y www-us.webofscience.com.cdn.cloudflare.net. respectivamente, y las de tipo A entregan las IP 104.18.25.24 y 104.18.24.24, por lo que no hay ningún problema que se deba resolver en este caso.

Para el comando:
```
dig -p8000 @[IP_SERVIDOR_DNS] www.cc4303.bachmann.cl
```
no se obtiene una respuesta soportada por el resolver, ya que la respuesta que recibe el servidor para resolver no contiene ningún resource record de tipo A en la respuesta, ni recibe un resource record de tipo NS en la sección authority, por lo que, según enunciado, se debe ignorar, retornando el último mensaje recibido.

En este caso se esperaba una respuesta de parte del servidor equivalente al comando ejecutado con cc4303.bachmann.cl, pero luego de realizar la misma consulta a @1.1.1.1, se puede apreciar que esta y la del servidor externo reciben respuestas de tipo SOA en la sección authority, con un rname bachmann.cl. y rdata ns1.digitalocean.com. hostmaster.bachmann.cl. 0 10800 3600 604800 1800. Esto probablemente ocurre porque se está dando un name server donde podría encontrarse www.cc4303.bachmann.cl, ya que no se logró encontrar esta dirección.

Para el último experimento se hicieron 10 consultas de la siguiente forma:
```
dig -p8000 @[IP_SERVIDOR_DNS] example.com
```
donde todas fueron en distintas instancias del servidor (se reiniciaba luego de cada consulta) con el fin de no utilizar la memoria caché. Finalmente, como resultado se obtuvo que en las 10 consultas, siempre se hicieron al mismo name server ("**.**", con IP 198.41.0.4). Esto seguramente se debe a que nuestro resolver es de tipo recursivo.
