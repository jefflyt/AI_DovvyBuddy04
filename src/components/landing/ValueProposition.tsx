interface Feature {
  icon: string
  title: string
  description: string
}

interface ValuePropositionProps {
  features: Feature[]
}

export default function ValueProposition({ features }: ValuePropositionProps) {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-4">
              Your Diving Journey, Simplified
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              Whether you&apos;re exploring certifications or planning your next dive trip,
              DovvyBuddy provides grounded, judgment-free guidance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-neutral-50 rounded-lg p-8 hover:shadow-medium transition-shadow duration-200"
              >
                <div className="text-5xl mb-4" role="img" aria-label={feature.title}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-neutral-700 leading-relaxed">
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
