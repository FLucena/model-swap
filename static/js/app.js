document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const convertBtn = document.getElementById('convertBtn');
    const outputFormat = document.getElementById('outputFormat');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');
    const cleanupBtn = document.getElementById('cleanupBtn');
    const themeToggle = document.getElementById('themeToggle');
    const langBtns = document.querySelectorAll('.lang-btn');
    const faqItems = document.querySelectorAll('.faq-item');
    const prevFormatBtn = document.getElementById('prevFormat');
    const nextFormatBtn = document.getElementById('nextFormat');
    const formatDots = document.getElementById('formatDots');

    let selectedFiles = [];
    let fileMap = new Map(); // To prevent duplicates
    let currentLanguage = 'en';
    let currentTheme = localStorage.getItem('theme') || 'light';
    let currentFormatSlide = 0;
    let formatSlides = [];
    let carouselInterval;

    // Initialize theme and language
    initializeTheme();
    initializeLanguage();
    initializeFormatsCarousel();

    // Theme toggle functionality
    themeToggle.addEventListener('click', function() {
        toggleTheme();
    });

    // Language switch functionality
    langBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            switchLanguage(lang);
        });
    });

    // FAQ accordion functionality
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', function() {
            toggleFAQ(item);
        });
    });

    function toggleFAQ(clickedItem) {
        // Close all other FAQ items
        faqItems.forEach(item => {
            if (item !== clickedItem) {
                item.classList.remove('active');
            }
        });
        
        // Toggle the clicked item
        clickedItem.classList.toggle('active');
    }

    function initializeTheme() {
        document.documentElement.setAttribute('data-theme', currentTheme);
        updateThemeIcon();
    }

    function toggleTheme() {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
        updateThemeIcon();
    }

    function updateThemeIcon() {
        const themeIcon = themeToggle.querySelector('.theme-icon');
        if (currentTheme === 'dark') {
            themeIcon.textContent = '☀️';
        } else {
            themeIcon.textContent = '🌙';
        }
    }

    function initializeLanguage() {
        const savedLang = localStorage.getItem('language') || 'en';
        switchLanguage(savedLang);
    }

    function switchLanguage(lang) {
        currentLanguage = lang;
        localStorage.setItem('language', lang);
        
        // Update language buttons
        langBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-lang') === lang) {
                btn.classList.add('active');
            }
        });

        // Update all translatable elements
        updateTexts();
    }

    function updateTexts() {
        const translatableElements = document.querySelectorAll('[data-en][data-es]');
        translatableElements.forEach(element => {
            const text = element.getAttribute(`data-${currentLanguage}`);
            if (text) {
                element.textContent = text;
            }
        });

        // Update dynamic content
        if (selectedFiles.length > 0) {
            showFileList();
        }
    }

    // Global drag and drop functionality - works anywhere on the page
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        // Add visual feedback to the upload area when dragging anywhere
        uploadArea.classList.add('dragover');
    });

    document.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        // Only remove dragover class if we're leaving the document entirely
        if (e.relatedTarget === null) {
            uploadArea.classList.remove('dragover');
        }
    });

    document.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });

    // Prevent default drag behaviors on specific elements that shouldn't interfere
    document.addEventListener('dragenter', function(e) {
        e.preventDefault();
        e.stopPropagation();
    });

    // Upload area click functionality (still works for file browser)
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });

    function handleFiles(files) {
        const supportedFormats = ['obj', 'stl', 'ply', 'dae', 'gltf', 'glb', 'off'];
        let added = false;
        for (const file of files) {
            const extension = file.name.split('.').pop().toLowerCase();
            const key = file.name + '_' + file.size;
            if (supportedFormats.includes(extension) && !fileMap.has(key)) {
                if (selectedFiles.length >= 10) {
                    const message = currentLanguage === 'es'
                        ? 'Máximo 10 archivos permitidos. Por favor, elimina algunos archivos antes de agregar más.'
                        : 'Maximum 10 files allowed. Please remove some files before adding more.';
                    alert(message);
                    break;
                }
                selectedFiles.push(file);
                fileMap.set(key, file);
                added = true;
            }
        }
        if (added) {
            convertBtn.disabled = false;
            showFileList();
        } else if (selectedFiles.length === 0) {
            convertBtn.disabled = true;
            const message = currentLanguage === 'es'
                ? 'Por favor selecciona archivos de modelos 3D válidos (.obj, .stl, .ply, .dae, .gltf, .glb, .off)'
                : 'Please select valid 3D model files (.obj, .stl, .ply, .dae, .gltf, .glb, .off)';
            alert(message);
        }
    }

    function showFileList() {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        selectedFiles.forEach((file, idx) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <span class="file-name">${file.name}</span>
                <div class="file-progress"><div class="file-progress-bar" id="progressBar${idx}"></div></div>
                <span class="file-status" id="fileStatus${idx}"></span>
            `;
            fileList.appendChild(item);
        });
    }

    // Convert files
    convertBtn.addEventListener('click', function() {
        if (selectedFiles.length === 0) return;
        convertBtn.disabled = true;
        // For each file, upload individually with a delay to prevent overwhelming the server
        selectedFiles.forEach((file, idx) => {
            setTimeout(() => {
                uploadSingleFile(file, idx);
            }, idx * 500); // 500ms delay between each upload
        });
    });

    function uploadSingleFile(file, idx) {
        const progressBar = document.getElementById(`progressBar${idx}`);
        const statusSpan = document.getElementById(`fileStatus${idx}`);
        statusSpan.textContent = currentLanguage === 'es' ? 'Subiendo...' : 'Uploading...';
        const formData = new FormData();
        formData.append('files[]', file);
        formData.append('output_format', outputFormat.value);
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = (e.loaded / e.total) * 100;
                progressBar.style.width = percent + '%';
            }
        };
        xhr.onload = function() {
            progressBar.style.width = '100%';
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                if (data.success && data.converted_files.length > 0) {
                    statusSpan.textContent = currentLanguage === 'es' ? '¡Listo!' : 'Done!';
                    statusSpan.className = 'file-status success';
                    // Add download link
                    const link = document.createElement('a');
                    link.href = data.converted_files[0].download_url;
                    link.textContent = currentLanguage === 'es' ? 'Descargar' : 'Download';
                    link.className = 'download-btn';
                    link.style.marginLeft = '10px';
                    statusSpan.appendChild(link);
                } else if (data.errors && data.errors.length > 0) {
                    statusSpan.textContent = data.errors[0];
                    statusSpan.className = 'file-status error';
                } else {
                    statusSpan.textContent = currentLanguage === 'es' ? 'Error' : 'Error';
                    statusSpan.className = 'file-status error';
                }
            } else {
                statusSpan.textContent = currentLanguage === 'es' ? 'Error de red' : 'Network error';
                statusSpan.className = 'file-status error';
            }
        };
        xhr.onerror = function() {
            statusSpan.textContent = currentLanguage === 'es' ? 'Error de red' : 'Network error';
            statusSpan.className = 'file-status error';
        };
        xhr.send(formData);
    }

    function showResults(convertedFiles, errors) {
        // Hide the upload section
        const uploadSection = document.querySelector('.upload-section');
        uploadSection.style.display = 'none';
        
        // Show results in place of upload section
        resultsSection.style.display = 'block';
        resultsContent.innerHTML = '';

        // Add a header for the results
        const resultsHeader = document.createElement('div');
        resultsHeader.className = 'results-header';
        const headerText = currentLanguage === 'es' ? 'Resultados de Conversión' : 'Conversion Results';
        resultsHeader.innerHTML = `
            <h3>${headerText}</h3>
            <button class="back-btn" id="backToUpload">
                <span data-en="Convert More Files" data-es="Convertir Más Archivos">Convert More Files</span>
            </button>
        `;
        resultsSection.insertBefore(resultsHeader, resultsContent);

        // Show successful conversions
        convertedFiles.forEach(file => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            const convertedText = currentLanguage === 'es' 
                ? `Convertido a ${file.converted_name}`
                : `Converted to ${file.converted_name}`;
            const downloadText = currentLanguage === 'es' ? 'Descargar' : 'Download';
            
            resultItem.innerHTML = `
                <div class="result-info">
                    <div class="result-name">${file.original_name}</div>
                    <div class="result-status">${convertedText}</div>
                </div>
                <a href="${file.download_url}" class="download-btn" download>${downloadText}</a>
            `;
            resultsContent.appendChild(resultItem);
        });

        // Show errors
        errors.forEach(error => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item error';
            const errorText = currentLanguage === 'es' ? 'Error' : 'Error';
            
            resultItem.innerHTML = `
                <div class="result-info">
                    <div class="result-name">${errorText}</div>
                    <div class="result-status">${error}</div>
                </div>
            `;
            resultsContent.appendChild(resultItem);
        });

        // Add event listener for back button
        document.getElementById('backToUpload').addEventListener('click', function() {
            backToUpload();
        });

        // Update texts for the new elements
        updateTexts();
    }

    function showError(message) {
        // Hide the upload section
        const uploadSection = document.querySelector('.upload-section');
        uploadSection.style.display = 'none';
        
        // Show results in place of upload section
        resultsSection.style.display = 'block';
        const errorText = currentLanguage === 'es' ? 'Error' : 'Error';
        
        // Add a header for the results
        const resultsHeader = document.createElement('div');
        resultsHeader.className = 'results-header';
        const headerText = currentLanguage === 'es' ? 'Error de Conversión' : 'Conversion Error';
        resultsHeader.innerHTML = `
            <h3>${headerText}</h3>
            <button class="back-btn" id="backToUpload">
                <span data-en="Try Again" data-es="Intentar de Nuevo">Try Again</span>
            </button>
        `;
        resultsSection.insertBefore(resultsHeader, resultsContent);
        
        resultsContent.innerHTML = `
            <div class="result-item error">
                <div class="result-info">
                    <div class="result-name">${errorText}</div>
                    <div class="result-status">${message}</div>
                </div>
            </div>
        `;

        // Add event listener for back button
        document.getElementById('backToUpload').addEventListener('click', function() {
            backToUpload();
        });

        // Update texts for the new elements
        updateTexts();
    }

    function backToUpload() {
        // Show the upload section again
        const uploadSection = document.querySelector('.upload-section');
        uploadSection.style.display = 'block';
        
        // Hide results section
        resultsSection.style.display = 'none';
        
        // Clear the results content
        resultsContent.innerHTML = '';
        
        // Reset file selection
        selectedFiles = [];
        fileMap = new Map();
        convertBtn.disabled = true;
        const uploadTitle = uploadArea.querySelector('h3');
        const uploadSubtitle = uploadArea.querySelector('p');
        
        if (currentLanguage === 'es') {
            uploadTitle.textContent = 'Arrastra y Suelta Archivos Aquí';
            uploadSubtitle.textContent = 'o haz clic para explorar';
        } else {
            uploadTitle.textContent = 'Drag & Drop Files Here';
            uploadSubtitle.textContent = 'or click to browse';
        }
        fileInput.value = '';
        const fileList = document.getElementById('fileList');
        if (fileList) fileList.innerHTML = '';
    }

    // Cleanup functionality
    cleanupBtn.addEventListener('click', function() {
        fetch('/cleanup', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                backToUpload();
            }
            // No alerts or popups
        })
        .catch(error => {
            // No alerts or popups
        });
    });

    // Format selection change
    outputFormat.addEventListener('change', function() {
        console.log('Output format changed to:', this.value);
    });

    // Add some visual feedback for format items
    document.querySelectorAll('.format-item').forEach(item => {
        item.addEventListener('click', function() {
            const formatName = this.querySelector('.format-name').textContent.toLowerCase();
            const formatMap = {
                'obj': 'obj',
                'stl': 'stl',
                'ply': 'ply',
                'collada': 'dae',
                'gltf': 'gltf',
                'glb': 'glb',
                'off': 'off'
            };
            
            if (formatMap[formatName]) {
                outputFormat.value = formatMap[formatName];
                // Add visual feedback
                document.querySelectorAll('.format-item').forEach(fi => fi.style.opacity = '0.7');
                this.style.opacity = '1';
                setTimeout(() => {
                    document.querySelectorAll('.format-item').forEach(fi => fi.style.opacity = '1');
                }, 500);
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to convert
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (!convertBtn.disabled) {
                convertBtn.click();
            }
        }
        
        // Escape to clear selection
        if (e.key === 'Escape') {
            // If results are showing, go back to upload
            if (resultsSection.style.display === 'block') {
                backToUpload();
            } else {
                // Otherwise clear file selection
                selectedFiles = [];
                fileMap = new Map();
                convertBtn.disabled = true;
                const uploadTitle = uploadArea.querySelector('h3');
                const uploadSubtitle = uploadArea.querySelector('p');
                
                if (currentLanguage === 'es') {
                    uploadTitle.textContent = 'Arrastra y Suelta Archivos Aquí';
                    uploadSubtitle.textContent = 'o haz clic para explorar';
                } else {
                    uploadTitle.textContent = 'Drag & Drop Files Here';
                    uploadSubtitle.textContent = 'or click to browse';
                }
                fileInput.value = '';
            }
        }

        // T for theme toggle
        if (e.key === 't' || e.key === 'T') {
            toggleTheme();
        }

        // L for language toggle
        if (e.key === 'l' || e.key === 'L') {
            const newLang = currentLanguage === 'en' ? 'es' : 'en';
            switchLanguage(newLang);
        }

        // F for FAQ (opens first FAQ item)
        if (e.key === 'f' || e.key === 'F') {
            if (faqItems.length > 0) {
                faqItems[0].scrollIntoView({ behavior: 'smooth' });
                if (!faqItems[0].classList.contains('active')) {
                    toggleFAQ(faqItems[0]);
                }
            }
        }

        // Arrow keys for format carousel
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            if (currentFormatSlide > 0) {
                currentFormatSlide--;
                updateFormatSlide();
                resetCarouselAutoPlay();
            }
        }
        
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            if (currentFormatSlide < formatSlides.length - 1) {
                currentFormatSlide++;
                updateFormatSlide();
                resetCarouselAutoPlay();
            }
        }
    });

    // Add file size validation
    function validateFileSize(file) {
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (file.size > maxSize) {
            const message = currentLanguage === 'es' 
                ? `El archivo ${file.name} es demasiado grande. Tamaño máximo es 100MB.`
                : `File ${file.name} is too large. Maximum size is 100MB.`;
            alert(message);
            return false;
        }
        return true;
    }

    // Update handleFiles to include size validation
    const originalHandleFiles = handleFiles;
    handleFiles = function(files) {
        const validFiles = files.filter(file => validateFileSize(file));
        originalHandleFiles(validFiles);
    };

    function initializeFormatsCarousel() {
        formatSlides = document.querySelectorAll('.format-slide');
        createFormatDots();
        updateFormatSlide();
        startCarouselAutoPlay();
        
        // Add event listeners for carousel controls
        prevFormatBtn.addEventListener('click', () => {
            currentFormatSlide = (currentFormatSlide - 1 + formatSlides.length) % formatSlides.length;
            updateFormatSlide();
            resetCarouselAutoPlay();
        });
        
        nextFormatBtn.addEventListener('click', () => {
            currentFormatSlide = (currentFormatSlide + 1) % formatSlides.length;
            updateFormatSlide();
            resetCarouselAutoPlay();
        });
    }

    function createFormatDots() {
        formatDots.innerHTML = '';
        for (let i = 0; i < formatSlides.length; i++) {
            const dot = document.createElement('div');
            dot.className = 'carousel-dot';
            dot.addEventListener('click', () => {
                currentFormatSlide = i;
                updateFormatSlide();
                resetCarouselAutoPlay();
            });
            formatDots.appendChild(dot);
        }
    }

    function updateFormatSlide() {
        formatSlides.forEach((slide, index) => {
            slide.classList.remove('active');
            if (index === currentFormatSlide) {
                slide.classList.add('active');
            }
        });
        
        // Update dots
        const dots = formatDots.querySelectorAll('.carousel-dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentFormatSlide);
        });
        
        // Update navigation buttons
        prevFormatBtn.disabled = currentFormatSlide === 0;
        nextFormatBtn.disabled = currentFormatSlide === formatSlides.length - 1;
    }

    function startCarouselAutoPlay() {
        carouselInterval = setInterval(() => {
            currentFormatSlide = (currentFormatSlide + 1) % formatSlides.length;
            updateFormatSlide();
        }, 3000); // Change slide every 3 seconds
    }

    function resetCarouselAutoPlay() {
        clearInterval(carouselInterval);
        startCarouselAutoPlay();
    }
}); 