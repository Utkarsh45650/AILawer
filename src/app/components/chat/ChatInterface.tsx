'use client';

import { getAiChatResponse } from '@/lib/actions';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, Send, User } from 'lucide-react';
import { FormEvent, useRef, useState, useTransition } from 'react';
import { MarkdownRenderer } from '../MarkdownRenderer';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import { AppLogo } from '../AppLogo';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

const initialMessage: Message = {
  role: 'assistant',
  content: "Hello! I'm LawLens AI. How can I help you with your legal questions today? Please note that I am an AI assistant and my advice does not constitute legal counsel.",
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([initialMessage]);
  const [input, setInput] = useState('');
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    startTransition(async () => {
      const response = await getAiChatResponse({ query: input });
      if (response.success && response.data) {
        const assistantMessage: Message = { role: 'assistant', content: response.data.adviceChecklist };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        toast({
          variant: 'destructive',
          title: 'Error',
          description: response.error || 'Something went wrong.',
        });
        // Remove the user message if the API call fails
        setMessages((prev) => prev.slice(0, prev.length - 1));
      }
    });
  };
  
  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-6">
          {messages.map((message, index) => (
            <div key={index} className={`flex items-start gap-4 ${message.role === 'user' ? 'justify-end' : ''}`}>
              {message.role === 'assistant' && (
                <Avatar className="h-8 w-8 border">
                   <div className="flex h-full w-full items-center justify-center rounded-full bg-primary">
                    <Bot className="h-5 w-5 text-primary-foreground" />
                   </div>
                </Avatar>
              )}
              <div
                className={`max-w-[75%] rounded-lg p-3 text-sm ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <MarkdownRenderer content={message.content} />
              </div>
              {message.role === 'user' && (
                <Avatar className="h-8 w-8 border">
                   <div className="flex h-full w-full items-center justify-center rounded-full bg-secondary">
                    <User className="h-5 w-5 text-secondary-foreground" />
                   </div>
                </Avatar>
              )}
            </div>
          ))}
           {isPending && (
            <div className="flex items-start gap-4">
               <Avatar className="h-8 w-8 border">
                 <div className="flex h-full w-full items-center justify-center rounded-full bg-primary">
                    <Bot className="h-5 w-5 text-primary-foreground" />
                   </div>
              </Avatar>
              <div className="max-w-[75%] rounded-lg bg-muted p-3">
                <div className="space-y-2">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about property law, contracts, etc."
            className="flex-1"
            disabled={isPending}
          />
          <Button type="submit" size="icon" disabled={!input.trim() || isPending}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
