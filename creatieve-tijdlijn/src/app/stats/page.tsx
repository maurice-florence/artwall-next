"use client";

import React, { useMemo } from 'react';
import { useArtworks } from '../context/ArtworksContext';
import { PageWrapper, StatGrid, StatCard, StatTitle, StatValue } from './StatsPage.styles';

const StatsPage: React.FC = () => {
  const { artworks: allArtworks } = useArtworks();

  const stats = useMemo(() => {
    if (allArtworks.length === 0) return null;

    const total = allArtworks.length;
    const counts: Record<string, number> = allArtworks.reduce(
      (acc, art) => {
        acc[art.category] = (acc[art.category] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    const first = [...allArtworks].sort((a, b) => a.year - b.year)[0];
    const last = [...allArtworks].sort((a, b) => b.year - a.year)[0];

    return {
      total,
      counts,
      first: first ? `${first.title} (${first.year})` : 'N/A',
      last: last ? `${last.title} (${last.year})` : 'N/A',
    };
  }, [allArtworks]);

  if (!stats) return <PageWrapper>Geen data beschikbaar.</PageWrapper>;

  return (
    <PageWrapper>
      <h2>Statistieken</h2>
      <StatGrid>
        <StatCard>
          <StatTitle>Totaal aantal werken</StatTitle>
          <StatValue>{stats.total}</StatValue>
        </StatCard>
        {Object.entries(stats.counts).map(([cat, count]) => (
          <StatCard key={cat}>
            <StatTitle>{cat}</StatTitle>
            <StatValue>{count}</StatValue>
          </StatCard>
        ))}
        <StatCard>
          <StatTitle>Eerste werk</StatTitle>
          <StatValue>{stats.first}</StatValue>
        </StatCard>
        <StatCard>
          <StatTitle>Laatste werk</StatTitle>
          <StatValue>{stats.last}</StatValue>
        </StatCard>
      </StatGrid>
    </PageWrapper>
  );
};

export default StatsPage;

// No useState hooks in this file that require explicit typing.
