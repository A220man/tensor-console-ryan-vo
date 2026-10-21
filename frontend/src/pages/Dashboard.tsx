import { BedrockRegionSelector } from '../components/BedrockRegionSelector'
import { checkHealth } from '../api/client'
import { useEffect, useState } from 'react'

interface RegionInfo {
  region: string
  prefix: string
  supports_on_demand: boolean
  supports_inference_profiles: boolean
  inference_profile_prefix: string
}

export function Dashboard() {
  const [healthy, setHealthy] = useState<boolean | null>(null)
  const [healthError, setHealthError] = useState<string | null>(null)

  useEffect(() => {
    checkHealth()
      .then(() => setHealthy(true))
      .catch((err: unknown) => {
        setHealthy(false)
        setHealthError(err instanceof Error ? err.message : String(err))
      })
  }, [])

  const handleRegionChange = (region: string, info: RegionInfo) => {
    console.log('Region changed:', region, info)
  }

  const handleModelResolve = (resolvedModel: string, isProfile: boolean) => {
    console.log('Model resolved:', resolvedModel, isProfile)
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Tensor Console</h1>
        <p style={styles.subtitle}>AI/ML Developer Tools — Bedrock Region Resolver</p>
        <div style={styles.health}>
          {healthy === null && <span style={styles.healthChecking}>Checking backend...</span>}
          {healthy === true && <span style={styles.healthOk}>✓ Backend healthy</span>}
          {healthy === false && <span style={styles.healthError}>✗ Backend unreachable: {healthError}</span>}
        </div>
      </header>

      <main style={styles.main}>
        <section style={styles.section}>
          <BedrockRegionSelector
            onRegionChange={handleRegionChange}
            onModelResolve={handleModelResolve}
          />
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>About</h2>
          <p style={styles.description}>
            Tensor Console resolves the correct AWS Bedrock cross-region inference profile identifiers
            for Anthropic Claude models based on the target AWS region.
          </p>
          <ul style={styles.features}>
            <li>Maps AWS regions to geographic prefixes (us, eu, au, apac)</li>
            <li>Resolves foundation model IDs to invokeable inference profiles</li>
            <li>Handles AU region (ap-southeast-2) requiring <code>au.anthropic.*</code> profiles</li>
            <li>Validates plugin hooks.json and .mcp.json configurations</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Reference Issues</h2>
          <ul style={styles.features}>
            <li><a href="https://github.com/anthropics/financial-services/issues/217" target="_blank" rel="noopener">#217</a> — AU Bedrock region model identifier fix</li>
            <li><a href="https://github.com/anthropics/financial-services/issues/179" target="_blank" rel="noopener">#179</a> — Expired Entra tokens to bootstrap endpoint</li>
            <li><a href="https://github.com/anthropics/financial-services/issues/86" target="_blank" rel="noopener">#86</a> — hooks.json schema bug (bare <code>[]</code>)</li>
            <li><a href="https://github.com/anthropics/financial-services/issues/355" target="_blank" rel="noopener">#355</a> — .mcp.json invalid JSON</li>
          </ul>
        </section>
      </main>

      <footer style={styles.footer}>
        <p>Tensor Console | Ryan Vo | AI & Machine Learning</p>
        <p style={styles.footerLinks}>
          <a href="https://github.com/A220man/tensor-console-ryan-vo" target="_blank" rel="noopener">GitHub</a>
        </p>
      </footer>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    padding: 'var(--spacing-xl) var(--spacing-lg)',
    borderBottom: '1px solid var(--color-border)',
    textAlign: 'center',
  },
  title: {
    fontSize: '2rem',
    fontWeight: 700,
    marginBottom: 'var(--spacing-xs)',
  },
  subtitle: {
    color: 'var(--color-fg-muted)',
    fontSize: '1.125rem',
  },
  health: {
    marginTop: 'var(--spacing-md)',
    fontSize: '0.875rem',
  },
  healthChecking: {
    color: 'var(--color-warning)',
  },
  healthOk: {
    color: 'var(--color-success)',
  },
  healthError: {
    color: 'var(--color-error)',
  },
  main: {
    flex: 1,
    padding: 'var(--spacing-xl) var(--spacing-lg)',
    maxWidth: '900px',
    margin: '0 auto',
    width: '100%',
  },
  section: {
    marginBottom: 'var(--spacing-xl)',
  },
  sectionTitle: {
    fontSize: '1.25rem',
    fontWeight: 600,
    marginBottom: 'var(--spacing-md)',
  },
  description: {
    color: 'var(--color-fg-muted)',
    marginBottom: 'var(--spacing-md)',
    lineHeight: 1.7,
  },
  features: {
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--spacing-sm)',
  },
  footer: {
    padding: 'var(--spacing-lg)',
    borderTop: '1px solid var(--color-border)',
    textAlign: 'center',
    color: 'var(--color-fg-muted)',
    fontSize: '0.875rem',
  },
  footerLinks: {
    marginTop: 'var(--spacing-xs)',
  },
}