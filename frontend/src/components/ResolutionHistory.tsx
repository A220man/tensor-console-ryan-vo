import { useEffect, useState, useCallback } from 'react'
import { fetchResolutionHistory, type ResolutionHistoryEntry } from '../api/client'

interface ResolutionHistoryProps {
  onResolve?: () => void
}

export function ResolutionHistory({ onResolve }: ResolutionHistoryProps) {
  const [history, setHistory] = useState<ResolutionHistoryEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadHistory = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchResolutionHistory(undefined, 50, 0)
      // Ensure data is an array
      if (Array.isArray(data)) {
        setHistory(data)
      } else {
        setHistory([])
        setError('Unexpected response format')
      }
    } catch (err) {
      setHistory([])
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  useEffect(() => {
    if (onResolve) {
      loadHistory()
    }
  }, [onResolve, loadHistory])

  const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleString()
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <h3 style={styles.title}>Resolution History</h3>
        <p style={styles.loading}>Loading history...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.container}>
        <h3 style={styles.title}>Resolution History</h3>
        <p style={styles.error}>Error: {error}</p>
        <button style={styles.retryButton} onClick={loadHistory}>Retry</button>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Resolution History</h3>
      {history.length === 0 ? (
        <p style={styles.empty}>No resolution history yet. Resolve a model to see it here.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Timestamp</th>
              <th style={styles.th}>Region</th>
              <th style={styles.th}>Requested Model</th>
              <th style={styles.th}>Resolved Model</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Prefix</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry) => (
              <tr key={entry.id} style={styles.tr}>
                <td style={styles.td}>{formatTimestamp(entry.created_at)}</td>
                <td style={styles.td}>{entry.region}</td>
                <td style={styles.td}>{entry.requested_model}</td>
                <td style={styles.td}>{entry.resolved_model}</td>
                <td style={styles.td}>
                  <span style={entry.is_inference_profile ? styles.profileBadge : styles.onDemandBadge}>
                    {entry.is_inference_profile ? 'Inference Profile' : 'On-Demand'}
                  </span>
                </td>
                <td style={styles.td}>{entry.prefix_used}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginTop: 'var(--spacing-lg)',
  },
  title: {
    fontSize: '1.125rem',
    fontWeight: 600,
    marginBottom: 'var(--spacing-md)',
  },
  loading: {
    color: 'var(--color-fg-muted)',
  },
  error: {
    color: 'var(--color-error)',
  },
  retryButton: {
    marginTop: 'var(--spacing-sm)',
    padding: 'var(--spacing-xs) var(--spacing-md)',
    backgroundColor: 'var(--color-accent)',
    color: 'var(--color-bg)',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer',
  },
  empty: {
    color: 'var(--color-fg-muted)',
    fontStyle: 'italic',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '0.875rem',
  },
  th: {
    textAlign: 'left',
    padding: 'var(--spacing-sm) var(--spacing-md)',
    borderBottom: '2px solid var(--color-border)',
    fontWeight: 600,
    color: 'var(--color-fg-muted)',
  },
  td: {
    padding: 'var(--spacing-sm) var(--spacing-md)',
    borderBottom: '1px solid var(--color-border)',
  },
  tr: {
    transition: 'background-color 0.15s',
  },
  profileBadge: {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 'var(--radius-sm)',
    backgroundColor: 'var(--color-accent)',
    color: 'var(--color-bg)',
    fontSize: '0.75rem',
    fontWeight: 500,
  },
  onDemandBadge: {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: 'var(--radius-sm)',
    backgroundColor: 'var(--color-success)',
    color: 'var(--color-bg)',
    fontSize: '0.75rem',
    fontWeight: 500,
  },
}
