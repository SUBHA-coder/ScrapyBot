document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const scrapedContent = document.getElementById("scraped-content");
    const scrapeContainer = document.getElementById("scrape-container");
    const toggleScrapeBtn = document.getElementById("toggle-scrape");

    function addMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender);
        msgDiv.textContent = text;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to latest message
    }

    async function scrapeData() {
        const url = document.getElementById("url").value.trim();
        if (!url) {
            addMessage("Error: Please enter a valid URL.", "error");
            return;
        }

        addMessage(`Scraping: ${url}`, "system");
        scrapedContent.innerText = "Scraping in progress...";

        try {
            const response = await fetch("/scrape", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            scrapedContent.innerText = data.data || "Error fetching content";
            addMessage("Scraping complete.", "system");

        } catch (error) {
            scrapedContent.innerText = `Error: ${error.message}`;
            addMessage(`Error: ${error.message}`, "error");
        }
    }

    async function askQuestion() {
        const question = document.getElementById("question").value.trim();
        if (!question) {
            addMessage("Error: Please enter a question.", "error");
            return;
        }

        addMessage(question, "user");
        addMessage("Processing...", "system");

        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            addMessage(data.answer || "No response from server.", "ai");

        } catch (error) {
            addMessage(`Error: ${error.message}`, "error");
        }
    }

    // Toggle Scraped Data View
    toggleScrapeBtn.addEventListener("click", () => {
        scrapeContainer.classList.toggle("hidden");
        toggleScrapeBtn.textContent = scrapeContainer.classList.contains("hidden")
            ? "Show Scraped Data"
            : "Hide Scraped Data";
    });

    // Make these functions available globally
    window.scrapeData = scrapeData;
    window.askQuestion = askQuestion;
});
