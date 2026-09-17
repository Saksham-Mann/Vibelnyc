import { FormEvent, useRef, useState, useEffect } from 'react'
import { Mood, MoodOption, SearchResultItem } from '@/types/music'

/**
 * Props for the Hero component.
 */
interface HeroProps {
  /** Current search input value. */
  query: string
  /** Callback fired when the search input changes. */
  onQueryChange: (query: string) => void
  /** Callback fired when the user submits a search query. */
  onSearchSubmit: (trackName: string, artistName?: string) => void
  /** Autocomplete suggestion results. */
  suggestions?: SearchResultItem[]
  /** Whether a search operation is currently pending. */
  isSearching?: boolean
  /** Currently active mood preset. */
  activeMood: Mood
  /** Callback fired when a mood preset button is clicked. */
  onSelectMood: (mood: Mood) => void
  /** List of available mood options with display styles. */
  moods: MoodOption[]
}

/**
 * Hero section component providing search input, autocomplete combobox, and mood filter toggles.
 *
 * @param props Component configuration options.
 * @returns JSX Element rendering the Hero search and mood navigation block.
 */
export function Hero({
  query,
  onQueryChange,
  onSearchSubmit,
  suggestions = [],
  isSearching = false,
  activeMood,
  onSelectMood,
  moods,
}: HeroProps) {
  const [showDropdown, setShowDropdown] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    setShowDropdown(false)
    if (query.trim()) {
      onSearchSubmit(query.trim())
    }
  }

  const handleSelectSuggestion = (item: SearchResultItem) => {
    onQueryChange(item.track_name)
    setShowDropdown(false)
    onSearchSubmit(item.track_name, item.artists)
  }

  return (
    <section className="hero">
      <h1>FIND TRACKS BY SONIC DNA</h1>

      <div
        ref={containerRef}
        style={{ position: 'relative', width: '100%', maxWidth: '640px' }}
      >
        <form className="searchbar" onSubmit={handleSubmit}>
          <input
            value={query}
            onChange={(event) => {
              onQueryChange(event.target.value)
              setShowDropdown(true)
            }}
            onFocus={() => {
              if (suggestions.length > 0) setShowDropdown(true)
            }}
            placeholder="Search tracks or artists (e.g. Creep, Midnight City)..."
            aria-label="Search tracks"
            disabled={isSearching}
          />
          <button type="submit" disabled={isSearching || !query.trim()}>
            {isSearching ? '[ MATCHING... ]' : '[ FIND ]'}
          </button>
        </form>

        {showDropdown && suggestions.length > 0 && (
          <ul
            className="search-suggestions"
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              marginTop: '4px',
              backgroundColor: '#0a0a0a',
              border: '2px solid #ffffff',
              zIndex: 50,
              listStyle: 'none',
              padding: 0,
              maxHeight: '260px',
              overflowY: 'auto',
            }}
          >
            {suggestions.map((item) => (
              <li
                key={item.track_id}
                onClick={() => handleSelectSuggestion(item)}
                style={{
                  padding: '10px 14px',
                  cursor: 'pointer',
                  borderBottom: '1px solid #222',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = '#1a1a1a')
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = '#0a0a0a')
                }
              >
                <div>
                  <strong style={{ display: 'block', color: '#fff' }}>
                    {item.track_name}
                  </strong>
                  <span style={{ fontSize: '0.8rem', color: '#888' }}>
                    {item.artists}
                  </span>
                </div>
                <span
                  style={{
                    fontSize: '0.75rem',
                    color: '#ffdd00',
                    fontWeight: 700,
                  }}
                >
                  POP {item.popularity}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

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
