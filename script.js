window.onload = function() {
    document.querySelector("button").addEventListener("click", summarizeVideo);
};

function summarizeVideo() {
    let urlInput = document.getElementById("youtubeUrl");
    
    if (!urlInput) {
        console.error("Input field not found!");
        return;
    }

    let url = urlInput.value.trim();
    if (!url) {
        alert("Please enter a YouTube URL!");
        return;
    }

    // ✅ Remove extra parameters from URL
    let cleanUrl = url.split("&")[0];

    console.log("🎥 Sending Clean URL:", cleanUrl);

    fetch("/summarize", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ youtube_url: cleanUrl })  // ✅ Use correct key
    })
    .then(response => response.json())
    .then(data => {
        console.log("🔹 Server Response:", data);
        document.getElementById("summary").innerText = data.summary || "Error: No summary received.";
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("summary").innerText = "An error occurred.";
    });
}
