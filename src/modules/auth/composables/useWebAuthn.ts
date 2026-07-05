import { startAuthentication, startRegistration } from '@simplewebauthn/browser'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
// modules/auth/composables/useWebAuthn.ts
import { twoFactorService } from '@/modules/auth/services/twoFactorService'
import { twoFactorQueryKeys } from './useTwoFactor'
import type { PublicKeyCredentialDescriptorJSON } from '@simplewebauthn/browser'
import type {
  ITwoFactorService,
  WebAuthnRegisterRequest,
} from '@/modules/auth/types/twoFactor.type'

function toBase64(buffer: ArrayBuffer | BufferSource): string {
  if (buffer instanceof ArrayBuffer) {
    return arrayBufferToBase64(buffer)
  }
  return arrayBufferToBase64(buffer.buffer)
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = ''
  const bytes = new Uint8Array(buffer)
  for (const byte of bytes) binary += String.fromCharCode(byte)
  return btoa(binary)
}


/**
 * Hook for registering a new passkey
 */
export function useRegisterPasskey(service?: ITwoFactorService) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (request: WebAuthnRegisterRequest) => {
      const svc = service ?? twoFactorService

      // Step 1: Get registration options from backend
      const registerResponse = await svc.registerPasskey(request)

      // Step 2: Start WebAuthn registration ceremony
      const credential = await startRegistration({
        optionsJSON: {
          rp: registerResponse.credentialCreationOptions.rp,
          user: {
            id: toBase64(registerResponse.credentialCreationOptions.user.id),
            name: registerResponse.credentialCreationOptions.user.name,
            displayName: registerResponse.credentialCreationOptions.user.displayName,
          },
          challenge: toBase64(registerResponse.credentialCreationOptions.challenge),
          pubKeyCredParams: registerResponse.credentialCreationOptions.pubKeyCredParams.map(param => ({
            type: param.type,
            alg: param.alg,
          })),
          timeout: registerResponse.credentialCreationOptions.timeout,
          excludeCredentials: registerResponse.credentialCreationOptions.excludeCredentials?.map((cred): PublicKeyCredentialDescriptorJSON => ({
            id: toBase64(cred.id),
            type: 'public-key' as const,
            transports: cred.transports,
          })),
          authenticatorSelection: registerResponse.credentialCreationOptions.authenticatorSelection,
          // hints: registerResponse.credentialCreationOptions.hints,
          attestation: registerResponse.credentialCreationOptions.attestation,
          // attestationFormats: registerResponse.credentialCreationOptions.attestationFormats,
          extensions: registerResponse.credentialCreationOptions.extensions,
        }
      })
      // Step 3: Complete registration with backend
      return await svc.completePasskeyRegistration(request.name, credential as unknown as PublicKeyCredential)
    },
    onSuccess: async () => {
      // Invalidate all 2FA queries to refresh status and passkey list
      await queryClient.invalidateQueries({ queryKey: twoFactorQueryKeys.all })
    },
  })
}

/**
 * Hook for verifying with a passkey during login
 */
export function useVerifyPasskey(service?: ITwoFactorService) {
  return useMutation({
    mutationFn: async () => {
      const svc = service ?? twoFactorService

      // Step 1: Get verification options from backend
      const verifyResponse = await svc.verifyPasskey()

      // Step 2: Start WebAuthn authentication ceremony
      const credential = await startAuthentication({
        optionsJSON: {
          extensions: verifyResponse.credentialRequestOptions.extensions,
          rpId: verifyResponse.credentialRequestOptions.rpId,
          timeout: verifyResponse.credentialRequestOptions.timeout,
          userVerification: verifyResponse.credentialRequestOptions.userVerification,
          challenge: verifyResponse.challenge,
        }
      })

      // Step 3: Complete verification with backend
      return await svc.completePasskeyVerification(credential as unknown as PublicKeyCredential)
    },
  })
}

/**
 * Hook for deleting a passkey
 */
export function useDeletePasskey(service?: ITwoFactorService) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (passkeyId: string) => {
      return (service ?? twoFactorService).deletePasskey(passkeyId)
    },
    onSuccess: async () => {
      // Invalidate all 2FA queries to refresh status and passkey list
      await queryClient.invalidateQueries({ queryKey: twoFactorQueryKeys.all })
    },
  })
}
