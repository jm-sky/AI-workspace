import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import { recognizeParameters, recognizeParametersForItems } from '../utils/parameterRecognition'
import { useGearMutations } from './useGearMutations'
import type { ComputedRef } from 'vue'

export const useItemsParamRecognition = (
    container: ComputedRef<IGearItemV2 | undefined>,
    items: ComputedRef<IGearItemV2[]>
) => {
    const { t } = useI18n()
    const { updateItem } = useGearMutations()

    const handleRecognizeParameters = async (item: IGearItemV2) => {
        try {
          const params = recognizeParameters(item.name)

          if (!params.brand && !params.color) {
            toast.info(t('gear.actions.noParametersFound'))
            return
          }

          const updateData: IUpdateGearItemV2Dto = {}
          if (params.brand && !item.brand) {
            updateData.brand = params.brand
          }
          if (params.color && !item.color) {
            updateData.color = params.color
          }
      
          if (Object.keys(updateData).length > 0) {
            await updateItem(item.id, updateData)
            toast.success(t('gear.actions.parametersRecognized'))
          } else {
            toast.info(t('gear.actions.noParametersFound'))
          }
        } catch (error) {
          toast.error(t('common.error'))
          console.error('Error recognizing parameters:', error)
        }
      }

    const handleRecognizeParametersAll = async () => {
        if (!container.value || !items.value || items.value.length === 0) return
      
        try {
          toast.loading(t('gear.actions.recognizing'))
      
          const paramsMap = recognizeParametersForItems(items.value)
          let updatedCount = 0
      
          for (const item of items.value) {
            const params = paramsMap.get(item.id)
            if (!params) continue
      
            const updateData: IUpdateGearItemV2Dto = {}
            if (params.brand && !item.brand) {
              updateData.brand = params.brand
            }
            if (params.color && !item.color) {
              updateData.color = params.color
            }
      
            if (Object.keys(updateData).length > 0) {
              await updateItem(item.id, updateData)
              updatedCount++
            }
          }
      
          toast.dismiss()
          if (updatedCount > 0) {
            toast.success(t('gear.actions.parametersRecognized', { count: updatedCount }))
          } else {
            toast.info(t('gear.actions.noParametersFound'))
          }
        } catch (error) {
          toast.dismiss()
          toast.error(t('common.error'))
          console.error('Error recognizing parameters:', error)
        }
      }

      return {
        handleRecognizeParameters,
        handleRecognizeParametersAll,
      }
}