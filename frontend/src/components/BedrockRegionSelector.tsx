import { useState, useEffect } from 'react'
import { fetchRegionInfo, fetchSupportedModels, fetchRegionMap, type RegionInfo } from '../api/client'

interface BedrockRegionSelectorProps {
  onRegionChange: (region: string, info: RegionInfo) => void
  onModelResolve: (resolvedModel: string, isProfile: boolean) => void
}

const MAJOR_REGIONS = [
  { value: 'us-east-1', label: 'US East (N. Virginia)' },
  { value: 'us-west-2', label: 'US West (Oregon)' },
  { value: 'eu-west-1', label: 'EU West (Ireland)' },
  { value: 'eu-central-1', label: 'EU Central (Frankfurt)' },
  { value: 'ap-southeast-1', label: 'APAC Southeast (Singapore)' },
  { value: 'ap-southeast-2', label: 'AU Southeast (Sydney)' },
  { value: 'ap-northeast-1', label: 'APAC Northeast (Tokyo)' },
  { value: 'ap-south-1', label: 'APAC South (Mumbai)' },
  { value: 'ca-central-1', label: 'Canada Central' },
  { value: 'sa-east-1', label: 'South America (São Paulo)' },
]

export function BedrockRegionSelector({ onRegionChange, onModelResolve }: BedrockRegionSelectorProps) {
  const [region, setRegion] = useState('us-east-1')
  const [regionInfo, setRegionInfo] = useState<RegionInfo | null>(null)
  const [models, setModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const [resolvedModel, setResolvedModel] = useState<string | null>(null)
  const [isProfile, setIsProfile] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadRegionMap()
    loadModels()
  }, [])

  const loadRegionMap = async () => {
    try {
      await fetchRegionMap()
    } catch (e) {
      console.warn('Failed to load region map', e)
    }
  }

  const loadModels = async () => {
    try {
      const modelList = await fetchSupportedModels()
      setModels(modelList)
      if (modelList.length > 0) {
        setSelectedModel(modelList[0])
      }
    } catch (e) {
      console.warn('Failed to load models', e)
    }
  }

  const handleRegionChange = async (newRegion: string) => {
    setRegion(newRegion)
    setLoading(true)
    setError(null)
    try {
      const info = await fetchRegionInfo(newRegion)
      setRegionInfo(info)
      onRegionChange(newRegion, info)
      
      // Also resolve current model
      if (selectedModel) {
        const resolved = await fetch(`${API_BASE}/bedrock/resolve-model`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ region: newRegion, model: selectedModel }),
        }).then(r => r.json())
        setResolvedModel(resolved.resolved_model)
        setIsProfile(resolved.is_inference_profile)
        onModelResolve(resolved.resolved_model, resolved.is_inference_profile)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load region info')
    } finally {
      setLoading(false)
    }
  }

  const handleModelChange = async (model: string) => {
    setSelectedModel(model)
    if (!region) return
    setLoading(true)
    try {
      const resolved = await fetch(`${API_BASE}/bedrock/resolve-model`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ region, model }),
      }).then(r => r.json())
      setResolvedModel(resolved.resolved_model)
      setIsProfile(resolved.is_inference_profile)
      onModelResolve(resolved.resolved_model, resolved.is_inference_profile)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to resolve model')
    } finally {
      setLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    handleRegionChange(region)
  }, [])

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Bedrock Region Configuration</h2>
      
      <div style={styles.field}>
        <label style={styles.label} htmlFor="region">AWS Region</label>
        <select
          id="region"
          value={region}
          onChange={(e) => handleRegionChange(e.target.value)}
          disabled={loading}
          style={styles.select}
        >
          {MAJOR_REGIONS.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
      </div>

      {regionInfo && (
        <div style={styles.infoPanel}>
          <div style={styles.infoRow}>
            <span style={styles.infoLabel}>Geographic Prefix:</span>
            <span style={styles.infoValue}>{regionInfo.prefix}</span>
          </div>
          <div style={styles.infoRow}>
            <span style={styles.infoLabel}>Inference Profile Prefix:</span>
            <span style={styles.infoValue}>{regionInfo.inference_profile_prefix}</span>
          </div>
          <div style={styles.infoRow}>
            <span style={styles.infoLabel}>Supports On-Demand:</span>
            <span style={{...styles.infoValue, color: regionInfo.supports_on_demand ? 'var(--color-success)' : 'var(--color-warning)'}}>
              {regionInfo.supports_on_demand ? 'Yes' : 'No (Inference Profile Required)'}
            </span>
          </div>
        </div>
      )}

      <div style={styles.field}>
        <label style={styles.label} htmlFor="model">Foundation Model</label>
        <select
          id="model"
          value={selectedModel}
          onChange={(e) => handleModelChange(e.target.value)}
          disabled={loading || models.length === 0}
          style={styles.select}
        >
          {Array.isArray(models) ? models.map((m) => (
            <option key={m} value={m}>{m}</option>
          )) : null}
        </select>
      </div>

      {resolvedModel && (
        <div style={styles.resultPanel}>
          <div style={styles.infoRow}>
            <span style={styles.infoLabel}>Resolved Identifier:</span>
            <code style={styles.resolvedCode}>{resolvedModel}</code>
          </div>
          <div style={styles.infoRow}>
            <span style={styles.infoLabel}>Type:</span>
            <span style={{...styles.infoValue, color: isProfile ? 'var(--color-accent)' : 'var(--color-success)'}}>
              {isProfile ? 'Cross-Region Inference Profile' : 'Foundation Model (On-Demand)'}
            </span>
          </div>
          {isProfile && regionInfo && !regionInfo.supports_on_demand && (
            <div style={styles.warning}>
              ⚠ This region requires inference profiles. Foundation model IDs cannot be invoked directly.
            </div>
          )}
        </div>
      )}

      {error && <div style={styles.error}>{error}</div>}
    </div>
  )
}

const API_BASE = '/api/v1'

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: 'var(--color-bg-secondary)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-md)',
    padding: 'var(--spacing-lg)',
  },
  title: {
    marginBottom: 'var(--spacing-md)',
    fontSize: '1.125rem',
    fontWeight: 600,
  },
  field: {
    marginBottom: 'var(--spacing-md)',
  },
  label: {
    display: 'block',
    marginBottom: 'var(--spacing-xs)',
    fontSize: '0.875rem',
    color: 'var(--color-fg-muted)',
  },
  select: {
    width: '100%',
    padding: 'var(--spacing-sm) var(--spacing-md)',
    background: 'var(--color-bg-tertiary)',
    border: '1px solid var(--color-border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--color-fg)',
    fontSize: '0.875rem',
  },
  infoPanel: {
    background: 'var(--color-bg-tertiary)',
    borderRadius: 'var(--radius-sm)',
    padding: 'var(--spacing-md)',
    marginBottom: 'var(--spacing-md)',
  },
  infoRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: 'var(--spacing-sm)',
    fontSize: '0.875rem',
  },
  infoLabel: {
    color: 'var(--color-fg-muted)',
  },
  infoValue: {
    fontFamily: 'var(--font-mono)',
    fontSize: '0.875rem',
  },
  resultPanel: {
    background: 'var(--color-bg-tertiary)',
    borderRadius: 'var(--radius-sm)',
    padding: 'var(--spacing-md)',
    marginBottom: 'var(--spacing-md)',
  },
  resolvedCode: {
    fontFamily: 'var(--font-mono)',
    fontSize: '0.875rem',
    color: 'var(--color-accent)',
  },
  warning: {
    marginTop: 'var(--spacing-sm)',
    padding: 'var(--spacing-sm)',
    background: 'rgba(210, 153, 34, 0.1)',
    border: '1px solid var(--color-warning)',
    borderRadius: 'var(--radius-sm)',
    fontSize: '0.75rem',
    color: 'var(--color-warning)',
  },
  error: {
    marginTop: 'var(--spacing-sm)',
    padding: 'var(--spacing-sm)',
    background: 'rgba(248, 81, 73, 0.1)',
    border: '1px solid var(--color-error)',
    borderRadius: 'var(--radius-sm)',
    fontSize: '0.875rem',
    color: 'var(--color-error)',
  },
}