/**
 * Props for the Metric progress bar component.
 */
interface MetricProps {
  /** Feature dimension label (e.g. 'ENG', 'VAL', 'DANCE'). */
  label: string
  /** Normalized percentage score between 0.0 and 100.0. */
  value: number
}

/**
 * Metric progress indicator component displaying an audio dimension label
 * alongside an animated horizontal bar reflecting the scalar intensity.
 *
 * @param props Label and normalized intensity value.
 * @returns JSX Element rendering the metric track bar.
 */
export function Metric({ label, value }: MetricProps) {
  const boundedValue = Math.min(100, Math.max(0, value))

  return (
    <div className="metric">
      <span>{label}</span>
      <div className="metric-track">
        <div style={{ width: `${boundedValue}%` }} />
      </div>
    </div>
  )
}
