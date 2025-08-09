import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox,
                             QSpinBox, QComboBox, QMessageBox, QFormLayout, QCheckBox, 
                             QColorDialog, QRadioButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PIL import Image, ImageOps, ImageDraw
import os

class PhotoResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redimensionador de Fotos com Logo - Desenvolvido por Hélio Tomé")
        self.setGeometry(100, 100, 700, 750)  # Aumentei a altura para acomodar os novos controles
        self.setMinimumSize(550, 700)  # Tamanho mínimo
        self.setMaximumSize(550, 700)  # Tamanho máximo
        
        self.initUI()
        self.set_default_values()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Grupo: Configurações de Entrada
        input_group = QGroupBox("Configurações de Entrada")
        input_layout = QVBoxLayout()
        
        # Pasta de origem
        self.origin_folder_btn = QPushButton("Selecionar Pasta com Fotos")
        self.origin_folder_btn.clicked.connect(self.select_origin_folder)
        self.origin_folder_label = QLabel("Nenhuma pasta selecionada")
        
        # Pasta de destino
        self.dest_folder_btn = QPushButton("Selecionar Pasta de Destino")
        self.dest_folder_btn.clicked.connect(self.select_dest_folder)
        self.dest_folder_label = QLabel("Nenhuma pasta selecionada")
        
        # Arquivo do logo
        self.logo_file_btn = QPushButton("Selecionar Arquivo do Logo")
        self.logo_file_btn.clicked.connect(self.select_logo_file)
        self.logo_file_label = QLabel("Nenhum logo selecionado")
        
        input_layout.addWidget(self.origin_folder_btn)
        input_layout.addWidget(self.origin_folder_label)
        input_layout.addWidget(self.dest_folder_btn)
        input_layout.addWidget(self.dest_folder_label)
        input_layout.addWidget(self.logo_file_btn)
        input_layout.addWidget(self.logo_file_label)
        input_group.setLayout(input_layout)
        
        # Grupo: Configurações de Saída
        output_group = QGroupBox("Configurações de Saída")
        output_layout = QVBoxLayout()
        
        # Tamanho da imagem
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Largura (cm):"))
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 100)
        size_layout.addWidget(self.width_input)
        
        size_layout.addWidget(QLabel("Altura (cm):"))
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 100)
        size_layout.addWidget(self.height_input)
        
        size_layout.addWidget(QLabel("DPI:"))
        self.dpi_input = QComboBox()
        self.dpi_input.addItems(["72 (Web)", "300 (Impressão)"])
        size_layout.addWidget(self.dpi_input)
        output_layout.addLayout(size_layout)
        
        # Posição do logo
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Posição do Logo:"))
        self.logo_pos_combo = QComboBox()
        self.logo_pos_combo.addItems([
            "Canto Inferior Direito", 
            "Canto Inferior Esquerdo",
            "Canto Superior Direito",
            "Canto Superior Esquerdo",
            "Centro"
        ])
        pos_layout.addWidget(self.logo_pos_combo)
        output_layout.addLayout(pos_layout)
        
        # Controles de Margem
        margins_group = QGroupBox("Configurações de Margem do Logo")
        margins_layout = QFormLayout()
        
        # Margens horizontais
        self.left_margin_input = QSpinBox()
        self.left_margin_input.setRange(0, 500)
        margins_layout.addRow("Margem Esquerda (px):", self.left_margin_input)
        
        self.right_margin_input = QSpinBox()
        self.right_margin_input.setRange(0, 500)
        margins_layout.addRow("Margem Direita (px):", self.right_margin_input)
        
        # Margens verticais
        self.top_margin_input = QSpinBox()
        self.top_margin_input.setRange(0, 500)
        margins_layout.addRow("Margem Superior (px):", self.top_margin_input)
        
        self.bottom_margin_input = QSpinBox()
        self.bottom_margin_input.setRange(0, 500)
        margins_layout.addRow("Margem Inferior (px):", self.bottom_margin_input)
        
        # Ajuste fino vertical
        self.vertical_adjust_input = QSpinBox()
        self.vertical_adjust_input.setRange(-500, 500)
        margins_layout.addRow("Ajuste Fino Vertical (px):", self.vertical_adjust_input)
        
        margins_group.setLayout(margins_layout)
        output_layout.addWidget(margins_group)
        
        # Grupo: Configurações de Borda
        border_group = QGroupBox("Configurações de Borda")
        border_layout = QFormLayout()
        
        # Checkbox para ativar/desativar borda
        self.border_checkbox = QCheckBox("Adicionar borda às imagens")
        self.border_checkbox.stateChanged.connect(self.toggle_border_controls)
        border_layout.addRow(self.border_checkbox)
        
        # Tipo de borda
        border_type_layout = QHBoxLayout()
        self.border_type_solid = QRadioButton("Contínua")
        self.border_type_solid.setChecked(True)
        self.border_type_dashed = QRadioButton("Pontilhada")
        border_type_layout.addWidget(self.border_type_solid)
        border_type_layout.addWidget(self.border_type_dashed)
        border_layout.addRow("Tipo de borda:", border_type_layout)
        
        # Espessura da borda
        self.border_width_input = QSpinBox()
        self.border_width_input.setRange(1, 100)
        self.border_width_input.setValue(5)
        border_layout.addRow("Espessura da borda (px):", self.border_width_input)
        
        # Cor da borda
        self.border_color_btn = QPushButton("Selecionar Cor da Borda")
        self.border_color_btn.clicked.connect(self.select_border_color)
        self.border_color_preview = QLabel()
        self.border_color_preview.setFixedSize(50, 20)
        self.border_color_preview.setStyleSheet("background-color: #FF0000;")  # Vermelho como padrão
        self.border_color = "#FF0000"  # Valor padrão
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.border_color_btn)
        color_layout.addWidget(self.border_color_preview)
        border_layout.addRow("Cor da borda:", color_layout)
        
        border_group.setLayout(border_layout)
        output_layout.addWidget(border_group)
        
        output_group.setLayout(output_layout)
        
        # Botão de processamento
        self.process_btn = QPushButton("Processar Imagens")
        self.process_btn.clicked.connect(self.process_images)
        self.process_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        
        # Barra de status
        self.status_label = QLabel("Pronto para processar imagens")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        # Créditos do desenvolvedor
        credit_label = QLabel("Software orgulhosamente desenvolvido por Hélio Tomé")
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setStyleSheet("font-style: italic; color: #555; margin-top: 10px;")
        
        # Adicionando todos os widgets ao layout principal
        main_layout.addWidget(input_group)
        main_layout.addWidget(output_group)
        main_layout.addWidget(self.process_btn)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(credit_label)
        
        # Inicialmente desativa os controles de borda
        self.toggle_border_controls(False)
        
    def set_default_values(self):
        """Define valores padrão para os campos"""
        self.width_input.setValue(10)
        self.height_input.setValue(15)
        self.dpi_input.setCurrentIndex(1)  # 300 DPI
        
        # Valores padrão para margens
        self.left_margin_input.setValue(20)
        self.right_margin_input.setValue(20)
        self.top_margin_input.setValue(20)
        self.bottom_margin_input.setValue(20)
        self.vertical_adjust_input.setValue(0)
        
    def toggle_border_controls(self, state):
        """Ativa/desativa os controles de borda"""
        enabled = state == Qt.Checked
        self.border_width_input.setEnabled(enabled)
        self.border_color_btn.setEnabled(enabled)
        self.border_color_preview.setEnabled(enabled)
        self.border_type_solid.setEnabled(enabled)
        self.border_type_dashed.setEnabled(enabled)
        
    def select_border_color(self):
        """Abre o diálogo para selecionar a cor da borda"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color = color.name()
            self.border_color_preview.setStyleSheet(f"background-color: {self.border_color};")
            
    def select_origin_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta com Fotos")
        if folder:
            self.origin_folder = folder
            self.origin_folder_label.setText(folder)
            self.origin_folder_label.setStyleSheet("color: green;")
            
    def select_dest_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Destino")
        if folder:
            self.dest_folder = folder
            self.dest_folder_label.setText(folder)
            self.dest_folder_label.setStyleSheet("color: green;")
            
    def select_logo_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo do Logo", "", 
                                            "Imagens (*.png *.jpg *.jpeg)")
        if file:
            self.logo_file = file
            self.logo_file_label.setText(file)
            self.logo_file_label.setStyleSheet("color: green;")
            
    def cm_to_pixels(self, cm, dpi):
        """Converte centímetros para pixels"""
        return int((cm * dpi) / 2.54)
    
    def hex_to_rgb(self, hex_color):
        """Converte cor hexadecimal para tupla RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def corrigir_orientacao(self, imagem):
        """Corrige a rotação automática baseada nos metadados EXIF"""
        try:
            exif = imagem._getexif()
            if exif:
                orientacao = exif.get(274)
                if orientacao == 3:
                    imagem = imagem.rotate(180, expand=True)
                elif orientacao == 6:
                    imagem = imagem.rotate(270, expand=True)
                elif orientacao == 8:
                    imagem = imagem.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        return imagem
    
    def redimensionar_mantendo_proporcao(self, imagem, novo_tamanho):
        """Redimensiona a imagem mantendo proporção"""
        imagem.thumbnail(novo_tamanho, Image.LANCZOS)
        nova_imagem = Image.new('RGB', novo_tamanho, 'white')
        pos_x = (novo_tamanho[0] - imagem.width) // 2
        pos_y = (novo_tamanho[1] - imagem.height) // 2
        nova_imagem.paste(imagem, (pos_x, pos_y))
        return nova_imagem
    
    def adicionar_borda_solida(self, imagem, espessura, cor):
        """Adiciona uma borda sólida à imagem"""
        if espessura <= 0:
            return imagem
        cor_rgb = self.hex_to_rgb(cor)
        return ImageOps.expand(imagem, border=espessura, fill=cor_rgb)
    
    def adicionar_borda_pontilhada(self, imagem, espessura, cor):
        """Adiciona uma borda pontilhada à imagem"""
        if espessura <= 0:
            return imagem
            
        cor_rgb = self.hex_to_rgb(cor)
        largura, altura = imagem.size
        
        # Cria uma imagem temporária com borda
        temp_img = ImageOps.expand(imagem, border=espessura, fill=cor_rgb)
        
        # Desenha a borda pontilhada
        draw = ImageDraw.Draw(temp_img)
        
        # Coordenadas para os retângulos
        coords = [
            (0, 0, largura + 2*espessura - 1, espessura - 1),  # Topo
            (0, altura + espessura, largura + 2*espessura - 1, altura + 2*espessura - 1),  # Base
            (0, 0, espessura - 1, altura + 2*espessura - 1),  # Esquerda
            (largura + espessura, 0, largura + 2*espessura - 1, altura + 2*espessura - 1)  # Direita
        ]
        
        # Desenha cada lado com padrão pontilhado
        for coord in coords:
            for i in range(0, max(coord[2]-coord[0], coord[3]-coord[1]), 10):
                if i % 20 < 10:  # Alterna entre desenhar e não desenhar
                    if coord[2] - coord[0] > coord[3] - coord[1]:  # Linha horizontal
                        draw.line([coord[0]+i, coord[1], coord[0]+i+5, coord[1]], fill="white")
                    else:  # Linha vertical
                        draw.line([coord[0], coord[1]+i, coord[0], coord[1]+i+5], fill="white")
        
        return temp_img
    
    def adicionar_borda(self, imagem, espessura, cor, pontilhada=False):
        """Adiciona borda à imagem conforme configuração"""
        if pontilhada:
            return self.adicionar_borda_pontilhada(imagem, espessura, cor)
        else:
            return self.adicionar_borda_solida(imagem, espessura, cor)
    
    def process_images(self):
        """Processa todas as imagens conforme configurações"""
        try:
            # Verifica se todos os campos foram preenchidos
            if not hasattr(self, 'origin_folder') or not hasattr(self, 'dest_folder') or not hasattr(self, 'logo_file'):
                QMessageBox.warning(self, "Atenção", "Por favor, selecione todas as pastas e o arquivo do logo!")
                return
                
            # Obtém configurações da interface
            width_cm = self.width_input.value()
            height_cm = self.height_input.value()
            dpi = 300 if self.dpi_input.currentText().startswith("300") else 72
            logo_pos = self.logo_pos_combo.currentText()
            
            # Obtém configurações de borda
            add_border = self.border_checkbox.isChecked()
            border_width = self.border_width_input.value() if add_border else 0
            border_color = self.border_color if add_border else "#FFFFFF"
            border_dashed = self.border_type_dashed.isChecked() if add_border else False
            
            # Obtém todas as margens
            left_margin = self.left_margin_input.value()
            right_margin = self.right_margin_input.value()
            top_margin = self.top_margin_input.value()
            bottom_margin = self.bottom_margin_input.value()
            vertical_adjust = self.vertical_adjust_input.value()
            
            # Converte medidas para pixels
            width_px = self.cm_to_pixels(width_cm, dpi)
            height_px = self.cm_to_pixels(height_cm, dpi)
            tamanho_final = (width_px, height_px)
            
            # Carrega a logomarca
            try:
                logo = Image.open(self.logo_file).convert("RGBA")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível carregar o logo: {str(e)}")
                return
            
            # Cria pasta de destino se não existir
            os.makedirs(self.dest_folder, exist_ok=True)
            
            # Processa cada imagem
            processed = 0
            for arquivo in os.listdir(self.origin_folder):
                if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    entrada = os.path.join(self.origin_folder, arquivo)
                    saida = os.path.join(self.dest_folder, arquivo)
                    
                    try:
                        with Image.open(entrada) as img:
                            # Corrige orientação
                            img = self.corrigir_orientacao(img)
                            
                            # Redimensiona mantendo proporção
                            img = self.redimensionar_mantendo_proporcao(img, tamanho_final)
                            
                            # Calcula posição do logo baseado na seleção
                            if logo_pos == "Canto Inferior Direito":
                                pos_x = img.width - logo.width - right_margin
                                pos_y = img.height - logo.height - bottom_margin + vertical_adjust
                            elif logo_pos == "Canto Inferior Esquerdo":
                                pos_x = left_margin
                                pos_y = img.height - logo.height - bottom_margin + vertical_adjust
                            elif logo_pos == "Canto Superior Direito":
                                pos_x = img.width - logo.width - right_margin
                                pos_y = top_margin + vertical_adjust
                            elif logo_pos == "Canto Superior Esquerdo":
                                pos_x = left_margin
                                pos_y = top_margin + vertical_adjust
                            else:  # Centro
                                pos_x = (img.width - logo.width) // 2
                                pos_y = (img.height - logo.height) // 2 + vertical_adjust
                            
                            # Garante que as posições não sejam negativas
                            pos_x = max(0, pos_x)
                            pos_y = max(0, pos_y)
                            
                            # Aplica a logo
                            img.paste(logo, (int(pos_x), int(pos_y)), logo)
                            
                            # Adiciona borda se necessário
                            if add_border:
                                img = self.adicionar_borda(img, border_width, border_color, border_dashed)
                            
                            # Salva com alta qualidade
                            img.save(saida, quality=95)
                            processed += 1
                            self.status_label.setText(f"Processando... {processed} imagens processadas")
                            QApplication.processEvents()  # Atualiza a UI
                            
                    except Exception as e:
                        print(f"Erro ao processar {arquivo}: {e}")
            
            QMessageBox.information(self, "Concluído", 
                                  f"Processamento finalizado!\n{processed} imagens foram processadas e salvas em:\n{self.dest_folder}")
            self.status_label.setText("Processamento concluído com sucesso!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante o processamento:\n{str(e)}")
            self.status_label.setText("Erro durante o processamento")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Melhora a aparência da interface
    window = PhotoResizerApp()
    window.show()
    sys.exit(app.exec_())