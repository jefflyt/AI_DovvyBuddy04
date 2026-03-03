'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle } from 'lucide-react'

interface ConversationTurn {
  user: string
  assistant: string
}

interface ChatExample {
  id: string
  label: string
  conversation: ConversationTurn
  prompt: string
}

const examples: ChatExample[] = [
  {
    id: 'certifications',
    label: 'Certifications',
    conversation: {
      user: 'What do I need before taking an Advanced Open Water course?',
      assistant:
        'You need a valid Open Water certification from any recognized agency (PADI, SSI, NAUI, etc.). Most operators require a minimum of 4 logged dives, though PADI officially only requires OW cert. Budget 2-3 days and $300-450 USD depending on location.',
    },
    prompt: 'What do I need before taking an Advanced Open Water course?',
  },
  {
    id: 'dive-site',
    label: 'Dive Site Match',
    conversation: {
      user: "I'm Advanced certified and want to see manta rays in Asia. Where should I go?",
      assistant:
        "Top options: Raja Ampat (Oct-Apr), Komodo (Apr-Nov), and Maldives (Nov-Apr). Raja Ampat has the highest biodiversity but requires liveaboard. Komodo offers strong currents—ensure you're comfortable with drift diving. Maldives has easier access but fewer guarantees outside peak season.",
    },
    prompt:
      "I'm Advanced certified and want to see manta rays in Asia. Where should I go?",
  },
  {
    id: 'trip-planning',
    label: 'Trip Planning',
    conversation: {
      user: 'When is the best time to dive in the Red Sea?',
      assistant:
        'May-October for warm water (26-28°C) and calmer seas. June-August is peak season—book early. November-April offers better visibility and fewer crowds, but water is cooler (22-24°C) and surface conditions can be rough. For wrecks like the Thistlegorm, September-November is ideal.',
    },
    prompt: 'When is the best time to dive in the Red Sea?',
  },
]

export const ChatPreview = () => {
  const [activeTab, setActiveTab] = useState(examples[0].id)
  const router = useRouter()

  const activeExample =
    examples.find((ex) => ex.id === activeTab) || examples[0]

  const handleTryThis = () => {
    const encoded = encodeURIComponent(activeExample.prompt)
    router.push(`/chat?prompt=${encoded}`)
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 md:p-8">
      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {examples.map((ex) => (
          <button
            key={ex.id}
            onClick={() => setActiveTab(ex.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors relative ${
              activeTab === ex.id
                ? 'text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {ex.label}
            {activeTab === ex.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600" />
            )}
          </button>
        ))}
      </div>

      {/* Conversation */}
      <div className="space-y-4 mb-6">
        {/* User message */}
        <div className="flex gap-3 items-start">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
            <MessageCircle className="w-4 h-4 text-gray-600" />
          </div>
          <div className="flex-1 bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
            <p className="text-sm text-gray-900">
              {activeExample.conversation.user}
            </p>
          </div>
        </div>

        {/* Assistant message */}
        <div className="flex gap-3 items-start">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-4 h-4 text-primary-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <div className="flex-1 bg-primary-50 rounded-2xl rounded-tl-sm px-4 py-3">
            <p className="text-sm text-gray-900 leading-relaxed">
              {activeExample.conversation.assistant}
            </p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <button
        onClick={handleTryThis}
        className="w-full bg-primary hover:bg-primary-600 text-white font-medium px-6 py-3 rounded-lg transition-colors duration-200"
      >
        Try this question
      </button>
    </div>
  )
}
