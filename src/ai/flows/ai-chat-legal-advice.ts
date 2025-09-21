'use server';
/**
 * @fileOverview An AI chat assistant for providing legal advice in a step-by-step checklist format.
 *
 * - aiChatLegalAdvice - A function that generates legal advice checklist.
 * - AiChatLegalAdviceInput - The input type for the aiChatLegalAdvice function.
 * - AiChatLegalAdviceOutput - The return type for the aiChatLegalAdvice function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AiChatLegalAdviceInputSchema = z.object({
  query: z.string().describe('The legal question or topic for which advice is sought.'),
});
export type AiChatLegalAdviceInput = z.infer<typeof AiChatLegalAdviceInputSchema>;

const AiChatLegalAdviceOutputSchema = z.object({
  adviceChecklist: z.string().describe('A step-by-step checklist providing legal advice, with links to .gov/.nic websites.'),
});
export type AiChatLegalAdviceOutput = z.infer<typeof AiChatLegalAdviceOutputSchema>;

export async function aiChatLegalAdvice(input: AiChatLegalAdviceInput): Promise<AiChatLegalAdviceOutput> {
  return aiChatLegalAdviceFlow(input);
}

const prompt = ai.definePrompt({
  name: 'aiChatLegalAdvicePrompt',
  input: {schema: AiChatLegalAdviceInputSchema},
  output: {schema: AiChatLegalAdviceOutputSchema},
  prompt: `You are a legal AI assistant that provides legal advice in the form of a step-by-step checklist.
  For each step, include links to relevant .gov/.nic websites.
  Respond to the following query: {{{query}}}
  Format your response as a markdown checklist.
  `,
});

const aiChatLegalAdviceFlow = ai.defineFlow(
  {
    name: 'aiChatLegalAdviceFlow',
    inputSchema: AiChatLegalAdviceInputSchema,
    outputSchema: AiChatLegalAdviceOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
