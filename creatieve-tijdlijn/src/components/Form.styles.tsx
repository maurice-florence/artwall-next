import styled from 'styled-components';
import { Link } from 'next/link';

// Een wrapper die het formulier mooi in het midden van de pagina zet
export const FormWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
`;

// Het formulier zelf, als een 'kaart'
export const StyledForm = styled.form`
  width: 100%;
  max-width: 500px;
  padding: 2.5rem;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
`;

// De titel van het formulier
export const FormTitle = styled.h2`
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
`;

// Een groep voor een label en zijn input
export const FormGroup = styled.div`
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
`;

// Het label voor een inputveld
export const StyledLabel = styled.label`
  margin-bottom: 0.5rem;
  font-weight: bold;
  font-size: 0.9rem;
`;

// Gedeelde stijlen voor input, select en textarea
const inputStyles = `
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 4px;
  border: 1px solid #DDDDDD;
  background: #F8F7F2;
  font-family: 'Nunito Sans', sans-serif;
  font-size: 1rem;
  color: #3D405B;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #1E3A8A; // Inkt Blauw
  }
`;

// De specifieke componenten
export const StyledInput = styled.input`
  ${inputStyles}
`;
export const StyledSelect = styled.select`
  ${inputStyles}
`;
export const StyledTextarea = styled.textarea`
  ${inputStyles}
  min-height: 120px;
  resize: vertical;
`;

// De primaire actieknop
export const StyledButton = styled.button`
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 4px;
  background: #1e3a8a; // Inkt Blauw
  color: #ffffff;
  font-family: 'Nunito Sans', sans-serif;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #3d405b; // Leisteen Grijs
  }
`;

export const BackToHomeLink = styled(Link)`
  display: block;
  text-align: center;
  margin-top: 1.5rem;
  color: #e07a5f; /* Zandsteen */
  text-decoration: none;
  font-weight: bold;

  &:hover {
    text-decoration: underline;
  }
`;
