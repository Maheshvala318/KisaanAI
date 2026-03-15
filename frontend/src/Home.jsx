// src/components/FarmerHero.jsx
import React, { useEffect, useState } from "react";
import styled, { keyframes } from "styled-components";
import { Link } from "react-router-dom"; 

// ===== Enhanced Color palette =====
const colors = {
  avocado: "#598216",
  olive1: "#6B911B",
  olive2: "#819A20",
  citrine: "#D9D40C",
  oxley: "#72A06A",
  moss: "#416422",
  freshGreen: "#7CB342",
  earthBrown: "#6D4C41",
  sunGold: "#FFA726",
  skyBlue: "#42A5F5",
};

// ===== Helper: auto-import all hero images from src/assets/farmhero =====
const importAll = (r) => r.keys().map(r);
const heroImages = importAll(
  require.context("./assets/farmhero", false, /\.(png|jpe?g|svg)$/i)
);

// ===== Animations =====
const fadeSlide = keyframes`
  0% {
    opacity: 0;
    transform: scale(1.08);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
`;

const fadeOut = keyframes`
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
`;

const float = keyframes`
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
`;

const shimmer = keyframes`
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
`;

// ===== Styled Components =====

const HeroRoot = styled.div`
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(
    135deg,
    #e8f5e9 0%,
    #f1f8e9 25%,
    #fff9c4 50%,
    #fff3e0 75%,
    #fce4ec 100%
  );
  color: #122109;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
`;

// Background wrapper
const HeroBg = styled.div`
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
`;

// Single full-screen background image with smooth crossfade
const HeroBgImage = styled.img`
  position: absolute;
  inset: -4%;
  width: 108%;
  height: 108%;
  object-fit: cover;
  filter: saturate(1.15) brightness(1.05);
  transition: opacity 1.5s ease-in-out;
  z-index: 0;
  
  &.entering {
    opacity: 0;
    animation: ${fadeSlide} 2s ease-out forwards;
  }
  
  &.exiting {
    opacity: 1;
    animation: ${fadeOut} 1.5s ease-out forwards;
  }
  
  &.active {
    opacity: 1;
  }
`;

// Enhanced overlay with gradient variety
const HeroBgOverlay = styled.div`
  position: absolute;
  inset: 0;
  background: linear-gradient(
      135deg,
      rgba(56, 142, 60, 0.35) 0%,
      rgba(104, 159, 56, 0.28) 35%,
      rgba(251, 192, 45, 0.18) 70%,
      rgba(255, 138, 101, 0.15) 100%
    ),
    radial-gradient(
      ellipse at top left,
      rgba(129, 199, 132, 0.3) 0%,
      transparent 50%
    ),
    radial-gradient(
      ellipse at bottom right,
      rgba(255, 183, 77, 0.25) 0%,
      transparent 50%
    );
  backdrop-filter: blur(3px);
  z-index: 1;
`;

// ===== Enhanced Header =====
const HeroNav = styled.header`
  position: relative;
  z-index: 2;
  padding: 18px 6vw;
  display: flex;
  align-items: center;
  justify-content: space-between;
  backdrop-filter: blur(12px) saturate(180%);
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.85) 0%,
    rgba(255, 255, 255, 0.75) 100%
  );
  border-bottom: 2px solid rgba(129, 199, 132, 0.4);
  box-shadow: 0 8px 32px rgba(56, 142, 60, 0.15),
    0 2px 8px rgba(104, 159, 56, 0.1);

  @media (max-width: 768px) {
    padding-inline: 1.5rem;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 800;
  font-size: 1.7rem;
  background: linear-gradient(135deg, ${colors.freshGreen}, ${colors.olive1});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 2px 4px rgba(124, 179, 66, 0.3));
`;

const LogoIcon = styled.span`
  font-size: 2.2rem;
  animation: ${float} 3s ease-in-out infinite;
`;

const NavLinks = styled.nav`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const NavLink = styled(Link)`
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.9) 0%,
    rgba(255, 255, 255, 0.7) 100%
  );
  border: 2px solid rgba(129, 199, 132, 0.6);
  font-size: 1.05rem;
  cursor: pointer;
  color: ${colors.freshGreen};
  font-weight: 700;
  padding: 10px 22px;
  border-radius: 999px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
  text-decoration: none;
  position: relative;
  overflow: hidden;

  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.4),
      transparent
    );
    transition: left 0.5s;
  }

  &:hover::before {
    left: 100%;
  }

  &:hover {
    background: linear-gradient(135deg, ${colors.freshGreen}, ${colors.olive1});
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(124, 179, 66, 0.4);
    border-color: ${colors.freshGreen};
  }
`;

// ===== Hero Content =====
const HeroContent = styled.main`
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin: 3rem auto 4rem;
  padding: 2.5rem 6vw 3rem;
  text-align: center;

  @media (max-width: 1100px) {
    padding-inline: 1.8rem;
  }
`;

const Badge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 20px;
  border-radius: 999px;
  background: linear-gradient(
    135deg,
    rgba(129, 199, 132, 0.2) 0%,
    rgba(255, 183, 77, 0.15) 100%
  );
  border: 1.5px solid rgba(129, 199, 132, 0.4);
  font-size: 0.95rem;
  font-weight: 600;
  color: ${colors.freshGreen};
  margin-bottom: 1.5rem;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(124, 179, 66, 0.2);
`;

const BadgeIcon = styled.span`
  font-size: 1.1rem;
  animation: ${float} 2.5s ease-in-out infinite;
`;

const Title = styled.h1`
  font-size: clamp(2.6rem, 5vw, 4rem);
  font-weight: 900;
  line-height: 1.1;
  margin: 0 0 0.5rem;
  background: linear-gradient(
    135deg,
    #ffffff 0%,
    #f1f8e9 50%,
    #ffffff 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  filter: drop-shadow(0 2px 8px rgba(56, 142, 60, 0.5))
    drop-shadow(0 4px 16px rgba(104, 159, 56, 0.3));
`;

const Subtitle = styled.p`
  font-size: 1.15rem;
  max-width: 50rem;
  margin: 0.3rem auto 0.5rem;
  color: #ffffff;
  font-weight: 500;
  line-height: 1.6;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2),
    0 4px 16px rgba(56, 142, 60, 0.3);
`;

// Buttons
const Actions = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  margin-top: 3rem;
  margin-bottom: 3rem;
`;

const Button = styled.button`
  border-radius: 999px;
  padding: 0.9rem 2rem;
  border: none;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;

  &::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
  }

  &:hover::before {
    width: 300px;
    height: 300px;
  }

  &:hover {
    transform: translateY(-3px) scale(1.05);
  }
`;

const PrimaryButton = styled(Button)`
  background: linear-gradient(
    135deg,
    ${colors.freshGreen} 0%,
    ${colors.olive1} 50%,
    ${colors.freshGreen} 100%
  );
  background-size: 200% 200%;
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(124, 179, 66, 0.4),
    0 4px 12px rgba(107, 145, 27, 0.3);

  &:hover {
    box-shadow: 0 12px 32px rgba(124, 179, 66, 0.5),
      0 6px 16px rgba(107, 145, 27, 0.4);
    animation: ${shimmer} 2s linear infinite;
  }
`;

const LightButton = styled(Button)`
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(255, 255, 255, 0.85) 100%
  );
  color: ${colors.freshGreen};
  border: 2px solid rgba(129, 199, 132, 0.6);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.3);

  &:hover {
    background: linear-gradient(
      135deg,
      rgba(241, 248, 233, 0.95) 0%,
      rgba(232, 245, 233, 0.9) 100%
    );
    border-color: ${colors.freshGreen};
    box-shadow: 0 12px 32px rgba(129, 199, 132, 0.4);
  }
`;

const FarmerButton = styled(Button)`
  background: linear-gradient(
    135deg,
    ${colors.sunGold} 0%,
    #FF9800 50%,
    ${colors.sunGold} 100%
  );
  background-size: 200% 200%;
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 24px rgba(255, 167, 38, 0.4);

  &:hover {
    box-shadow: 0 12px 32px rgba(255, 167, 38, 0.5);
    animation: ${shimmer} 2s linear infinite;
  }
`;

// Stats with enhanced design
const Stats = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 24px;
  margin-top: 2rem;
`;

const StatCard = styled.div`
  min-width: 130px;
  padding: 1rem 1.5rem;
  border-radius: 20px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(255, 255, 255, 0.85) 100%
  );
  border: 2px solid rgba(129, 199, 132, 0.4);
  box-shadow: 0 12px 32px rgba(124, 179, 66, 0.2),
    0 4px 12px rgba(129, 199, 132, 0.15);
  backdrop-filter: blur(12px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 16px 40px rgba(124, 179, 66, 0.3),
      0 8px 16px rgba(129, 199, 132, 0.2);
    border-color: ${colors.freshGreen};
  }
`;

const StatNumber = styled.span`
  display: block;
  font-size: 1.6rem;
  font-weight: 800;
  background: linear-gradient(135deg, ${colors.freshGreen}, ${colors.olive1});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const StatLabel = styled.span`
  font-size: 0.85rem;
  color: #5b6f35;
  font-weight: 600;
`;

// ===== Component =====

const Home = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [prevIndex, setPrevIndex] = useState(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Auto-slide background with smooth crossfade
  useEffect(() => {
    if (heroImages.length === 0) return;

    const interval = setInterval(() => {
      setIsTransitioning(true);
      setPrevIndex(currentIndex);
      
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % heroImages.length);
      }, 100);
      
      setTimeout(() => {
        setIsTransitioning(false);
        setPrevIndex(null);
      }, 1600);
    }, 4000);

    return () => clearInterval(interval);
  }, [currentIndex]);

  return (
    <HeroRoot>
      {/* Full-screen sliding background with crossfade */}
      <HeroBg>
        {heroImages.length > 0 && (
          <>
            {/* Previous image fading out */}
            {prevIndex !== null && isTransitioning && (
              <HeroBgImage
                className="exiting"
                src={heroImages[prevIndex]}
                alt={`farm-bg-${prevIndex}`}
              />
            )}
            {/* Current image fading in */}
            <HeroBgImage
              className={isTransitioning ? "entering" : "active"}
              src={heroImages[currentIndex]}
              alt={`farm-bg-${currentIndex}`}
            />
          </>
        )}
        <HeroBgOverlay />
      </HeroBg>

      {/* Top bar */}
      <HeroNav>
        <Logo>
          <LogoIcon>🌾</LogoIcon>
          <span>KissanAI</span>
        </Logo>
        <NavLinks>
          <NavLink to="/chat">Chat</NavLink>
          <NavLink to="/news">News</NavLink>
        </NavLinks>
      </HeroNav>

      {/* Center content */}
      <HeroContent>
        <Badge>
          <BadgeIcon>🧑‍🌾</BadgeIcon>
          Trusted by progressive farmers &amp; agri-startups
        </Badge>

        <Title>
          The AI Platform for Agriculture
        </Title>

        <Subtitle>
          Deploy intelligent agricultural features in weeks, not years – from
          multilingual advisory to visual crop analysis, built for real fields.
        </Subtitle>

        <Actions>
          <PrimaryButton>Schedule Demo</PrimaryButton>
          <LightButton>Explore Platform</LightButton>
          <FarmerButton>🌱 Farmers&apos; AI Agent</FarmerButton>
        </Actions>

        <Stats>
          <StatCard>
            <StatNumber>10K+</StatNumber>
            <StatLabel>Fields Analysed</StatLabel>
          </StatCard>
          <StatCard>
            <StatNumber>15+</StatNumber>
            <StatLabel>Crops Supported</StatLabel>
          </StatCard>
          <StatCard>
            <StatNumber>90%</StatNumber>
            <StatLabel>Farmer Satisfaction</StatLabel>
          </StatCard>
        </Stats>
      </HeroContent>
    </HeroRoot>
  );
};

export default Home;