import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, act } from '@testing-library/react'
import { Dashboard } from '../src/pages/Dashboard'

// Mock fetch globally before importing components
global.fetch = vi.fn()

// Helper to mock successful health check
const mockHealthSuccess = () => {
  ;(global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
    ok: true,
    json: async () => ({ status: 'healthy', service: 'tensor-console' }),
  })
}

// Helper to mock all Bedrock API calls
const mockBedrockAPIs = () => {
  ;(global.fetch as unknown as ReturnType<typeof vi.fn>)
    .mockResolvedValueOnce({ // region-map
      ok: true,
      json: async () => ({ 'us-east-1': 'us' }),
    })
    .mockResolvedValueOnce({ // supported-models
      ok: true,
      json: async () => ['claude-3-5-sonnet', 'claude-3-opus', 'claude-3-haiku'],
    })
    .mockResolvedValueOnce({ // region-info
      ok: true,
      json: async () => ({
        region: 'us-east-1',
        prefix: 'us',
        supports_on_demand: true,
        supports_inference_profiles: true,
        inference_profile_prefix: 'us.anthropic',
      }),
    })
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders title and subtitle', async () => {
    mockHealthSuccess()
    mockBedrockAPIs()

    await act(async () => {
      render(<Dashboard />)
    })

    expect(screen.getByText('Tensor Console')).toBeInTheDocument()
    expect(screen.getByText('AI/ML Developer Tools — Bedrock Region Resolver')).toBeInTheDocument()
  })

  it('shows checking state initially', async () => {
    const { promise } = Promise.withResolvers()
    ;(global.fetch as unknown as ReturnType<typeof vi.fn>).mockReturnValue(promise)
    mockBedrockAPIs()

    await act(async () => {
      render(<Dashboard />)
    })

    expect(screen.getByText('Checking backend...')).toBeInTheDocument()
  })

  it('shows healthy state when backend responds', async () => {
    mockHealthSuccess()
    mockBedrockAPIs()

    await act(async () => {
      render(<Dashboard />)
    })

    await waitFor(() => {
      expect(screen.getByText('✓ Backend healthy')).toBeInTheDocument()
    })
  })

  it('renders reference issues list', async () => {
    mockHealthSuccess()
    mockBedrockAPIs()

    await act(async () => {
      render(<Dashboard />)
    })

    expect(screen.getByText('#217')).toBeInTheDocument()
    expect(screen.getByText('#179')).toBeInTheDocument()
    expect(screen.getByText('#86')).toBeInTheDocument()
    expect(screen.getByText('#355')).toBeInTheDocument()
  })
})