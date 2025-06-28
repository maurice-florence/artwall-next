import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Link } from 'next/link';
import { db } from '../firebase';
import { ref, onValue } from 'firebase/database';
import { getAuth, onAuthStateChanged } from 'firebase/auth';

const FooterWrapper = styled.footer`
  text-align: center;
  padding: 3rem 2rem 2rem;
  margin-top: 4rem;
  border-top: 1px solid #dddddd;
  background-color: ${({ theme }) => theme.cardBg};
  color: ${({ theme }) => theme.cardText};
`;

const FooterNav = styled.nav`
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
  gap: 2rem;
`;

const FooterLink = styled(Link)`
  color: ${({ theme }) => theme.text};
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;

  &:hover {
    color: ${({ theme }) => theme.accent};
    text-decoration: underline;
  }
`;

const LastUpdatedText = styled.p`
  font-size: 0.8rem;
  color: #999;
`;

const Footer: React.FC = () => {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    const artworksRef = ref(db, 'artworks');
    onValue(artworksRef, (snapshot) => {
      setLastUpdated(new Date());
    });
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => setIsAdmin(!!user));
    return () => unsubscribe();
  }, []);

  return (
    <FooterWrapper>
      <FooterNav>
        <FooterLink to="/">Tijdlijn</FooterLink>
        <FooterLink to="/stats">Statistieken</FooterLink>
        <FooterLink to="/login">Admin Login</FooterLink>
        {isAdmin && (
          <>
            <a
              href="https://console.firebase.google.com/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#E07A5F', fontWeight: 'bold' }}
            >
              Firebase Storage
            </a>
            <a
              href="https://console.firebase.google.com/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#E07A5F', fontWeight: 'bold' }}
            >
              Firebase Database
            </a>
          </>
        )}
      </FooterNav>
      {lastUpdated && (
        <LastUpdatedText>
          Laatst bijgewerkt: {lastUpdated.toLocaleDateString('nl-NL')}
        </LastUpdatedText>
      )}
    </FooterWrapper>
  );
};

export default Footer;
