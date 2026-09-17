import { FormEvent } from 'react'
import { Mood, MoodOption } from '@/types/music'

interface HeroProps {
  query: string
  onQueryChange: (query: string) => void
  activeMood: Mood
  onSelectMood: (mood: Mood) => void
  moods: MoodOption[]
}

export function Hero({
  query,
  onQueryChange,
  activeMood,
  onSelectMood,
  moods,
}: HeroProps) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
  }

  return (
    <section className="hero">
      <h1>FIND TRACKS BY SONIC DNA</h1>
      <form className="searchbar" onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search tracks..."
          aria-label="Search tracks"
        />
        <button type="submit">[ FIND ]</button>
      </form>
      <div className="moods">
        <span>MOODS:</span>
        {moods.map((item) => (
          <button
            type="button"
            key={item.name}
            className={`${item.className} ${
              activeMood === item.name ? 'mood-active' : ''
            }`}
            onClick={() => onSelectMood(item.name)}
          >
            [ {item.name} ]
          </button>
        ))}
      </div>
    </section>
  )
}
