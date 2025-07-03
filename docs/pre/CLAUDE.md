# CLAUDE.md - AI Assistant Context Document

## Project Overview
**Project Name**: Korean File Name Normalizer  
**Purpose**: Web-based tool to convert Korean file names from NFD (Normalized Form Decomposed) to NFC (Normalized Form Composed) encoding  
**Problem Solved**: Fixes broken/garbled Korean file names when transferring files between macOS (NFD) and Windows/Linux (NFC)

## Tech Stack
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **File Processing**: HTML5 File API, Blob API
- **Normalization**: Native JavaScript `String.prototype.normalize('NFC')`
- **Build Tools**: None (static site)
- **Server Requirements**: Any static file server
- **Browser Support**: Modern browsers with File API support

## Coding Conventions
- **JavaScript Style**: ES6+ features, async/await for file operations
- **Naming**: camelCase for variables/functions, PascalCase for classes
- **File Organization**: Separate concerns (HTML structure, CSS styling, JS logic)
- **Error Handling**: User-friendly error messages in Korean and English
- **Comments**: Bilingual comments for critical logic
- **No Dependencies**: Keep it dependency-free for simplicity

## Project Structure
```
normalizer/
├── index.html          # Main application UI
├── style.css          # Responsive styling
├── script.js          # Core normalization logic
├── README.md          # User documentation (Korean/English)
├── overview.md        # Project overview
├── CLAUDE.md          # This file - AI context
├── What the Docs.md   # Documentation types reference
└── project-proposal.md # (Currently empty)
```

## Design Patterns
- **Module Pattern**: Encapsulate file processing logic
- **Observer Pattern**: Update UI based on file processing events
- **Factory Pattern**: Create normalized file objects
- **Singleton**: Single file processor instance

## Current Work Status
- [x] Project structure created
- [x] Documentation files initialized
- [x] HTML interface implementation
- [x] CSS styling
- [x] JavaScript normalization logic
- [x] File upload/download functionality
- [x] Batch processing support
- [x] Folder upload support with webkitdirectory
- [x] ZIP download for folders with JSZip
- [x] Error handling
- [x] Bilingual UI implementation
- [ ] Cross-browser testing

## Known Issues & Considerations
1. **File Size Limits**: Browser memory constraints for large files
2. **Character Edge Cases**: Some complex Korean characters may need special handling
3. **Browser Compatibility**: File API not supported in older browsers
4. **Performance**: Large batch operations may freeze UI (consider Web Workers)
5. **Security**: Ensure no file content is logged or sent externally

## Implementation Priorities
1. **Core Functionality**: Single file NFD→NFC conversion
2. **User Interface**: Clean, intuitive drag-and-drop interface
3. **Batch Processing**: Multiple file handling
4. **Error Handling**: Clear error messages for edge cases
5. **Accessibility**: Bilingual support (Korean/English)
6. **Testing**: Cross-browser and various file name patterns

## Testing Checklist
- [ ] Korean-only file names (한글.txt)
- [ ] Mixed Korean-English (한글file.txt)
- [ ] Special characters (한글!@#$.txt)
- [ ] Long file names
- [ ] Various file extensions
- [ ] Empty files
- [ ] Large files (>10MB)
- [ ] Batch operations (>50 files)

## Development Commands
```bash
# Serve locally with Python
python -m http.server 8000

# Serve with Node.js
npx serve

# Open in browser
open http://localhost:8000
```

## Key Functions to Implement
```javascript
// Core normalization
normalizeFileName(fileName) // NFD → NFC conversion
processFile(file) // Handle single file
processBatch(files) // Handle multiple files
downloadFile(file, newName) // Download with new name
createZip(files) // Batch download as ZIP
updateUI(status) // Update progress/status
handleError(error) // User-friendly error display

// Folder support
handleFolderSelect(e) // Process folder selection
processFolder(files) // Handle folder with structure
downloadAsZip(files, folderName) // ZIP with folder name
```

## Future Enhancements
- Progressive Web App (PWA) for offline use
- Folder structure preservation
- Reverse operation (NFC → NFD)
- File name pattern detection and suggestions
- Integration with cloud storage services
- Command-line version using Node.js