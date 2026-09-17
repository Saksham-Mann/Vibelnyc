import { Track } from '@/types/music'

/**
 * Props for the AlbumArt component.
 */
interface AlbumArtProps {
  /** The track object containing title, artwork monogram code, and styling class. */
  track: Pick<Track, 'title' | 'art' | 'artClass'>
  /** Whether to render the compact thumbnail variant for track cards. */
  small?: boolean
}

/**
 * Renders stylized album artwork or visual monogram for seed and candidate tracks.
 *
 * @param props Component properties containing track artwork details.
 * @returns JSX Element displaying the styled album art block.
 */
export function AlbumArt({ track, small = false }: AlbumArtProps) {
  return (
    <div
      className={`album-art ${track.artClass || 'art-generic'} ${
        small ? 'album-small' : ''
      }`}
      aria-label={`${track.title} album art`}
    >
      <span>{track.art || 'VN'}</span>
    </div>
  )
}
