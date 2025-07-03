# Technical Specification: Korean File Name Normalizer

## 1. System Architecture

### 1.1 Overview
The Korean File Name Normalizer is a client-side web application built with vanilla JavaScript, HTML5, and CSS3. The architecture follows a simple three-tier model with all processing occurring in the browser.

### 1.2 Architecture Diagram
```
┌─────────────────┐
│   Web Browser   │
├─────────────────┤
│  Presentation   │ ← HTML/CSS
├─────────────────┤
│ Business Logic  │ ← JavaScript
├─────────────────┤
│  Data Layer     │ ← File/Blob API
└─────────────────┘
        ↓
   Local Files
```

### 1.3 Component Structure
```
korean-normalizer/
├── index.html          # Main application entry point
├── css/
│   └── style.css      # Application styling
├── js/
│   ├── app.js         # Main application logic
│   ├── normalizer.js  # NFD→NFC conversion module
│   ├── fileHandler.js # File upload/download handling
│   └── ui.js          # UI update functions
└── assets/
    └── icons/         # UI icons (if needed)
```

## 2. Data Models

### 2.1 File Object Model
```javascript
class NormalizedFile {
  originalFile: File;          // Original HTML5 File object
  originalName: string;        // Original file name (NFD)
  normalizedName: string;      // Normalized file name (NFC)
  size: number;               // File size in bytes
  type: string;               // MIME type
  lastModified: number;       // Timestamp
  status: 'pending' | 'processing' | 'completed' | 'error';
  error?: string;             // Error message if failed
}
```

### 2.2 Application State Model
```javascript
class AppState {
  files: NormalizedFile[];     // Array of files being processed
  isProcessing: boolean;       // Batch processing status
  totalFiles: number;          // Total files in current batch
  processedFiles: number;      // Files completed
  settings: {
    language: 'ko' | 'en' | 'both';
    autoDownload: boolean;
  };
}
```

## 3. API Specifications

### 3.1 Core Normalization API
```javascript
/**
 * Normalize a file name from NFD to NFC
 * @param {string} fileName - Original file name
 * @returns {string} - Normalized file name
 */
function normalizeFileName(fileName) {
  return fileName.normalize('NFC');
}

/**
 * Check if a string needs normalization
 * @param {string} str - String to check
 * @returns {boolean} - True if NFD characters detected
 */
function needsNormalization(str) {
  return str !== str.normalize('NFC');
}
```

### 3.2 File Processing API
```javascript
/**
 * Process a single file
 * @param {File} file - HTML5 File object
 * @returns {Promise<NormalizedFile>} - Processed file object
 */
async function processFile(file) {
  const normalizedName = normalizeFileName(file.name);
  const newFile = new File([file], normalizedName, {
    type: file.type,
    lastModified: file.lastModified
  });
  
  return {
    originalFile: file,
    originalName: file.name,
    normalizedName: normalizedName,
    size: file.size,
    type: file.type,
    lastModified: file.lastModified,
    status: 'completed'
  };
}

/**
 * Process multiple files
 * @param {FileList|File[]} files - Files to process
 * @param {Function} onProgress - Progress callback
 * @returns {Promise<NormalizedFile[]>} - Processed files
 */
async function processBatch(files, onProgress) {
  const results = [];
  for (let i = 0; i < files.length; i++) {
    const result = await processFile(files[i]);
    results.push(result);
    onProgress(i + 1, files.length);
  }
  return results;
}
```

### 3.3 Download API
```javascript
/**
 * Download a single file
 * @param {File} file - File to download
 * @param {string} fileName - Name for download
 */
function downloadFile(file, fileName) {
  const url = URL.createObjectURL(file);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Create and download ZIP file
 * @param {NormalizedFile[]} files - Files to zip
 * @returns {Promise<void>}
 */
async function downloadAsZip(files, folderName) {
  // Implementation using JSZip
  const zip = new JSZip();
  
  // For folder uploads, preserve directory structure
  files.forEach(file => {
    const pathToUse = file.normalizedPath || file.normalizedName;
    zip.file(pathToUse, file.originalFile);
  });
  
  const blob = await zip.generateAsync({ 
    type: 'blob',
    compression: 'DEFLATE',
    compressionOptions: { level: 6 }
  });
  
  // Use folder name for ZIP file if available
  const zipName = folderName ? `${folderName}.zip` : 'normalized_files.zip';
  downloadFile(blob, zipName);
}
```

## 4. Implementation Details

### 4.1 HTML Structure
```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Korean File Name Normalizer | 한글 파일명 정규화</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div class="container">
    <header>
      <h1>한글 파일명 정규화 <span>Korean File Name Normalizer</span></h1>
    </header>
    
    <main>
      <div class="upload-area" id="uploadArea">
        <input type="file" id="fileInput" multiple hidden>
        <p>파일을 여기에 드래그하거나 클릭하세요</p>
        <p>Drag files here or click to select</p>
      </div>
      
      <div class="file-list" id="fileList"></div>
      
      <div class="actions">
        <button id="selectFolder">폴더 선택 | Select Folder</button>
        <button id="downloadAll">모두 다운로드 | Download All</button>
        <button id="clear">초기화 | Clear</button>
      </div>
    </main>
  </div>
  
  <script src="js/app.js" type="module"></script>
</body>
</html>
```

### 4.2 CSS Design System
```css
:root {
  /* Colors */
  --primary-color: #1976d2;
  --secondary-color: #f50057;
  --success-color: #4caf50;
  --error-color: #f44336;
  --warning-color: #ff9800;
  
  /* Typography */
  --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-base: 16px;
  
  /* Spacing */
  --spacing-unit: 8px;
  
  /* Borders */
  --border-radius: 4px;
}

/* Mobile-first responsive design */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-unit);
}

@media (min-width: 768px) {
  .container {
    padding: calc(var(--spacing-unit) * 2);
  }
}
```

### 4.3 JavaScript Module Structure

#### app.js - Main Application
```javascript
import { Normalizer } from './normalizer.js';
import { FileHandler } from './fileHandler.js';
import { UI } from './ui.js';

class App {
  constructor() {
    this.normalizer = new Normalizer();
    this.fileHandler = new FileHandler();
    this.ui = new UI();
    this.state = {
      files: [],
      isProcessing: false
    };
  }
  
  init() {
    this.setupEventListeners();
    this.checkBrowserSupport();
  }
  
  setupEventListeners() {
    // Drag and drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', this.handleDragOver);
    uploadArea.addEventListener('drop', this.handleDrop);
    uploadArea.addEventListener('click', this.handleClick);
    
    // File input
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', this.handleFileSelect);
  }
  
  async handleFiles(files) {
    this.state.isProcessing = true;
    this.ui.showProgress();
    
    try {
      const processed = await this.fileHandler.processBatch(
        files,
        (current, total) => this.ui.updateProgress(current, total)
      );
      
      this.state.files = processed;
      this.ui.displayFiles(processed);
    } catch (error) {
      this.ui.showError(error.message);
    } finally {
      this.state.isProcessing = false;
      this.ui.hideProgress();
    }
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
```

#### Folder Upload Support
```javascript
// Handle folder selection
function handleFolderSelect(e) {
  const files = e.target.files;
  if (files.length > 0) {
    const folderPath = files[0].webkitRelativePath.split('/')[0];
    currentFolderName = folderPath;
    isProcessingFolder = true;
    
    // Process all files in folder
    const filesArray = Array.from(files);
    processFiles(filesArray);
  }
}

// Folder button with webkitdirectory
<input type="file" id="folderInput" webkitdirectory multiple hidden>
```

#### normalizer.js - Normalization Logic
```javascript
export class Normalizer {
  /**
   * Normalize file name from NFD to NFC
   */
  normalize(fileName) {
    if (!fileName || typeof fileName !== 'string') {
      throw new Error('Invalid file name');
    }
    return fileName.normalize('NFC');
  }
  
  /**
   * Check if string contains NFD characters
   */
  isNFD(str) {
    return str !== str.normalize('NFC');
  }
  
  /**
   * Get character breakdown for debugging
   */
  getCharacterInfo(str) {
    return Array.from(str).map(char => ({
      char: char,
      codePoint: char.codePointAt(0),
      hex: char.codePointAt(0).toString(16).toUpperCase(),
      isNFD: this.isNFD(char)
    }));
  }
}
```

## 5. Testing Strategy

### 5.1 Unit Tests
```javascript
// Test cases for normalizer
describe('Normalizer', () => {
  test('should normalize Korean NFD to NFC', () => {
    const nfd = '한글';  // NFD form
    const nfc = normalizer.normalize(nfd);
    expect(nfc).toBe('한글');  // NFC form
  });
  
  test('should preserve non-Korean characters', () => {
    const input = 'test123!@#';
    expect(normalizer.normalize(input)).toBe(input);
  });
  
  test('should handle mixed content', () => {
    const input = '한글test파일.txt';
    const expected = '한글test파일.txt';
    expect(normalizer.normalize(input)).toBe(expected);
  });
});
```

### 5.2 Browser Compatibility Tests
- Chrome 90+: File API, normalize()
- Firefox 88+: File API, normalize()
- Safari 14+: File API, normalize()
- Edge 90+: File API, normalize()

### 5.3 Performance Benchmarks
- Single file: < 10ms
- 100 files: < 5 seconds
- 1000 files: < 30 seconds

## 6. Security Considerations

### 6.1 Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data:; 
               connect-src 'none';">
```

### 6.2 Input Validation
- Validate file types and sizes
- Sanitize file names for display
- Prevent XSS through file names
- No eval() or innerHTML usage

### 6.3 Privacy Protection
- No external requests
- No analytics or tracking
- No local storage of file data
- Clear memory after processing

## 7. Performance Optimization

### 7.1 Lazy Loading
- Load ZIP library only when needed
- Defer non-critical CSS

### 7.2 Memory Management
```javascript
// Clean up blob URLs
function cleanup(url) {
  URL.revokeObjectURL(url);
}

// Process large batches in chunks
async function processLargeBatch(files, chunkSize = 10) {
  for (let i = 0; i < files.length; i += chunkSize) {
    const chunk = Array.from(files).slice(i, i + chunkSize);
    await processChunk(chunk);
    
    // Allow browser to breathe
    await new Promise(resolve => setTimeout(resolve, 0));
  }
}
```

### 7.3 Web Workers (Future Enhancement)
```javascript
// worker.js
self.addEventListener('message', (e) => {
  const { files } = e.data;
  const results = files.map(file => ({
    ...file,
    normalizedName: file.name.normalize('NFC')
  }));
  self.postMessage(results);
});
```

## 8. Deployment Configuration

### 8.1 Build Process
```bash
# No build process required for vanilla JS
# Optional: Minification
npm run minify

# Deploy to GitHub Pages
git push origin main
```

### 8.2 Server Configuration
```nginx
# nginx.conf
location / {
  add_header X-Frame-Options "SAMEORIGIN";
  add_header X-Content-Type-Options "nosniff";
  add_header X-XSS-Protection "1; mode=block";
  add_header Referrer-Policy "no-referrer";
}
```

### 8.3 Monitoring
- Google Analytics (optional)
- Error tracking with Sentry (optional)
- Performance monitoring

## 9. Future Enhancements

### 9.1 Progressive Web App
- Service worker for offline use
- App manifest for installation
- Background sync for batch processing

### 9.2 Additional Features
- Folder upload support
- Cloud storage integration
- Command-line tool version
- Browser extension version
- Real-time collaboration