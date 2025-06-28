import React from 'react';
import styled from 'styled-components';
import { FaTimes, FaSoundcloud, FaShareAlt } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import { formatDate } from '../utils';
import { Artwork } from '../types';

const ModalBackdrop = styled.div.attrs({
  role: 'dialog',
  'aria-modal': true,
  'aria-label': 'Kunstwerk details',
})`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(61, 64, 91, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  padding: 1rem;
`;

const ModalContent = styled.div`
  background: ${({ theme }) => theme.cardBg};
  color: ${({ theme }) => theme.cardText};
  padding: 2rem 3rem;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);

  h2 {
    color: ${({ theme }) => theme.text};
  }

  @media (max-width: 600px) {
    padding: 1rem;
    max-width: 100vw;
    max-height: 95vh;
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: ${({ theme }) => theme.cardText};
  cursor: pointer;
  line-height: 1;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.2);
  }
`;

const MediaContainer = styled.div`
  width: 100%;
  margin-top: 1.5rem;
`;

const ModalImage = styled.img`
  width: 100%;
  height: auto;
  max-height: calc(85vh - 200px);
  object-fit: contain;
  border-radius: 4px;
`;

const PdfViewer = styled.iframe`
  width: 100%;
  height: 70vh;
  border: 1px solid #ddd;
  border-radius: 4px;
`;

const SoundCloudEmbed = styled.iframe`
  width: 100%;
  height: 166px;
  border: none;
  border-radius: 4px;
`;

const SoundCloudLinkButton = styled.a`
  display: inline-flex;
  align-self: flex-start;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #ff5500;
  color: white;
  text-decoration: none;
  font-weight: bold;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #cc4400;
  }
`;

const LyricsChordsSection = styled.div`
  background: ${({ theme }) => theme.body};
  color: ${({ theme }) => theme.text};
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  white-space: pre-wrap;
  font-family: monospace;
  max-height: 30vh;
  overflow-y: auto;
`;

const StyledHr = styled.hr`
  border: none;
  border-top: 1px solid #dddddd;
  margin: 1.5rem 0;
`;

const isMobile = window.innerWidth < 768;

type ModalProps = {
  item: Artwork;
  onClose: () => void;
};

const Modal: React.FC<ModalProps> = ({ item, onClose }) => {
  const formattedDateStr = formatDate(item);

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: item.title,
        text: item.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Link gekopieerd!');
    }
  };

  return (
    <ModalBackdrop onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <CloseButton onClick={onClose} aria-label="Sluit modal">
          <FaTimes />
        </CloseButton>
        <h2>{item.title}</h2>
        <p style={{ marginTop: '0.25rem', opacity: 0.8 }}>({formattedDateStr})</p>
        <p style={{ marginTop: '1rem', fontStyle: 'italic' }}>{item.description}</p>
        <StyledHr />

        <MediaContainer>
          {item.category === 'proza' && (
            <>
              {item.coverImageUrl && (
                <ModalImage
                  src={item.coverImageUrl}
                  alt={`Cover voor ${item.title}`}
                  style={{ marginBottom: '1rem' }}
                />
              )}
              {item.mediaUrl &&
                (isMobile ? (
                  <div style={{ color: '#888', fontStyle: 'italic', margin: '1rem 0' }}>
                    PDF alleen leesbaar op desktop.
                  </div>
                ) : (
                  <PdfViewer src={item.mediaUrl} title={`PDF voor ${item.title}`} />
                ))}
            </>
          )}

          {item.mediaType === 'image' && item.category !== 'proza' && (
            <ModalImage src={item.mediaUrl || '/logo192.png'} alt={item.title} loading="lazy" />
          )}

          {item.mediaType === 'audio' &&
            (item.soundcloudEmbedUrl ? (
              <SoundCloudEmbed
                scrolling="no"
                frameBorder="no"
                allow="autoplay"
                src={item.soundcloudEmbedUrl}
              ></SoundCloudEmbed>
            ) : (
              item.mediaUrl && (
                <audio controls src={item.mediaUrl} style={{ width: '100%' }}>
                  <track kind="captions" />
                  Your browser does not support the audio element.
                </audio>
              )
            ))}

          {item.mediaType === 'text' && (
            <div style={{ whiteSpace: 'pre-wrap' }}>
              <ReactMarkdown>{item.content || ''}</ReactMarkdown>
            </div>
          )}
        </MediaContainer>

        {item.soundcloudTrackUrl && (
          <SoundCloudLinkButton
            href={item.soundcloudTrackUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaSoundcloud size="1.5em" />
            <span>Luister op SoundCloud</span>
          </SoundCloudLinkButton>
        )}

        {item.lyrics && (
          <LyricsChordsSection>
            <h3>Songtekst / Extra Tekst</h3>
            <ReactMarkdown>{item.lyrics}</ReactMarkdown>
          </LyricsChordsSection>
        )}
        {item.chords && item.mediaType !== 'audio' && (
          <LyricsChordsSection>
            <h3>Akkoorden / Notities</h3>
            <p>{item.chords}</p>
          </LyricsChordsSection>
        )}

        <button onClick={handleShare} style={{ marginTop: 8 }}>
          <FaShareAlt /> Delen
        </button>
      </ModalContent>
    </ModalBackdrop>
  );
};

export default Modal;
