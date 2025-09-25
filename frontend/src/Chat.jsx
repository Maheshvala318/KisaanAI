import React, { useState, useRef, useEffect } from "react";
import styled, { keyframes } from "styled-components";
import axios from "axios";
import logo from "./logo.png"; // Your uploaded logo

// ====== Colors & Gradient ======
const colors = {
  darkBlue: "#3C467B",
  midBlue: "#50589C",
  lightBlue: "#636CCB",
  brightBlue: "#6E8CFB"
};

const gradient = `linear-gradient(135deg, ${colors.darkBlue}, ${colors.brightBlue})`;

// ====== Styled Components ======
const PageContainer = styled.div`
  display: flex;
  height: 100vh;
  font-family: 'Arial', sans-serif;
  background: #f4f8fb;
`;

const Sidebar = styled.div`
  width: 260px;
  background-color: ${colors.darkBlue};
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 20px;
`;

const SidebarLogo = styled.img`
  height: 170px;        // increased size
  margin-bottom: 30px;  // give it a little more spacing
  border-radius: 12px;
  object-fit: contain;
`;

const SidebarMenu = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const MenuItem = styled.button`
  padding: 12px 18px;
  background: ${props => props.active ? gradient : "transparent"};
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  font-weight: 500;
  transition: all 0.3s;
  &:hover { background: ${gradient}; }
`;

const RecentSection = styled.div`
  margin-top: 30px;
  font-size: 0.9rem;
  color: #c1c1c1;
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const ChatHeader = styled.div`
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: ${gradient};
  color: #fff;
  font-size: 1.2rem;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const MessageBox = styled.div`
  max-width: 70%;
  align-self: ${props => props.sender === "user" ? "flex-end" : "flex-start"};
  background: ${props => props.sender === "user" 
    ? `linear-gradient(135deg, ${colors.midBlue}, ${colors.darkBlue})` 
    : `linear-gradient(135deg, ${colors.lightBlue}, ${colors.brightBlue})`};
  color: #fff;
  padding: 12px 18px;
  border-radius: 20px;
  word-wrap: break-word;
  box-shadow: 0 3px 6px rgba(0,0,0,0.2);
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
  background-color: #e0e7ff;

  div {
    width: 8px;
    height: 8px;
    background-color: ${colors.brightBlue};
    border-radius: 50%;
    animation: ${TypingDots} 1.4s infinite;
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
`;

const InputContainer = styled.div`
  display: flex;
  padding: 18px 20px;   // slightly bigger padding
  border-top: 1px solid #e0e0e0;
  background-color: #fff;
  box-shadow: 0 -3px 10px rgba(0,0,0,0.1); // shadow below
  margin-bottom: 5px;   // moves it a little up
  border-radius: 12px 12px 0 0; // rounded top edges
`;

const Input = styled.input`
  flex: 1;
  padding: 14px 20px;   // slightly bigger input
  border-radius: 30px;
  border: 1px solid #ccc;
  font-size: 1.05rem;   // slightly bigger font
  outline: none;
  box-shadow: inset 0 2px 5px rgba(0,0,0,0.05); // subtle inner shadow
`;

const SendButton = styled.button`
  padding: 14px 24px;    // bigger button
  margin-left: 12px;
  background: ${gradient};
  color: #fff;
  border: none;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  box-shadow: 0 3px 6px rgba(0,0,0,0.15); // button shadow
  &:hover { opacity: 0.85; }
`;

// ====== Main Component ======
const JeevanAIChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [botTyping, setBotTyping] = useState(false);
  const [activeMenu, setActiveMenu] = useState("General");
  const messagesEndRef = useRef(null);

  const menuItems = ["General", "Health", "Finance", "Education", "Tech"];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, botTyping]);

  const sendMessage = async () => {
    if (!input) return;

    setMessages(prev => [...prev, { sender: "user", text: input }]);
    setInput("");
    setBotTyping(true);

    try {
      const response = await axios.post(
        "http://localhost:5005/webhooks/rest/webhook",
        { sender: "user123", message: input }
      );

      setBotTyping(false);
      response.data.forEach(msg => {
        setMessages(prev => [...prev, { sender: "bot", text: msg.text }]);
      });
    } catch (err) {
      console.error(err);
      setBotTyping(false);
      setMessages(prev => [...prev, { sender: "bot", text: "Oops! Something went wrong." }]);
    }
  };

  return (
    <PageContainer>
      <Sidebar>
        <SidebarLogo src={logo} alt="JeevanAI Logo" />
        <SidebarMenu>
          {menuItems.map(item => (
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
          <h4>Recent</h4>
          <p>Retro Navratri Image Enhancement</p>
          <p>Indian Style Image Enhancement</p>
          <p>Image Editing Request</p>
        </RecentSection>
      </Sidebar>

      <ChatContainer>
        <ChatHeader>JeevanAI - {activeMenu} Chat</ChatHeader>
        <MessagesContainer>
          {messages.map((msg, idx) => (
            <MessageBox key={idx} sender={msg.sender}>
              {msg.text}
            </MessageBox>
          ))}
          {botTyping && <BotTyping><div/><div/><div/></BotTyping>}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        <InputContainer>
          <Input
            type="text"
            placeholder={`Ask something in ${activeMenu}...`}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
          />
          <SendButton onClick={sendMessage}>Send</SendButton>
        </InputContainer>
      </ChatContainer>
    </PageContainer>
  );
};

export default JeevanAIChat;
