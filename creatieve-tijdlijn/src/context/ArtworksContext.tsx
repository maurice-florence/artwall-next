import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { db } from '../firebase';
import { ref, onValue } from 'firebase/database';
import { Artwork } from '../app/types';

interface ArtworksContextType {
  artworks: Artwork[];
  isLoading: boolean;
}

const ArtworksContext = createContext<ArtworksContextType>({ artworks: [], isLoading: true });

export const useArtworks = () => useContext(ArtworksContext);

export const ArtworksProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const artworksRef = ref(db, 'artworks');
    const unsubscribe = onValue(artworksRef, (snapshot) => {
      const data = snapshot.val();
      const loadedArtworks: Artwork[] = data
        ? Object.entries(data).map(([id, value]) => ({ id, ...(value as Omit<Artwork, 'id'>) }))
        : [];
      setArtworks(loadedArtworks);
      setIsLoading(false);
    });
    return () => unsubscribe();
  }, []);

  return (
    <ArtworksContext.Provider value={{ artworks, isLoading }}>{children}</ArtworksContext.Provider>
  );
};
