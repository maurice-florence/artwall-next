"use client";

import React, { useState, useEffect } from 'react';
import { auth } from '../firebase';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { useNavigate } from 'next/link';
import {
  FormWrapper,
  StyledForm,
  FormTitle,
  FormGroup,
  StyledLabel,
  StyledInput,
  StyledButton,
  BackToHomeLink,
} from '../components/Form.styles';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    if (auth.currentUser) {
      navigate('/admin');
    }
  }, [navigate]);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate('/admin');
    } catch (error) {
      if (error instanceof Error) {
        alert('Login mislukt: ' + error.message);
      } else {
        alert('Login mislukt: Onbekende fout');
      }
    }
  };

  return (
    <FormWrapper>
      <FormTitle>Inloggen</FormTitle>
      <StyledForm onSubmit={handleLogin}>
        <FormGroup>
          <StyledLabel htmlFor="email">E-mail</StyledLabel>
          <StyledInput
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </FormGroup>
        <FormGroup>
          <StyledLabel htmlFor="password">Wachtwoord</StyledLabel>
          <StyledInput
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </FormGroup>
        <StyledButton type="submit">Login</StyledButton>
      </StyledForm>
      <BackToHomeLink to="/">Terug naar tijdlijn</BackToHomeLink>
    </FormWrapper>
  );
};

export default LoginPage;
