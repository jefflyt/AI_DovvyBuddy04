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
    <section className="relative bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 text-white">
      <div className="container mx-auto px-4 py-24 md:py-32 lg:py-40">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
            {headline}
          </h1>
          <p className="text-xl md:text-2xl mb-10 text-primary-50 leading-relaxed">
            {subheadline}
          </p>
          <Link
            href={ctaLink}
            onClick={onCtaClick}
            className="inline-block bg-accent-500 hover:bg-accent-600 text-white font-semibold text-lg px-8 py-4 rounded-lg shadow-medium hover:shadow-hard transition-all duration-200 transform hover:scale-105"
          >
            {ctaText}
          </Link>
        </div>
      </div>

      {/* Decorative wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg
          viewBox="0 0 1440 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-12 md:h-16"
        >
          <path
            d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            fill="white"
          />
        </svg>
      </div>
    </section>
  )
}
