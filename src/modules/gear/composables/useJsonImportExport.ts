import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { downloadBlob } from '@/shared/utils/downloadBlob'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { exportContainersToJSONV2 } from '../utils/exportToJsonV2'
import { importContainersFromJSONV2 } from '../utils/importFromJsonV2'
import { useGearV2 } from './useGearV2'

export const useJsonImportExport = () => {
    const { t } = useI18n()
    const store = useGearStoreV2()
    const { createItem, refreshAll } = useGearV2()

    const genExportFilename = (): string => {
        return `gear-stack-export-${new Date().toISOString().split('T')[0]}.json`
    }

    const handleJsonExport = async () => {
        try {
          // Load the full gear tree into the store, then serialize all root containers
          await refreshAll()
          const json = exportContainersToJSONV2(store.getRootContainers, {
            getChildrenOfItem: id => store.getChildrenOfItem(id),
            includeNestedContainers: true,
          })
          const blob = new Blob([json], { type: 'application/json' })
          downloadBlob(blob, genExportFilename())
          toast.success(t('common.success'))
        } catch {
          toast.error(t('common.error'))
        }
      }

      const handleJsonImport = () => {
        // Use native input element for file selection
        const createInput = (): HTMLInputElement => {
            const input = document.createElement('input')
            input.type = 'file'
            input.accept = 'application/json'
            return input
        }

        const onReaderLoadHandler = async (event: ProgressEvent<FileReader>) => {
            try {
                const json = event.target?.result as string
                await importContainersFromJSONV2(json, { createItem })
                toast.success(t('common.success'))
                // Reload page to show imported data (and refresh any query caches)
                window.location.reload()
            } catch (error) {
                toast.error(t('common.error'))
                console.error('Import error:', error)
            }
        }

        const onChangeHandler = (e: Event) => {
            const file = (e.target as HTMLInputElement).files?.[0]
            if (!file) return

            const reader = new FileReader()
            reader.onload = (e) => onReaderLoadHandler(e)
            reader.readAsText(file)
        }

        const input = createInput()
        input.onchange = (e) => onChangeHandler(e)
        input.click()
      }

      return {
        handleJsonExport,
        handleJsonImport,
      }
}
