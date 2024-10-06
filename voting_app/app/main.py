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
