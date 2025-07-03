// File processing state
let processedFiles = [];

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const folderInput = document.getElementById('folderInput');
const fileList = document.getElementById('fileList');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const actions = document.getElementById('actions');
const selectFolderBtn = document.getElementById('selectFolder');
const downloadAllBtn = document.getElementById('downloadAll');
const clearAllBtn = document.getElementById('clearAll');
const docModal = document.getElementById('docModal');
const docContent = document.getElementById('docContent');
const modalClose = document.querySelector('.modal-close');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    // File upload events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    folderInput.addEventListener('change', handleFolderSelect);
    
    // Button events
    selectFolderBtn.addEventListener('click', () => folderInput.click());
    downloadAllBtn.addEventListener('click', downloadAll);
    clearAllBtn.addEventListener('click', clearAll);
    
    // Tab events
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });
    
    // Document link events
    document.querySelectorAll('.doc-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            loadDocument(link.dataset.doc);
        });
    });
    
    // Modal events
    modalClose.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === docModal) closeModal();
    });
});

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    processFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    processFiles(files);
}

function handleFolderSelect(e) {
    const files = e.target.files;
    // Show folder structure info
    if (files.length > 0) {
        console.log(`Selected folder with ${files.length} files`);
        // Extract folder path from first file
        const folderPath = files[0].webkitRelativePath.split('/')[0];
        progressText.textContent = `Processing folder: ${folderPath}`;
    }
    processFiles(files);
}

// Main file processing function
async function processFiles(files) {
    if (files.length === 0) return;
    
    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = `Processing 0 / ${files.length} files...`;
    
    processedFiles = [];
    fileList.innerHTML = '';
    
    // Process each file
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const normalizedName = normalizeFileName(file.name);
        
        // Handle folder path if present
        let normalizedPath = file.name;
        if (file.webkitRelativePath) {
            const pathParts = file.webkitRelativePath.split('/');
            const normalizedParts = pathParts.map(part => normalizeFileName(part));
            normalizedPath = normalizedParts.join('/');
        }
        
        // Create processed file object
        const processedFile = {
            originalFile: file,
            originalName: file.name,
            normalizedName: normalizedName,
            originalPath: file.webkitRelativePath || file.name,
            normalizedPath: normalizedPath,
            needsNormalization: file.name !== normalizedName || (file.webkitRelativePath && file.webkitRelativePath !== normalizedPath),
            size: file.size
        };
        
        processedFiles.push(processedFile);
        displayFile(processedFile);
        
        // Update progress
        const progress = ((i + 1) / files.length) * 100;
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `Processing ${i + 1} / ${files.length} files...`;
        
        // Allow UI to update
        await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    // Hide progress and show action buttons
    progressContainer.style.display = 'none';
    if (processedFiles.length > 0) {
        downloadAllBtn.style.display = 'inline-flex';
        clearAllBtn.style.display = 'inline-flex';
    }
}

// NFD to NFC normalization
function normalizeFileName(fileName) {
    // Normalize the entire filename from NFD to NFC
    return fileName.normalize('NFC');
}

// Display a processed file
function displayFile(fileData) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    
    const statusIcon = fileData.needsNormalization ? '✅' : '➖';
    const statusText = fileData.needsNormalization ? 'Normalized' : 'No change needed';
    
    // Show full path if it's from a folder
    const originalDisplay = fileData.originalPath || fileData.originalName;
    const normalizedDisplay = fileData.normalizedPath || fileData.normalizedName;
    
    fileItem.innerHTML = `
        <div class="file-item-header">
            <div class="file-info">
                <div class="file-name original">
                    <strong>Original:</strong> ${escapeHtml(originalDisplay)}
                </div>
                <div class="file-name normalized">
                    <strong>Normalized:</strong> ${escapeHtml(normalizedDisplay)}
                </div>
                <div class="file-size">
                    ${formatFileSize(fileData.size)} · ${statusIcon} ${statusText}
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-primary btn-small" onclick="downloadFile(${processedFiles.length - 1})">
                    Download
                </button>
            </div>
        </div>
    `;
    
    fileList.appendChild(fileItem);
}

// Download individual file
function downloadFile(index) {
    const fileData = processedFiles[index];
    const file = fileData.originalFile;
    
    // Create a new File object with the normalized name
    const normalizedFile = new File([file], fileData.normalizedName, {
        type: file.type,
        lastModified: file.lastModified
    });
    
    // Create download link
    const url = URL.createObjectURL(normalizedFile);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileData.normalizedName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Download all files as ZIP
async function downloadAll() {
    // For simplicity, download files individually
    // In production, you'd use a library like JSZip
    for (let i = 0; i < processedFiles.length; i++) {
        downloadFile(i);
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}

// Clear all files
function clearAll() {
    processedFiles = [];
    fileList.innerHTML = '';
    downloadAllBtn.style.display = 'none';
    clearAllBtn.style.display = 'none';
    fileInput.value = '';
    folderInput.value = '';
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tabName);
    });
    
    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === tabName);
    });
}

// Load documentation
async function loadDocument(docName) {
    try {
        const response = await fetch(`docs/pre/${docName}.md`);
        if (!response.ok) throw new Error('Document not found');
        
        const markdown = await response.text();
        const html = marked.parse(markdown);
        
        docContent.innerHTML = html;
        docModal.style.display = 'block';
    } catch (error) {
        docContent.innerHTML = '<p>Error loading document.</p>';
        docModal.style.display = 'block';
    }
}

// Close modal
function closeModal() {
    docModal.style.display = 'none';
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Check for browser support
if (!String.prototype.normalize) {
    alert('Your browser does not support Unicode normalization. Please use a modern browser.');
}

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {
            // Service worker registration failed, app will still work
        });
    });
}