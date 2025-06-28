import React from 'react';
import styled from 'styled-components';
import { FaBars } from 'react-icons/fa';
import LanguageSwitcher from './ThemeSwitcher';

const HeaderWrapper = styled.header`
  background: ${({ theme }) => theme.headerBg};
  color: ${({ theme }) => theme.headerText};
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Title = styled.h1`
  font-family: 'Lora', serif;
  font-size: 1.8rem;
  color: ${({ theme }) => theme.headerText};
  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.headerText};
  font-size: 1.5rem;
  cursor: pointer;
`;

type HeaderProps = {
  onToggleSidebar: () => void;
};

const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  return (
    <HeaderWrapper>
      <ToggleButton onClick={onToggleSidebar} title="Toggle Sidebar">
        <FaBars />
      </ToggleButton>
      <Title>Mijn Creatieve Tijdlijn</Title>
      <LanguageSwitcher /> {/* Assuming LanguageSwitcher is now ThemeSwitcher based on context */}
    </HeaderWrapper>
  );
};

export default Header;
