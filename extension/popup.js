// configurações do tema
document.getElementById('theme-toggle').addEventListener('click', () => {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    chrome.storage.local.set({ theme: newTheme });
});

chrome.storage.local.get(['theme'], (result) => {
    const theme = result.theme || 'light';
    document.documentElement.setAttribute('data-theme', theme);
});
// validação da url
function validarUrl(url) {
    try {
        new URL(url);
        return /^https?:\/\//i.test(url);
    } catch { return false; }
}
// escape html contra ataque xss
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getStatusIcon(status) {
    const s = status.toLowerCase();
    if (s.includes('seguro')) return '✓';
    if (s.includes('suspeito')) return '!';
    if (s.includes('perigoso')) return '✗';
    return '?';
}

function getStatusClass(status) {
    const s = status.toLowerCase();
    if (s.includes('seguro')) return 'status-seguro';
    if (s.includes('suspeito')) return 'status-suspeito';
    if (s.includes('perigoso')) return 'status-perigoso';
    return 'status-desconhecido';
}

function setButtonLoading(loading) {
    const btn = document.getElementById("analyze-btn");
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> Analisando...';
    } else {
        btn.disabled = false;
        btn.innerHTML = '<span class="button-text">Analisar URL</span>';
    }
}

document.getElementById("analyze-btn").addEventListener("click", analyze);
document.getElementById("url-input").addEventListener("keypress", e => {
    if (e.key === "Enter") analyze();
});

async function analyze() {
const modal = document.getElementById("resultModal");
const modalBody = document.getElementById("modalBody");
const closeModal = document.getElementById("closeModal");

    const url = document.getElementById("url-input").value.trim();
    if (!url) return showError("Por favor, insira uma URL.");
    if (!validarUrl(url)) return showError("URL inválida. Use https://exemplo.com");

    modal.style.display = "flex";
    modalBody.innerHTML = `<p style="text-align:center; padding:20px;">Analisando...</p>`;

    const API_URL = "http://127.0.0.1:5000/api/check";
    setButtonLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Erro na API");

        renderResult(data);
    } catch (error) {
        showError(`Erro: ${error.message}`);
    } finally {
        setButtonLoading(false);
    }
}

function renderResult(data) {
    let status = "Desconhecido", score = "N/A", feedback = ["Sem detalhes"], urlAnalisada = "N/A";

    if (data.resultado) {
        status = data.resultado.status || status;
        score = data.resultado.score ?? score;
        feedback = data.resultado.feedback || feedback;
        urlAnalisada = data.url_analisada || urlAnalisada;
    }

    const statusClass = getStatusClass(status);

    modalBody.innerHTML = `
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
                ${feedback.map(item => `<div class="feedback-item">${escapeHtml(item)}</div>`).join('')}
            </div>
        </div>
        <button class="json-toggle" id="toggle-json">Ver JSON bruto</button>
        <pre class="json-view" id="json-view" style="display:none;">${JSON.stringify(data, null, 2)}</pre>
    `;

    document.getElementById("toggle-json").addEventListener("click", () => {
        const view = document.getElementById("json-view");
        const btn = document.getElementById("toggle-json");
        view.style.display = view.style.display === "none" ? "block" : "none";
        btn.textContent = view.style.display === "block" ? "Ocultar JSON" : "Ver JSON bruto";
    });
}
// mostra o erro na modal 
function showError(message) {
    modal.style.display = "flex";
    modalBody.innerHTML = `
        <div class="status-header">
            <div class="status-icon status-perigoso">!</div>
            <div class="status-text">Erro</div>
        </div>
        <p style="color: var(--error-color); margin: 16px 0; text-align: center;">${escapeHtml(message)}</p>
    `;
}

const closeModal = document.getElementById("closeModal");
const modal = document.getElementById("resultModal");

if (closeModal && modal) {
    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const urlInput = document.getElementById("url-input");
    if (urlInput) urlInput.focus();
});