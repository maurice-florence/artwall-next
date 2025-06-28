export const atelierTheme = {
  body: '#F8F7F2',
  text: '#3D405B',
  headerBg: '#3D405B',
  headerText: '#F8F7F2',
  accent: '#E07A5F',
  accentText: '#FFFFFF',
  cardBg: '#FFFFFF',
  cardText: '#3D405B',
  categories: {
    muziek: '#D94A4A',
    poëzie: '#2E86C1',
    proza: '#28B463',
    sculptuur: '#AF601A',
    tekening: '#884EA0',
  },
};

export const blueprintTheme = {
  body: '#EAF2F8',
  text: '#17202A',
  headerBg: '#2E86C1',
  headerText: '#FFFFFF',
  accent: '#1F618D',
  accentText: '#FFFFFF',
  cardBg: '#FFFFFF',
  cardText: '#17202A',
  categories: {
    muziek: '#C0392B',
    poëzie: '#2980B9',
    proza: '#27AE60',
    sculptuur: '#D35400',
    tekening: '#8E44AD',
  },
};

export const darkModeTheme = {
  body: '#17202A',
  text: '#EAF2F8',
  headerBg: '#000000',
  headerText: '#EAF2F8',
  accent: '#BB86FC',
  accentText: '#000000',
  cardBg: '#1E2732',
  cardText: '#EAF2F8',
  categories: {
    muziek: '#CF6679',
    poëzie: '#74B9FF',
    proza: '#55E6C1',
    sculptuur: '#FFB74D',
    tekening: '#BA68C8',
  },
};

// We export the themes so they can be used in the application
export const themes = {
  atelier: atelierTheme,
  blueprint: blueprintTheme,
  dark: darkModeTheme,
};

// EXPORTEER HET TYPE VAN ONS THEMA-OBJECT
export type Theme = typeof atelierTheme;
export type ThemeName = 'atelier' | 'blueprint' | 'dark';
