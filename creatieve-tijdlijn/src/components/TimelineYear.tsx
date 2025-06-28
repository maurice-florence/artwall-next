import React from 'react';
import { Artwork } from '../types';

interface TimelineYearProps {
  year: number | string;
  artworks: Artwork[];
  renderArtwork: (artwork: Artwork, index: number) => React.ReactNode;
}

const TimelineYear: React.FC<TimelineYearProps> = ({ year, artworks, renderArtwork }) => (
  <div>
    <h2>{year}</h2>
    {artworks.map(renderArtwork)}
  </div>
);

export default TimelineYear;
