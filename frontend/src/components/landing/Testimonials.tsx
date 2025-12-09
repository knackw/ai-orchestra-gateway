'use client'

import * as React from 'react'
import { ChevronLeft, ChevronRight, Star } from 'lucide-react'

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
      'AI Legal Ops hat unsere AI-Integration revolutioniert. Der PII Shield gibt uns die Sicherheit, dass keine sensiblen Daten unserer Mandanten an externe AI-Provider gelangen. DSGVO-Compliance war noch nie so einfach.',
    author: 'Dr. Sarah Müller',
    role: 'CTO',
    company: 'LegalTech Solutions GmbH',
    avatar: '/avatars/sarah-mueller.jpg',
    rating: 5,
  },
  {
    quote:
      'Die Multi-Tenant-Architektur ist perfekt für unsere SaaS-Plattform. Jeder Kunde hat seine eigenen Credits und API-Keys. Die Abrechnung funktioniert automatisch. Wir haben in 2 Tagen integriert, was sonst Wochen gedauert hätte.',
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
    company: 'InnovateTech',
    avatar: '/avatars/jennifer-schmidt.jpg',
    rating: 5,
  },
  {
    quote:
      'Die Analytics-Dashboards geben uns volle Transparenz über unsere AI-Kosten. Wir können genau nachvollziehen, welche Features wie viele Credits verbrauchen. Das hilft enorm bei der Budgetplanung.',
    author: 'Thomas Klein',
    role: 'CFO',
    company: 'FinanceAI GmbH',
    avatar: '/avatars/thomas-klein.jpg',
    rating: 5,
  },
  {
    quote:
      'Der Support ist hervorragend. Innerhalb von 2 Stunden hatten wir eine individuelle Integration für unseren Use Case. Das Team versteht wirklich, was Enterprise-Kunden brauchen. Absolute Empfehlung!',
    author: 'Lisa Wagner',
    role: 'Head of Engineering',
    company: 'Enterprise Solutions SE',
    avatar: '/avatars/lisa-wagner.jpg',
    rating: 5,
  },
]

export function Testimonials() {
  const [currentIndex, setCurrentIndex] = React.useState(0)
  const [isPaused, setIsPaused] = React.useState(false)

  // Auto-play functionality
  React.useEffect(() => {
    if (isPaused) return

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length)
    }, 5000)

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
            <Card className="overflow-hidden">
              <CardHeader className="pb-4">
                {/* Rating Stars */}
                <div className="flex gap-1">
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

              <CardContent className="pb-8">
                {/* Quote */}
                <blockquote className="text-lg leading-relaxed md:text-xl">
                  &quot;{currentTestimonial.quote}&quot;
                </blockquote>
              </CardContent>

              <CardFooter className="flex items-center gap-4">
                {/* Avatar */}
                <Avatar className="h-12 w-12">
                  <AvatarImage
                    src={currentTestimonial.avatar}
                    alt={currentTestimonial.author}
                  />
                  <AvatarFallback>
                    {currentTestimonial.author
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </AvatarFallback>
                </Avatar>

                {/* Author Info */}
                <div>
                  <div className="font-semibold">
                    {currentTestimonial.author}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {currentTestimonial.role} • {currentTestimonial.company}
                  </div>
                </div>
              </CardFooter>
            </Card>

            {/* Navigation Buttons */}
            <div className="absolute left-0 right-0 top-1/2 flex -translate-y-1/2 justify-between px-4">
              <Button
                variant="outline"
                size="icon"
                onClick={goToPrevious}
                className="h-10 w-10 rounded-full bg-background shadow-lg"
                aria-label="Previous testimonial"
              >
                <ChevronLeft className="h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={goToNext}
                className="h-10 w-10 rounded-full bg-background shadow-lg"
                aria-label="Next testimonial"
              >
                <ChevronRight className="h-5 w-5" />
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
        </div>
      </div>
    </section>
  )
}
