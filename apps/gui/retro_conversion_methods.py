#!/usr/bin/env python3
# X-Seti - November23 2025 - Multi-Emulator Launcher - Retro Conversion GUI Methods
#this belongs in apps/gui/retro_conversion_methods.py - Version: 1
"""
Retro Conversion GUI Methods - Button handlers and dialogs for retro system conversion.
Integrates with retro_convert.py core functionality.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QCheckBox, QComboBox, QSpinBox,
                            QFileDialog, QGroupBox, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt
from PIL import Image
import os

##Methods list -
# show_batch_convert_dialog
# show_texture_resize_dialog
# show_texture_upscale_dialog

def show_batch_convert_dialog(main_window, input_image_path: str = None): #vers 1
    """Show dialog for batch converting to multiple retro systems"""
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Batch Convert to Retro Systems")
    dialog.setMinimumWidth(400)
    
    layout = QVBoxLayout(dialog)
    
    # Input file selection
    input_layout = QHBoxLayout()
    input_label = QLabel("Input Image:")
    input_path = QLabel(input_image_path if input_image_path else "No file selected")
    input_btn = QPushButton("Browse")
    
    def select_input():
        path, _ = QFileDialog.getOpenFileName(
            dialog, "Select Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            input_path.setText(path)
    
    input_btn.clicked.connect(select_input)
    input_layout.addWidget(input_label)
    input_layout.addWidget(input_path, 1)
    input_layout.addWidget(input_btn)
    layout.addLayout(input_layout)
    
    # Output directory
    output_layout = QHBoxLayout()
    output_label = QLabel("Output Directory:")
    output_path = QLabel(os.path.expanduser("~/retro_exports"))
    output_btn = QPushButton("Browse")
    
    def select_output():
        path = QFileDialog.getExistingDirectory(dialog, "Select Output Directory")
        if path:
            output_path.setText(path)
    
    output_btn.clicked.connect(select_output)
    output_layout.addWidget(output_label)
    output_layout.addWidget(output_path, 1)
    output_layout.addWidget(output_btn)
    layout.addLayout(output_layout)
    
    # System selection (8-bit)
    bit8_group = QGroupBox("8-bit Systems")
    bit8_layout = QVBoxLayout()
    
    systems_8bit = {
        'zx': QCheckBox("ZX Spectrum (.scr)"),
        'c64': QCheckBox("Commodore 64 (.koa)"),
        'cpc': QCheckBox("Amstrad CPC (.scr)"),
        'bbc': QCheckBox("BBC Micro (.ssd)")
    }
    
    for checkbox in systems_8bit.values():
        checkbox.setChecked(True)
        bit8_layout.addWidget(checkbox)
    
    bit8_group.setLayout(bit8_layout)
    layout.addWidget(bit8_group)
    
    # System selection (16-bit)
    bit16_group = QGroupBox("16-bit Systems")
    bit16_layout = QVBoxLayout()
    
    systems_16bit = {
        'amiga': QCheckBox("Amiga (32 colors)"),
        'snes': QCheckBox("SNES (256 colors)"),
        'genesis': QCheckBox("Genesis/Mega Drive (64 colors)")
    }
    
    for checkbox in systems_16bit.values():
        checkbox.setChecked(True)
        bit16_layout.addWidget(checkbox)
    
    bit16_group.setLayout(bit16_layout)
    layout.addWidget(bit16_group)
    
    # Progress bar
    progress = QProgressBar()
    progress.setVisible(False)
    layout.addWidget(progress)
    
    # Buttons
    btn_layout = QHBoxLayout()
    convert_btn = QPushButton("Convert")
    cancel_btn = QPushButton("Cancel")
    
    def do_conversion():
        input_file = input_path.text()
        output_dir = output_path.text()
        
        if not input_file or input_file == "No file selected":
            QMessageBox.warning(dialog, "Error", "Please select an input image")
            return
        
        if not os.path.exists(input_file):
            QMessageBox.warning(dialog, "Error", "Input file does not exist")
            return
        
        # Get selected systems
        selected = []
        for key, checkbox in {**systems_8bit, **systems_16bit}.items():
            if checkbox.isChecked():
                selected.append(key)
        
        if not selected:
            QMessageBox.warning(dialog, "Error", "Please select at least one system")
            return
        
        # Show progress
        progress.setVisible(True)
        progress.setMaximum(len(selected))
        progress.setValue(0)
        
        # Import conversion module
        try:
            from components.retro_convert import batch_convert_retro
            
            results = batch_convert_retro(input_file, output_dir, selected)
            
            # Update progress
            progress.setValue(len(selected))
            
            # Show results
            success_count = sum(1 for v in results.values() if not v.startswith("Error"))
            msg = f"Conversion complete!\n\n"
            msg += f"Successfully converted: {success_count}/{len(selected)} systems\n"
            msg += f"Output directory: {output_dir}"
            
            QMessageBox.information(dialog, "Conversion Complete", msg)
            dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Conversion failed:\n{str(e)}")
            progress.setVisible(False)
    
    convert_btn.clicked.connect(do_conversion)
    cancel_btn.clicked.connect(dialog.reject)
    
    btn_layout.addWidget(convert_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    
    dialog.exec()

def show_texture_resize_dialog(main_window, current_image: Image.Image = None): #vers 1
    """Show dialog for resizing textures"""
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Resize Texture")
    dialog.setMinimumWidth(350)
    
    layout = QVBoxLayout(dialog)
    
    # Current size info
    if current_image:
        w, h = current_image.size
        current_label = QLabel(f"Current Size: {w} × {h}")
        layout.addWidget(current_label)
    
    # Size inputs
    size_layout = QHBoxLayout()
    width_label = QLabel("Width:")
    width_spin = QSpinBox()
    width_spin.setRange(1, 8192)
    width_spin.setValue(current_image.size[0] if current_image else 256)
    
    height_label = QLabel("Height:")
    height_spin = QSpinBox()
    height_spin.setRange(1, 8192)
    height_spin.setValue(current_image.size[1] if current_image else 256)
    
    size_layout.addWidget(width_label)
    size_layout.addWidget(width_spin)
    size_layout.addWidget(height_label)
    size_layout.addWidget(height_spin)
    layout.addLayout(size_layout)
    
    # Aspect ratio lock
    aspect_check = QCheckBox("Maintain Aspect Ratio")
    aspect_check.setChecked(True)
    layout.addWidget(aspect_check)
    
    # Resampling method
    method_layout = QHBoxLayout()
    method_label = QLabel("Method:")
    method_combo = QComboBox()
    method_combo.addItems(["Lanczos (Best Quality)", "Bicubic", "Bilinear", "Nearest (Pixel Art)"])
    method_layout.addWidget(method_label)
    method_layout.addWidget(method_combo, 1)
    layout.addLayout(method_layout)
    
    # Preset sizes
    preset_group = QGroupBox("Common Presets")
    preset_layout = QVBoxLayout()
    
    presets = {
        "C64 (160×200)": (160, 200),
        "ZX Spectrum (256×192)": (256, 192),
        "CPC (160×200)": (160, 200),
        "Amiga (320×256)": (320, 256),
        "SNES (256×224)": (256, 224),
        "Genesis (320×224)": (320, 224),
        "Power of 2 - 256×256": (256, 256),
        "Power of 2 - 512×512": (512, 512),
        "Power of 2 - 1024×1024": (1024, 1024)
    }
    
    def apply_preset(w, h):
        width_spin.setValue(w)
        height_spin.setValue(h)
    
    preset_btn_layout = QVBoxLayout()
    for name, (w, h) in presets.items():
        btn = QPushButton(name)
        btn.clicked.connect(lambda checked, w=w, h=h: apply_preset(w, h))
        preset_btn_layout.addWidget(btn)
    
    preset_layout.addLayout(preset_btn_layout)
    preset_group.setLayout(preset_layout)
    layout.addWidget(preset_group)
    
    # Buttons
    btn_layout = QHBoxLayout()
    apply_btn = QPushButton("Apply")
    cancel_btn = QPushButton("Cancel")
    
    def do_resize():
        if not current_image:
            QMessageBox.warning(dialog, "Error", "No image loaded")
            return
        
        try:
            from components.retro_convert import resize_texture
            
            new_w = width_spin.value()
            new_h = height_spin.value()
            maintain_aspect = aspect_check.isChecked()
            
            resized = resize_texture(current_image, new_w, new_h, maintain_aspect)
            
            # Return the resized image through dialog result
            dialog.resized_image = resized
            dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Resize failed:\n{str(e)}")
    
    apply_btn.clicked.connect(do_resize)
    cancel_btn.clicked.connect(dialog.reject)
    
    btn_layout.addWidget(apply_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    
    if dialog.exec():
        return getattr(dialog, 'resized_image', None)
    return None

def show_texture_upscale_dialog(main_window, current_image: Image.Image = None): #vers 1
    """Show dialog for upscaling textures"""
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Upscale Texture")
    dialog.setMinimumWidth(350)
    
    layout = QVBoxLayout(dialog)
    
    # Current size info
    if current_image:
        w, h = current_image.size
        current_label = QLabel(f"Current Size: {w} × {h}")
        layout.addWidget(current_label)
    
    # Scale factor
    scale_layout = QHBoxLayout()
    scale_label = QLabel("Scale Factor:")
    scale_spin = QSpinBox()
    scale_spin.setRange(2, 8)
    scale_spin.setValue(2)
    scale_layout.addWidget(scale_label)
    scale_layout.addWidget(scale_spin)
    layout.addLayout(scale_layout)
    
    # Preview result size
    def update_preview():
        if current_image:
            w, h = current_image.size
            factor = scale_spin.value()
            preview_label.setText(f"Result Size: {w * factor} × {h * factor}")
    
    preview_label = QLabel("Result Size: N/A")
    layout.addWidget(preview_label)
    scale_spin.valueChanged.connect(update_preview)
    if current_image:
        update_preview()
    
    # Method selection
    method_layout = QHBoxLayout()
    method_label = QLabel("Method:")
    method_combo = QComboBox()
    method_combo.addItems([
        "Lanczos (Best Quality)",
        "Bicubic (Good Quality)",
        "Bilinear (Fast)",
        "Nearest (Pixel Art)"
    ])
    method_layout.addWidget(method_label)
    method_layout.addWidget(method_combo, 1)
    layout.addLayout(method_layout)
    
    # Info text
    info_label = QLabel(
        "Note: For AI upscaling, use external tools like:\n"
        "• waifu2x (anime/art)\n"
        "• ESRGAN (photos)\n"
        "• Real-ESRGAN (general)"
    )
    info_label.setStyleSheet("color: gray; font-size: 10px;")
    layout.addWidget(info_label)
    
    # Buttons
    btn_layout = QHBoxLayout()
    apply_btn = QPushButton("Upscale")
    cancel_btn = QPushButton("Cancel")
    
    def do_upscale():
        if not current_image:
            QMessageBox.warning(dialog, "Error", "No image loaded")
            return
        
        try:
            from components.retro_convert import texture_upscale
            
            scale = scale_spin.value()
            method_map = {
                0: 'lanczos',
                1: 'bicubic',
                2: 'bilinear',
                3: 'nearest'
            }
            method = method_map[method_combo.currentIndex()]
            
            upscaled = texture_upscale(current_image, scale, method)
            
            # Return the upscaled image through dialog result
            dialog.upscaled_image = upscaled
            dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Upscale failed:\n{str(e)}")
    
    apply_btn.clicked.connect(do_upscale)
    cancel_btn.clicked.connect(dialog.reject)
    
    btn_layout.addWidget(apply_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    
    if dialog.exec():
        return getattr(dialog, 'upscaled_image', None)
    return None
