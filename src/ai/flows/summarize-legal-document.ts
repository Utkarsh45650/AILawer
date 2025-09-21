'use server';

/**
 * @fileOverview Summarizes a legal document and generates a mind map and flowchart.
 *
 * - summarizeLegalDocument - A function that takes a legal document (PDF) as input and returns a summarized version, along with a mind map and flowchart.
 * - SummarizeLegalDocumentInput - The input type for the summarizeLegalDocument function.
 * - SummarizeLegalDocumentOutput - The return type for the summarizeLegalDocument function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { googleAI } from '@genkit-ai/googleai';
import wav from 'wav';

const SummarizeLegalDocumentInputSchema = z.object({
  documentDataUri: z
    .string()
    .describe(
      "A legal document (PDF), as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'."
    ),
});
export type SummarizeLegalDocumentInput = z.infer<typeof SummarizeLegalDocumentInputSchema>;

const SummarizeLegalDocumentOutputSchema = z.object({
  summary: z.string().describe('A summarized version of the legal document.'),
  mindMap: z.string().describe('A mind map representation of the legal document.'),
  flowchart: z.string().describe('A flowchart representation of the legal document.'),
});
export type SummarizeLegalDocumentOutput = z.infer<typeof SummarizeLegalDocumentOutputSchema>;

export async function summarizeLegalDocument(
  input: SummarizeLegalDocumentInput
): Promise<SummarizeLegalDocumentOutput> {
  return summarizeLegalDocumentFlow(input);
}

const summarizationPrompt = ai.definePrompt({
  name: 'summarizationPrompt',
  input: {schema: SummarizeLegalDocumentInputSchema},
  output: {schema: z.object({summary: z.string()})},
  prompt: `You are a legal expert. Summarize the following legal document.

Legal Document: {{media url=documentDataUri}}`,
});

const mindMapPrompt = ai.definePrompt({
  name: 'mindMapPrompt',
  input: {schema: z.object({summary: z.string()})},
  output: {schema: z.object({mindMap: z.string()})},
  prompt: `You are an expert at creating mind maps. Create a mind map from the following summary. Use Mermaid syntax.

Summary: {{{summary}}}`,
});

const flowchartPrompt = ai.definePrompt({
  name: 'flowchartPrompt',
  input: {schema: z.object({summary: z.string()})},
  output: {schema: z.object({flowchart: z.string()})},
  prompt: `You are an expert at creating flowcharts. Create a flowchart from the following summary. Use Mermaid syntax.

Summary: {{{summary}}}`,
});

const summarizeLegalDocumentFlow = ai.defineFlow(
  {
    name: 'summarizeLegalDocumentFlow',
    inputSchema: SummarizeLegalDocumentInputSchema,
    outputSchema: SummarizeLegalDocumentOutputSchema,
  },
  async input => {
    const {output: summarizationOutput} = await summarizationPrompt(input);
    const {output: mindMapOutput} = await mindMapPrompt({
      summary: summarizationOutput!.summary,
    });
    const {output: flowchartOutput} = await flowchartPrompt({
      summary: summarizationOutput!.summary,
    });

    return {
      summary: summarizationOutput!.summary,
      mindMap: mindMapOutput!.mindMap,
      flowchart: flowchartOutput!.flowchart,
    };
  }
);
