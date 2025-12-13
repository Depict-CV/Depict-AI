export const useApi = () => {
  const config = useRuntimeConfig()
  const { $clerk } = useNuxtApp()

  const apiFetch = async (endpoint: string, options: any = {}) => {
    if (!$clerk || !$clerk.session) {
      throw new Error('Not authenticated')
    }

    const token = await $clerk.session.getToken()

    return $fetch(`${config.public.apiBaseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
  }

  return {
    get: (endpoint: string, params?: any) => {
      // Build query string from params
      if (params) {
        const queryString = new URLSearchParams(
          Object.entries(params).reduce(
            (acc, [key, value]) => {
              if (value !== undefined && value !== null) {
                acc[key] = String(value)
              }
              return acc
            },
            {} as Record<string, string>
          )
        ).toString()
        endpoint = queryString ? `${endpoint}?${queryString}` : endpoint
      }
      return apiFetch(endpoint)
    },
    post: (endpoint: string, data: any) => apiFetch(endpoint, { method: 'POST', body: data }),
    put: (endpoint: string, data: any) => apiFetch(endpoint, { method: 'PUT', body: data }),
    delete: (endpoint: string) => apiFetch(endpoint, { method: 'DELETE' }),
  }
}
