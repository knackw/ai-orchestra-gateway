'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { useAccessibility } from '@/hooks/use-accessibility'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Settings, X } from 'lucide-react'

export function AccessibilityPanel() {
  const t = useTranslations('accessibility')
  const [isOpen, setIsOpen] = useState(false)
  const {
    fontSize,
    highContrast,
    reducedMotion,
    focusIndicators,
    setFontSize,
    setHighContrast,
    setReducedMotion,
    setFocusIndicators,
    resetToDefaults,
  } = useAccessibility()

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            size="icon"
            variant="outline"
            className="h-12 w-12 rounded-full shadow-lg"
            aria-label={t('panel_title')}
          >
            <Settings className="h-5 w-5" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="w-80 p-6"
          align="end"
          side="top"
          sideOffset={8}
        >
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">{t('panel_title')}</h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                aria-label={t('close')}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Font Size */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="font-size">{t('font_size')}</Label>
                <span className="text-sm text-muted-foreground">
                  {fontSize}%
                </span>
              </div>
              <Slider
                id="font-size"
                min={80}
                max={150}
                step={10}
                value={[fontSize]}
                onValueChange={([value]) => setFontSize(value)}
                className="w-full"
                aria-label={t('font_size')}
              />
            </div>

            {/* High Contrast */}
            <div className="flex items-center justify-between">
              <Label htmlFor="high-contrast" className="cursor-pointer">
                {t('high_contrast')}
              </Label>
              <Switch
                id="high-contrast"
                checked={highContrast}
                onCheckedChange={setHighContrast}
                aria-label={t('high_contrast')}
              />
            </div>

            {/* Reduced Motion */}
            <div className="flex items-center justify-between">
              <Label htmlFor="reduced-motion" className="cursor-pointer">
                {t('reduced_motion')}
              </Label>
              <Switch
                id="reduced-motion"
                checked={reducedMotion}
                onCheckedChange={setReducedMotion}
                aria-label={t('reduced_motion')}
              />
            </div>

            {/* Focus Indicators */}
            <div className="flex items-center justify-between">
              <Label htmlFor="focus-indicators" className="cursor-pointer">
                {t('focus_indicators')}
              </Label>
              <Switch
                id="focus-indicators"
                checked={focusIndicators}
                onCheckedChange={setFocusIndicators}
                aria-label={t('focus_indicators')}
              />
            </div>

            {/* Reset Button */}
            <Button
              variant="outline"
              className="w-full"
              onClick={resetToDefaults}
            >
              {t('reset')}
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
