export type Mood = 'MELANCHOLY' | 'HIGH ENERGY' | 'CHILL' | 'POP'

export interface MoodOption {
  name: Mood
  className: string
}

export interface Track {
  title: string
  artist: string
  art: string
  artClass: string
  energy: number
  valence: number
  dance: number
  match: number
}

export interface MetricData {
  label: string
  value: number
}
