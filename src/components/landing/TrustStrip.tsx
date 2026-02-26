import { Shield, BookOpen, AlertCircle } from 'lucide-react'

const items = [
  {
    icon: BookOpen,
    title: 'Source-backed guidance',
    description:
      'Answers cite official certification standards and dive site data',
  },
  {
    icon: Shield,
    title: 'Conservative recommendations',
    description: 'We err on the side of caution when safety is involved',
  },
  {
    icon: AlertCircle,
    title: 'Not a substitute',
    description:
      'Always consult certified instructors and medical professionals',
  },
]

export const TrustStrip = () => {
  return (
    <div className="border-y border-gray-200/50 bg-white/40 backdrop-blur-sm py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {items.map((item, index) => {
            const Icon = item.icon
            return (
              <div key={index} className="flex gap-4 items-start">
                <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {item.title}
                  </h3>
                  <p className="text-sm text-gray-600">{item.description}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
