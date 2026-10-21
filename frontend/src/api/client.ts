const API_BASE = '/api/v1'

export interface RegionInfo {
  region: string
  prefix: string
  supports_on_demand: boolean
  supports_inference_profiles: boolean
  inference_profile_prefix: string
}

export interface ModelResolveResponse {
  region: string
  requested_model: string
  resolved_model: string
  is_inference_profile: boolean
  prefix_used: string
}

export interface RegionMap {
  [region: string]: string
}

export interface SupportedModelsResponse {
  models: string[]
}

export async function fetchRegionInfo(region: string): Promise<RegionInfo> {
  const response = await fetch(`${API_BASE}/bedrock/region-info`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ region }),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch region info: ${response.statusText}`)
  }
  return response.json()
}

export async function resolveModel(region: string, model: string): Promise<ModelResolveResponse> {
  const response = await fetch(`${API_BASE}/bedrock/resolve-model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ region, model }),
  })
  if (!response.ok) {
    throw new Error(`Failed to resolve model: ${response.statusText}`)
  }
  return response.json()
}

export async function fetchRegionMap(): Promise<RegionMap> {
  const response = await fetch(`${API_BASE}/bedrock/region-map`)
  if (!response.ok) {
    throw new Error(`Failed to fetch region map: ${response.statusText}`)
  }
  return response.json()
}

export async function fetchSupportedModels(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/bedrock/supported-models`)
  if (!response.ok) {
    throw new Error(`Failed to fetch supported models: ${response.statusText}`)
  }
  return response.json()
}

export async function fetchBootstrapConfig() {
  const response = await fetch(`${API_BASE}/bootstrap/config`)
  if (!response.ok) {
    throw new Error(`Failed to fetch bootstrap config: ${response.statusText}`)
  }
  return response.json()
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`)
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`)
  }
  return response.json()
}