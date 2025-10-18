// 🌙 Toggle Dark Mode
// Dark Mode Toggle
document.getElementById('theme-toggle').addEventListener('click', function() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    chrome.storage.local.set({ theme: newTheme });
});

// Carregar tema salvo
chrome.storage.local.get(['theme'], function(result) {
    const savedTheme = result.theme || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
});


// Função para validar URL
function validarUrl(url) {
    try {
        new URL(url); // Verifica se é uma URL válida
        return /^https?:\/\//i.test(url); // Aceita apenas http ou https
    } catch {
        return false;
    }
}

// Função para sanitizar strings contra XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// Função para determinar o ícone do status
function getStatusIcon(status) {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('seguro')) return '✓';
    if (statusLower.includes('suspeito')) return '!';
    if (statusLower.includes('perigoso')) return '✗';
    return '?';
}
// Função para determinar a classe CSS do status
function getStatusClass(status) {
    const s = status.toLowerCase();
    if (s.includes('seguro')) return 'status-seguro';
    if (s.includes('suspeito')) return 'status-suspeito';
    if (s.includes('perigoso')) return 'status-perigoso';
    return 'status-desconhecido';
}
// Função para mostrar erros
function showError(resultSection, resultDiv, message) {
    resultSection.style.display = "block";
    resultDiv.innerHTML = `
        <div class="status-header">
            <div class="status-icon status-perigoso">!</div>
            <div class="status-text">Erro</div>
        </div>
        <p style="color: var(--error-color, #d32f2f); margin: 0;">${escapeHtml(message)}</p>
    `;
}

// Função para mostrar resultados
function showResult(resultSection, resultDiv, data) {
    let status, score, feedback, urlAnalisada, timestamp;

    // Estrutura da resposta
    if (data.resultado) {
        status = data.resultado.status || "Desconhecido";
        score = data.resultado.score ?? "N/A";
        feedback = data.resultado.feedback || ["Sem detalhes"];
        subdomainCount = data.resultado.subdomain_count ?? 0;
        urlAnalisada = data.url_analisada || "N/A";
        timestamp = data.timestamp || new Date().toISOString();
    } else {
        score = data.score ?? 0;
        status = score === 0 ? "Seguro" : score <= 2 ? "Suspeito" : "Perigoso";
        feedback = data.feedback || ["Sem detalhes"];
        subdomainCount = data.resultado.subdomain_count ?? 0;
        urlAnalisada = data.url_analisada || "N/A";
        timestamp = data.timestamp || new Date().toISOString();
    }

    const statusClass = getStatusClass(status);

    resultSection.style.display = "block";
    resultDiv.innerHTML = `
        <div class="result-item">
            <span class="result-label">URL Analisada:</span>
            <span class="result-value">${escapeHtml(urlAnalisada)}</span>
        </div>
        <div class="status-header">
            <div class="status-icon ${statusClass}">${getStatusIcon(status)}</div>
            <div class="status-text">Status: ${escapeHtml(status)}</div>
        </div>
        <div class="result-item">
            <span class="result-label">Score:</span>
            <span class="result-value">${score}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Feedback:</span>
            <div class="feedback-list">
                ${Array.isArray(feedback)
                    ? feedback.map(item => `<div class="feedback-item">${escapeHtml(item)}</div>`).join('')
                    : `<div class="feedback-item">${escapeHtml(feedback)}</div>`}
            </div>
        </div>
        <div class="result-item">
            <span class="result-label">Analisado em:</span>
            <span class="result-value">${new Date(timestamp).toLocaleString()}</span>
        </div>
        <button class="json-toggle" id="toggle-json">Ver JSON bruto</button>
        <pre class="json-view" id="json-view" style="display:none;">${JSON.stringify(data, null, 2)}</pre>
    `;


    // Botão para expandir JSON
    const toggleBtn = document.getElementById("toggle-json");
    const jsonView = document.getElementById("json-view");
    toggleBtn.addEventListener("click", () => {
        const isHidden = jsonView.style.display === "none";
        jsonView.style.display = isHidden ? "block" : "none";
        toggleBtn.textContent = isHidden ? "Ocultar JSON" : "Ver JSON bruto";
    });
}

// Função para gerenciar estado do botão
function setButtonLoading(loading) {
    const button = document.getElementById("analyze-btn");
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> Analisando...';
    } else {
        button.disabled = false;
        button.textContent = "Analisar URL";
    }
}

// Evento principal de análise
document.getElementById("analyze-btn").addEventListener("click", async () => {
    const urlInput = document.getElementById("url-input");
    const resultSection = document.getElementById("result-section");
    const resultDiv = document.getElementById("resultado");
    const url = urlInput.value.trim();

    // Validações
    if (!url) {
        showError(resultSection, resultDiv, "Por favor, insira uma URL.");
        return;
    }

    if (!validarUrl(url)) {
        showError(resultSection, resultDiv, "URL inválida. Use o formato: https://exemplo.com");
        return;
    }

    const API_URL = "http://127.0.0.1:5000/api/check";

    setButtonLoading(true);
    resultSection.style.display = "none";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, timeout: 10 })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `Erro na requisição: ${response.status}`);
        }

        showResult(resultSection, resultDiv, data);

    } catch (error) {
        console.error("❌ Erro completo:", error);
        showError(resultSection, resultDiv, `Não foi possível analisar a URL. Detalhes: ${escapeHtml(error.message)}`);
    } finally {
        setButtonLoading(false);
    }
});


// Suporte à tecla Enter
document.getElementById("url-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        document.getElementById("analyze-btn").click();
    }
});

// Focar no input quando a extensão abrir
document.addEventListener("DOMContentLoaded", () => {
    const urlInput = document.getElementById("url-input");
    urlInput.focus();
    const resultSection = document.getElementById("result-section");
    resultSection.style.display = "none";
});