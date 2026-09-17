'use client'

import { useMemo, useState } from 'react'
import { ArrowUpRight } from 'lucide-react'
import { Mood } from '@/types/music'
import { MOODS, MOCK_TRACKS, SEED_TRACK } from '@/data/mock-tracks'
import { Header } from '@/components/features/header'
import { Hero } from '@/components/features/hero'
import { AlbumArt } from '@/components/features/album-art'
import { Waveform } from '@/components/features/waveform'
import { TrackCard } from '@/components/features/track-card'
import { AlgorithmPanel } from '@/components/features/algorithm-panel'

export default function Page() {
  const [mood, setMood] = useState<Mood>('MELANCHOLY')
  const [query, setQuery] = useState('')

  const visibleTracks = useMemo(() => {
    const list = MOCK_TRACKS[mood] || []
    if (!query.trim()) return list
    const q = query.toLowerCase()
    return list.filter(
      (t) =>
        t.title.toLowerCase().includes(q) || t.artist.toLowerCase().includes(q)
    )
  }, [mood, query])

  return (
    <main className="app-shell">
      <Header />

      <Hero
        query={query}
        onQueryChange={setQuery}
        activeMood={mood}
        onSelectMood={setMood}
        moods={MOODS}
      />

      <section className="seed-card">
        <AlbumArt track={SEED_TRACK} />
        <div className="seed-info">
          <span>SEED TRACK</span>
          <strong>
            {SEED_TRACK.title} - {SEED_TRACK.artist}
          </strong>
        </div>
        <Waveform />
      </section>

      <div className="content-grid">
        <section className="recommendations">
          <h2>RECOMMENDED</h2>
          <div className="track-grid">
            {visibleTracks.map((track) => (
              <TrackCard track={track} key={`${track.artist}-${track.title}`} />
            ))}
          </div>
        </section>

        <div id="algorithm">
          <AlgorithmPanel mood={mood} />
        </div>
      </div>

      <footer>
        VIBELNYC <span>SONIC MATCHING ENGINE / 2026</span>
        <ArrowUpRight size={15} />
      </footer>
    </main>
  )
}
