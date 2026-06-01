'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { apiClient } from '@/shared/lib/api-client'
import type { SessionSummary } from '@/shared/lib/api-client/types'
import { ArrowLeft, MessageSquare, Clock } from 'lucide-react'
import { WatercolorBackground } from '@/shared/components/ui/WatercolorBackground'

const PAGE_SIZE = 20

function formatRelativeTime(isoString: string | null | undefined): string {
  if (!isoString) return 'Unknown'
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadSessions = async (currentOffset: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.listSessions(currentOffset, PAGE_SIZE)
      setSessions(data.sessions)
      setTotal(data.total)
      setOffset(data.offset)
    } catch (err) {
      setError('Failed to load sessions. Please try again.')
      console.error('Failed to list sessions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSessions(0)
  }, [])

  const hasMore = offset + sessions.length < total
  const hasPrevious = offset > 0

  return (
    <main className="relative min-h-screen">
      <WatercolorBackground />
      <div className="w-full max-w-3xl h-[calc(100vh-2rem)] my-4 mx-4 md:mx-auto glass-panel rounded-2xl overflow-hidden relative z-10 flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-border/50 bg-white/50 backdrop-blur-sm flex items-center gap-4 z-20">
          <Link
            href="/"
            className="p-2 text-muted-foreground hover:text-primary transition-colors rounded-full hover:bg-primary/5"
            title="Back to home"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-primary-800 tracking-tight">
              Chat History
            </h1>
            <p className="text-xs text-muted-foreground">
              {total} {total === 1 ? 'conversation' : 'conversations'}
            </p>
          </div>
        </div>

        {/* Session List */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
          {loading && sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mb-4"></div>
              <p className="text-sm text-muted-foreground">Loading sessions...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <p className="text-sm text-red-600 mb-4">{error}</p>
              <button
                onClick={() => loadSessions(offset)}
                className="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary-600"
              >
                Retry
              </button>
            </div>
          ) : sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-60">
              <MessageSquare size={48} className="mb-4 text-muted-foreground" />
              <h2 className="text-lg font-medium text-primary-900 mb-2">
                No conversations yet
              </h2>
              <p className="text-sm text-muted-foreground max-w-md mb-6">
                Start a chat to see your history here.
              </p>
              <Link
                href="/chat"
                className="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary-600"
              >
                Start chatting
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <Link
                  key={session.id}
                  href={`/chat?sessionId=${session.id}`}
                  className="block p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-border/50 hover:bg-white/70 hover:border-primary/20 transition-all group"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/5 text-primary group-hover:bg-primary/10 transition-colors">
                      <MessageSquare size={16} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-primary-900 truncate">
                        {session.first_message_preview || 'New conversation'}
                      </p>
                      <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {formatRelativeTime(session.updated_at || session.created_at)}
                        </span>
                        <span>{session.message_count} messages</span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* Pagination */}
          {!loading && sessions.length > 0 && (hasPrevious || hasMore) && (
            <div className="flex justify-center gap-4 mt-6 pt-4 border-t border-border/30">
              <button
                onClick={() => loadSessions(offset - PAGE_SIZE)}
                disabled={!hasPrevious}
                className="px-4 py-2 text-sm rounded-lg border border-border/50 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-white/50 transition-colors"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-sm text-muted-foreground">
                {offset + 1}–{offset + sessions.length} of {total}
              </span>
              <button
                onClick={() => loadSessions(offset + PAGE_SIZE)}
                disabled={!hasMore}
                className="px-4 py-2 text-sm rounded-lg border border-border/50 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-white/50 transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
