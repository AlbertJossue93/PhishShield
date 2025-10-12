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

// ⏳ Função para mostrar "carregando" no botão
function setButtonLoading(loading) {
    const button = document.getElementById('analyze-btn');
    const buttonText = button.querySelector('.button-text');

    if (loading) {
        button.classList.add('button-loading');
        buttonText.textContent = 'Analisando...';
        button.disabled = true;
    } else {
        button.classList.remove('button-loading');
        buttonText.textContent = 'Analisar URL';
        button.disabled = false;
    }
}

// Função para determinar o ícone do status
function getStatusIcon(status) {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('seguro')) return '✓';
    if (statusLower.includes('suspeito')) return '!';
    if (statusLower.includes('perigoso')) return '✗';
    return '?';
}

//  Função para validar URL
function validarUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
        return false;
    }
}

// Evento principal de análise
document.getElementById("analyze-btn").addEventListener("click", async () => {
    const urlInput = document.getElementById("url-input");
    const resultSection = document.getElementById("result-section");
    const resultDiv = document.getElementById("resultado");
    const url = urlInput.value.trim();

    //  Validações
    if (!url) {
        showError(resultSection, resultDiv, "Por favor, insira uma URL.");
        return;
    }

    if (!validarUrl(url)) { 
        showError(resultSection, resultDiv, "URL inválida. Use o formato: https://exemplo.com");
        return;
    }

    const API_URL = "http://127.0.0.1:5000/api/check";

    // ⏳ Ativar loading
    setButtonLoading(true);

    // Limpar resultado anterior
    resultSection.style.display = "none";
    

    // tratamento de erro para tratar a requisição
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        console.log("📦 Resposta da API:", data);

        //  Exibir resultado
        showResult(resultSection, resultDiv, data);

    } catch (error) {
        console.error("❌ Erro completo:", error);
        showError(resultSection, resultDiv, `Não foi possível analisar a URL. Detalhes: ${error.message}`);
    } finally {
       
        setButtonLoading(false);
    }
});

// Função para mostrar resultados
function showResult(resultSection, resultDiv, data) {
    let status, score, feedback;

    // 🧠 Detecta estrutura da resposta (nova ou antiga)
    if (data.resultado) {
        status = data.resultado.status || "Desconhecido";
        score = data.resultado.score ?? "N/A";
        feedback = data.resultado.feedback || ["Sem detalhes"];
    } else {
        score = data.score ?? 0;
        status = score === 0 ? "Seguro" : score <= 2 ? "Suspeito" : "Perigoso";
        feedback = data.feedback || ["Sem detalhes"];
    }

    //  Garante que a classe de status exista
    const statusClass = getStatusClass(status);

    resultSection.style.display = "block";
    resultDiv.innerHTML = `
        <div class="status-header">
            <div class="status-icon ${statusClass}">${getStatusIcon(status)}</div>
            <div class="status-text">Status: ${status}</div>
        </div>
        <div class="result-item">
            <span class="result-label">Score:</span>
            <span class="result-value">${score}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Feedback:</span>
            <div class="feedback-list">
                ${Array.isArray(feedback)
                    ? feedback.map(item => `<div class="feedback-item">${item}</div>`).join('')
                    : `<div class="feedback-item">${feedback}</div>`}
            </div>
        </div>
        <button class="json-toggle" id="toggle-json">Ver JSON bruto</button>
        <pre class="json-view" id="json-view" style="display:none;">${JSON.stringify(data, null, 2)}</pre>
    `;

    //  Botão para expandir JSON
    const toggleBtn = document.getElementById("toggle-json");
    const jsonView = document.getElementById("json-view");
    toggleBtn.addEventListener("click", () => {
        const isHidden = jsonView.style.display === "none";
        jsonView.style.display = isHidden ? "block" : "none";
        toggleBtn.textContent = isHidden ? "Ocultar JSON" : "Ver JSON bruto";
    });
}

// Função auxiliar (⚡️necessária)
function getStatusClass(status) {
    const s = status.toLowerCase();
    if (s.includes("seguro")) return "status-seguro";
    if (s.includes("suspeito")) return "status-suspeito";
    if (s.includes("perigoso")) return "status-perigoso";
    return "status-desconhecido";
}

// Função para mostrar erros
function showError(resultSection, resultDiv, message) {
    resultSection.style.display = "block";
    resultDiv.innerHTML = `
        <div class="status-header">
            <div class="status-icon status-perigoso">!</div>
            <div class="status-text">Erro</div>
        </div>
        <p style="color: var(--error-color); margin: 0;">${message}</p>
    `;
}

// Enter key support
document.getElementById("url-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        document.getElementById("analyze-btn").click();
    }
});

// Focar no input quando a extensão abrir
document.addEventListener("DOMContentLoaded", () => {
    const urlInput = document.getElementById("url-input");
    urlInput.focus();

    // Limpar resultados anteriores
    const resultSection = document.getElementById("result-section");
    resultSection.style.display = "none";
});






