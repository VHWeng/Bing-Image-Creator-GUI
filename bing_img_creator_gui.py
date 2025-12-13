import sys
import os
import json
import requests
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QComboBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from bing_create.main import ImageGenerator

# Style categories from the provided list
STYLE_CATEGORIES = {
    "Photographic & Realistic": [
        "Photorealistic",
        "Cinematic Film Still",
        "Analog Film (35mm / Kodak / Fujifilm)",
        "Film Noir",
        "Portrait Photography",
        "Food Photography",
        "Macro Photography",
        "Street Photography",
        "Old Photograph BW",
        "Old Photograph Colorized"
    ],
    "Artistic & Painting": [
        "Oil Painting",
        "Watercolor",
        "BW Pencil Sketch",
        "Color Pencil Sketch",
        "BW Charcoal Drawing",
        "Color Charcoal Drawing",
        "Digital Painting",
        "Surrealism",
        "Impressionism"
    ],
    "Graphic & Stylized": [
        "Illustration",
        "Anime",
        "Comic Book",
        "Graphic Novel",
        "Pixel Art",
        "Vector Graphics",
        "Flat Design"
    ],
    "3D & Rendering": [
        "3D Rendering",
        "Octane Render / Unreal Engine",
        "Lowpoly",
        "Isometric",
        "Blender Render"
    ],
    "Genre & Aesthetic": [
        "Cyberpunk",
        "Neonpunk",
        "Steampunk",
        "Fantasy",
        "Sci-Fi",
        "Art Deco",
        "Art Nouveau",
        "Minimalist",
        "Vintage / Retro",
        "Concept Art"
    ]
}


class ImageGenerationThread(QThread):
    """Thread for generating images without blocking the UI"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    status = pyqtSignal(str)
    
    def __init__(self, generator, prompt, num_images):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.num_images = num_images
    
    def run(self):
        try:
            self.status.emit(f"Generating {self.num_images} image(s)...")
            images = self.generator.generate(prompt=self.prompt, num_images=self.num_images)
            # Extract image URLs from the response
            image_urls = []
            if isinstance(images, list):
                for img in images:
                    if isinstance(img, dict) and 'url' in img:
                        image_urls.append(img['url'])
                    elif isinstance(img, str):
                        image_urls.append(img)
            self.finished.emit(image_urls)
        except Exception as e:
            self.error.emit(str(e))


class BingImageCreatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bing Image Creator GUI")
        self.setMinimumSize(900, 1000)
        
        self.current_images = []
        self.current_image_index = 0
        self.image_counter = 1
        self.generator = None
        
        self.init_ui()
        self.load_environment_vars()
    
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Cookie Configuration Group
        cookie_group = QGroupBox("Cookie Configuration")
        cookie_layout = QVBoxLayout()
        
        # U_COOKIE
        u_cookie_layout = QHBoxLayout()
        u_cookie_layout.addWidget(QLabel("U_COOKIE:"))
        self.u_cookie_input = QLineEdit()
        self.u_cookie_input.setPlaceholderText("Enter U_COOKIE value")
        u_cookie_layout.addWidget(self.u_cookie_input)
        cookie_layout.addLayout(u_cookie_layout)
        
        # SRCHHPGUSR
        srchhpgusr_layout = QHBoxLayout()
        srchhpgusr_layout.addWidget(QLabel("SRCHHPGUSR:"))
        self.srchhpgusr_input = QLineEdit()
        self.srchhpgusr_input.setPlaceholderText("Enter SRCHHPGUSR value")
        srchhpgusr_layout.addWidget(self.srchhpgusr_input)
        cookie_layout.addLayout(srchhpgusr_layout)
        
        # Validation buttons
        button_layout = QHBoxLayout()
        self.validate_btn = QPushButton("Validate Cookies")
        self.validate_btn.clicked.connect(self.validate_cookies)
        button_layout.addWidget(self.validate_btn)
        
        self.update_env_btn = QPushButton("Update Environment Variables")
        self.update_env_btn.clicked.connect(self.update_environment_vars)
        button_layout.addWidget(self.update_env_btn)
        cookie_layout.addLayout(button_layout)
        
        cookie_group.setLayout(cookie_layout)
        layout.addWidget(cookie_group)
        
        # Prompt Generation Group
        prompt_group = QGroupBox("Prompt Generation")
        prompt_layout = QVBoxLayout()
        
        # Word/Phrase input
        phrase_layout = QHBoxLayout()
        phrase_layout.addWidget(QLabel("Word/Phrase:"))
        self.phrase_input = QLineEdit()
        self.phrase_input.setPlaceholderText("Enter subject for image generation")
        phrase_layout.addWidget(self.phrase_input)
        prompt_layout.addLayout(phrase_layout)
        
        # Ollama model selection
        ollama_layout = QHBoxLayout()
        ollama_layout.addWidget(QLabel("Ollama Model:"))
        self.ollama_combo = QComboBox()
        self.ollama_combo.addItem("None (Direct prompt)")
        ollama_layout.addWidget(self.ollama_combo)
        
        self.refresh_ollama_btn = QPushButton("Refresh Models")
        self.refresh_ollama_btn.clicked.connect(self.refresh_ollama_models)
        ollama_layout.addWidget(self.refresh_ollama_btn)
        prompt_layout.addLayout(ollama_layout)
        
        # Generated prompt display
        prompt_display_layout = QHBoxLayout()
        prompt_display_layout.addWidget(QLabel("Generated Prompt:"))
        self.generated_prompt_display = QLineEdit()
        self.generated_prompt_display.setReadOnly(True)
        self.generated_prompt_display.setPlaceholderText("Generated prompt will appear here...")
        prompt_display_layout.addWidget(self.generated_prompt_display)
        prompt_layout.addLayout(prompt_display_layout)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Style Selection Group
        style_group = QGroupBox("Style Selection")
        style_layout = QVBoxLayout()
        
        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.populate_styles()
        style_row.addWidget(self.style_combo)
        
        style_row.addWidget(QLabel("Custom Style:"))
        self.custom_style_input = QLineEdit()
        self.custom_style_input.setPlaceholderText("Override with custom style")
        style_row.addWidget(self.custom_style_input)
        style_layout.addLayout(style_row)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Image Controls Group
        controls_group = QGroupBox("Image Controls")
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Number of Images:"))
        self.num_images_spin = QSpinBox()
        self.num_images_spin.setRange(1, 4)
        self.num_images_spin.setValue(1)
        controls_layout.addWidget(self.num_images_spin)
        
        controls_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Images")
        self.generate_btn.clicked.connect(self.generate_images)
        controls_layout.addWidget(self.generate_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Image Preview
        preview_group = QGroupBox("Image Preview")
        preview_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(700, 700)
        self.image_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        self.image_label.setText("No image loaded")
        preview_layout.addWidget(self.image_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◄ Previous")
        self.prev_btn.clicked.connect(self.show_previous_image)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)
        
        self.image_counter_label = QLabel("0 / 0")
        self.image_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.image_counter_label)
        
        self.next_btn = QPushButton("Next ►")
        self.next_btn.clicked.connect(self.show_next_image)
        self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)
        preview_layout.addLayout(nav_layout)
        
        # Save and Exit buttons
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Image (JPG)")
        self.save_btn.clicked.connect(self.save_current_image)
        self.save_btn.setEnabled(False)
        action_layout.addWidget(self.save_btn)
        
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)
        action_layout.addWidget(self.exit_btn)
        preview_layout.addLayout(action_layout)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(80)
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText("Status and error messages will appear here...")
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_text)
        
        # Initialize Ollama models
        self.refresh_ollama_models()
    
    def populate_styles(self):
        """Populate the style combo box with categorized styles"""
        self.style_combo.addItem("Custom", "custom")
        
        for category, styles in STYLE_CATEGORIES.items():
            self.style_combo.addItem(f"--- {category} ---", None)
            for style in styles:
                self.style_combo.addItem(f"  {style}", style)
        
        # Set default to Photorealistic
        index = self.style_combo.findText("  Photorealistic")
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
    
    def load_environment_vars(self):
        """Load cookie values from environment variables"""
        u_cookie = os.getenv("BING_IMG_U", "")
        srchhpgusr = os.getenv("BING_IMG_SRCHHPGUSR", "")
        
        self.u_cookie_input.setText(u_cookie)
        self.srchhpgusr_input.setText(srchhpgusr)
        
        if u_cookie and srchhpgusr:
            self.log_status("Loaded cookies from environment variables")
        else:
            self.log_status("No environment variables found. Please enter cookies manually.")
    
    def validate_cookies(self):
        """Validate the provided cookies"""
        u_cookie = self.u_cookie_input.text().strip()
        srchhpgusr = self.srchhpgusr_input.text().strip()
        
        if not u_cookie or not srchhpgusr:
            self.log_error("Both U_COOKIE and SRCHHPGUSR are required")
            return
        
        try:
            # Test by creating an ImageGenerator instance
            self.generator = ImageGenerator(
                auth_cookie_u=u_cookie,
                auth_cookie_srchhpgusr=srchhpgusr
            )
            self.log_status("✓ Cookies validated successfully!")
        except Exception as e:
            self.log_error(f"Cookie validation failed: {str(e)}")
            self.generator = None
    
    def update_environment_vars(self):
        """Update environment variables with current cookie values"""
        u_cookie = self.u_cookie_input.text().strip()
        srchhpgusr = self.srchhpgusr_input.text().strip()
        
        if not u_cookie or not srchhpgusr:
            self.log_error("Both U_COOKIE and SRCHHPGUSR are required")
            return
        
        os.environ["BING_IMG_U"] = u_cookie
        os.environ["BING_IMG_SRCHHPGUSR"] = srchhpgusr
        
        self.log_status("Environment variables updated for this session")
    
    def refresh_ollama_models(self):
        """Refresh the list of available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                current_text = self.ollama_combo.currentText()
                
                self.ollama_combo.clear()
                self.ollama_combo.addItem("None (Direct prompt)")
                
                for model in models:
                    self.ollama_combo.addItem(model["name"])
                
                # Restore selection if possible
                index = self.ollama_combo.findText(current_text)
                if index >= 0:
                    self.ollama_combo.setCurrentIndex(index)
                
                self.log_status(f"Found {len(models)} Ollama model(s)")
            else:
                self.log_error("Failed to fetch Ollama models")
        except requests.exceptions.RequestException:
            self.log_status("Ollama not available (optional feature)")
    
    def generate_prompt_with_ollama(self, phrase, style):
        """Generate an enhanced prompt using Ollama"""
        model = self.ollama_combo.currentText()
        
        if model == "None (Direct prompt)":
            return f"{phrase}, {style}"
        
        try:
            prompt = f"Create a detailed image generation prompt for: '{phrase}' in {style} style. Only respond with the prompt, no explanations."
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                self.log_status(f"Generated prompt with {model}")
                return result
            else:
                self.log_error("Ollama generation failed, using direct prompt")
                return f"{phrase}, {style}"
        except Exception as e:
            self.log_error(f"Ollama error: {str(e)}, using direct prompt")
            return f"{phrase}, {style}"
    
    def generate_images(self):
        """Generate images using Bing Image Creator"""
        phrase = self.phrase_input.text().strip()
        if not phrase:
            self.log_error("Please enter a word or phrase")
            return
        
        u_cookie = self.u_cookie_input.text().strip()
        srchhpgusr = self.srchhpgusr_input.text().strip()
        
        if not u_cookie or not srchhpgusr:
            self.log_error("Please provide valid cookies")
            return
        
        # Get style
        custom_style = self.custom_style_input.text().strip()
        if custom_style:
            style = custom_style
        else:
            style_data = self.style_combo.currentData()
            if style_data is None or style_data == "custom":
                style = "photorealistic"
            else:
                style = style_data
        
        # Generate prompt
        prompt = self.generate_prompt_with_ollama(phrase, style)
        self.generated_prompt_display.setText(prompt)
        self.log_status(f"Using prompt: {prompt}")
        
        # Create ImageGenerator instance if not already created
        try:
            if not self.generator:
                self.generator = ImageGenerator(
                    auth_cookie_u=u_cookie,
                    auth_cookie_srchhpgusr=srchhpgusr
                )
            
            num_images = self.num_images_spin.value()
            
            # Disable generate button
            self.generate_btn.setEnabled(False)
            
            # Start generation thread
            self.generation_thread = ImageGenerationThread(self.generator, prompt, num_images)
            self.generation_thread.finished.connect(self.on_generation_finished)
            self.generation_thread.error.connect(self.on_generation_error)
            self.generation_thread.status.connect(self.log_status)
            self.generation_thread.start()
            
        except Exception as e:
            self.log_error(f"Failed to initialize: {str(e)}")
            self.generate_btn.setEnabled(True)
    
    def on_generation_finished(self, image_urls):
        """Handle successful image generation"""
        self.generate_btn.setEnabled(True)
        
        if not image_urls:
            self.log_error("No images were generated")
            return
        
        self.current_images = image_urls
        self.current_image_index = 0
        
        self.log_status(f"Successfully generated {len(image_urls)} image(s)")
        self.display_current_image()
        
        # Enable navigation
        self.update_navigation_buttons()
        self.save_btn.setEnabled(True)
    
    def on_generation_error(self, error_msg):
        """Handle generation errors"""
        self.generate_btn.setEnabled(True)
        self.log_error(f"Generation failed: {error_msg}")
    
    def display_current_image(self):
        """Display the current image in the preview"""
        if not self.current_images:
            return
        
        try:
            url = self.current_images[self.current_image_index]
            response = requests.get(url, timeout=10)
            
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            # Scale to fit label
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            self.image_counter_label.setText(
                f"{self.current_image_index + 1} / {len(self.current_images)}"
            )
        except Exception as e:
            self.log_error(f"Failed to load image: {str(e)}")
    
    def show_previous_image(self):
        """Show the previous image"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def show_next_image(self):
        """Show the next image"""
        if self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        self.prev_btn.setEnabled(self.current_image_index > 0)
        self.next_btn.setEnabled(
            self.current_image_index < len(self.current_images) - 1
        )
    
    def save_current_image(self):
        """Save the current image to disk"""
        if not self.current_images:
            return
        
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("Output")
            output_dir.mkdir(exist_ok=True)
            
            url = self.current_images[self.current_image_index]
            response = requests.get(url, timeout=10)
            
            phrase = self.phrase_input.text().strip().replace(" ", "_")
            filename = output_dir / f"{phrase}_{self.image_counter:04d}.jpg"
            
            with open(filename, "wb") as f:
                f.write(response.content)
            
            self.image_counter += 1
            self.log_status(f"✓ Saved: {filename}")
        except Exception as e:
            self.log_error(f"Failed to save image: {str(e)}")
    
    def log_status(self, message):
        """Log a status message"""
        self.status_text.append(f"[INFO] {message}")
    
    def log_error(self, message):
        """Log an error message"""
        self.status_text.append(f"[ERROR] {message}")


def main():
    app = QApplication(sys.argv)
    window = BingImageCreatorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()