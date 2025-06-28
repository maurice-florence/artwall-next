import React, { createContext, useState, useEffect, ReactNode } from 'react';

export type FiltersType = { category: string | string[]; year: string };
export interface FilterContextType {
  filters: FiltersType;
  setFilters: React.Dispatch<React.SetStateAction<FiltersType>>;
  saveFiltersAsDefault: () => void;
  resetFiltersToDefault: () => void;
}

export const FilterContext = createContext<FilterContextType | undefined>(undefined);

function isFiltersType(obj: any): obj is FiltersType {
  return (
    obj &&
    typeof obj === 'object' &&
    'category' in obj &&
    'year' in obj &&
    (typeof obj.category === 'string' || Array.isArray(obj.category)) &&
    typeof obj.year === 'string'
  );
}

export const FilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const getDefaultFilters = (): FiltersType => {
    const saved = localStorage.getItem('timelineDefaultFilters');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (isFiltersType(parsed)) return parsed;
      } catch {
        // ignore
      }
    }
    return { category: 'all', year: 'all' };
  };
  const [filters, setFilters] = useState<FiltersType>(() => {
    const saved = localStorage.getItem('timelineFilters');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (isFiltersType(parsed)) return parsed;
      } catch {
        // ignore
      }
    }
    return getDefaultFilters();
  });

  useEffect(() => {
    localStorage.setItem('timelineFilters', JSON.stringify(filters));
  }, [filters]);

  const saveFiltersAsDefault = () => {
    localStorage.setItem('timelineDefaultFilters', JSON.stringify(filters));
  };
  const resetFiltersToDefault = () => {
    const def = getDefaultFilters();
    setFilters(def);
  };

  return (
    <FilterContext.Provider
      value={{ filters, setFilters, saveFiltersAsDefault, resetFiltersToDefault }}
    >
      {children}
    </FilterContext.Provider>
  );
};

export const useFilter = () => {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error('useFilter must be used within FilterProvider');
  return ctx;
};

// Define types for view options
export type ViewOptionsType = {
  spacing: 'comfortabel' | 'compact';
  details: 'volledig' | 'samenvatting' | 'titels';
  layout: 'alternerend' | 'links' | 'rechts';
  theme: string;
  showEmptyYears: boolean;
  colorfulCategories: boolean;
  animatedTimeline: boolean;
};

export interface ViewOptionsContextType {
  viewOptions: ViewOptionsType;
  setViewOptions: React.Dispatch<React.SetStateAction<ViewOptionsType>>;
  saveViewOptionsAsDefault: () => void;
  resetViewOptionsToDefault: () => void;
}

export const ViewOptionsContext = createContext<ViewOptionsContextType | undefined>(undefined);

function isViewOptionsType(obj: any): obj is ViewOptionsType {
  return (
    obj &&
    typeof obj === 'object' &&
    'spacing' in obj &&
    'details' in obj &&
    'layout' in obj &&
    'theme' in obj &&
    'showEmptyYears' in obj &&
    'colorfulCategories' in obj &&
    'animatedTimeline' in obj &&
    (obj.spacing === 'comfortabel' || obj.spacing === 'compact') &&
    (obj.details === 'volledig' || obj.details === 'samenvatting' || obj.details === 'titels') &&
    (obj.layout === 'alternerend' || obj.layout === 'links' || obj.layout === 'rechts') &&
    typeof obj.theme === 'string' &&
    typeof obj.showEmptyYears === 'boolean' &&
    typeof obj.colorfulCategories === 'boolean' &&
    typeof obj.animatedTimeline === 'boolean'
  );
}

export const ViewOptionsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const getDefaultViewOptions = (): ViewOptionsType => {
    const saved = localStorage.getItem('timelineDefaultViewOptions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (isViewOptionsType(parsed)) return parsed;
      } catch {
        // ignore
      }
    }
    return {
      spacing: 'comfortabel',
      details: 'volledig',
      layout: 'alternerend',
      theme: 'atelier',
      showEmptyYears: false,
      colorfulCategories: true,
      animatedTimeline: true,
    };
  };
  const [viewOptions, setViewOptions] = useState<ViewOptionsType>(() => {
    const saved = localStorage.getItem('timelineViewOptions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (isViewOptionsType(parsed)) return parsed;
      } catch {
        // ignore
      }
    }
    return getDefaultViewOptions();
  });

  useEffect(() => {
    localStorage.setItem('timelineViewOptions', JSON.stringify(viewOptions));
  }, [viewOptions]);

  const saveViewOptionsAsDefault = () => {
    localStorage.setItem('timelineDefaultViewOptions', JSON.stringify(viewOptions));
  };
  const resetViewOptionsToDefault = () => {
    const def = getDefaultViewOptions();
    setViewOptions(def);
  };

  return (
    <ViewOptionsContext.Provider
      value={{ viewOptions, setViewOptions, saveViewOptionsAsDefault, resetViewOptionsToDefault }}
    >
      {children}
    </ViewOptionsContext.Provider>
  );
};

export const useViewOptions = () => {
  const ctx = useContext(ViewOptionsContext);
  if (!ctx) throw new Error('useViewOptions must be used within ViewOptionsProvider');
  return ctx;
};
