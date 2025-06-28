export interface Artwork {
  id: string;
  title: string;
  year: number;
  month: number;
  day: number;
  category: 'poëzie' | 'proza' | 'sculptuur' | 'tekening' | 'muziek' | 'beeld' | 'video' | 'overig';
  description: string;
  mediaType?: 'text' | 'image' | 'audio';
  mediaUrl?: string;
  coverImageUrl?: string;
  soundcloudEmbedUrl?: string;
  soundcloudTrackUrl?: string;
  content?: string;
  lyrics?: string;
  chords?: string;
  isHidden?: boolean;
}
