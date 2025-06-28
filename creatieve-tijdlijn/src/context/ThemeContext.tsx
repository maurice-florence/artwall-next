import React, { createContext, useState, ReactNode } from 'react';
import { atelierTheme, blueprintTheme, darkModeTheme, ThemeName, Theme } from '../themes';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';

// Definieer het type voor de waarde van de context
interface ThemeContextType {
  theme: ThemeName;
  toggleTheme: (themeName: ThemeName) => void;
}

// Geef een default waarde die overeenkomt met de interface
export const ThemeContext = createContext<ThemeContextType>({
  theme: 'atelier',
  toggleTheme: () => console.warn('no theme provider'),
});

const themes: Record<ThemeName, Theme> = {
  atelier: atelierTheme,
  blueprint: blueprintTheme,
  dark: darkModeTheme,
};

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [theme, setTheme] = useState<ThemeName>('atelier');

  const toggleTheme = (themeName: ThemeName) => {
    setTheme(themeName);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <StyledThemeProvider theme={themes[theme]}>{children}</StyledThemeProvider>
    </ThemeContext.Provider>
  );
};
