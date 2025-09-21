'use client';

import { getDocumentSummary } from '@/lib/actions';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { FileUp, Loader2 } from 'lucide-react';
import { useState, useTransition } from 'react';
import MermaidChart from '../MermaidChart';
import { MarkdownRenderer } from '../MarkdownRenderer';
import { Skeleton } from '@/components/ui/skeleton';

type SummaryResult = {
  summary: string;
  mindMap: string;
  flowchart: string;
};

export default function SummarizationInterface() {
  const [documentDataUri, setDocumentDataUri] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [result, setResult] = useState<SummaryResult | null>(null);
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        toast({
          variant: 'destructive',
          title: 'Invalid File Type',
          description: 'Please upload a PDF file.',
        });
        return;
      }
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        setDocumentDataUri(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!documentDataUri || isPending) return;

    setResult(null);

    startTransition(async () => {
      const response = await getDocumentSummary({ documentDataUri });
      if (response.success && response.data) {
        setResult(response.data);
      } else {
        toast({
          variant: 'destructive',
          title: 'Summarization Failed',
          description: response.error || 'An unexpected error occurred.',
        });
      }
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="document-upload" className="mb-2 block font-semibold">
                Upload Document
              </Label>
              <div className="flex items-center gap-4">
                <Label
                  htmlFor="document-upload"
                  className="flex-1 cursor-pointer rounded-md border-2 border-dashed border-muted-foreground/50 p-4 text-center text-muted-foreground transition-colors hover:border-primary hover:bg-primary/5 hover:text-primary"
                >
                  <FileUp className="mx-auto mb-2 h-8 w-8" />
                  {fileName ? (
                    <span className="font-semibold text-foreground">{fileName}</span>
                  ) : (
                    'Click to upload or drag & drop a PDF'
                  )}
                </Label>
                <Input
                  id="document-upload"
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept="application/pdf"
                />
                <Button type="submit" disabled={!documentDataUri || isPending} className="self-end">
                  {isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    'Generate Summary'
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
      
      {isPending && (
        <Card>
            <CardContent className="p-6 space-y-4">
              <Skeleton className="h-8 w-1/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
        </Card>
      )}

      {result && (
        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="mindmap">Mind Map</TabsTrigger>
            <TabsTrigger value="flowchart">Flowchart</TabsTrigger>
          </TabsList>
          <TabsContent value="summary">
            <Card>
              <CardContent className="p-6">
                <MarkdownRenderer content={result.summary} />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="mindmap">
            <Card>
              <CardContent className="p-0">
                <MermaidChart chart={result.mindMap} />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="flowchart">
            <Card>
              <CardContent className="p-0">
                <MermaidChart chart={result.flowchart} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
