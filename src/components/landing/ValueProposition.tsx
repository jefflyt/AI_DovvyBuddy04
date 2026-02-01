import Image from 'next/image';

interface Feature {
  icon?: string
  iconPath?: string // New prop for image assets
  title: string
  description: string
}

interface ValuePropositionProps {
  features: Feature[]
}

export default function ValueProposition({ features }: ValuePropositionProps) {
  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-primary-900 mb-4">
              Your Diving Journey, Simplified
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Whether you&apos;re exploring certifications or planning your next dive trip,
              DovvyBuddy provides grounded, judgment-free guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white/60 backdrop-blur-md rounded-2xl p-8 shadow-sm border border-white/50 hover:shadow-md transition-all duration-300 group"
              >
                <div className="h-40 mb-6 flex items-center justify-center relative">
                  {feature.iconPath ? (
                    <div className="relative w-full h-full">
                      <Image
                        src={feature.iconPath}
                        alt={feature.title}
                        fill
                        className="object-contain drop-shadow-sm group-hover:scale-105 transition-transform duration-500"
                      />
                    </div>
                  ) : (
                    <div className="text-5xl" role="img" aria-label={feature.title}>
                      {feature.icon}
                    </div>
                  )}
                </div>
                <h3 className="text-xl font-semibold text-primary-900 mb-3 text-center">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed text-center">
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
