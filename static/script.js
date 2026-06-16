document.addEventListener('DOMContentLoaded', () => {
    // 1. Load data from the script tag
    let rawSymptoms = [];
    try {
        rawSymptoms = JSON.parse(document.getElementById('symptoms-data').textContent);
    } catch (e) {
        console.error('Failed to parse symptoms data:', e);
    }

    // DOM Elements
    const symptomDescription = document.getElementById('symptom-description');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');

    // Result State Panels
    const stateAwaiting = document.getElementById('result-state-awaiting');
    const stateLoading = document.getElementById('result-state-loading');
    const stateLoaded = document.getElementById('result-state-loaded');

    // Result Details DOM
    const predictedTitle = document.getElementById('predicted-disease-title');
    const confidencePercent = document.getElementById('confidence-percentage');
    const confidenceProgress = document.getElementById('confidence-progress');
    const diseaseDescription = document.getElementById('disease-description');
    const precautionsList = document.getElementById('precautions-list');
    const alternativesContainer = document.getElementById('alternatives-ranking-list');
    
    const clinicalFactorsCard = document.getElementById('clinical-factors-card');
    const urgentWarning = document.getElementById('urgent-warning');
    const factorDuration = document.getElementById('factor-duration');
    const factorTriggers = document.getElementById('factor-triggers');
    const factorSeverity = document.getElementById('factor-severity');
    const factorAge = document.getElementById('factor-age');

    // 2. Initialize Event Listeners
    symptomDescription.addEventListener('input', () => {
        analyzeBtn.disabled = symptomDescription.value.trim().length === 0;
    });

    analyzeBtn.addEventListener('click', runPrediction);

    // 3. Predict API Connection
    async function runPrediction() {
        const text = symptomDescription.value.trim();
        if (text.length === 0) return;

        // Set loading state
        analyzeBtn.disabled = true;
        btnText.style.opacity = '0.3';
        btnLoader.style.display = 'flex';

        // Hide current loaded/awaiting card and show loading skeleton
        stateAwaiting.classList.remove('active');
        stateAwaiting.style.display = 'none';
        stateLoaded.style.display = 'none';
        stateLoading.style.display = 'block';

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    description: text
                })
            });

            const result = await response.json();

            // Wait a small delay to simulate processing for smooth UX
            setTimeout(() => {
                // Remove loading button states
                analyzeBtn.disabled = false;
                btnText.style.opacity = '1';
                btnLoader.style.display = 'none';

                if (response.ok && result.status === 'success') {
                    renderPredictionResults(result);
                } else {
                    renderErrorState(result.message || 'An error occurred during prediction.');
                }
            }, 600);

        } catch (error) {
            console.error('Prediction request error:', error);
            setTimeout(() => {
                analyzeBtn.disabled = false;
                btnText.style.opacity = '1';
                btnLoader.style.display = 'none';
                renderErrorState('Failed to connect to the medical AI server. Please verify the backend is running.');
            }, 600);
        }
    }

    // 7. Render Success Results state
    function renderPredictionResults(data) {
        // Hide loading
        stateLoading.style.display = 'none';
        stateLoaded.style.display = 'block';

        // 1. Primary Disease & Description
        predictedTitle.textContent = data.predicted_disease;
        diseaseDescription.textContent = data.description;

        // 2. Confidence Indicator (Circular Ring)
        const confidence = data.confidence;
        confidencePercent.textContent = `${confidence}%`;

        // SVG circle logic
        const radius = 40;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (confidence / 100) * circumference;
        confidenceProgress.style.strokeDashoffset = offset;

        // Set color according to confidence levels
        if (confidence >= 80) {
            confidenceProgress.style.stroke = 'var(--color-success)';
        } else if (confidence >= 50) {
            confidenceProgress.style.stroke = 'var(--color-warning)';
        } else {
            confidenceProgress.style.stroke = 'var(--color-danger)';
        }

        // 3. Recommended Precautions List
        precautionsList.innerHTML = '';
        if (data.precautions && data.precautions.length > 0) {
            data.precautions.forEach((precaution, index) => {
                const li = document.createElement('li');
                li.className = 'precaution-item';
                li.innerHTML = `
                    <input type="checkbox" id="prec-${index}">
                    <label for="prec-${index}"><span>${precaution}</span></label>
                `;

                // Add interactive checkbox event
                const checkbox = li.querySelector('input');
                checkbox.addEventListener('change', () => {
                    if (checkbox.checked) {
                        li.classList.add('checked');
                    } else {
                        li.classList.remove('checked');
                    }
                });

                // Toggle click by row
                li.addEventListener('click', (e) => {
                    if (e.target !== checkbox) {
                        checkbox.checked = !checkbox.checked;
                        // Fire event manually
                        const event = new Event('change');
                        checkbox.dispatchEvent(event);
                    }
                });

                precautionsList.appendChild(li);
            });
        } else {
            precautionsList.innerHTML = `<li style="font-size: 13px; color: var(--text-muted);">No recommended precautions found. Consult a physician.</li>`;
        }

        // 4. Alternatives Ranking Accordion
        alternativesContainer.innerHTML = '';
        if (data.top_3 && data.top_3.length > 0) {
            data.top_3.forEach((item, index) => {
                const altCard = document.createElement('div');
                altCard.className = 'alternative-item';
                
                altCard.innerHTML = `
                    <div class="alternative-item-header" data-index="${index}">
                        <div class="alternative-title-box">
                            <span class="alternative-rank">${index + 1}</span>
                            <span class="alternative-name">${item.disease_name}</span>
                        </div>
                        <span class="alternative-prob-badge">${item.confidence}% match</span>
                    </div>
                    <div class="alternative-item-content" style="display: none;">
                        <p class="alternative-desc">${item.description}</p>
                        <div class="alternative-precautions">
                            <span class="alternative-precautions-title">Precautions</span>
                            <div class="alternative-prec-pills">
                                ${item.precautions.map(p => `<span class="alt-prec-tag">${p}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                `;

                // Accordion slide action
                const header = altCard.querySelector('.alternative-item-header');
                const content = altCard.querySelector('.alternative-item-content');

                header.addEventListener('click', () => {
                    const isVisible = content.style.display === 'block';
                    // Toggle visibility
                    content.style.display = isVisible ? 'none' : 'block';
                    
                    // Style adjustments on active headers
                    header.style.backgroundColor = isVisible ? '' : '#f1f5f9';
                });

                alternativesContainer.appendChild(altCard);
            });
        }

        // 5. Clinical Factors
        if (clinicalFactorsCard) {
            clinicalFactorsCard.style.display = 'block';
            
            if (data.urgent_medical_attention_recommended) {
                urgentWarning.style.display = 'block';
            } else {
                urgentWarning.style.display = 'none';
            }

            factorDuration.textContent = data.duration_information || 'None identified';
            
            factorTriggers.textContent = data.triggers && data.triggers.length > 0 
                ? data.triggers.join(', ') 
                : 'None identified';
                
            factorSeverity.textContent = data.severity_indicators && data.severity_indicators.length > 0 
                ? data.severity_indicators.join(', ') 
                : 'None identified';
                
            factorAge.textContent = data.age_related_factors || 'None identified';
        }
    }

    // 8. Render Error Results state
    function renderErrorState(message) {
        stateLoading.style.display = 'none';
        stateLoaded.style.display = 'none';
        
        // Show awaiting card but rewrite content with error details
        stateAwaiting.style.display = 'flex';
        stateAwaiting.classList.add('active');
        stateAwaiting.innerHTML = `
            <div class="pulse-icon-container" style="color: var(--color-danger); background-color: var(--color-danger-light); border-color: var(--color-danger);">
                <svg viewBox="0 0 24 24" width="36" height="36" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
            </div>
            <h3 style="color: var(--color-danger);">Analysis Failed</h3>
            <p style="color: var(--text-secondary); max-width: 320px;">${message}</p>
            <button type="button" id="reset-result-btn" class="chip-btn" style="margin-top: 10px; border-color: var(--text-muted);">Reset Diagnostics</button>
        `;

        document.getElementById('reset-result-btn').addEventListener('click', () => {
            // Restore default awaiting view
            stateAwaiting.innerHTML = `
                <div class="pulse-icon-container">
                    <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" class="beating-heart">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                </div>
                <h3>Awaiting Symptom Analysis</h3>
                <p>Describe your symptoms in the text area and click the "Analyze Symptoms" button. The AI model will evaluate inputs against 40+ disease classifications.</p>
            `;
            symptomDescription.value = '';
            analyzeBtn.disabled = true;
        });
    }

    // Initialization is handled by event listeners
});
