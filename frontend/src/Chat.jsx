import React, { useState, useRef, useEffect } from "react";
import { SendIcon, MicIcon, MicOffIcon } from "./icons";
import { translateText } from "./translate";
import styled, { keyframes } from "styled-components";
import axios from "axios";
import logo from "./logo.png";
import { classifyPlantImage } from "./plantApi";
import { marked } from "marked";

// Simple HTML sanitizer for safety
const sanitizeHtml = (html) => {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  // Simple check: remove script tags
  const scripts = doc.querySelectorAll('script');
  scripts.forEach(s => s.remove());
  return doc.body.innerHTML;
};

const RASA_URL = process.env.REACT_APP_RASA_URL || "http://localhost:5005/webhooks/rest/webhook";

// ====== Colors & Gradient ======
const colors = {
  darkGreen: "#2E7D32",
  midGreen: "#388E3C",
  lightGreen: "#66BB6A",
  brightGreen: "#81C784",
};
const gradient = `linear-gradient(135deg, ${colors.darkGreen}, ${colors.brightGreen})`;

// ====== Styled Components ======
const PageContainer = styled.div`
  display: flex;
  height: 100vh;
  font-family: "Arial", sans-serif;
  background: #f4f8fb;
  overflow: hidden;
  padding: 16px;
  box-sizing: border-box;
`;

const Sidebar = styled.div`
  width: 260px;
  background-color: ${colors.darkGreen};
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 20px;
  border-radius: 16px 0 0 16px;
`;

const SidebarLogo = styled.img`
  height: 140px;
  margin-bottom: 20px;
  border-radius: 12px;
  object-fit: contain;
  mix-blend-mode: lighten;
  filter: brightness(1.1) contrast(1.1);
  transition: transform 0.3s ease;

  &:hover {
    transform: scale(1.05);
  }
`;

const SidebarMenu = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const MenuItem = styled.button`
  padding: 12px 18px;
  background: ${(props) => (props.active ? gradient : "transparent")};
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  font-weight: 500;
  transition: all 0.3s;
  &:hover {
    background: ${gradient};
  }
`;

const RecentSection = styled.div`
  margin-top: auto;
  font-size: 0.9rem;
  color: #c1c1c1;
`;

const StatusRow = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.85rem;
`;

const StatusSmall = styled.span`
  font-size: 0.85rem;
  color: #d1d1d1;
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f9fbff;
  border-radius: 0 16px 16px 0;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
`;

const ChatHeader = styled.div`
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: ${gradient};
  color: #fff;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 0 16px 0 0;
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const MessageBox = styled.div`
  max-width: 70%;
  align-self: ${(props) =>
    props.sender === "user" ? "flex-end" : "flex-start"};
  background: ${(props) =>
    props.sender === "user"
      ? `linear-gradient(135deg, ${colors.midGreen}, ${colors.darkGreen})`
      : `linear-gradient(135deg, ${colors.lightGreen}, ${colors.brightGreen})`};
  color: #fff;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  line-height: 1.5;

  p { margin: 8px 0; }
  ul, ol { margin: 8px 0; padding-left: 20px; }
  li { margin: 4px 0; }
  strong { font-weight: 700; color: #fff; }
  code { background: rgba(0,0,0,0.1); padding: 2px 4px; border-radius: 4px; }
`;

const MessageImage = styled.img`
  max-width: 100%;
  border-radius: 14px;
  display: block;
  margin-bottom: ${(props) => (props.hasText ? "6px" : "0")};
`;

const TypingDots = keyframes`
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
  60% { transform: translateY(-2px); }
`;

const BotTyping = styled.div`
  max-width: 50%;
  align-self: flex-start;
  display: flex;
  gap: 6px;
  padding: 12px 18px;
  border-radius: 20px;
  background-color: #e8f5e9;

  div {
    width: 8px;
    height: 8px;
    background-color: ${colors.brightGreen};
    border-radius: 50%;
    animation: ${TypingDots} 1.4s infinite;
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
`;

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: 12px 16px 16px 16px;
  border-top: 1px solid #ddd;
  background-color: #fff;
  border-radius: 0 0 16px 0;
`;

// New container for the staged image preview above the input line
const StagedImagePreview = styled.div`
  display: flex;
  padding: 8px;
  margin-bottom: 8px;
  position: relative;
  width: fit-content;

  img {
    height: 80px;
    border-radius: 10px;
    border: 2px solid ${colors.lightGreen};
  }

  button {
    position: absolute;
    top: -5px;
    right: -5px;
    background: #ff4444;
    color: white;
    border: none;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    cursor: pointer;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
  }
`;

const InputRow = styled.div`
  display: flex;
  align-items: center;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 18px;
  border-radius: 25px;
  border: none;
  font-size: 1rem;
  outline: none;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.08);
`;

const VoiceButton = styled.button`
  padding: 8px 10px;
  margin-left: 8px;
  background: transparent;
  color: ${colors.brightGreen};
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
`;

const AttachButton = styled.button`
  padding: 8px 10px;
  margin-left: 8px;
  background: transparent;
  color: ${colors.brightGreen};
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
`;

const SendButton = styled.button`
  padding: 10px 14px;
  margin-left: 8px;
  background: ${gradient};
  color: #fff;
  border: none;
  border-radius: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  &[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

// ====== Main Component ======
const KrishiAIChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [stagedFile, setStagedFile] = useState(null); // The actual image file
  const [stagedPreview, setStagedPreview] = useState(null); // The blob URL for preview
  const [botTyping, setBotTyping] = useState(false);
  const [language, setLanguage] = useState("en");
  const [listening, setListening] = useState(false);
  const [activeMenu, setActiveMenu] = useState("General");
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const fileInputRef = useRef(null);

  const RASA_WEBHOOK = RASA_URL;

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recog = new SpeechRecognition();
    recog.continuous = false;
    recog.interimResults = false;
    recog.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setListening(false);
    };
    recog.onend = () => setListening(false);
    recog.onerror = () => setListening(false);
    recognitionRef.current = recog;
  }, []);

  const startListening = () => {
    if (!recognitionRef.current) {
      alert("Speech Recognition not supported in this browser");
      return;
    }
    const langMap = { en: "en-US", hi: "hi-IN", gu: "gu-IN" };
    recognitionRef.current.lang = langMap[language] || "en-US";
    try {
      setListening(true);
      recognitionRef.current.start();
    } catch (e) {
      setListening(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, botTyping]);

  // STAGE IMAGE (Selection)
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setStagedFile(file);
      setStagedPreview(URL.createObjectURL(file));
    }
    e.target.value = "";
  };

  // STAGE IMAGE (Paste)
  const handlePaste = (e) => {
    if (!e.clipboardData) return;
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          setStagedFile(file);
          setStagedPreview(URL.createObjectURL(file));
          e.preventDefault();
          break;
        }
      }
    }
  };

  // Clear Staged Image
  const clearStagedImage = () => {
    setStagedFile(null);
    setStagedPreview(null);
  };

  // SEND MESSAGE (Text + Staged Image)
  const sendMessage = async () => {
    if (!input.trim() && !stagedFile) return;

    const userText = input;
    const currentFile = stagedFile;
    const currentPreview = stagedPreview;

    // Reset inputs immediately
    setInput("");
    clearStagedImage();

    // Add user message with image to UI
    setMessages((prev) => [
      ...prev,
      { sender: "user", text: userText, imageUrl: currentPreview },
    ]);
    
    setBotTyping(true);

    try {
      let detectedLabel = null;

      // 1) Handle Image Classification if exists
      if (currentFile) {
        try {
          const result = await classifyPlantImage(currentFile);
          detectedLabel = result.predicted_label;
        } catch (imageErr) {
          console.error("Plant classification failed, proceeding with text-only:", imageErr);
        }
      }

      // 2) Language Translation for user text
      let translatedInput = userText || "image_uploaded";
      if (language !== "en" && userText) {
        translatedInput = await translateText(userText, "en", language);
      }

      // 3) Send to Rasa
      const resp = await axios.post(
        RASA_WEBHOOK,
        {
          sender: "web_user",
          message: userText || "image_uploaded",
          metadata: {
            detected_disease: detectedLabel,
            language: language, // Pass language to backend
          },
        },
        { timeout: 30000 }
      );

      // 4) Proactively join all text segments from Rasa to FORCE a single bubble
      const rawBotResponse = resp.data || [];
      const botTextChunks = rawBotResponse
        .map((r) => r.text)
        .filter((t) => typeof t === "string" && t.trim().length > 0);

      const consolidatedText = (detectedLabel ? [`**Image Analysis: ${detectedLabel}**`] : [])
        .concat(botTextChunks)
        .join("\n\n");

      if (consolidatedText) {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: consolidatedText },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: "I received your message but couldn't generate a text response. Please try again." },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error connecting to service." },
      ]);
    } finally {
      setBotTyping(false);
    }
  };

  const menuItems = ["General", "Crop Info", "Diseases", "Treatment", "Prevention"];

  return (
    <PageContainer>
      <Sidebar>
        <SidebarLogo src={logo} alt="KrishiAI Logo" />
        <SidebarMenu>
          {menuItems.map((item) => (
            <MenuItem
              key={item}
              active={item === activeMenu}
              onClick={() => setActiveMenu(item)}
            >
              {item}
            </MenuItem>
          ))}
        </SidebarMenu>

        <RecentSection>
          <h4>About</h4>
          <p>Multilingual assistant for crops & farmers.</p>
          <StatusRow>
            <div>
              <strong>Status:</strong>{" "}
              <StatusSmall style={{ color: "#2ecc71" }}>online</StatusSmall>
            </div>
          </StatusRow>
        </RecentSection>
      </Sidebar>

      <ChatContainer>
        <ChatHeader>
          KisaanAI - {activeMenu}
          <span style={{ marginLeft: "auto" }}>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              style={{
                marginLeft: 10,
                padding: 6,
                borderRadius: 8,
                border: "none",
              }}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="gu">Gujarati</option>
            </select>
          </span>
        </ChatHeader>

        <MessagesContainer>
          {messages.map((msg, idx) => (
            <MessageBox key={idx} sender={msg.sender}>
              {msg.imageUrl && (
                <MessageImage
                  src={msg.imageUrl}
                  alt="uploaded"
                  hasText={!!msg.text}
                />
              )}
              {msg.text && (
                <div
                  className="markdown-content"
                  dangerouslySetInnerHTML={{
                    __html: sanitizeHtml(marked.parse(msg.text)),
                  }}
                />
              )}
            </MessageBox>
          ))}
          {botTyping && (
            <BotTyping>
              <div />
              <div />
              <div />
            </BotTyping>
          )}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        <InputContainer>
          {/* GEMINI STYLE STAGING AREA */}
          {stagedPreview && (
            <StagedImagePreview>
              <img src={stagedPreview} alt="Staged" />
              <button onClick={clearStagedImage}>×</button>
            </StagedImagePreview>
          )}

          <InputRow>
            <Input
              type="text"
              placeholder={`Ask about ${activeMenu.toLowerCase()}...`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              onPaste={handlePaste}
            />

            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              style={{ display: "none" }}
              onChange={handleFileChange}
            />

            <AttachButton
              title="Attach image"
              onClick={() =>
                fileInputRef.current && fileInputRef.current.click()
              }
            >
              📎
            </AttachButton>

            <VoiceButton title="Speak" onClick={startListening}>
              {listening ? <MicOffIcon size={22} /> : <MicIcon size={22} />}
            </VoiceButton>

            <SendButton onClick={sendMessage} disabled={(!input.trim() && !stagedFile) || botTyping}>
              <SendIcon size={20} />
            </SendButton>
          </InputRow>
        </InputContainer>
      </ChatContainer>
    </PageContainer>
  );
};

export default KrishiAIChat;