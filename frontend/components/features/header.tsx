import { Disc3 } from 'lucide-react'

/**
 * Props for the Header navigation component.
 */
interface HeaderProps {
  /** Optional indicator of whether the FastAPI backend is online. */
  isBackendConnected?: boolean
}

/**
 * Top navigation header component featuring the Vibelnyc brand identity,
 * internal navigation anchor, and live server connection status badge.
 *
 * @param props Component configuration options.
 * @returns JSX Element representing the topbar navigation.
 */
export function Header({ isBackendConnected = true }: HeaderProps) {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-disc">
          <Disc3 size={25} />
        </span>
        <strong>VIBELNYC</strong>
      </div>
      <nav>
        <a href="#algorithm">ALGORITHM</a>
        <button
          className="connected"
          style={{
            borderColor: isBackendConnected ? '#10b981' : '#f59e0b',
            color: isBackendConnected ? '#fff' : '#f59e0b',
          }}
        >
          <span
            style={{
              backgroundColor: isBackendConnected ? '#10b981' : '#f59e0b',
            }}
          />
          {isBackendConnected ? 'ML ENGINE ONLINE' : 'OFFLINE MODE (MOCK DATA)'}
        </button>
      </nav>
    </header>
  )
}
