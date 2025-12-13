# Bing Image Creator GUI

A PyQt6-based graphical user interface for generating images using Bing's Image Creator (DALL-E 3) with optional Ollama integration for enhanced prompt generation.

## Features

- 🎨 Generate 1-4 images per request
- 🎭 40+ pre-defined style templates (Photorealistic, Anime, Oil Painting, etc.)
- 🤖 Optional Ollama integration for AI-enhanced prompt generation
- 🖼️ Image preview with navigation
- 💾 Automatic image saving to organized output directory
- 🔐 Cookie management with environment variable support
- 📝 Real-time status and error messages

## Installation

### Prerequisites

- Python 3.8 or higher
- Microsoft Edge or Chrome browser (for cookie extraction)

### Install Required Packages

```bash
pip install PyQt6 bing-create requests
```

### Optional: Install Ollama (for AI-enhanced prompts)

Download and install Ollama from [ollama.ai](https://ollama.ai), then pull a model:

```bash
ollama pull llama2
```

## Getting Your Cookies

To use Bing Image Creator, you need two cookie values: `_U` and `SRCHHPGUSR`.

### Step 1: Login to Bing Image Creator

Navigate to [https://www.bing.com/images/create](https://www.bing.com/images/create) and login with your Microsoft account.

### Step 2: Extract Cookies

Choose one of the following methods:

#### Option 1: Using Browser Developer Tools

1. Open your browser's developer tools by pressing **F12**
2. Navigate to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox)
3. Expand the **Cookies** section in the left sidebar
4. Click on `https://www.bing.com`
5. Find and copy the values for:
   - `_U` cookie
   - `SRCHHPGUSR` cookie

#### Option 2: Using Cookie Quick Manager (Firefox)

1. Go to [addons.mozilla.org/firefox/extensions/](https://addons.mozilla.org/firefox/extensions/)
2. Search for and install **Cookie Quick Manager**
3. Navigate back to [https://www.bing.com/images/create](https://www.bing.com/images/create)
4. Click the Cookie Quick Manager extension icon
5. Locate `_U` and `SRCHHPGUSR` cookies and copy their values

## Setting Up Environment Variables

### PowerShell (Windows)

#### Current Session Only (Temporary)

```powershell
$env:BING_IMG_U = "your_u_cookie_value_here"
$env:BING_IMG_SRCHHPGUSR = "your_srchhpgusr_value_here"
```

#### Permanent (Current User)

```powershell
[System.Environment]::SetEnvironmentVariable('BING_IMG_U', 'your_u_cookie_value_here', 'User')
[System.Environment]::SetEnvironmentVariable('BING_IMG_SRCHHPGUSR', 'your_srchhpgusr_value_here', 'User')
```

**Note:** After setting permanent variables, restart PowerShell or your application.

### Linux/Mac (Bash)

#### Current Session Only

```bash
export BING_IMG_U="your_u_cookie_value_here"
export BING_IMG_SRCHHPGUSR="your_srchhpgusr_value_here"
```

#### Permanent

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export BING_IMG_U="your_u_cookie_value_here"
export BING_IMG_SRCHHPGUSR="your_srchhpgusr_value_here"
```

Then reload: `source ~/.bashrc`

## Usage

### Starting the Application

```bash
python bing_img_creator_gui.py
```

### Workflow

1. **Cookie Configuration**
   - The app will automatically load cookies from environment variables if available
   - Otherwise, paste your cookie values into the text boxes
   - Click **Validate Cookies** to verify they work
   - Optionally click **Update Environment Variables** to save them for the current session

2. **Create Your Prompt**
   - Enter a word or phrase describing what you want to generate
   - (Optional) Select an Ollama model to enhance your prompt
   - Select a style from the dropdown or enter a custom style
   - The generated prompt will be displayed in the text box

3. **Generate Images**
   - Set the number of images (1-4)
   - Click **Generate Images**
   - Wait for the generation to complete (typically 30-60 seconds)

4. **Review and Save**
   - Use **Previous/Next** buttons to navigate through generated images
   - Click **Save Image (JPG)** to save the current image
   - Images are saved to the `Output` subdirectory with automatic naming: `phrase_0001.jpg`

## Style Categories

The app includes 40+ pre-organized styles across 5 categories:

- **Photographic & Realistic**: Photorealistic, Cinematic, Film Noir, Portrait, etc.
- **Artistic & Painting**: Oil Painting, Watercolor, Sketches, Impressionism, etc.
- **Graphic & Stylized**: Illustration, Anime, Comic Book, Pixel Art, etc.
- **3D & Rendering**: 3D Rendering, Octane Render, Lowpoly, Isometric, etc.
- **Genre & Aesthetic**: Cyberpunk, Steampunk, Fantasy, Sci-Fi, Art Deco, etc.

## Troubleshooting

### "Cookie validation failed"

- Your cookies may have expired. Extract fresh cookies from your browser.
- Ensure you're logged into Bing Image Creator in your browser.
- Make sure you copied the complete cookie values without extra spaces.

### "Could not connect to Ollama"

- This is optional. If you don't have Ollama installed, select "None (Direct prompt)"
- If you want to use Ollama, ensure it's running: `ollama serve`

### "Generation failed"

- Check your internet connection
- Verify your cookies are still valid
- Try a simpler prompt first to test
- Check if Bing Image Creator is experiencing service issues

### CPU Random Generator Warning

The warning about CPU random generator is from the cryptography library and can be safely ignored. It doesn't affect functionality.

## Output

- Generated images are saved to the `Output` subdirectory
- Files are named: `[your_phrase]_0001.jpg`, `[your_phrase]_0002.jpg`, etc.
- Images are saved at full original resolution (typically 1024x1024)

## Tips for Best Results

1. **Be Specific**: Include details about composition, lighting, mood, and style
2. **Use Style Keywords**: Combine your phrase with style terms like "cinematic lighting", "highly detailed", "4k"
3. **Experiment**: Try different Ollama models for varied prompt enhancements
4. **Iterate**: Generate multiple images and refine your prompt based on results

## License

This project is provided as-is for educational and personal use.

## Credits

- Built with PyQt6
- Uses [bing-create](https://pypi.org/project/bing-create/) library
- Optional integration with [Ollama](https://ollama.ai)
- Powered by Bing Image Creator (DALL-E 3)

## Support

For issues or questions:
- Check that your cookies are valid and up-to-date
- Ensure all dependencies are installed correctly
- Verify Bing Image Creator service is operational