import sys
from PyQt4 import QtGui,QtCore, uic
from xmlrpc.client import ServerProxy 

class VentanaCliente(QtGui.QMainWindow):
    def __init__(self):
        super(VentanaCliente, self).__init__()
        uic.loadUi('cliente.ui', self)
        self.expandir_cuadros_tabla()
        self.pushButton.clicked.connect(self.manejo_servidor)
        self.pushButton_2.clicked.connect(self.participar_juego)
        self.pushButton_2.clicked.connect(self.reiniciar)
        self.id_usuario = 0 
        self.direccion = 2 
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection) 
        self.creado_usuario = False 
        self.doomed = False
        self.intervalo_server = 0
        self.timer= QtCore.QTimer(self)
        self.timer.timeout.connect(self.poner_tabla_bien) 
        self.timer.timeout.connect(self.comenzar_juego)
        self.timer.timeout.connect(self.actualizar_timer_interval)
        self.timer.start(self.intervalo_server)
        self.show()
        self.server = None

    def poner_tabla_bien(self):
        if self.creado_usuario:
            game = self.server.estado_del_juego()
            self.tableWidget.setRowCount(game["tamY"])
            self.tableWidget.setColumnCount(game["tamX"])
            self.llenar_tabla() 

    def llenar_tabla(self):
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(82,135,135))

    def comenzar_juego(self):
        if self.creado_usuario:
            if self.ha_muerto():
                self.lineEdit.setText("¡MORISTE!")
            self.llenar_tabla() 
            self.tableWidget.installEventFilter(self)
            diccionario = self.server.estado_del_juego()  
            lista_viboras = diccionario["viboras"]
            for vibora in lista_viboras:
                lista_camino = vibora["camino"]
                colores = vibora["color"]
                self.dibuja_vibora(lista_camino, colores) 
    
    def actualizar_timer_interval(self):
        if self.creado_usuario:
            diccionario = self.server.estado_del_juego()
            intervalo = diccionario["espera"]
            if self.intervalo_server != intervalo:
                self.intervalo_server = intervalo
                self.timer.setInterval(self.intervalo_server) 
    
    def dibuja_vibora(self, lista_camino, colores):
        for tupla in lista_camino:
            self.tableWidget.item(tupla[0], tupla[1]).setBackground(QtGui.QColor(colores['r'], colores['g'], colores['b']))

    def manejo_servidor(self):
        self.pushButton.setText("Pinging...") 
        try:
            self.crea_servidor()
            pong = self.server.ping() 
            self.pushButton.setText("¡Pong!") 
        except: 
            self.pushButton.setText("No PONG :(")

    def crea_servidor(self):
        self.url = self.lineEdit_3.text()
        self.port = self.spinBox.value() 
        self.direccion = "http://" + self.url + ":" + str(self.port) 
        self.server = ServerProxy(self.direccion) 
 
    def participar_juego(self):
        try:
            self.crea_servidor() 
            informacion = self.server.yo_juego()
            self.lineEdit.setText(informacion["id"])
            self.id_usuario = informacion["id"]
            self.color = informacion["color"]
            self.red = self.color["r"]
            self.green = self.color["g"]
            self.blue = self.color["b"]
            self.lineEdit_2.setText("R:" + str(self.red) + " G:" + str(self.green) + " B:" + str(self.blue))
            self.lineEdit_2.setStyleSheet('QLineEdit {background-color: rgb('+str(self.red)+','+ str(self.green) + ',' + str(self.blue)+');}')
            self.creado_usuario = True 
        except: 
            self.lineEdit.setText("Conexión fallida: servidor inalcanzable.")
            self.lineEdit_2.setText("Verifica que el URL y puerto sean correctos.")


    def ha_muerto(self):
        diccionario = self.server.estado_del_juego()
        lista_serpientes = diccionario["viboras"]
        for vibora in lista_serpientes:
            if vibora["id"] == self.id_usuario:
                return False
        self.doomed = True
        return True 

    def reiniciar(self):
        if self.doomed: 
            self.doomed = False 
            self.lineEdit.setText("") 
            self.lineEdit.setText("")
            self.participar_juego()
            self.timer.start()
            self.comenzar_juego()


    def expandir_cuadros_tabla(self):
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget): 
                key = event.key() 
                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    if self.direccion != 2:
                        self.direccion = 0
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    if self.direccion != 0:
                        self.direccion = 2
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    if self.direccion != 3:
                        self.direccion = 1
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    if self.direccion != 1:
                        self.direccion = 3
                self.server.cambia_direccion(self.id_usuario, self.direccion)
        return QtGui.QMainWindow.eventFilter(self, source, event) 

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv) 
    ventana = VentanaCliente() 
    sys.exit(app.exec_()) 
