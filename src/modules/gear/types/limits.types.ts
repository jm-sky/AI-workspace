export type TAccountTier = 'free' | 'pro' | 'pro_plus'

export interface IUserLimits {
  tier: TAccountTier
  limits: {
    items: number
    containers: number
  }
  usage: {
    items: number
    containers: number
  }
  percentage: {
    items: number
    containers: number
  }
}

