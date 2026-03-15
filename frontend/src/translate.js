// Gemini translation API call
export async function translateText(text, targetLang, sourceLang = "auto") {
  // You should create a backend endpoint to call Gemini securely
  // Here is a sample POST request to your backend
  const response = await fetch("http://localhost:5000/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, targetLang, sourceLang })
  });
  const data = await response.json();
  return data.translatedText;
}
