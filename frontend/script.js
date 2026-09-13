const textInput = document.getElementById("textInput");
const checkBtn = document.getElementById("checkBtn");
const charCount = document.getElementById("charCount");
const loading = document.getElementById("loading");
const resultCard = document.getElementById("resultCard");
const resultLabel = document.getElementById("resultLabel");
const confidenceText = document.getElementById("confidenceText");
const confidenceBar = document.getElementById("confidenceBar");
const errorMessage = document.getElementById("errorMessage");
const historyList = document.getElementById("historyList");
const clearHistory = document.getElementById("clearHistory");

let history = JSON.parse(sessionStorage.getItem("predictionHistory")) || [];

textInput.addEventListener("input", () => {
    charCount.textContent = `${textInput.value.length} / 1000`;
});

checkBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();

    if (!text) {
        showError("Please enter some text first.");
        return;
    }

    setLoading(true);
    hideError();
    resultCard.classList.add("hidden");

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong.");
        }

        showResult(data.label, data.confidence);
        addToHistory(text, data.label, data.confidence);
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    loading.classList.toggle("hidden", !isLoading);
    checkBtn.disabled = isLoading;
    checkBtn.textContent = isLoading ? "Checking..." : "Check Text";
}

function showResult(label, confidence) {
    const className = label.toLowerCase();

    resultCard.className = `result ${className}`;
    resultLabel.textContent = label;
    confidenceText.textContent = `${confidence.toFixed(2)}%`;

    setTimeout(() => {
        confidenceBar.style.width = `${confidence}%`;
    }, 50);
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}

function hideError() {
    errorMessage.classList.add("hidden");
}

function addToHistory(text, label, confidence) {
    history.unshift({
        text,
        label,
        confidence
    });

    history = history.slice(0, 5);
    sessionStorage.setItem("predictionHistory", JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    if (history.length === 0) {
        historyList.innerHTML =
            '<p class="empty-state">No predictions yet.</p>';
        return;
    }

    historyList.innerHTML = history
        .map(item => `
            <div class="history-item">
                <p title="${escapeHtml(item.text)}">${escapeHtml(item.text)}</p>
                <span class="history-label ${item.label.toLowerCase()}">
                    ${item.label} · ${Number(item.confidence).toFixed(1)}%
                </span>
            </div>
        `)
        .join("");
}

clearHistory.addEventListener("click", () => {
    history = [];
    sessionStorage.removeItem("predictionHistory");
    renderHistory();
});

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

renderHistory();
