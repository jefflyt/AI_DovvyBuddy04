import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
}

export const ChatMessage = ({ role, content, timestamp }: ChatMessageProps) => {
    const isUser = role === 'user';
    const isSystem = role === 'system';

    return (
        <div
            className={cn(
                "flex w-full mb-6",
                isUser ? "justify-end" : "justify-start",
                isSystem && "justify-center"
            )}
        >
            <div
                className={cn(
                    "flex max-w-[85%] md:max-w-[75%] gap-3",
                    isUser ? "flex-row-reverse" : "flex-row"
                )}
            >
                {/* Avatar */}
                {!isSystem && (
                    <div
                        className={cn(
                            "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm",
                            isUser ? "bg-primary text-primary-foreground" : "bg-white text-primary border border-primary/20"
                        )}
                    >
                        {isUser ? <User size={16} /> : <Bot size={16} />}
                    </div>
                )}

                {/* Message Bubble */}
                <div
                    className={cn(
                        "relative px-4 py-3 shadow-md",
                        isSystem
                            ? "bg-accent/10 border border-accent/20 text-accent-foreground text-center rounded-lg text-sm"
                            : "rounded-2xl",
                        isUser
                            ? "bg-primary text-primary-foreground rounded-tr-sm"
                            : "bg-white text-foreground border border-border/50 rounded-tl-sm"
                    )}
                >
                    <div className="prose prose-sm max-w-none break-words leading-relaxed">
                        {isSystem ? (
                            <p>{content}</p>
                        ) : (
                            <ReactMarkdown
                                components={{
                                    ul: ({ node: _node, ...props }) => <ul className="pl-4 my-2 list-disc" {...props} />,
                                    ol: ({ node: _node, ...props }) => <ol className="pl-4 my-2 list-decimal" {...props} />,
                                    li: ({ node: _node, ...props }) => <li className="mb-1" {...props} />,
                                    p: ({ node: _node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                    strong: ({ node: _node, ...props }) => <strong className="font-semibold" {...props} />,
                                    a: ({ node: _node, ...props }) => <a className="underline hover:opacity-80 transition-opacity" target="_blank" rel="noopener noreferrer" {...props} />,
                                }}
                            >
                                {content}
                            </ReactMarkdown>
                        )}
                    </div>

                    <div
                        className={cn(
                            "text-[10px] mt-1 opacity-70",
                            isUser ? "text-primary-foreground/80 text-right" : "text-muted-foreground text-left",
                            isSystem && "justify-center text-center"
                        )}
                    >
                        {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                </div>
            </div>
        </div>
    );
};
