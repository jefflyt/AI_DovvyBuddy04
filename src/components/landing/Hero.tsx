import Link from 'next/link'

interface HeroProps {
  headline: string
  subheadline: string
  ctaText: string
  ctaLink: string
  onCtaClick?: () => void
}

export default function Hero({
  headline,
  subheadline,
  ctaText,
  ctaLink,
  onCtaClick,
}: HeroProps) {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight text-primary-900">
            {headline}
          </h1>
          <p className="text-xl md:text-2xl mb-10 text-primary-700/80 leading-relaxed font-light">
            {subheadline}
          </p>
          <Link
            href={ctaLink}
            onClick={onCtaClick}
            className="inline-block bg-primary hover:bg-primary-600 text-white font-medium text-lg px-8 py-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
          >
            {ctaText}
          </Link>
        </div>
      </div>
    </section>
  )
}
