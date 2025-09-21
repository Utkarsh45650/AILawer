import SummarizationInterface from '@/app/components/summarize/SummarizationInterface';

export default function SummarizePage() {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="font-headline text-3xl font-bold">Legal Document Summarization</h1>
        <p className="text-muted-foreground">
          Upload a legal document (PDF) to generate a summary, mind map, and flowchart.
        </p>
      </div>
      <SummarizationInterface />
    </div>
  );
}
