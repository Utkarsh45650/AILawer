'use client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import { ClassAttributes, HTMLAttributes } from 'react';

export function MarkdownRenderer({ content, className }: { content: string, className?: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className={cn("prose prose-sm dark:prose-invert max-w-none prose-p:my-2 prose-ul:my-2 prose-li:my-0", className)}
      components={{
        a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline" />,
        p: ({node, ...props}) => <p {...props} className="text-foreground" />,
        ul: ({node, ordered, ...props}) => <ul {...props} className="text-foreground" />,
        ol: ({node, ordered, ...props}) => <ol {...props} className="text-foreground" />,
        li: ({node, ordered, ...props}) => <li {...props} className="text-foreground" />,
        strong: ({node, ...props}) => <strong {...props} className="text-foreground font-bold" />,
        h1: ({node, ...props}) => <h1 {...props} className="font-headline text-foreground" />,
        h2: ({node, ...props}) => <h2 {...props} className="font-headline text-foreground" />,
        h3: ({node, ...props}) => <h3 {...props} className="font-headline text-foreground" />,
        input: ({node, disabled, ...props}) => {
          if (props.type === 'checkbox') {
            return <input {...props} disabled={false} className="mr-2" />;
          }
          return <input {...props} />;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
