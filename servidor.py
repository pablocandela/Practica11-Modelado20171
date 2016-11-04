import sys
from xmlrpc.server import SimpleXMLRPCServer 
from PyQt4 import QtGui, QtCore, uic
from random import randint 
import uuid 

class Serpiente():
    def __init__(self):
        self.id = str(uuid.uuid4())[:8] 
        red, green, blue = randint(0,255), randint(0,255), randint(0,255)
        self.color = {"r": red, "g": green, "b": blue} 
        self.camino = [] 
        self.casillas = [] 
        self.camino = []
        self.tam = len(self.casillas)
        self.direccion = "Abajo" 
        

    def obtener_diccionario(self):
        diccionario = dict()
        diccionario = {
            'id': self.id,
            'camino': self.camino, 
            'color': self.color
        }
        return diccionario 

class VentanaServidor(QtGui.QMainWindow):

    def __init__(self):
        super(VentanaServidor, self).__init__()
        uic.loadUi('servidor.ui', self) 
        self.terminar.hide() 
        self.pushButton.clicked.connect(self.inicializar_servidor) 
        self.juego_empezado = False 
        self.juego_pausado = False
        self.timer = None 
        self.timer_s = None
        self.timer_camino = None 
        self.serpientes_juego = []
        self.expandir_cuadros_tabla() 
        self.llenar_tabla() 
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection) 
        self.spinBox_2.valueChanged.connect(self.actualizar_tabla)
        self.spinBox_3.valueChanged.connect(self.actualizar_tabla)
        self.spinBox.valueChanged.connect(self.actualizar_timer) 
        self.time.valueChanged.connect(self.actualizar_timeout)
        self.iniciar_pausar.clicked.connect(self.comenzar_juego) 
        self.terminar.clicked.connect(self.terminar_juego)
        self.show() 

    def hacer(self):
        self.servidor.handle_request()

    def actualizar_camino(self):
        for serpiente in self.serpientes_juego:
            serpiente.camino = []
            for casilla in serpiente.casillas:
                serpiente.camino.append((casilla[0], casilla[1]))
    
    def inicializar_servidor(self):
        puerto = self.h.value()
        direccion = self.lineEdit.text()
        print(puerto)
        self.servidor = SimpleXMLRPCServer((direccion, 0)) 
        puerto2 = self.servidor.server_address[1]
        print(puerto2)
        self.h.setValue(puerto2)
        self.pushButton.setText(str(puerto2))
        self.h.setValue(puerto) 
        self.h.setReadOnly(True)
        self.lineEdit.setReadOnly(True) 
        self.pushButton.setEnabled(False)
        self.servidor.register_function(self.ping)
        self.servidor.register_function(self.yo_juego)
        self.servidor.register_function(self.cambia_direccion)
        self.servidor.register_function(self.estado_del_juego)
        self.servidor.timeout = 0 
        self.timer_s = QtCore.QTimer(self)
        self.timer_s.timeout.connect(self.hacer) 
        self.timer_s.start(self.servidor.timeout) 

    
    def lista_viboras(self):
        lista = list()
        for serpiente in self.serpientes_juego:
            lista.append(serpiente.obtener_diccionario())
        return lista

    def ping(self):
        return "¡Pong!"

    def highscore_game(self):
    	return self.highscore

    def yo_juego(self):
        serpiente_nueva = self.crear_serpiente()
        diccionario = {"id": serpiente_nueva.id, "color": serpiente_nueva.color}
        return diccionario

    def cambia_direccion(self, identificador, numero):
        for s in self.serpientes_juego:
            if s.id == identificador:
                if numero == 0:
                    if s.direccion is not "Abajo": 
                        s.direccion = "Arriba"
                if numero == 1:
                    if s.direccion is not "Izquierda":
                        s.direccion = "Derecha"
                if numero == 2: 
                    if s.direccion is not "Arriba":
                        s.direccion = "Abajo"
                if numero == 3: 
                    if s.direccion is not "Derecha":
                        s.direccion = "Izquierda"
        return True 

    def estado_del_juego(self):
        diccionario = dict()
        diccionario = {
            'espera': self.spinBox.value(), 
            'tamX': self.tableWidget.columnCount(),
            'tamY': self.tableWidget.rowCount(),
            'viboras': self.lista_viboras() 
        }
        return diccionario

    def crear_serpiente(self):
        serpiente_nueva = Serpiente()
        creada = False
        while not creada:
            creada = True
            uno = randint(1, self.tableWidget.rowCount()/2)
            dos = uno + 1
            tres = dos +1 
            ancho = randint(1, self.tableWidget.columnCount()-1)
            achecar_1, achecar_2, achecar_3 = [uno, ancho], [dos, ancho], [tres, ancho]
            for s in self.serpientes_juego:
                if achecar_1 in s.casillas or achecar_2 in s.casillas or achecar_3 in s.casillas:
                    creada = False
                    break
            serpiente_nueva.casillas = [achecar_1, achecar_2, achecar_3]
            self.serpientes_juego.append(serpiente_nueva) 
            return serpiente_nueva

    def actualizar_timeout(self):
        self.servidor.timeout = self.time.value() 
        self.timer_s.setInterval(self.time.value())

    def comenzar_juego(self):
        if not self.juego_empezado:
            self.terminar.show()
            self.crear_serpiente() 
            self.iniciar_pausar.setText("Pausar el Juego") 
            self.dibujar_serpientes()
            self.timer = QtCore.QTimer(self) 
            self.timer.timeout.connect(self.mover_serpientes) 
            self.timer.start(200) 
            self.timer_camino = QtCore.QTimer(self)
            self.timer_camino.timeout.connect(self.actualizar_camino)
            self.timer_camino.start(100)
            self.tableWidget.installEventFilter(self) 
            self.juego_empezado = True 
        elif self.juego_empezado and not self.juego_pausado: 
            self.timer.stop()
            self.juego_pausado = True 
            self.iniciar_pausar.setText("Reanudar el Juego") 
        elif self.juego_pausado: 
            self.timer.start() 
            self.juego_pausado = False 
            self.iniciar_pausar.setText("Pausar el Juego") 

    def terminar_juego(self):
        self.serpientes_juego = [] 
        self.timer.stop()
        self.juego_empezado = False 
        self.terminar.hide() 
        self.iniciar_pausar.setText("Inicia Juego") 
        self.llenar_tabla() 

    def actualizar_timer(self):
        valor = self.spinBox.value()
        self.timer.setInterval(valor)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget): 
                key = event.key() 
                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    for serpiente in self.serpientes_juego:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
        return QtGui.QMainWindow.eventFilter(self, source, event) 

    def dibujar_serpientes(self):
        for serpiente in self.serpientes_juego:
            for seccion_corporal in serpiente.casillas:
                self.tableWidget.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))
    
    
    def ha_chocado_consigo(self, serpiente):
        for seccion_corporal in serpiente.casillas[0:len(serpiente.casillas)-2]: 
            if serpiente.casillas[-1][0] == seccion_corporal[0] and serpiente.casillas[-1][1] == seccion_corporal[1]:
                return True
        return False

    def ha_chocado_con_otra_serpiente(self, serpiente_a_checar):
        for serpiente in self.serpientes_juego:
            if serpiente.id != serpiente_a_checar.id:
                for seccion_corporal in serpiente.casillas[:]: 
                    if serpiente_a_checar.casillas[-1][0] == seccion_corporal[0] and serpiente_a_checar.casillas[-1][1] == seccion_corporal[1]:
                        self.serpientes_juego.remove(serpiente_a_checar) 

    def mover_serpientes(self):
        for serpiente in self.serpientes_juego: 
            if self.ha_chocado_consigo(serpiente) or self.ha_chocado_con_otra_serpiente(serpiente):
                self.serpientes_juego.remove(serpiente) 
                self.llenar_tabla() 
                serpiente_1 = self.crear_serpiente()
                self.serpientes_juego = [serpiente_1]
            self.tableWidget.item(serpiente.casillas[0][0],serpiente.casillas[0][1]).setBackground(QtGui.QColor(82,135,135))
            x = 0 
            for tupla in serpiente.casillas[0: len(serpiente.casillas)-1]:
                x += 1
                tupla[0] = serpiente.casillas[x][0]
                tupla[1] = serpiente.casillas[x][1]
            if serpiente.direccion is "Abajo":
                if serpiente.casillas[-1][0] + 1 < self.tableWidget.rowCount():
                    serpiente.casillas[-1][0] += 1
                else:
                    serpiente.casillas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.casillas[-1][1] + 1 < self.tableWidget.columnCount():
                    serpiente.casillas[-1][1] += 1
                else:
                    serpiente.casillas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.casillas[-1][0] != 0:
                    serpiente.casillas[-1][0] -= 1
                else:
                    serpiente.casillas[-1][0] = self.tableWidget.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.casillas[-1][1] != 0:
                    serpiente.casillas[-1][1] -= 1
                else:
                    serpiente.casillas[-1][1] = self.tableWidget.columnCount()-1
        self.dibujar_serpientes() 

    def llenar_tabla(self):
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(82,135,135))

    def expandir_cuadros_tabla(self):
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def actualizar_tabla(self):
        num_filas = self.spinBox_3.value() 
        num_columnas = self.spinBox_2.value()
        self.tableWidget.setRowCount(num_filas) 
        self.tableWidget.setColumnCount(num_columnas)
        self.llenar_tabla() 

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ventana = VentanaServidor() 
    sys.exit(app.exec_())
