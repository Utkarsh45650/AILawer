"use server";

import { aiChatLegalAdvice, AiChatLegalAdviceInput } from "@/ai/flows/ai-chat-legal-advice";
import { summarizeLegalDocument, SummarizeLegalDocumentInput } from "@/ai/flows/summarize-legal-document";

export async function getAiChatResponse(input: AiChatLegalAdviceInput) {
  try {
    const result = await aiChatLegalAdvice(input);
    return { success: true, data: result };
  } catch (error) {
    console.error("Error in getAiChatResponse:", error);
    return { success: false, error: "Failed to get AI response." };
  }
}

export async function getDocumentSummary(input: SummarizeLegalDocumentInput) {
  try {
    const result = await summarizeLegalDocument(input);
    return { success: true, data: result };
  } catch (error) {
    console.error("Error in getDocumentSummary:", error);
    return { success: false, error: "Failed to summarize document." };
  }
}
