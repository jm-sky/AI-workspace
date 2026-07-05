import { z } from 'zod'
import { weightUnitEnum } from '@/modules/gear/utils/weightUnits'

export const cataloguePriceTierEnum = z.enum(['low', 'medium', 'high'])
export const gearQualityEnum = z.enum(['low', 'medium', 'high'])

export const catalogueItemSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  category: z.string().min(1, 'Kategoria jest wymagana'),
  weight: z.number().min(0, 'Waga nie może być ujemna'),
  weightUnit: weightUnitEnum,
  description: z.string().optional(),
  brand: z.string().optional(),
  model: z.string().optional(),
  priceTier: cataloguePriceTierEnum.optional(),
  price: z.number().min(0, 'Cena nie może być ujemna').optional(),
  currency: z.string().optional(),
  quality: gearQualityEnum.optional(),
  url: z.string().url('Nieprawidłowy URL').optional().or(z.literal('')),
  color: z.string().optional(),
  isActive: z.boolean().optional(),
})

export type CatalogueItemFormData = z.infer<typeof catalogueItemSchema>

