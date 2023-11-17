import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, Label, Entry, Button
import threading

class SocketApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Conexion de socket")

        # Configurar colores de fondo y texto para la ventana principal
        self.root.configure(bg="gray")  # Puedes cambiar el color de fondo a tu preferencia

        self.connection_type_label = tk.Label(self.root, text="Tipo de coneccion:", bg="gray", fg="black")
        self.connection_type_label.pack(pady=5)

        self.connection_type_var = tk.StringVar()
        self.connection_type_var.set("Server")

        self.server_radio = tk.Radiobutton(self.root, text="Servidor", variable=self.connection_type_var, value="Server", bg="gray", fg="black")
        self.server_radio.pack(anchor=tk.W)
        self.client_radio = tk.Radiobutton(self.root, text="Cliente", variable=self.connection_type_var, value="Client", bg="gray", fg="black")
        self.client_radio.pack(anchor=tk.W)

        self.ip_label = tk.Label(self.root, text="Introduce la direccion IP:", bg="gray", fg="black")
        self.ip_label.pack(pady=5)

        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=40, height=10, bg="dark gray", fg="black")  # Configurar colores del área de texto
        self.text_area.pack(padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Buscar", command=self.start_connection, bg="#4CAF50", fg="white")  # Configurar colores del botón
        self.start_button.pack(pady=10)

        self.send_message_button = tk.Button(self.root, text="Enviar mensaje", command=self.open_send_window, bg="#008CBA", fg="white")  # Configurar colores del botón
        self.send_message_button.pack(pady=10)

        self.client_socket = None

    def start_connection(self):
        connection_type = self.connection_type_var.get()
        ip_address = self.ip_entry.get()

        if connection_type == "Server":
            threading.Thread(target=self.start_server, args=(ip_address,), daemon=True).start()
        elif connection_type == "Client":
            threading.Thread(target=self.start_client, args=(ip_address,), daemon=True).start()

    def start_server(self, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, 65433))
                s.listen()
                self.text_area.insert(tk.END, f"Server listening on {host}:65433\n")
                conn, addr = s.accept()
                self.client_socket = conn
                with conn:
                    self.text_area.insert(tk.END, f"Connected by {addr}\n")
                    while True:
                        try:
                            data = conn.recv(1024)
                            if not data:
                                self.text_area.insert(tk.END, 'Client disconnected\n')
                                break
                            self.text_area.insert(tk.END, f"Received: {data.decode('utf-8')}\n")
                        except Exception as e:
                            self.text_area.insert(tk.END, f'Error on server: {e}\n')
                            break
            except Exception as e:
                messagebox.showerror("Error", f"Server error: {e}")

    def start_client(self, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, 65433))
                self.client_socket = s
                self.text_area.insert(tk.END, f'Connected to {host}:65433\n')
                while True:
                    data = s.recv(1024)
                    self.text_area.insert(tk.END, f"Received: {data.decode('utf-8')}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Client error: {e}")

    def open_send_window(self):
        send_window = Toplevel(self.root)
        send_window.title("Enviar mensaje")

        # Configurar colores de fondo y texto para la ventana secundaria
        send_window.configure(bg="dark gray")
        
        message_label = Label(send_window, text="Introduce el mensaje:", bg="dark gray", fg="black")
        message_label.pack(pady=5)

        message_entry = Entry(send_window, width=60)
        message_entry.pack(pady=5)

        send_button = Button(send_window, text="Enviar", command=lambda: self.send_message(message_entry.get()), bg="#008CBA", fg="white")  # Configurar colores del botón
        send_button.pack(pady=10)

    def send_message(self, message):
        try:
            if self.client_socket:
                self.client_socket.sendall(message.encode('utf-8'))
                self.text_area.insert(tk.END, f"Sent: {message}\n")
            else:
                messagebox.showerror("Error", "No hay coneccion activa.")
        except Exception as e:
            messagebox.showerror("Error", f"Error sending message: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SocketApp()
    app.run()
