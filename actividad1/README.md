# Actividad 1 - CC4303 Redes

**En esta actividad, se utilizó el modelo GLM 5.3 Flash en OpenCode para generar la página web que devuelve el proxy al intentar ingresar a una página prohibida**

## Ejecución

Corra: `python3 server.py [(<archivo> | <archivo> <ruta-relativa-al-archivo>)]`. El programa no depende de ninguna librería externa.

## Decisiones de implementación

### Diseño

El servidor puede recibir mensajes extensos con un buffer relativamete pequeño ya que lee continuamente trozos del mensaje que se le envia, para construir el mensaje completo. El servidor sabe cuando acaba el mensaje, ya que es capar de detectar cuando el trozo que recibe es menor que el buffer (lo que indica implícitamente que no queda mas mensaje).

Se separaron las funciones de parseo y creación de mensajes HTTP en archivos distintos, esto se hizo al inicio de la actividad, para encapsular estas funcionalidades. Para parsear y construir mensajes usamos **diccionarios**, Almacenamos cada pieza del mensaje como **strings**. 

La respuesta del servidor al intentar ingresar a una página prohibida es flexible, en castellano, el servidor puede responder un HTML cualquiera. El mensaje HTTP asociado a este HTML arbitrario se construye dinámicamente.

Para el manejo de las peticiones de imágenes, se definió una función capaz de generar un mensaje HTTP para responder la petición para una imagen cualquiera. Esta se invoca solo cuando la petición solicita un tipo de dato `image/`.

Se separó la recepción de mensajes en dos, una que se dedica únicamente a capturar el HEAD, asegurando lo mejor posible que se recibe el HEAD completo, y otra que captura todo el mensaje que logre recibir.

La implementación del archivo de configuración asume, en primera instancia, que el nombre del archivo es `json_nombre.json` y que está ubicado en el mismo directorio que `server.py`. Es posible elegir un nombre de archivo arbitrario y una dirección relativa para ese nombre de archivo, para ello se le entregan argumentos a `server-py`. El servidor intentará abrir ese archivo, no se implementó un manejo de error para estos argumentos, se asume que los argumentos son válidos.

El servidor solo responde si el mensaje que recibe es de tipo GET. Primero revisa si es una imagen, luego determina el host y la ruta de la petición. Con toda esa información, se revisa si es una dirección prohibida, luego se revisa si existen palabras prohibidas, por último, revisa si se trata de una imagen. El servidor responde según corresponda.

El servidor va _printeando_ lo que hace constantemente. Indica lo que ha hecho, lo que ha recibido, lo que _proxeará_ y si es que se cierra algún proxy.

El servidor asume que los sitios _forbidden_ están escritos de esta forma: `<host> | <host>/<ruta>`, **sin** anteponer `http://`. Notar que el servidor busca matches exactos entre lo que pide el cliente y las direcciones prohibidas.

### Funcionamiento

El mensaje es capaz de garantizar la recepción completa del HEAD con `receive_full_head()`, ya que se asegura que el mensaje recibido contiene el salto de linea `\r\n\r\n`, que separa el HEAD del BODY. La recepción del HEAD con el BODY, usando `recieve_full_message()` es mas fragil. Al no haber un caracter que indique el fin del BODY, el servidor solo se dedica a leer hasta que no haya mas que leer.

`gen_image_response()` toma como argumento la ubicación de una imagen, la lee **en bytes** y retorna un mensaje HTTP en la forma parseada que definimos en el diseño (como diccionario).

Ejecutar `python3 server.py` tomará el archivo de configuración que existe por defecto, pero podemos entregarle otro archivo de esta manera: `python3 server.py [nombre-archivo] [ruta-relativa-al-archivo]`. El servidor asume, de recbir solo el nombre, que el archivo está en la misma ruta que `server.py`. El servidor solo tira error si le entregamos más argumentos de lo esperado.

Para ver si hay que bloquear la página usamos un _flag_, `block`. Para manejar peticiones de imágenes, usamos una lista, donde el primer elemento es un _flag_ y el otro es un string con la ruta de la imagen (de existir).

La búsqueda del host, la deficición de la ruta, el censurado de palabras prohibidas y la determinación de que una petición sea o no para una imagen se hizo enteramente con manejo de strings. Tras parsear la respuesta que hayamos recibido del cliente.

Notar que verificar si la petición era para una imagen es el último paso. Ya que si en efecto, era una petición por una imagen, lo que retorna el servidor ignora todo el trabajo previo y corresponde a la generación de la respuesta de imagen.

## Observaciones al experimentar

A la hora de servir la página de La Negra al intentar acceder una página prohibida, se hacen multiples llamadas HTTP. Una para recibir el propio HTML y luego una llamada por cada imagen incrustada en el HTML. Naturalmente, el request de cada uno pide y espera un tipo de dato distinto.

Al intentar acceder a `http://cc4303.bachmann.cl/secret`, el proxy envia al usuario la página construida en `html_response.html` junto al código 403 en el respose header. Acceder a la página `http://cc4303.bachmann.cl/` muestra el nombre Oscar, tal como se especifica en `json_nombre.json`, además, hay palabras que fueron reemplazadas por `[REDACTED]`, `[FORBIDDEN]` y `[???]`. El resto del texto no parece haber sido alterado.

Se probó el proxy con distintos tamaños del buffer, no se vió una diferencia entre los distintos valores probados.
