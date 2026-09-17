import { Disc3 } from 'lucide-react'

export function Header() {
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
        <button className="connected">
          <span /> SPOTIFY CONNECTED
        </button>
      </nav>
    </header>
  )
}
