interface SocialProofProps {
  title?: string
  subtitle?: string
}

export default function SocialProof({
  title = 'Built by Divers, for Divers',
  subtitle = 'Trusted guidance for recreational diving enthusiasts worldwide',
}: SocialProofProps) {
  return (
    <section className="py-16 relative border-t border-gray-300/50">
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">
            {title}
          </h2>
          <p className="text-lg text-gray-700">{subtitle}</p>
        </div>
      </div>
    </section>
  )
}
