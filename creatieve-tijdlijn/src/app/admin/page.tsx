"use client";

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'next/link';
import { db, storage, auth } from '../firebase';
import { ref as dbRef, push, set, update } from 'firebase/database';
import { ref as storageRef, uploadBytes, getDownloadURL } from 'firebase/storage';
import { signOut } from 'firebase/auth';
import {
  FormWrapper,
  StyledForm,
  FormTitle,
  FormGroup,
  StyledLabel,
  StyledInput,
  StyledSelect,
  StyledTextarea,
  StyledButton,
  BackToHomeLink,
} from '../components/Form.styles';
import toast from 'react-hot-toast';
import { CATEGORIES, CATEGORY_LABELS } from '../constants';
import { Artwork } from '../types';

const AdminPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const artworkToEdit = location.state?.artworkToEdit as Artwork | undefined;

  // State voor alle velden
  const [title, setTitle] = useState<string>('');
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);
  const [day, setDay] = useState<number>(new Date().getDate());
  const [category, setCategory] = useState<Artwork['category']>('poëzie');
  const [description, setDescription] = useState<string>('');
  const [mediaType, setMediaType] = useState<Artwork['mediaType']>('text');
  const [content, setContent] = useState<string>('');
  const [lyrics, setLyrics] = useState<string>('');
  const [chords, setChords] = useState<string>('');
  const [soundcloudEmbedUrl, setSoundcloudEmbedUrl] = useState<string>('');
  const [soundcloudTrackUrl, setSoundcloudTrackUrl] = useState<string>('');
  const [isHidden, setIsHidden] = useState<boolean>(false);
  const [file, setFile] = useState<File | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (artworkToEdit) {
      setTitle(artworkToEdit.title);
      setYear(artworkToEdit.year);
      setMonth(artworkToEdit.month || 1);
      setDay(artworkToEdit.day || 1);
      setCategory(artworkToEdit.category);
      setDescription(artworkToEdit.description || '');
      setMediaType(artworkToEdit.mediaType || 'text');
      setContent(artworkToEdit.content || '');
      setLyrics(artworkToEdit.lyrics || '');
      setChords(artworkToEdit.chords || '');
      setSoundcloudEmbedUrl(artworkToEdit.soundcloudEmbedUrl || '');
      setSoundcloudTrackUrl(artworkToEdit.soundcloudTrackUrl || '');
      setIsHidden(artworkToEdit.isHidden || false);
    }
  }, [artworkToEdit]);

  const handleLogout = async (): Promise<void> => {
    try {
      await signOut(auth);
      navigate('/login');
    } catch (error: any) {
      toast.error('Uitloggen mislukt: ' + error.message);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsLoading(true);

    let artworkData: Partial<Artwork> = {
      title,
      year: Number(year),
      month: Number(month),
      day: Number(day),
      category,
      description,
      mediaType,
      content,
      lyrics,
      chords,
      soundcloudEmbedUrl,
      soundcloudTrackUrl,
      isHidden,
      mediaUrl: artworkToEdit?.mediaUrl || '',
      coverImageUrl: artworkToEdit?.coverImageUrl || '',
    };

    try {
      if (file && category !== 'proza') {
        const fileRef = storageRef(storage, `${category}/${Date.now()}_${file.name}`);
        await uploadBytes(fileRef, file);
        artworkData.mediaUrl = await getDownloadURL(fileRef);
      }

      if (category === 'proza') {
        if (file) {
          const pdfRef = storageRef(storage, `proza/pdf/${Date.now()}_${file.name}`);
          await uploadBytes(pdfRef, file);
          artworkData.mediaUrl = await getDownloadURL(pdfRef);
        }
        if (coverFile) {
          const coverRef = storageRef(storage, `proza/covers/${Date.now()}_${coverFile.name}`);
          await uploadBytes(coverRef, coverFile);
          artworkData.coverImageUrl = await getDownloadURL(coverRef);
        }
      }

      if (artworkToEdit) {
        await update(dbRef(db, 'artworks/' + artworkToEdit.id), artworkData);
        toast.success('Kunstwerk succesvol bijgewerkt!');
      } else {
        await set(push(dbRef(db, 'artworks')), artworkData);
        toast.success('Kunstwerk succesvol toegevoegd!');
      }
      navigate('/');
    } catch (error: any) {
      toast.error('Er is een fout opgetreden: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <FormWrapper>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
        }}
      >
        <FormTitle>{artworkToEdit ? 'Kunstwerk Bewerken' : 'Nieuw Kunstwerk'}</FormTitle>
        <button
          type="button"
          onClick={handleLogout}
          style={{
            background: 'none',
            border: 'none',
            color: '#E07A5F',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          Uitloggen
        </button>
      </div>
      <StyledForm onSubmit={handleSubmit}>
        <FormGroup>
          <StyledLabel htmlFor="title">Titel</StyledLabel>
          <StyledInput
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </FormGroup>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <FormGroup style={{ flex: 1 }}>
            <StyledLabel htmlFor="day">Dag</StyledLabel>
            <StyledInput
              id="day"
              type="number"
              min="1"
              max="31"
              value={day}
              onChange={(e) => setDay(Number(e.target.value))}
            />
          </FormGroup>
          <FormGroup style={{ flex: 1 }}>
            <StyledLabel htmlFor="month">Maand</StyledLabel>
            <StyledInput
              id="month"
              type="number"
              min="1"
              max="12"
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              required
            />
          </FormGroup>
          <FormGroup style={{ flex: 2 }}>
            <StyledLabel htmlFor="year">Jaartal</StyledLabel>
            <StyledInput
              id="year"
              type="number"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              required
            />
          </FormGroup>
        </div>

        <FormGroup>
          <StyledLabel htmlFor="category">Categorie</StyledLabel>
          <StyledSelect
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value as Artwork['category'])}
            disabled={!!artworkToEdit}
          >
            <option value="">Kies een categorie...</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {CATEGORY_LABELS[cat as keyof typeof CATEGORY_LABELS]}
              </option>
            ))}
          </StyledSelect>
        </FormGroup>

        {/* Alleen tonen als categorie gekozen of bij bewerken */}
        {!!category && (
          <>
            {/* Dynamische velden per categorie */}
            {category === 'poëzie' && (
              <FormGroup>
                <StyledLabel htmlFor="content">Gedicht / Tekst</StyledLabel>
                <StyledTextarea
                  id="content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={10}
                ></StyledTextarea>
                <small>U kunt *italic* en **bold** gebruiken (Markdown).</small>
              </FormGroup>
            )}

            {category === 'proza' && (
              <>
                <FormGroup>
                  <StyledLabel htmlFor="pdfFile">PDF Bestand (.pdf)</StyledLabel>
                  <StyledInput
                    id="pdfFile"
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </FormGroup>
                <FormGroup>
                  <StyledLabel htmlFor="coverFile">Cover Afbeelding (.jpg, .png)</StyledLabel>
                  <StyledInput
                    id="coverFile"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setCoverFile(e.target.files?.[0] || null)}
                  />
                </FormGroup>
              </>
            )}

            {category === 'muziek' && (
              <>
                <FormGroup>
                  <StyledLabel htmlFor="file">Audio Uploaden (mp3, wav, etc)</StyledLabel>
                  <StyledInput
                    id="file"
                    type="file"
                    accept="audio/*"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </FormGroup>
                <FormGroup>
                  <StyledLabel htmlFor="lyrics">Songtekst</StyledLabel>
                  <StyledTextarea
                    id="lyrics"
                    value={lyrics}
                    onChange={(e) => setLyrics(e.target.value)}
                    rows={6}
                  ></StyledTextarea>
                </FormGroup>
                <FormGroup>
                  <StyledLabel htmlFor="chords">Akkoorden / Notities</StyledLabel>
                  <StyledTextarea
                    id="chords"
                    value={chords}
                    onChange={(e) => setChords(e.target.value)}
                    rows={4}
                  ></StyledTextarea>
                </FormGroup>
                <FormGroup>
                  <StyledLabel htmlFor="soundcloudEmbedUrl">SoundCloud Embed URL</StyledLabel>
                  <StyledInput
                    id="soundcloudEmbedUrl"
                    type="url"
                    value={soundcloudEmbedUrl}
                    onChange={(e) => setSoundcloudEmbedUrl(e.target.value)}
                    placeholder="https://w.soundcloud.com/player/..."
                  />
                </FormGroup>
                <FormGroup>
                  <StyledLabel htmlFor="soundcloudTrackUrl">SoundCloud Track URL</StyledLabel>
                  <StyledInput
                    id="soundcloudTrackUrl"
                    type="url"
                    value={soundcloudTrackUrl}
                    onChange={(e) => setSoundcloudTrackUrl(e.target.value)}
                    placeholder="https://soundcloud.com/user/track"
                  />
                </FormGroup>
              </>
            )}

            {category === 'beeld' && (
              <FormGroup>
                <StyledLabel htmlFor="file">Afbeelding Uploaden</StyledLabel>
                <StyledInput
                  id="file"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
              </FormGroup>
            )}

            {category === 'video' && (
              <>
                <FormGroup>
                  <StyledLabel htmlFor="file">Video Uploaden (mp4, webm)</StyledLabel>
                  <StyledInput
                    id="file"
                    type="file"
                    accept="video/mp4,video/webm"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </FormGroup>
                <FormGroup>
                  <StyledLabel htmlFor="videoUrl">YouTube/Vimeo Link (optioneel)</StyledLabel>
                  <StyledInput
                    id="videoUrl"
                    type="url"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="https://youtu.be/... of https://vimeo.com/..."
                  />
                </FormGroup>
              </>
            )}

            {category === 'overig' && (
              <FormGroup>
                <StyledLabel htmlFor="file">Bestand Uploaden (alles toegestaan)</StyledLabel>
                <StyledInput
                  id="file"
                  type="file"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
              </FormGroup>
            )}

            <FormGroup>
              <StyledLabel htmlFor="description">
                Korte Beschrijving (zichtbaar op tijdlijn)
              </StyledLabel>
              <StyledTextarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </FormGroup>

            {category !== 'proza' && (
              <FormGroup>
                <StyledLabel htmlFor="mediaType">Media Type</StyledLabel>
                <StyledSelect
                  id="mediaType"
                  value={mediaType}
                  onChange={(e) => setMediaType(e.target.value as Artwork['mediaType'])}
                >
                  <option value="text">Lange Tekst</option>
                  <option value="image">Beeld</option>
                  <option value="audio">Audio</option>
                </StyledSelect>
              </FormGroup>
            )}

            <FormGroup
              style={{ flexDirection: 'row', alignItems: 'center', gap: '10px', marginTop: '1rem' }}
            >
              <StyledInput
                type="checkbox"
                id="isHidden"
                checked={isHidden}
                onChange={(e) => setIsHidden(e.target.checked)}
                style={{ width: 'auto' }}
              />
              <StyledLabel htmlFor="isHidden" style={{ marginBottom: 0, fontWeight: 'normal' }}>
                Verberg dit item op de tijdlijn
              </StyledLabel>
            </FormGroup>
          </>
        )}

        <StyledButton type="submit" disabled={isLoading} style={{ marginTop: '1rem' }}>
          {isLoading ? 'Opslaan...' : artworkToEdit ? 'Wijzigingen Opslaan' : 'Kunstwerk Opslaan'}
        </StyledButton>
      </StyledForm>
      <BackToHomeLink to="/">← Terug naar de tijdlijn</BackToHomeLink>
    </FormWrapper>
  );
};

export default AdminPage;
