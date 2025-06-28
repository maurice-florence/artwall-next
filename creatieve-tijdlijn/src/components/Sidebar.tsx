import React, { useMemo, useContext, Dispatch, SetStateAction } from 'react';
import styled from 'styled-components';
import { StyledFilterSelect } from '../pages/HomePage.styles';
import { ThemeContext } from '../../../context/ThemeContext';
import { Artwork } from '../types';
import { FilterOptions, ViewOptions } from '../pages/HomePage';

type SidebarProps = {
  isOpen: boolean;
  allArtworks: Artwork[];
  filters: FilterOptions;
  setFilters: Dispatch<SetStateAction<FilterOptions>>;
  viewOptions: ViewOptions;
  setViewOptions: Dispatch<SetStateAction<ViewOptions>>;
  searchTerm: string;
  setSearchTerm: Dispatch<SetStateAction<string>>;
};

const SidebarContainer = styled.aside<{ $isOpen: boolean }>`
  width: 350px;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  background-color: ${({ theme }) => theme.cardBg};
  border-right: 1px solid #ddd;
  padding: 2rem;
  overflow-y: auto;
  transform: ${(props) => (props.$isOpen ? 'translateX(0)' : 'translateX(-100%)')};
  transition: transform 0.3s ease-in-out;
  z-index: 101;

  @media (max-width: 1024px) {
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }
`;

const SectionTitle = styled.h3`
  font-family: 'Lora', serif;
  color: ${({ theme }) => theme.accent};
  border-bottom: 2px solid ${({ theme }) => theme.accent};
  padding-bottom: 0.5rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
`;

const IntroText = styled.p`
  line-height: 1.7;
  color: ${({ theme }) => theme.text};
  font-size: 0.9rem;
`;

const OptionGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const OptionRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
`;

const ToggleButtonGroup = styled.div`
  display: flex;
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden;
`;

const ToggleButton = styled.button<{ $active: boolean }>`
  padding: 0.5rem 0.75rem;
  border: none;
  background-color: ${(props) => (props.$active ? props.theme.accent : 'transparent')};
  color: ${(props) => (props.$active ? props.theme.accentText : props.theme.text)};
  cursor: pointer;
  transition: background-color 0.2s;

  &:not(:last-child) {
    border-right: 1px solid #ccc;
  }
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
`;

const ThemeButton = styled.button<{ $active: boolean; color: string }>`
  width: 25px;
  height: 25px;
  border-radius: 50%;
  border: 2px solid ${(props) => (props.$active ? props.theme.accent : '#ccc')};
  cursor: pointer;
  background-color: ${(props) => props.color};
  transition: border-color 0.2s;
`;

const SearchInput = styled(StyledFilterSelect)``;

const Sidebar = ({
  isOpen,
  allArtworks,
  filters,
  setFilters,
  viewOptions,
  setViewOptions,
  searchTerm,
  setSearchTerm,
}: SidebarProps) => {
  const { toggleTheme } = useContext(ThemeContext);

  const availableYears = useMemo(() => {
    const years = new Set(allArtworks.map((art) => art.year));
    return Array.from(years).sort((a, b) => b - a);
  }, [allArtworks]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleViewOptionChange = (option: keyof ViewOptions, value: any) => {
    setViewOptions((prev) => ({ ...prev, [option]: value }));
  };

  return (
    <SidebarContainer $isOpen={isOpen}>
      <SectionTitle>Over Deze Site</SectionTitle>
      <IntroText>
        Welkom op mijn creatieve tijdlijn. Een persoonlijk archief van hersenspinsels, probeersels
        en creaties door de jaren heen.
      </IntroText>

      <SectionTitle>Filters</SectionTitle>
      <OptionGroup>
        <StyledFilterSelect name="category" value={filters.category} onChange={handleFilterChange}>
          <option value="all">Alle Categorieën</option>
          <option value="poëzie">Poëzie</option>
          <option value="proza">Proza</option>
          <option value="sculptuur">Sculptuur</option>
          <option value="tekening">Tekening</option>
          <option value="muziek">Muziek</option>
        </StyledFilterSelect>
        <StyledFilterSelect name="year" value={filters.year} onChange={handleFilterChange}>
          <option value="all">Alle Jaren</option>
          {availableYears.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </StyledFilterSelect>
        <SearchInput
          as="input"
          type="text"
          placeholder="Zoek op trefwoord..."
          value={searchTerm}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
        />
      </OptionGroup>

      <SectionTitle>Weergave Opties</SectionTitle>
      <OptionGroup>
        <OptionRow>
          <span>Afstand</span>
          <ToggleButtonGroup>
            <ToggleButton
              $active={viewOptions.spacing === 'compact'}
              onClick={() => handleViewOptionChange('spacing', 'compact')}
            >
              Compact
            </ToggleButton>
            <ToggleButton
              $active={viewOptions.spacing === 'comfortabel'}
              onClick={() => handleViewOptionChange('spacing', 'comfortabel')}
            >
              Comfortabel
            </ToggleButton>
          </ToggleButtonGroup>
        </OptionRow>
        <OptionRow>
          <span>Layout</span>
          <ToggleButtonGroup>
            <ToggleButton
              $active={viewOptions.layout === 'alternerend'}
              onClick={() => handleViewOptionChange('layout', 'alternerend')}
            >
              Alternerend
            </ToggleButton>
            <ToggleButton
              $active={viewOptions.layout === 'enkelzijdig'}
              onClick={() => handleViewOptionChange('layout', 'enkelzijdig')}
            >
              Enkelzijdig
            </ToggleButton>
          </ToggleButtonGroup>
        </OptionRow>
        <OptionRow>
          <span>Details</span>
          <ToggleButtonGroup>
            <ToggleButton
              $active={viewOptions.details === 'titels'}
              onClick={() => handleViewOptionChange('details', 'titels')}
            >
              Alleen Titels
            </ToggleButton>
            <ToggleButton
              $active={viewOptions.details === 'volledig'}
              onClick={() => handleViewOptionChange('details', 'volledig')}
            >
              Volledig
            </ToggleButton>
          </ToggleButtonGroup>
        </OptionRow>
        <OptionRow>
          <span>Animaties</span>
          <CheckboxLabel>
            <input
              type="checkbox"
              checked={viewOptions.animations}
              onChange={(e) => handleViewOptionChange('animations', e.target.checked)}
            />
            Aan
          </CheckboxLabel>
        </OptionRow>
        <OptionRow>
          <span>Thema</span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <ThemeButton
              color="#E07A5F"
              $active={viewOptions.theme === 'atelier'}
              onClick={() => {
                if (toggleTheme) toggleTheme('atelier');
                handleViewOptionChange('theme', 'atelier');
              }}
              title="Atelier Thema"
            />
            <ThemeButton
              color="#2E86C1"
              $active={viewOptions.theme === 'blueprint'}
              onClick={() => {
                if (toggleTheme) toggleTheme('blueprint');
                handleViewOptionChange('theme', 'blueprint');
              }}
              title="Blueprint Thema"
            />
            <ThemeButton
              color="#1E2732"
              $active={viewOptions.theme === 'dark'}
              onClick={() => {
                if (toggleTheme) toggleTheme('dark');
                handleViewOptionChange('theme', 'dark');
              }}
              title="Dark Mode"
            />
          </div>
        </OptionRow>
      </OptionGroup>
    </SidebarContainer>
  );
};

export default Sidebar;
