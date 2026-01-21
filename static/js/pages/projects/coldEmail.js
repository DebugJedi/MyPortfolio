/* ==========================================
   COLD EMAIL GENERATOR - FIXED JAVASCRIPT
   ========================================== */

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const resumeUpload = document.getElementById('resume-upload');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');
const jobUrlInput = document.getElementById('job-url');
const submitBtn = document.getElementById('submit-button');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const emailContent = document.getElementById('email-content');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const generateAnotherBtn = document.getElementById('generate-another');

let uploadedFile = null;

// ==========================================
// FILE UPLOAD FUNCTIONALITY - FIXED
// ==========================================

// Click anywhere in upload area to trigger file input
uploadArea.addEventListener('click', (e) => {
    // Don't trigger if clicking the remove button
    if (e.target.closest('.remove-file')) {
        return;
    }
    resumeUpload.click();
});

// File selection via input
resumeUpload.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        handleFileUpload(e.target.files[0]);
    }
});

// Drag and drop events
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
});

// Handle file upload
function handleFileUpload(file) {
    if (!file) {
        console.log('No file provided');
        return;
    }
    
    console.log('File selected:', file.name, 'Type:', file.type);
    
    // Check if it's a PDF
    if (file.type !== 'application/pdf') {
        alert('❌ Please upload a PDF file only');
        return;
    }
    
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('❌ File size must be less than 10MB');
        return;
    }
    
    uploadedFile = file;
    
    // Update UI
    const uploadContent = document.querySelector('.upload-content');
    if (uploadContent) {
        uploadContent.style.display = 'none';
    }
    
    if (fileInfo) {
        fileInfo.style.display = 'flex';
        fileName.textContent = file.name;
    }
    
    console.log('✅ File uploaded successfully');
}

// Remove file
if (removeFileBtn) {
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering upload area click
        removeFile();
    });
}

function removeFile() {
    uploadedFile = null;
    resumeUpload.value = '';
    
    const uploadContent = document.querySelector('.upload-content');
    if (uploadContent) {
        uploadContent.style.display = 'flex';
    }
    
    if (fileInfo) {
        fileInfo.style.display = 'none';
    }
    
    console.log('File removed');
}

// ==========================================
// FORM SUBMISSION
// ==========================================

submitBtn.addEventListener('click', async () => {
    console.log('Submit button clicked');
    
    // Validation
    if (!uploadedFile) {
        alert('❌ Please upload your resume first');
        return;
    }
    
    const jobUrl = jobUrlInput.value.trim();
    if (!jobUrl) {
        alert('❌ Please enter a job posting URL');
        return;
    }
    
    // Validate URL format
    try {
        new URL(jobUrl);
    } catch {
        alert('❌ Please enter a valid URL (must start with http:// or https://)');
        return;
    }
    
    console.log('Form validation passed');
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Generating...</span>';
    loading.style.display = 'block';
    result.style.display = 'none';
    
    // Prepare form data
    const formData = new FormData();
    formData.append('resume', uploadedFile);
    formData.append('job_url', jobUrl);
    
    try {
        console.log('Sending request to backend...');
        
        // Submit to backend
        const response = await fetch('/api/generate-email', {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // Display result
        const generatedEmail = data.email || data.generated_email || data.content || 'Email generated successfully!';
        emailContent.textContent = generatedEmail;
        
        // Hide loading, show result
        loading.style.display = 'none';
        result.style.display = 'block';
        
        // Scroll to result
        setTimeout(() => {
            result.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
        console.log('✅ Email generated successfully');
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to generate email. Please try again.\n\nError: ' + error.message);
        loading.style.display = 'none';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-magic"></i> <span>Generate Cold Email</span>';
    }
});

// ==========================================
// RESULT ACTIONS
// ==========================================

// Copy to clipboard
if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
        const text = emailContent.textContent;
        
        try {
            await navigator.clipboard.writeText(text);
            
            // Visual feedback
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> <span>Copied!</span>';
            copyBtn.style.background = 'rgba(16, 185, 129, 0.2)';
            copyBtn.style.borderColor = 'var(--color-green)';
            copyBtn.style.color = 'var(--color-green)';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                copyBtn.style.background = '';
                copyBtn.style.borderColor = '';
                copyBtn.style.color = '';
            }, 2000);
            
            console.log('✅ Copied to clipboard');
        } catch (error) {
            console.error('Copy failed:', error);
            
            // Fallback: select text
            const range = document.createRange();
            range.selectNode(emailContent);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            
            alert('Text selected! Press Ctrl+C (or Cmd+C) to copy.');
        }
    });
}

// Download as text file
if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
        const text = emailContent.textContent;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cold-email-' + Date.now() + '.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✅ Email downloaded');
    });
}

// Generate another email
if (generateAnotherBtn) {
    generateAnotherBtn.addEventListener('click', () => {
        // Reset form
        removeFile();
        jobUrlInput.value = '';
        
        // Hide result
        result.style.display = 'none';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        console.log('Form reset');
    });
}

// ==========================================
// KEYBOARD SHORTCUTS
// ==========================================

document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + Enter to submit
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        if (!submitBtn.disabled && uploadedFile && jobUrlInput.value.trim()) {
            submitBtn.click();
        }
    }
    
    // Escape to reset
    if (e.key === 'Escape' && result.style.display === 'block') {
        generateAnotherBtn.click();
    }
});

// ==========================================
// SMOOTH ANIMATIONS ON LOAD
// ==========================================

window.addEventListener('load', () => {
    console.log('Page loaded');
    
    // Fade in sections
    const sections = document.querySelectorAll('.input-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'all 0.6s ease-out';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// ==========================================
// DEBUG INFO
// ==========================================

console.log('✅ Cold Email Generator JavaScript loaded');
console.log('Upload area:', uploadArea ? 'Found' : 'NOT FOUND');
console.log('File input:', resumeUpload ? 'Found' : 'NOT FOUND');
console.log('Submit button:', submitBtn ? 'Found' : 'NOT FOUND');