#!/bin/bash
# X-Seti - November23 2025 - GUI Window Button Integration Script
# This script updates gui_window.py to connect retro conversion buttons

# File to modify
GUI_FILE="apps/gui/gui_window.py"

echo "=== Updating gui_window.py buttons ==="

# 1. Update Button 1 (Export All) to Batch Convert
sed -i '1224s/self.export_all_btn = QPushButton("Button")/self.export_all_btn = QPushButton("Batch Convert")/' "$GUI_FILE"
sed -i '1228,1229s|#self.export_all_btn.clicked.connect(self.export_all)|self.export_all_btn.clicked.connect(self._show_batch_convert)|' "$GUI_FILE"
sed -i '1229s/self.export_all_btn.setEnabled(False)/self.export_all_btn.setEnabled(True)/' "$GUI_FILE"

# 2. Update Button 2 (Switch) to Texture Resize
sed -i '1235s/self.switch_btn = QPushButton("Button 2")/self.switch_btn = QPushButton("Resize")/' "$GUI_FILE"
sed -i '1239s|#self.switch_btn.clicked.connect(self.switch_texture_view)|self.switch_btn.clicked.connect(self._show_texture_resize)|' "$GUI_FILE"
sed -i '1240s/self.switch_btn.setEnabled(False)/self.switch_btn.setEnabled(True)/' "$GUI_FILE"
sed -i '1241s/self.switch_btn.setToolTip("Cycle: Normal → Second → Both → Overlay")/self.switch_btn.setToolTip("Resize texture to common retro system dimensions")/' "$GUI_FILE"

# 3. Add import for retro conversion methods at top of file
# Find line with "from typing import" and add after it
sed -i '/^from typing import/a\
\
# Retro conversion imports\
try:\
    from gui.retro_conversion_methods import (\
        show_batch_convert_dialog,\
        show_texture_resize_dialog,\
        show_texture_upscale_dialog\
    )\
    RETRO_CONVERSION_AVAILABLE = True\
except ImportError:\
    RETRO_CONVERSION_AVAILABLE = False\
    print("Warning: Retro conversion methods not available")' "$GUI_FILE"

# 4. Add button handler methods before setup_ui method
# Find the line number of "def setup_ui(self):" and insert before it
LINE_NUM=$(grep -n "def setup_ui(self):" "$GUI_FILE" | head -1 | cut -d: -f1)

# Create temporary file with new methods
cat > /tmp/retro_methods.txt << 'EOF'

    def _show_batch_convert(self): #vers 1
        """Show batch conversion dialog"""
        if not RETRO_CONVERSION_AVAILABLE:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Retro conversion module not available")
            return
        
        # Get current image if available
        current_image = None
        # Add logic here to get current image from your app
        
        show_batch_convert_dialog(self.main_window, None)

    def _show_texture_resize(self): #vers 1
        """Show texture resize dialog"""
        if not RETRO_CONVERSION_AVAILABLE:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Retro conversion module not available")
            return
        
        # Get current image if available
        current_image = None
        # Add logic here to get current image from your app
        
        result = show_texture_resize_dialog(self.main_window, current_image)
        if result:
            # Handle the resized image
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Texture resized successfully")

    def _show_texture_upscale(self): #vers 1
        """Show texture upscale dialog"""
        if not RETRO_CONVERSION_AVAILABLE:
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Retro conversion module not available")
            return
        
        # Get current image if available
        current_image = None
        # Add logic here to get current image from your app
        
        result = show_texture_upscale_dialog(self.main_window, current_image)
        if result:
            # Handle the upscaled image
            if hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("Texture upscaled successfully")

EOF

# Insert the methods before setup_ui
sed -i "${LINE_NUM}r /tmp/retro_methods.txt" "$GUI_FILE"

echo "=== Button integration complete ==="
echo ""
echo "Updated buttons:"
echo "  • 'Button' → 'Batch Convert' (connected to batch retro conversion)"
echo "  • 'Button 2' → 'Resize' (connected to texture resizing)"
echo ""
echo "To add Upscale button, add another button in toolbar section."
