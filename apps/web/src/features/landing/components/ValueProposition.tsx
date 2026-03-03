import Image from 'next/image'

interface Feature {
  icon?: string
  iconPath?: string
  title: string
  description: string
}

interface ValuePropositionProps {
  features: Feature[]
}

export default function ValueProposition({ features }: ValuePropositionProps) {
  return (
    <section className="py-16 md:py-24 relative">
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Your Diving Journey, Simplified
            </h2>
            <p className="text-lg text-gray-700 max-w-2xl mx-auto">
              Whether you&apos;re exploring certifications or planning your next
              dive trip, DovvyBuddy provides grounded, judgment-free guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-16 md:gap-12">
            {features.map((feature, index) => (
              <div
                key={index}
                className="relative group text-center transform transition-transform duration-300 hover:-translate-y-2"
              >
                {/* Animal icon - no white box */}
                <div className="h-48 md:h-56 mb-6 flex items-center justify-center relative">
                  {feature.iconPath ? (
                    <div className="relative w-full h-full">
                      <Image
                        src={feature.iconPath}
                        alt={feature.title}
                        fill
                        className="object-contain drop-shadow-2xl group-hover:scale-110 transition-transform duration-500"
                      />
                    </div>
                  ) : (
                    <div
                      className="text-6xl"
                      role="img"
                      aria-label={feature.title}
                    >
                      {feature.icon}
                    </div>
                  )}
                </div>

                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-700 leading-relaxed max-w-xs mx-auto">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
