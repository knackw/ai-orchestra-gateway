'use client'

import * as React from 'react'
import { ChevronLeft, ChevronRight, Star, Quote } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

const testimonials = [
  {
    quote:
      'AI Legal Ops hat unsere AI-Integration revolutioniert. Der Privacy Shield gibt uns die Sicherheit, dass keine sensiblen Daten unserer Mandanten an externe AI-Provider gelangen. DSGVO-Compliance war noch nie so einfach.',
    author: 'Dr. Sarah Müller',
    role: 'CTO',
    company: 'LegalTech Solutions GmbH',
    avatar: '/avatars/sarah-mueller.jpg',
    rating: 5,
  },
  {
    quote:
      'Die Multi-Provider-Architektur ist perfekt für unsere SaaS-Plattform. Jeder Kunde hat seine eigenen Credits und API-Keys. Die Abrechnung funktioniert automatisch. Wir haben in 2 Tagen integriert, was sonst Wochen gedauert hätte.',
    author: 'Marcus Weber',
    role: 'Lead Developer',
    company: 'CloudApp AG',
    avatar: '/avatars/marcus-weber.jpg',
    rating: 5,
  },
  {
    quote:
      'Das automatische Failover zwischen AI-Providern ist ein Game-Changer. Wir hatten letzten Monat einen Anthropic-Ausfall und haben es nicht mal bemerkt - das System ist nahtlos zu Scaleway gewechselt. 99.9% Uptime ist keine leere Versprechung.',
    author: 'Jennifer Schmidt',
    role: 'Product Manager',
    company: 'InnovateTech GmbH',
    avatar: '/avatars/jennifer-schmidt.jpg',
    rating: 5,
  },
]

export function TestimonialsSection() {
  const [currentIndex, setCurrentIndex] = React.useState(0)
  const [isPaused, setIsPaused] = React.useState(false)

  // Auto-play functionality
  React.useEffect(() => {
    if (isPaused) return

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length)
    }, 6000)

    return () => clearInterval(interval)
  }, [isPaused])

  const goToPrevious = () => {
    setCurrentIndex(
      (prev) => (prev - 1 + testimonials.length) % testimonials.length
    )
  }

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length)
  }

  const currentTestimonial = testimonials[currentIndex]

  return (
    <section className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Was unsere Kunden sagen
          </h2>
          <p className="mb-16 text-lg text-muted-foreground">
            Über 500 Unternehmen vertrauen auf AI Legal Ops
          </p>
        </div>

        <div className="mx-auto max-w-4xl">
          <div
            className="relative"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
          >
            <Card className="overflow-hidden border-2 shadow-xl">
              {/* Quote Icon */}
              <div className="absolute left-8 top-8 opacity-10">
                <Quote className="h-16 w-16 text-primary" />
              </div>

              <CardHeader className="pb-4 pt-16">
                {/* Rating Stars */}
                <div className="flex justify-center gap-1">
                  {Array.from({ length: currentTestimonial.rating }).map(
                    (_, i) => (
                      <Star
                        key={i}
                        className="h-5 w-5 fill-yellow-400 text-yellow-400"
                      />
                    )
                  )}
                </div>
              </CardHeader>

              <CardContent className="pb-8 pt-4">
                {/* Quote */}
                <blockquote className="text-center text-lg leading-relaxed md:text-xl">
                  {currentTestimonial.quote}
                </blockquote>
              </CardContent>

              <CardFooter className="flex flex-col items-center gap-4 pb-8">
                {/* Avatar */}
                <Avatar className="h-16 w-16 border-2 border-primary/20">
                  <AvatarImage
                    src={currentTestimonial.avatar}
                    alt={currentTestimonial.author}
                  />
                  <AvatarFallback className="text-lg font-semibold">
                    {currentTestimonial.author
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </AvatarFallback>
                </Avatar>

                {/* Author Info */}
                <div className="text-center">
                  <div className="text-lg font-semibold">
                    {currentTestimonial.author}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {currentTestimonial.role} bei {currentTestimonial.company}
                  </div>
                </div>
              </CardFooter>
            </Card>

            {/* Navigation Buttons */}
            <div className="absolute left-0 right-0 top-1/2 flex -translate-y-1/2 justify-between">
              <Button
                variant="outline"
                size="icon"
                onClick={goToPrevious}
                className="-ml-4 h-12 w-12 rounded-full bg-background shadow-xl hover:scale-110 transition-transform"
                aria-label="Previous testimonial"
              >
                <ChevronLeft className="h-6 w-6" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={goToNext}
                className="-mr-4 h-12 w-12 rounded-full bg-background shadow-xl hover:scale-110 transition-transform"
                aria-label="Next testimonial"
              >
                <ChevronRight className="h-6 w-6" />
              </Button>
            </div>
          </div>

          {/* Dots Navigation */}
          <div className="mt-8 flex justify-center gap-2">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={cn(
                  'h-2 w-2 rounded-full transition-all',
                  index === currentIndex
                    ? 'w-8 bg-primary'
                    : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                )}
                aria-label={`Go to testimonial ${index + 1}`}
              />
            ))}
          </div>

          {/* Trust indicator */}
          <div className="mt-12 text-center">
            <p className="text-sm text-muted-foreground">
              Über 10.000+ erfolgreiche AI-Anfragen pro Tag
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
