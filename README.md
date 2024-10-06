# Votaciones
Programa de votaciones

---


Voy a guiarte a través de la creación de una aplicación web en Python que permita la creación y participación en votaciones, con el entorno completo en Docker usando contenedores para Python, MySQL y NGINX. No usaremos ningún framework de desarrollo web como Flask o Django, solo código Python nativo y HTML/CSS.

### Estructura general

La aplicación constará de:

1. **Servidor web en Python** que gestionará la votación.
2. **Base de datos MySQL** para almacenar las votaciones y los resultados.
3. **Servidor NGINX** para servir los archivos estáticos (HTML/CSS) y hacer de [[Proxy inverso]].
4. **Entorno Docker** para contener cada parte de la aplicación.

### Paso 1: Crear la estructura de directorios

Comienza creando la estructura de directorios para la aplicación:

```
voting_app/
│
├── app/
│   ├── main.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── styles.css
├── db/
│   └── init.sql
├── nginx/
│   └── default.conf
└── docker-compose.yml
```

### Paso 2: Implementar el código de la aplicación

#### 2.1. **Python app (app/main.py)**

Este archivo manejará la lógica de la aplicación. Usaremos Python nativo para manejar HTTP requests.

```python
import http.server
import socketserver
import cgi
import mysql.connector

PORT = 8080

# Conexión a la base de datos MySQL
db_connection = mysql.connector.connect(
    host="db",
    user="root",
    password="rootpassword",
    database="voting"
)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "templates/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/vote":
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if ctype == 'multipart/form-data':
                post_vars = cgi.parse_multipart(self.rfile, pdict)
            else:
                length = int(self.headers.get('Content-length'))
                post_vars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)

            vote = post_vars[b'vote'][0].decode('utf-8')

            # Guardar el voto en la base de datos
            cursor = db_connection.cursor()
            cursor.execute("INSERT INTO votes (option) VALUES (%s)", (vote,))
            db_connection.commit()

            # Redirigir de nuevo a la página principal
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

# Iniciar servidor web
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
```

#### 2.2. **Página HTML (app/templates/index.html)**

Esta es la interfaz que los usuarios verán.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/styles.css">
    <title>Votación</title>
</head>
<body>
    <h1>Participa en la votación</h1>
    <form action="/vote" method="post">
        <p>¿Cuál es tu lenguaje de programación favorito?</p>
        <label><input type="radio" name="vote" value="Python"> Python</label><br>
        <label><input type="radio" name="vote" value="JavaScript"> JavaScript</label><br>
        <label><input type="radio" name="vote" value="Java"> Java</label><br>
        <label><input type="radio" name="vote" value="C++"> C++</label><br>
        <label><input type="radio" name="vote" value="Go"> Go</label><br>
        <button type="submit">Votar</button>
    </form>
</body>
</html>
```

#### 2.3. **Hoja de estilos CSS (app/static/styles.css)**

```css
body {
    font-family: Arial, sans-serif;
    text-align: center;
    margin-top: 50px;
}
h1 {
    color: #333;
}
button {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
}
```

### Paso 3: Crear la base de datos

#### 3.1. **Archivo de inicialización de MySQL (db/init.sql)**

Este archivo inicializa la base de datos y crea una tabla para almacenar los votos.

```sql
CREATE DATABASE IF NOT EXISTS voting;
USE voting;

CREATE TABLE IF NOT EXISTS votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    option VARCHAR(50)
);
```

### Paso 4: Configurar NGINX

#### 4.1. **Archivo de configuración de NGINX (nginx/default.conf)**

Este archivo configurará NGINX como un proxy inverso para la aplicación.

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/static/;
    }
}
```

### Paso 5: Crear el archivo docker-compose.yml

Este archivo define los servicios que se ejecutarán en los contenedores de Docker.

```yaml
services:
  app:
    build: ./app
    volumes:
      - ./app:/app
    ports:
      - "8080:8080"
    depends_on:
      - db

  db:
    image: mysql:latest
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - ./db:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./app/static:/app/static
    ports:
      - "80:80"
    depends_on:
      - app
```

### Paso 6: Crear los Dockerfiles

#### 6.1. **Dockerfile para la aplicación Python (app/Dockerfile)**

Este Dockerfile define el entorno para ejecutar la aplicación.

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install mysql-connector-python

CMD ["python", "main.py"]
```

### Paso 7: Iniciar los contenedores

Una vez que todos los archivos estén listos, puedes ejecutar la aplicación.

1. Ve al directorio donde está el archivo `docker-compose.yml`.
2. Ejecuta el siguiente comando para construir y ejecutar los contenedores:

```bash
docker-compose up --build
```

Esto iniciará la aplicación y podrás acceder a ella en tu navegador en `http://localhost`. NGINX se encargará de redirigir las solicitudes al servidor Python y las votaciones se almacenarán en la base de datos MySQL.

### Paso 8: Eliminar el entorno

Para detener y eliminar todos los contenedores, redes y volúmenes creados por Docker Compose, puedes usar el siguiente comando:

```bash
docker-compose down --volumes
```

### Conclusión

Este instructivo te permite montar rápidamente una aplicación de votación sencilla sin el uso de frameworks, utilizando solo Python nativo, HTML, CSS y Docker para manejar el entorno de desarrollo. ¡Espero que te sea útil para aprender y practicar!


---

export PS1='\[\e[32m\]\u@\h:\[\e[34m\]\w\[\e[33m\] $(parse_git_branch)\[\e[0m\] $ '
