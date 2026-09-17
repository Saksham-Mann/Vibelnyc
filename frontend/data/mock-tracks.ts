/**
 * Fallback and test fixture mock data for Vibelnyc.
 * Used when the FastAPI recommendation backend is unavailable or during offline testing.
 */

import { Mood, MoodOption, Track } from '@/types/music'

/**
 * Predefined mood category filter buttons for UI navigation.
 */
export const MOODS: MoodOption[] = [
  { name: 'MELANCHOLY', className: 'mood-lavender' },
  { name: 'HIGH ENERGY', className: 'mood-yellow' },
  { name: 'CHILL', className: 'mood-white' },
  { name: 'POP', className: 'mood-green' },
]

/**
 * Fallback mock tracks indexed by mood preset.
 * Strictly used when the backend engine cannot be reached.
 */
export const MOCK_TRACKS: Record<Mood, Track[]> = {
  MELANCHOLY: [
    {
      title: 'Intro',
      artist: 'The xx',
      art: 'XX',
      artClass: 'art-xx',
      energy: 42,
      valence: 38,
      dance: 55,
      match: 98,
    },
    {
      title: 'Weird Fishes',
      artist: 'Radiohead',
      art: 'RF',
      artClass: 'art-fishes',
      energy: 62,
      valence: 44,
      dance: 58,
      match: 98,
    },
    {
      title: 'Unreve Fin',
      artist: 'Radiohead',
      art: 'RH',
      artClass: 'art-radiohead',
      energy: 58,
      valence: 35,
      dance: 50,
      match: 98,
    },
  ],
  'HIGH ENERGY': [
    {
      title: 'D.A.N.C.E.',
      artist: 'Justice',
      art: 'J',
      artClass: 'art-justice',
      energy: 91,
      valence: 76,
      dance: 88,
      match: 97,
    },
    {
      title: 'Go!',
      artist: 'The Chemical Brothers',
      art: 'CB',
      artClass: 'art-chem',
      energy: 94,
      valence: 72,
      dance: 93,
      match: 96,
    },
    {
      title: '1901',
      artist: 'Phoenix',
      art: 'PH',
      artClass: 'art-phoenix',
      energy: 83,
      valence: 79,
      dance: 86,
      match: 95,
    },
  ],
  CHILL: [
    {
      title: 'A Walk',
      artist: 'Tycho',
      art: 'TY',
      artClass: 'art-tycho',
      energy: 34,
      valence: 62,
      dance: 47,
      match: 97,
    },
    {
      title: 'Kerala',
      artist: 'Bonobo',
      art: 'BO',
      artClass: 'art-bonobo',
      energy: 49,
      valence: 57,
      dance: 67,
      match: 96,
    },
    {
      title: 'Open Eye Signal',
      artist: 'Jon Hopkins',
      art: 'JH',
      artClass: 'art-hopkins',
      energy: 51,
      valence: 48,
      dance: 60,
      match: 95,
    },
  ],
  POP: [
    {
      title: 'Electric Feel',
      artist: 'MGMT',
      art: 'MG',
      artClass: 'art-mgmt',
      energy: 78,
      valence: 84,
      dance: 81,
      match: 97,
    },
    {
      title: 'Midnight City',
      artist: 'M83',
      art: 'M83',
      artClass: 'art-m83',
      energy: 73,
      valence: 68,
      dance: 76,
      match: 96,
    },
    {
      title: 'Sweet Disposition',
      artist: 'The Temper Trap',
      art: 'TT',
      artClass: 'art-temp',
      energy: 69,
      valence: 77,
      dance: 70,
      match: 95,
    },
  ],
}

/**
 * Initial fallback seed track for cold-start rendering.
 */
export const SEED_TRACK: Track = {
  ...MOCK_TRACKS.MELANCHOLY[1],
  title: 'Midnight City',
  artist: 'M83',
}
