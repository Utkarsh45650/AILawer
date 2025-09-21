import ChatInterface from '@/app/components/chat/ChatInterface';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4">
        <h1 className="font-headline text-3xl font-bold">AI Chat Assistant</h1>
        <p className="text-muted-foreground">
          Get step-by-step legal advice. For informational purposes only. Always consult a qualified lawyer.
        </p>
      </div>
      <Card className="flex-1">
        <ChatInterface />
      </Card>
    </div>
  );
}
