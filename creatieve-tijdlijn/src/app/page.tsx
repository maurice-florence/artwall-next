"use client";

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'next/link';
import { db } from '../firebase';
import { ref, onValue, remove, update } from 'firebase/database';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { getStorage, ref as storageRef, deleteObject } from 'firebase/storage';
import {
  PageLayout,
  MainContent,
  TimelineContainer,
  YearHeader,
  TimelineEntry,
  TimelineDot,
  TimelineItemWrapper,
  ItemHeader,
  ItemCategory,
  ActionsContainer,
  CompactYearHeader,
  SkeletonCard,
  NoResultsMessage,
} from './HomePage.styles';
import {
  FaPenNib,
  FaPaintBrush,
  FaMusic,
  FaEdit,
  FaTrash,
  FaEye,
  FaEyeSlash,
  FaBookOpen,
} from 'react-icons/fa';
import Modal from '../components/Modal';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import toast from 'react-hot-toast';
import { Artwork } from '../types';
import TimelineYear from '../components/TimelineYear';

export interface FilterOptions {
  category: string;
  year: string;
}

export interface ViewOptions {
  spacing: 'compact' | 'comfortabel';
  layout: 'alternerend' | 'enkelzijdig';
  details: 'volledig' | 'titels';
  animations: boolean;
  theme: string;
}

const iconMap: { [key: string]: React.ReactElement } = {
  poëzie: <FaPenNib />,
  proza: <FaBookOpen />,
  sculptuur: <FaPaintBrush />,
  tekening: <FaPaintBrush />,
  muziek: <FaMusic />,
};

const HomePage: React.FC = () => {
  const [allArtworks, setAllArtworks] = useState<Artwork[]>([]);
  const [selectedItem, setSelectedItem] = useState<Artwork | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [isSidebarOpen, setSidebarOpen] = useState<boolean>(window.innerWidth > 1024);
  const [filters, setFilters] = useState<FilterOptions>(() => {
    const saved = localStorage.getItem('timelineFilters');
    return saved ? JSON.parse(saved) : { category: 'all', year: 'all' };
  });
  const [viewOptions, setViewOptions] = useState<ViewOptions>(() => {
    const saved = localStorage.getItem('timelineViewOptions');
    return saved
      ? JSON.parse(saved)
      : {
          spacing: 'comfortabel',
          layout: 'alternerend',
          details: 'volledig',
          animations: true,
          theme: 'atelier',
        };
  });
  const [searchTerm, setSearchTerm] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.setItem('timelineFilters', JSON.stringify(filters));
  }, [filters]);
  useEffect(() => {
    localStorage.setItem('timelineViewOptions', JSON.stringify(viewOptions));
  }, [viewOptions]);

  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => setIsAdmin(!!user));
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    const artworksRef = ref(db, 'artworks');
    const unsubscribe = onValue(artworksRef, (snapshot) => {
      const data = snapshot.val();
      const loadedArtworks: Artwork[] = data
        ? Object.entries(data).map(([id, value]) => ({ id, ...(value as Omit<Artwork, 'id'>) }))
        : [];
      setAllArtworks(loadedArtworks);
    });
    return () => unsubscribe();
  }, []);

  // Memoized filtered and grouped artworks
  const filteredArtworks = useMemo(() => {
    let result = allArtworks;
    if (filters.category && filters.category !== 'all') {
      result = result.filter((a) => a.category === filters.category);
    }
    if (filters.year && filters.year !== 'all') {
      result = result.filter((a) => String(a.year) === String(filters.year));
    }
    if (searchTerm) {
      result = result.filter((a) => a.title.toLowerCase().includes(searchTerm.toLowerCase()));
    }
    return result;
  }, [allArtworks, filters, searchTerm]);

  // Group by year
  const groupedByYear = useMemo(() => {
    const groups: { [year: string]: Artwork[] } = {};
    filteredArtworks.forEach((art) => {
      const year = String(art.year);
      if (!groups[year]) groups[year] = [];
      groups[year].push(art);
    });
    return groups;
  }, [filteredArtworks]);

  // Handlers
  const handleSidebarToggle = useCallback(() => setSidebarOpen((open) => !open), []);
  const handleFilterChange = useCallback((newFilters: FilterOptions) => setFilters(newFilters), []);
  const handleViewOptionsChange = useCallback(
    (newOptions: ViewOptions) => setViewOptions(newOptions),
    [],
  );
  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value),
    [],
  );

  // Render artwork item
  const renderArtwork = useCallback(
    (artwork: Artwork, idx: number) => (
      <TimelineItemWrapper key={artwork.id}>
        <ItemHeader $details={viewOptions.details}>
          <span>{artwork.title}</span>
          <ItemCategory category={artwork.category}>
            {iconMap[artwork.category] || null} {artwork.category}
          </ItemCategory>
        </ItemHeader>
        {/* ...other artwork details... */}
      </TimelineItemWrapper>
    ),
    [viewOptions.details],
  );

  return (
    <PageLayout>
      <Sidebar
        isOpen={isSidebarOpen}
        filters={filters}
        setFilters={setFilters}
        viewOptions={viewOptions}
        setViewOptions={setViewOptions}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        allArtworks={allArtworks}
      />
      <MainContent $isSidebarOpen={isSidebarOpen}>
        <Header onToggleSidebar={handleSidebarToggle} />
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearchChange}
          placeholder="Zoek op titel..."
        />
        <TimelineContainer>
          {Object.entries(groupedByYear).map(([year, artworks]) => (
            <div key={year}>
              <YearHeader>{year}</YearHeader>
              <TimelineYear year={year} artworks={artworks} renderArtwork={renderArtwork} />
            </div>
          ))}
          {filteredArtworks.length === 0 && (
            <NoResultsMessage>Geen resultaten gevonden.</NoResultsMessage>
          )}
        </TimelineContainer>
        <Footer />
      </MainContent>
      {selectedItem && <Modal item={selectedItem} onClose={() => setSelectedItem(null)} />}
    </PageLayout>
  );
};

export default HomePage;
