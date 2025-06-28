// src/app/layout.tsx
"use client"; // Nodig voor de ThemeProvider

import React from 'react';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from '../context/ThemeContext';
import { GlobalStyle } from '../GlobalStyle'; // We maken dit bestand zo
import ScrollToTop from '../components/ScrollToTop';
import StyledComponentsRegistry from '../lib/registry';



export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="nl">
      <body>
        <ThemeProvider>
            <StyledComponentsRegistry>
              <GlobalStyle />
              <Toaster position="bottom-center" />
              {children}
              <ScrollToTop />
            </StyledComponentsRegistry>
        </ThemeProvider>
      </body>
    </html>
  )
}
