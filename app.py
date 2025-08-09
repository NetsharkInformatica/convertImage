import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox,
                             QSpinBox, QComboBox, QMessageBox, QFormLayout, QCheckBox, 
                             QColorDialog, QRadioButton, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PIL import Image, ImageOps, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
import os
import math

#___________________________Splash Screen___________________________


#___________________________fim Splash Screen___________________________

class PhotoResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redimensionador de Fotos com Logo - By Hélio Tomé")
        self.setGeometry(100, 100, 650, 680)
        self.setMaximumSize(650, 680)
        self.setMinimumSize(650, 680)
        
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
            QPushButton {
                min-height: 28px;
                padding: 4px;
            }
            QSpinBox, QComboBox, QLineEdit {
                max-height: 26px;
            }
            QLabel {
                margin-bottom: 2px;
            }
        """)
        
        self.initUI()
        self.set_default_values()
        
    def initUI(self):
        central_widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(central_widget)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        input_group = QGroupBox("Configurações de Entrada")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(6)
        
        self.origin_folder_btn = QPushButton("Selecionar Pasta com Fotos")
        self.origin_folder_btn.clicked.connect(self.select_origin_folder)
        self.origin_folder_label = QLabel("Nenhuma pasta selecionada")
        self.origin_folder_label.setWordWrap(True)
        
        self.dest_folder_btn = QPushButton("Selecionar Pasta de Destino")
        self.dest_folder_btn.clicked.connect(self.select_dest_folder)
        self.dest_folder_label = QLabel("Nenhuma pasta selecionada")
        self.dest_folder_label.setWordWrap(True)
        
        self.logo_file_btn = QPushButton("Selecionar Arquivo do Logo")
        self.logo_file_btn.clicked.connect(self.select_logo_file)
        self.logo_file_label = QLabel("Nenhum logo selecionado")
        self.logo_file_label.setWordWrap(True)
        
        input_layout.addWidget(self.origin_folder_btn)
        input_layout.addWidget(self.origin_folder_label)
        input_layout.addWidget(self.dest_folder_btn)
        input_layout.addWidget(self.dest_folder_label)
        input_layout.addWidget(self.logo_file_btn)
        input_layout.addWidget(self.logo_file_label)
        input_group.setLayout(input_layout)
        
        output_group = QGroupBox("Configurações de Saída")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(6)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Largura (cm):"))
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 100)
        size_layout.addWidget(self.width_input)
        
        size_layout.addWidget(QLabel("Altura (cm):"))
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 50)
        size_layout.addWidget(self.height_input)
        
        size_layout.addWidget(QLabel("DPI:"))
        self.dpi_input = QComboBox()
        self.dpi_input.addItems(["72 (Web)", "300 (Impressão)"])
        size_layout.addWidget(self.dpi_input)
        output_layout.addLayout(size_layout)
        
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
        
        margins_group = QGroupBox("Margens do Logo (px)")
        margins_layout = QFormLayout()
        margins_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        margins_layout.setHorizontalSpacing(15)
        
        self.left_margin_input = QSpinBox()
        self.left_margin_input.setRange(0, 500)
        margins_layout.addRow("Esquerda:", self.left_margin_input)
        
        self.right_margin_input = QSpinBox()
        self.right_margin_input.setRange(0, 500)
        margins_layout.addRow("Direita:", self.right_margin_input)
        
        self.top_margin_input = QSpinBox()
        self.top_margin_input.setRange(0, 500)
        margins_layout.addRow("Superior:", self.top_margin_input)
        
        self.bottom_margin_input = QSpinBox()
        self.bottom_margin_input.setRange(0, 500)
        margins_layout.addRow("Inferior:", self.bottom_margin_input)
        
        self.vertical_adjust_input = QSpinBox()
        self.vertical_adjust_input.setRange(-500, 500)
        margins_layout.addRow("Ajuste Vertical:", self.vertical_adjust_input)
        
        margins_group.setLayout(margins_layout)
        output_layout.addWidget(margins_group)
        
        border_group = QGroupBox("Configurações de Borda")
        border_layout = QFormLayout()
        border_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        
        self.border_checkbox = QCheckBox("Adicionar borda às imagens")
        self.border_checkbox.stateChanged.connect(self.toggle_border_controls)
        border_layout.addRow(self.border_checkbox)
        
        border_type_layout = QHBoxLayout()
        self.border_type_solid = QRadioButton("Contínua")
        self.border_type_solid.setChecked(True)
        self.border_type_dashed = QRadioButton("Pontilhada")
        border_type_layout.addWidget(self.border_type_solid)
        border_type_layout.addWidget(self.border_type_dashed)
        border_layout.addRow("Tipo:", border_type_layout)
        
        self.border_width_input = QSpinBox()
        self.border_width_input.setRange(1, 100)
        self.border_width_input.setValue(5)
        border_layout.addRow("Espessura (px):", self.border_width_input)
        
        self.border_color_btn = QPushButton("Cor da Borda")
        self.border_color_btn.clicked.connect(self.select_border_color)
        self.border_color_preview = QLabel()
        self.border_color_preview.setFixedSize(40, 20)
        self.border_color_preview.setStyleSheet("background-color: #FF0000;")
        self.border_color = "#FF0000"
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.border_color_btn)
        color_layout.addWidget(self.border_color_preview)
        border_layout.addRow("Cor:", color_layout)
        
        border_group.setLayout(border_layout)
        output_layout.addWidget(border_group)
        
        pdf_group = QGroupBox("Configurações de PDF")
        pdf_layout = QFormLayout()
        
        self.pdf_checkbox = QCheckBox("Exportar para PDF (A4 paisagem, 2 fotos/página)")
        self.pdf_checkbox.setChecked(True)
        pdf_layout.addRow(self.pdf_checkbox)
        
        self.pdf_filename_input = QLineEdit()
        self.pdf_filename_input.setPlaceholderText("nome_do_arquivo.pdf")
        self.pdf_filename_input.setText("fotos.pdf")
        pdf_layout.addRow("Nome do PDF:", self.pdf_filename_input)
        
        pdf_group.setLayout(pdf_layout)
        output_layout.addWidget(pdf_group)
        
        output_group.setLayout(output_layout)
        
        self.process_btn = QPushButton("PROCESSAR IMAGENS")
        self.process_btn.clicked.connect(self.process_images)
        self.process_btn.setStyleSheet("""
            background-color: #4CAF50; 
            color: white; 
            font-weight: bold; 
            padding: 8px;
            min-height: 35px;
        """)
        
        self.status_label = QLabel("Pronto para processar imagens")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        credit_label = QLabel("Desenvolvido por Hélio Tomé")
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setStyleSheet("font-style: italic; color: #555;")
        
        main_layout.addWidget(input_group)
        main_layout.addWidget(output_group)
        main_layout.addWidget(self.process_btn)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(credit_label)
        
        self.toggle_border_controls(False)

    def set_default_values(self):
        self.width_input.setValue(10)
        self.height_input.setValue(15)
        self.dpi_input.setCurrentIndex(1)
        self.left_margin_input.setValue(20)
        self.right_margin_input.setValue(20)
        self.top_margin_input.setValue(20)
        self.bottom_margin_input.setValue(20)
        self.vertical_adjust_input.setValue(0)

    def toggle_border_controls(self, state):
        enabled = state == Qt.Checked
        self.border_width_input.setEnabled(enabled)
        self.border_color_btn.setEnabled(enabled)
        self.border_color_preview.setEnabled(enabled)
        self.border_type_solid.setEnabled(enabled)
        self.border_type_dashed.setEnabled(enabled)

    def select_border_color(self):
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
        return int((cm * dpi) / 2.54)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def corrigir_orientacao(self, imagem):
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
        imagem.thumbnail(novo_tamanho, Image.LANCZOS)
        nova_imagem = Image.new('RGB', novo_tamanho, 'white')
        pos_x = (novo_tamanho[0] - imagem.width) // 2
        pos_y = (novo_tamanho[1] - imagem.height) // 2
        nova_imagem.paste(imagem, (pos_x, pos_y))
        return nova_imagem
    
    def adicionar_borda_solida(self, imagem, espessura, cor):
        if espessura <= 0:
            return imagem
        cor_rgb = self.hex_to_rgb(cor)
        return ImageOps.expand(imagem, border=espessura, fill=cor_rgb)
    
    def adicionar_borda_pontilhada(self, imagem, espessura, cor):
        if espessura <= 0:
            return imagem
            
        cor_rgb = self.hex_to_rgb(cor)
        largura, altura = imagem.size
        
        temp_img = ImageOps.expand(imagem, border=espessura, fill=cor_rgb)
        draw = ImageDraw.Draw(temp_img)
        
        coords = [
            (0, 0, largura + 2*espessura - 1, espessura - 1),
            (0, altura + espessura, largura + 2*espessura - 1, altura + 2*espessura - 1),
            (0, 0, espessura - 1, altura + 2*espessura - 1),
            (largura + espessura, 0, largura + 2*espessura - 1, altura + 2*espessura - 1)
        ]
        
        for coord in coords:
            for i in range(0, max(coord[2]-coord[0], coord[3]-coord[1]), 10):
                if i % 20 < 10:
                    if coord[2] - coord[0] > coord[3] - coord[1]:
                        draw.line([coord[0]+i, coord[1], coord[0]+i+5, coord[1]], fill="white")
                    else:
                        draw.line([coord[0], coord[1]+i, coord[0], coord[1]+i+5], fill="white")
        
        return temp_img
    
    def adicionar_borda(self, imagem, espessura, cor, pontilhada=False):
        if pontilhada:
            return self.adicionar_borda_pontilhada(imagem, espessura, cor)
        else:
            return self.adicionar_borda_solida(imagem, espessura, cor)
    
    def criar_pdf(self, imagens, pdf_path, dpi):
        try:
            a4_landscape = landscape(A4)
            page_width, page_height = a4_landscape

            width_cm = self.width_input.value()
            height_cm = self.height_input.value()
            img_width_pt = width_cm * 28.35
            img_height_pt = height_cm * 28.35

            margin = 28.35
            space_between = 28.35

            if (2 * img_width_pt + space_between + 2 * margin) > page_width:
                QMessageBox.warning(self, "Aviso", 
                    "As imagens são muito largas para caberem 2 por página. Será gerado 1 por página.")
                img_per_page = 1
            else:
                img_per_page = 2

            c = canvas.Canvas(pdf_path, pagesize=a4_landscape)

            for i in range(0, len(imagens), img_per_page):
                if i > 0:
                    c.showPage()

                for j in range(img_per_page):
                    if i + j < len(imagens):
                        img = ImageReader(imagens[i + j])
                        
                        if img_per_page == 2:
                            x = margin + j * (img_width_pt + space_between)
                        else:
                            x = (page_width - img_width_pt) / 2
                        
                        y = page_height - margin - img_height_pt
                        c.drawImage(img, x, y, width=img_width_pt, height=img_height_pt)

            c.save()
            return True
        except Exception as e:
            print(f"Erro ao criar PDF: {e}")
            return False
    
    def process_images(self):
        try:
            if not hasattr(self, 'origin_folder') or not hasattr(self, 'dest_folder') or not hasattr(self, 'logo_file'):
                QMessageBox.warning(self, "Atenção", "Por favor, selecione todas as pastas e o arquivo do logo!")
                return
                
            width_cm = self.width_input.value()
            height_cm = self.height_input.value()
            dpi = 300 if self.dpi_input.currentText().startswith("300") else 72
            logo_pos = self.logo_pos_combo.currentText()
            
            add_border = self.border_checkbox.isChecked()
            border_width = self.border_width_input.value() if add_border else 0
            border_color = self.border_color if add_border else "#FFFFFF"
            border_dashed = self.border_type_dashed.isChecked() if add_border else False
            
            export_pdf = self.pdf_checkbox.isChecked()
            pdf_filename = self.pdf_filename_input.text()
            if not pdf_filename.lower().endswith('.pdf'):
                pdf_filename += '.pdf'
            
            left_margin = self.left_margin_input.value()
            right_margin = self.right_margin_input.value()
            top_margin = self.top_margin_input.value()
            bottom_margin = self.bottom_margin_input.value()
            vertical_adjust = self.vertical_adjust_input.value()
            
            width_px = self.cm_to_pixels(width_cm, dpi)
            height_px = self.cm_to_pixels(height_cm, dpi)
            tamanho_final = (width_px, height_px)
            
            try:
                logo = Image.open(self.logo_file).convert("RGBA")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível carregar o logo: {str(e)}")
                return
            
            os.makedirs(self.dest_folder, exist_ok=True)
            
            processed = 0
            processed_images = []
            
            for arquivo in os.listdir(self.origin_folder):
                if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    entrada = os.path.join(self.origin_folder, arquivo)
                    saida = os.path.join(self.dest_folder, arquivo)
                    
                    try:
                        with Image.open(entrada) as img:
                            img = self.corrigir_orientacao(img)
                            img = self.redimensionar_mantendo_proporcao(img, tamanho_final)
                            
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
                            else:
                                pos_x = (img.width - logo.width) // 2
                                pos_y = (img.height - logo.height) // 2 + vertical_adjust
                            
                            pos_x = max(0, pos_x)
                            pos_y = max(0, pos_y)
                            
                            img.paste(logo, (int(pos_x), int(pos_y)), logo)
                            
                            if add_border:
                                img = self.adicionar_borda(img, border_width, border_color, border_dashed)
                            
                            img.save(saida, quality=95)
                            processed += 1
                            processed_images.append(saida)
                            self.status_label.setText(f"Processando... {processed} imagens processadas")
                            QApplication.processEvents()
                            
                    except Exception as e:
                        print(f"Erro ao processar {arquivo}: {e}")
            
            if export_pdf and processed_images:
                pdf_path = os.path.join(self.dest_folder, pdf_filename)
                if self.criar_pdf(processed_images, pdf_path, dpi):
                    pdf_msg = f"\nPDF criado: {pdf_filename}"
                else:
                    pdf_msg = "\nErro ao criar o PDF"
            else:
                pdf_msg = ""
            
            QMessageBox.information(self, "Concluído", 
                                  f"Processamento finalizado!\n{processed} imagens foram processadas e salvas em:\n{self.dest_folder}{pdf_msg}")
            self.status_label.setText("Processamento concluído com sucesso!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante o processamento:\n{str(e)}")
            self.status_label.setText("Erro durante o processamento")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PhotoResizerApp()
    window.show()
    sys.exit(app.exec_())