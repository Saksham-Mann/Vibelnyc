import { Mood, ClusterInfo } from '@/types/music'

/**
 * Props for the AlgorithmPanel component.
 */
interface AlgorithmPanelProps {
  /** Currently active mood preset. */
  mood: Mood
  /** Optional live cluster information returned by the ML backend. */
  clusterInfo?: ClusterInfo | null
}

/**
 * Technical aside panel illustrating the underlying vector geometry,
 * KMeans cluster assignment, and audio feature weighting sliders.
 *
 * @param props Contains active mood and optional cluster classification data.
 * @returns JSX Element rendering the algorithmic vector display.
 */
export function AlgorithmPanel({ mood, clusterInfo }: AlgorithmPanelProps) {
  const clusterLabel =
    clusterInfo?.cluster_name ||
    (mood === 'HIGH ENERGY'
      ? 'High Energy Club & Dance'
      : mood === 'CHILL'
      ? 'Chill Downtempo & Groove'
      : mood === 'POP'
      ? 'Mainstream Pop & Anthems'
      : 'Late Night Melancholic')

  const clusterIdText =
    clusterInfo !== undefined && clusterInfo !== null
      ? `#0${clusterInfo.cluster_id}`
      : '#07'

  return (
    <aside className="algorithm-panel">
      <h2>ALGORITHM</h2>
      <div className="vector-map">
        <svg
          viewBox="0 0 190 125"
          role="img"
          aria-label="Similarity vector diagram"
        >
          <line x1="82" y1="68" x2="85" y2="13" />
          <line x1="82" y1="68" x2="150" y2="84" />
          <line x1="82" y1="68" x2="35" y2="105" />
          <line x1="82" y1="68" x2="51" y2="42" />
          <line x1="82" y1="68" x2="129" y2="52" />
          <path d="M85 13l-5 10m5-10l6 9M150 84l-12-5m12 5l-12 3M35 105l9-11m-9 11l13-4M51 42l12 4m-12-4l5 12M129 52l-12 2m12-2l-6 8" />
        </svg>
      </div>

      <div className="algorithm-copy">
        Cosine Similarity &amp; K-Means
        <br />
        Cluster {clusterIdText}: {clusterLabel}
      </div>

      <div className="rule" />

      <h3>WEIGHTING:</h3>
      <div className="sliders">
        <div>
          <label>ENERGY</label>
          <i>
            <b style={{ left: '32%' }} />
          </i>
        </div>
        <div>
          <label>ACOUSTIC</label>
          <i>
            <b style={{ left: '66%' }} />
          </i>
        </div>
        <div>
          <label>DANCE</label>
          <i>
            <b style={{ left: '57%' }} />
          </i>
        </div>
      </div>
    </aside>
  )
}
