import socket
import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QTextEdit, QLabel
from PyQt5.QtCore import pyqtSlot
#Pourquoi j'utilise pyqtSlot parce que j'ai découvert que c'est plus facile pour gerer le demmarage et l'arret en basculant d'un état a l'autre, j'espere que c'est pas dérangeant car j'ai ma SAE sur ça
class TPTESTGREG(QWidget):
    def __init__(self):
        super().__init__()
        self.appGR()
        self.server_socket = None
        self.demarrer = False
        self.client_threads = []
        self.client_sockets = []
    def appGR(self):
        self.setWindowTitle("Serveur TPTEST Greg")
        self.setGeometry(100, 100, 400, 400)
        layout = QGridLayout()

        self.ip_label = QLabel("Adresse IP :")
        self.ip_input = QLineEdit("localhost")
        layout.addWidget(self.ip_label,0,0)
        layout.addWidget(self.ip_input,0,1)
        self.port_label = QLabel("Port :")
        self.port_input = QLineEdit("4200")
        layout.addWidget(self.port_label,1,0)
        layout.addWidget(self.port_input,1,1)
        self.clients_label = QLabel("Nombre max de clients :")
        self.clients_input = QLineEdit("5")
        layout.addWidget(self.clients_label,2,0)
        layout.addWidget(self.clients_input,2,1)
        self.start_button = QPushButton("Démarrer le serveur")
        self.start_button.clicked.connect(self.toggle_server)
        layout.addWidget(self.start_button,3,0,1,2)
        self.clients_display = QTextEdit()
        self.clients_display.setReadOnly(True)
        layout.addWidget(self.clients_display, 4,0, 1,2)
        self.setLayout(layout)
    @pyqtSlot()
    def toggle_server(self):
        if not self.demarrer:
            self.__demarage()
        else:
            self.stop_server()
    def __demarage(self):
        try:
            ip = self.ip_input.text()
            port = int(self.port_input.text())
            max_clients = int(self.clients_input.text())

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(max_clients)

            self.clients_display.append(f"serveur démarré sur {ip}:{port}")
            self.start_button.setText("arrêter le serveur")
            self.demarrer = True

            self.accept_thread = threading.Thread(target=self.__accept)
            self.accept_thread.start()
        except Exception as e:
            self.clients_display.append(f"erreur : {e}")
    def stop_server(self):
        self.demarrer = False
        if self.server_socket:
            for client_socket in self.client_sockets:
                try:
                    client_socket.close()
                except Exception as e:
                    self.clients_display.append(f"Erreur en fermant un client : {e}")

            self.server_socket.close()
            self.server_socket = None

        self.clients_display.append("Serveur arrêté.")
        self.start_button.setText("Démarrer le serveur")
    def __accept(self):
        while self.demarrer:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients_display.append(f"Client connecté : {client_address}")

                client_thread = threading.Thread(target=self.client, args=(client_socket,))
                self.client_threads.append(client_thread)
                self.client_sockets.append(client_socket)
                client_thread.start()
            except Exception as e:
                if self.demarrer:
                    self.clients_display.append(f"Erreur de l'acceptation : {e}")
    def client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024)
                if not message or message.strip() == "arret":
                    break
                self.clients_display.append(f"Message de client : {message}")
        except Exception as e:
            self.clients_display.append(f"erreur client : {e}")
        finally:
            self.clients_display.append("client déconnecter")
            try:
                client_socket.close()
            except Exception as e:
                self.clients_display.append(f"Erreur en fermant le client : {e}")
            self.client_sockets.remove(client_socket)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TPTESTGREG()
    window.show()
    app.exec_()

'''
PARTIE 8
Question 1 : je n'ai pas put tester avec le votre, mais il faut "arreter le serveur" en cliquant sur le bouton push 
puis kill le processus en cours, le serveur se ferme mal si on kill le processus avant d'avoir cliquer sur le bouton PUSH
Question 2: ...
'''
