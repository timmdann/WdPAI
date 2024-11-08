import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Type
import uuid
import psycopg2
import os
import time


DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ.get('DB_NAME', 'mydatabase')
DB_USER = os.environ.get('DB_USER', 'myuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mypassword')

def connect_to_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Connected to the database")
            return conn
        except psycopg2.OperationalError:
            print("Database connection error, retrying in 5 seconds...")
            time.sleep(5)


conn = connect_to_db()
cursor = conn.cursor()

class SimpleRequestHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def clear_database():
        cursor.execute("DELETE FROM users")
        conn.commit()

    clear_database()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_cors_headers()
        self.end_headers()


    def do_GET(self) -> None:
        if self.path == "/team":
            cursor.execute("SELECT id, first_name, last_name, role FROM users")
            rows = cursor.fetchall()
            team_members = [
                {"id": row[0], "first_name": row[1], "last_name": row[2], "role": row[3]}
                for row in rows
            ]
            response = {"team_members": team_members}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()


    def do_POST(self) -> None:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        received_data = json.loads(post_data.decode())

        first_name = received_data.get('first_name')
        last_name = received_data.get('last_name')
        role = received_data.get('role')


        cursor.execute(
            "SELECT id FROM users WHERE first_name = %s AND last_name = %s AND role = %s",
            (first_name, last_name, role)
        )
        existing_member = cursor.fetchone()

        if existing_member:
            response = {"error": "A team member with the same first name, last name, and role already exists."}
            self.send_response(200)
        else:

            cursor.execute(
                "INSERT INTO users (first_name, last_name, role) VALUES (%s, %s, %s) RETURNING id",
                (first_name, last_name, role)
            )
            new_member_id = cursor.fetchone()[0]
            conn.commit()

            response = {
                "message": "New team member added successfully",
                "team_members": [{"id": new_member_id, "first_name": first_name, "last_name": last_name, "role": role}]
            }
            self.send_response(200)

        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


    def do_DELETE(self) -> None:
        path_parts = self.path.split('/')
        if len(path_parts) == 3 and path_parts[1] == "team":
            member_id = path_parts[2]

            try:
                cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", (member_id,))
                deleted_member = cursor.fetchone()

                if deleted_member:
                    conn.commit()
                    response = {"message": "User deleted successfully"}
                    self.send_response(200)
                else:
                    response = {"error": "User not found"}
                    self.send_response(404)

                self.send_header('Content-type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                print("Error occurred:", e)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "An error occurred"}).encode())
        else:
            self.send_response(400)
            self.send_cors_headers()
            self.end_headers()


def run(
        server_class: Type[HTTPServer] = HTTPServer,
        handler_class: Type[BaseHTTPRequestHandler] = SimpleRequestHandler,
        port: int = 8000
) -> None:
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
