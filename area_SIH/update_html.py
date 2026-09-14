import sys

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Header
header_old = '''        <header class="header glass-panel">
            <div class="logo">
                <div class="logo-icon"></div>
                <h1>Agentic RS <span>Area Measurement</span></h1>
            </div>
            <div class="reference-badge">Ref: BigEarthNet.txt (arXiv:2603.29630)</div>
        </header>'''

header_new = '''        <header class="header glass-panel">
            <div class="logo">
                <div class="logo-icon"></div>
                <h1>Agentic RS <span>Analysis Suite</span></h1>
            </div>
            <div class="nav-tabs" style="display: flex; gap: 10px; margin-left: auto; margin-right: 20px;">
                <button class="btn primary-btn" id="tab-area" onclick="switchTab('area')">Area Measurement</button>
                <button class="btn secondary-btn" id="tab-grounding" onclick="switchTab('grounding')">Object Grounding</button>
            </div>
            <div class="reference-badge">Ref: BigEarthNet.txt (arXiv:2603.29630)</div>
        </header>'''

content = content.replace(header_old, header_new)

# 2. Wrap area measurement content
content = content.replace('<main class="main-content">', '<main class="main-content">\n            <!-- Area View -->\n            <div id="area-view">')

# 3. Add grounding view before scripts
grounding_html = '''
            </div> <!-- End Area View -->
            
            <!-- Grounding View -->
            <div id="grounding-view" style="display: none;">
                <section id="upload-section-grounding" class="upload-section glass-panel">
                    <div class="upload-header">
                        <h2>Upload & Detect Objects</h2>
                        <p>Upload a satellite image and type what you want to find using natural language.</p>
                    </div>
                    
                    <form id="upload-form-grounding" class="upload-form">
                        <div class="file-drop-area" id="drop-area-grounding">
                            <span class="file-msg-grounding">Drag & drop image here or click to browse</span>
                            <input class="file-input" type="file" id="image-input-grounding" name="image" accept=".jpg,.jpeg,.png,.tif,.tiff,.bmp,.webp" required>
                        </div>

                        <div class="options-area" style="display: flex; flex-direction: column; gap: 15px; margin-top: 20px;">
                            <div style="display: flex; flex-direction: column; text-align: left;">
                                <label for="query" style="font-weight: 500; margin-bottom: 5px;">What do you want to find?</label>
                                <input type="text" id="query" name="query" placeholder="e.g., 'Where are the buildings?'" required style="padding: 10px; border-radius: 5px; border: 1px solid #ccc; font-family: inherit;">
                            </div>
                            
                            <div style="display: flex; flex-direction: column; text-align: left;">
                                <label for="box_threshold" style="font-weight: 500; margin-bottom: 5px;">Confidence Threshold: <span id="threshold-val">0.3</span></label>
                                <input type="range" id="box_threshold" name="box_threshold" min="0.1" max="0.9" step="0.05" value="0.3">
                            </div>
                        </div>

                        <button type="submit" class="btn primary-btn" id="analyze-btn-grounding" disabled style="margin-top: 20px;">
                            <span>Detect / Ground</span>
                            <div class="loader-spinner-grounding" style="display: none;"></div>
                        </button>
                    </form>

                    <div id="error-message-grounding" class="error-message" style="display: none;"></div>
                </section>

                <!-- Grounding Loading State -->
                <section id="loading-section-grounding" class="loading-section glass-panel" style="display: none;">
                    <div class="loader-container">
                        <div class="radar-scanner"></div>
                        <h3>Detecting Objects...</h3>
                        <p>Running Zero-Shot Vision-Language Model</p>
                    </div>
                </section>

                <!-- Grounding Results Section -->
                <section id="results-section-grounding" class="results-section" style="display: none;">
                    <div class="results-header glass-panel">
                        <h2>Detection Results</h2>
                        <div class="action-buttons">
                            <button id="new-analysis-btn-grounding" class="btn secondary-btn">New Query</button>
                        </div>
                    </div>

                    <div class="image-comparison">
                        <div class="image-card glass-panel">
                            <div class="card-header">
                                <h3>Original Image</h3>
                            </div>
                            <div class="image-wrapper">
                                <img id="original-img-grounding" src="" alt="Original Image">
                            </div>
                        </div>
                        
                        <div class="image-card glass-panel annotated-card">
                            <div class="card-header">
                                <h3>Grounded/Annotated Image</h3>
                                <span id="model-badge-grounding" class="badge">Grounding DINO</span>
                            </div>
                            <div class="image-wrapper">
                                <img id="annotated-img-grounding" src="" alt="Annotated Image">
                            </div>
                        </div>
                    </div>

                    <!-- Detection Table -->
                    <div class="table-container glass-panel" style="margin-top: 20px;">
                        <div class="table-header">
                            <h3>Detected Objects</h3>
                        </div>
                        <div class="table-responsive">
                            <table class="data-table" id="results-table-grounding">
                                <thead>
                                    <tr>
                                        <th>Object Label</th>
                                        <th>Confidence</th>
                                        <th>Bounding Box (x1, y1, x2, y2)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Populated by JS -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>
            </div>
'''
content = content.replace('</main>', grounding_html + '\n        </main>')

# 4. Add JavaScript for grounding
script_insertion = '''
            function switchTab(tab) {
                if (tab === 'area') {
                    document.getElementById('area-view').style.display = 'block';
                    document.getElementById('grounding-view').style.display = 'none';
                    document.getElementById('tab-area').className = 'btn primary-btn';
                    document.getElementById('tab-grounding').className = 'btn secondary-btn';
                } else {
                    document.getElementById('area-view').style.display = 'none';
                    document.getElementById('grounding-view').style.display = 'block';
                    document.getElementById('tab-area').className = 'btn secondary-btn';
                    document.getElementById('tab-grounding').className = 'btn primary-btn';
                }
            }

            // GROUNDING LOGIC
            const uploadFormG = document.getElementById('upload-form-grounding');
            const fileInputG = document.getElementById('image-input-grounding');
            const fileMsgG = document.querySelector('.file-msg-grounding');
            const analyzeBtnG = document.getElementById('analyze-btn-grounding');
            const errorMsgG = document.getElementById('error-message-grounding');
            
            const uploadSectionG = document.getElementById('upload-section-grounding');
            const loadingSectionG = document.getElementById('loading-section-grounding');
            const resultsSectionG = document.getElementById('results-section-grounding');
            const newAnalysisBtnG = document.getElementById('new-analysis-btn-grounding');
            
            const threshInput = document.getElementById('box_threshold');
            const threshVal = document.getElementById('threshold-val');
            
            threshInput.addEventListener('input', (e) => {
                threshVal.textContent = parseFloat(e.target.value).toFixed(2);
            });

            fileInputG.addEventListener('change', () => {
                if (fileInputG.files.length > 0) {
                    fileMsgG.textContent = fileInputG.files[0].name;
                    analyzeBtnG.disabled = false;
                } else {
                    fileMsgG.textContent = 'Drag & drop image here or click to browse';
                    analyzeBtnG.disabled = true;
                }
            });

            newAnalysisBtnG.addEventListener('click', () => {
                resultsSectionG.style.display = 'none';
                uploadSectionG.style.display = 'block';
            });

            uploadFormG.addEventListener('submit', async (e) => {
                e.preventDefault();
                if (fileInputG.files.length === 0) return;

                const formData = new FormData(uploadFormG);
                
                uploadSectionG.style.display = 'none';
                errorMsgG.style.display = 'none';
                loadingSectionG.style.display = 'flex';

                try {
                    const response = await fetch('/ground', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok || !data.success) {
                        throw new Error(data.error || 'Grounding failed');
                    }

                    document.getElementById('original-img-grounding').src = `data:image/png;base64,${data.original_image}`;
                    document.getElementById('annotated-img-grounding').src = `data:image/png;base64,${data.annotated_image}`;
                    
                    const tbody = document.querySelector('#results-table-grounding tbody');
                    tbody.innerHTML = '';
                    
                    data.detections.forEach((det, idx) => {
                        const tr = document.createElement('tr');
                        const box = det.box;
                        tr.innerHTML = `
                            <td>${det.label.toUpperCase()} #${idx+1}</td>
                            <td>${det.score.toFixed(3)}</td>
                            <td>(${box.xmin}, ${box.ymin}, ${box.xmax}, ${box.ymax})</td>
                        `;
                        tbody.appendChild(tr);
                    });

                    loadingSectionG.style.display = 'none';
                    resultsSectionG.style.display = 'block';
                    resultsSectionG.scrollIntoView({ behavior: 'smooth' });

                } catch (error) {
                    loadingSectionG.style.display = 'none';
                    uploadSectionG.style.display = 'block';
                    errorMsgG.textContent = error.message;
                    errorMsgG.style.display = 'block';
                }
            });
'''

content = content.replace('// New analysis button', script_insertion + '\n            // New analysis button')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated index.html successfully')
