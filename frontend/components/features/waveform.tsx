export function Waveform() {
  const bars = Array.from({ length: 86 }, (_, index) => {
    const height = 8 + Math.abs(Math.sin(index * 1.7)) * 22 + (index % 7 === 0 ? 8 : 0)
    return <span key={index} style={{ height: `${height}px` }} />
  })

  return (
    <div className="waveform" aria-label="Audio waveform">
      {bars}
    </div>
  )
}
