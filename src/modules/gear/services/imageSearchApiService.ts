import { apiClient } from '@/shared/services/apiClient'

/**
 * Image Search Result
 */
export interface IImageSearchResult {
  imageUrl: string
  thumbnailUrl: string | null
  sourceUrl: string | null
  sourceName: string | null
  searchEngineId: string
  searchEngineName: string
}

/**
 * Image Search Response
 */
export interface IImageSearchResponse {
  results: IImageSearchResult[]
  total: number
}

/**
 * Image Search Request
 */
export interface IImageSearchRequest {
  itemId: string
  query?: string
  engineIds?: string[]
}

/**
 * Download and Add Image Request
 */
export interface IDownloadAndAddImageRequest {
  itemId: string
  imageUrl: string
  sourceUrl?: string | null
  sourceName?: string | null
  searchEngineId: string
  isPrimary?: boolean
}

export interface IDownloadAndAddImageResponse {
  id: string
  itemId: string
  userId: string
  url: string
  fileName: string
  fileSize: number
  mimeType: string
  width: number
  height: number
  isPrimary: boolean
  order?: number | null
  createdAt: string
  updatedAt?: string | null
  sourceUrl: string
  sourceName: string
}

/**
 * Image Search API Service
 *
 * Provides methods to interact with image search API endpoints.
 * All methods require admin authentication.
 */
class ImageSearchApiService {
  /**
   * Search for images for an item
   *
   * @param request - Search request with itemId and optional query/engineIds
   * @returns Search results
   */
  async searchImages(request: IImageSearchRequest): Promise<IImageSearchResponse> {
    const response = await apiClient.post<IImageSearchResponse>(
      '/gear/image-search/search',
      request,
    )
    return response.data
  }

  /**
   * Download image from URL and add it to item gallery
   *
   * @param request - Download request with imageUrl and source info
   * @returns Added image metadata
   */
  async downloadAndAddImage(request: IDownloadAndAddImageRequest): Promise<IDownloadAndAddImageResponse> {
    const response = await apiClient.post<IDownloadAndAddImageResponse>('/gear/image-search/download-and-add', request)
    return response.data
  }
}

export const imageSearchApiService = new ImageSearchApiService()

