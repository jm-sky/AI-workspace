import { isAxiosError } from 'axios'

interface FastApiValidationError {
  msg: string
}

interface FastApiErrorBody {
  detail?: string | FastApiValidationError[]
  message?: string
}

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong'): string {
  if (isAxiosError(error)) {
    const data = error.response?.data as FastApiErrorBody | undefined

    if (typeof data?.detail === 'string') {
      return data.detail
    }

    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      return data.detail.map((item) => item.msg).join(', ')
    }

    if (data?.message) {
      return data.message
    }
  }

  if (error instanceof Error && !error.message.startsWith('Request failed with status code')) {
    return error.message
  }

  return fallback
}
