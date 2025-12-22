// Placeholder types file
// Real types will be added as features are implemented

export interface DiverProfile {
  certificationAgency?: string
  certificationLevel?: string
  approximateDiveCount?: number
  comfortLevel?: string
  concerns?: string[]
  travelIntent?: string
}

export interface Session {
  id: string
  diverProfile: DiverProfile
  conversationHistory: unknown[] // To be defined with chat implementation
  createdAt: Date
  expiresAt: Date
}

export interface Destination {
  id: string
  name: string
  country: string
  isActive: boolean
  createdAt: Date
}

export interface DiveSite {
  id: string
  destinationId: string
  name: string
  minCertificationLevel: string
  minLoggedDives?: number
  difficultyBand: 'Beginner' | 'Intermediate' | 'Advanced'
  accessType: 'Shore' | 'Boat'
  isActive: boolean
  createdAt: Date
}

export interface Lead {
  id: string
  type: 'training' | 'trip'
  diverProfile: DiverProfile
  requestDetails: Record<string, unknown>
  createdAt: Date
}
