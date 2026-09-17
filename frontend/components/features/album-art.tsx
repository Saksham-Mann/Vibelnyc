import { Track } from '@/types/music'

interface AlbumArtProps {
  track: Pick<Track, 'title' | 'art' | 'artClass'>
  small?: boolean
}

export function AlbumArt({ track, small = false }: AlbumArtProps) {
  return (
    <div
      className={`album-art ${track.artClass} ${small ? 'album-small' : ''}`}
      aria-label={`${track.title} album art`}
    >
      <span>{track.art}</span>
    </div>
  )
}
