#!/usr/bin/python
# coding=utf-8

import sys, os
from PyQt4 import QtGui, QtCore
import shutil
import Image, ImageDraw

class CentralWidget(QtGui.QWidget):
    def __init__(self, parent= None):
        QtGui.QWidget.__init__(self, parent)
        
        # spinbox para alterar o ângulo da imagem
        self.graus = QtGui.QSpinBox()
        self.graus.setRange(0, 359)
        self.graus.setValue(0)
        self.graus.setWrapping(True)
        self.graus.setMaximumWidth(40)
        
        # barra de rolagem vertical para deslocar a imagem.
        self.deslocamento = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.deslocamento.setRange(-30, 30)
        self.deslocamento.setValue(0)
        self.deslocamento.setMaximumWidth(200)
        self.desloc_label = QtGui.QLabel('0')
        
        self.ok = QtGui.QPushButton('ok', self)
        self.ok.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.ok.setMaximumWidth(40)

        # exibe a imagem em um label
        self.label = QtGui.QLabel(self)
        
        grid = QtGui.QGridLayout()
        grid.addWidget(self.label, 0, 0)
        grid.addWidget(self.graus,0,2)
        spacer = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum) 
        grid.addItem(spacer,0,1)
        grid.addWidget(self.deslocamento,1,0)
        grid.addWidget(self.desloc_label, 1,2)
        grid.addWidget(self.ok, 2, 2, 1, 1) 
        self.setLayout(grid)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(700, 300)
        self.setWindowTitle(u'Gerador de Rostos Simétricos')
        self.filename = 'vazio.png'

        exit = QtGui.QAction(QtGui.QIcon('Exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        abre_arquivo = QtGui.QAction( 'Open File', self)
        self.connect(abre_arquivo, QtCore.SIGNAL('triggered()'), self.abre_arquivo)

        file = self.menuBar().addMenu('&File')
        file.addAction(abre_arquivo)
        file.addAction(exit)
        
        self.cw = CentralWidget()
        self.setCentralWidget(self.cw)

        self.connect(self.cw.graus, QtCore.SIGNAL('valueChanged(int)'), self.atualiza_imagem)
        self.connect(self.cw.deslocamento, QtCore.SIGNAL('valueChanged(int)'), self.atualiza_imagem)
        self.connect(self.cw.ok, QtCore.SIGNAL('clicked()'), self.processa_imagem)
                
        self.atualiza_imagem()

    def processa_imagem(self):
        ''' gera os dois rostos a partir da imagem calibrada
        '''
        
        # se já estava exibindo a imagem resultado, volta a exibir a imagem original
        if self.cw.label.width() == 600:
            self.atualiza_imagem()
            return()
            
        # define nomes de arquivos temporários
        fname = './temp/temp_'+ str(self.filename).split('/')[-1]
        rname = './temp/result_'+ str(self.filename).split('/')[-1]
        
        # abre imagem calibrada
        im = Image.open(fname)

        # gera as duas imagens a partir da original
        lefthalf = im.crop((0,0,(im.size[0]/2), im.size[1]))
        righthalf = im.crop(((im.size[0]/2),0,im.size[0], im.size[1]))
        
        # gera as imagens espelho
        leftflip = lefthalf.transpose(Image.FLIP_LEFT_RIGHT)
        rightflip = righthalf.transpose(Image.FLIP_LEFT_RIGHT)

        # cria o objeto para armazenar a imagem resultado
        result = Image.new("RGBA", (im.size[0]*3,im.size[1]))

        # cola a original
        result.paste(im,(0,0))

        # a gerada a partir do lado esquerdo
        result.paste(lefthalf, (im.size[0],0))
        result.paste(leftflip, ((im.size[0] + im.size[0]/2) ,0))

        # a gerada a partir do lado direito
        result.paste(rightflip, (im.size[0]*2,0))
        result.paste(righthalf, (im.size[0]*2+im.size[0]/2,0))

        result.save(rname)
        
        # mostra a imagem resultado
        pixmap = QtGui.QPixmap(rname)
        pixmap = pixmap.scaled(600,200, QtCore.Qt.KeepAspectRatio)
        self.cw.label.setPixmap(pixmap)

    def atualiza_imagem(self, valor=0):
        '''' exibe a imagem original com o deslocamento e rotação corretos. 
        ''' 
        
        # define nomes de arquivos temporários
        fname = './temp/temp_'+ str(self.filename).split('/')[-1]
        redfname = './temp/red_' + str(self.filename).split('/')[-1]
        
        # usa a imagem original
        image = Image.open(str(self.filename))
        
        # primeiro rotaciona
        if self.cw.graus.value() >0:
            image = image.rotate(self.cw.graus.value())
            
        # desloca a imagem
        delta = self.cw.deslocamento.value()
        self.cw.desloc_label.setText(str(delta))
        
        if delta !=0: 
        
            xsize, ysize = image.size
        
            result = Image.new("RGBA", (image.size[0],image.size[1]))
        
            if delta >0:
                # se positivo desloca a imagem para direita
                xsize = xsize -int(xsize*delta/100.0)
                part1 = image.crop((0, 0, xsize, ysize))
                result.paste(part1,(image.size[0]-xsize,0,image.size[0], ysize))
            else:
                # se negativo, desloca a imagem paa esquerda
                xsize = xsize +int(xsize*delta/100.0)
                part1 = image.crop((image.size[0]-xsize,0,image.size[0], ysize))
                result.paste(part1,(0,0,xsize,ysize))
                
            image  = result

        image.save(fname)
        
        # desenha linha vermelha central para auxiliar a calibração da imagem.
        draw = ImageDraw.Draw(image)
        draw.line((image.size[0]/2,0,image.size[0]/2,image.size[1]), fill='red')
        image.save(redfname)
            
        # mostra a imagem
        pixmap = QtGui.QPixmap(redfname)
        pixmap = pixmap.scaled(200,200, QtCore.Qt.KeepAspectRatio)
        self.cw.label.setPixmap(pixmap)        

    def abre_arquivo(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', './fotos')
        
        if filename  != "":
            self.filename = filename
            fname = str(self.filename).split('/')[-1]
            shutil.copyfile(self.filename,'./temp/temp_' + fname )
            self.cw.deslocamento.setValue(0)
            self.cw.graus.setValue(0)
            self.atualiza_imagem()


# cria diretórios e imagem auxiliar, se preciso
if not os.path.exists('./temp'):
    os.mkdir('./temp')
    
if not os.path.exists('./fotos'):
    os.mkdir('./fotos')

if not os.path.exists('vazio.png'):
    imagem = Image.new("RGBA", (200,200))
    imagem.save('vazio.png')

# inicia a GUI
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
