# **App Name**: LawLens AI

## Core Features:

- AI Chat Assistant: Provides legal advice using Llama 3.1 in a step-by-step checklist format with checkboxes and links to .gov/.nic sites.
- Legal Document Summarization: Analyzes legal PDFs using a custom RAG pipeline, generating mind maps and flowcharts to explain documents better. Uses Llama 3.1 and Gemini 1.5 Pro as reasoning tools to identify what parts of the uploaded legal text to incorporate in the output.
- Lawyer Directory & Booking: Lists expert lawyers with specialities and availability, allowing users to book appointments (limited by subscription tier).
- Subscription Management: Manages user subscription tiers (Basic, Standard, Premium, Platinum) and enforces feature limits based on the chosen tier.
- Document Upload: Allows users to upload legal documents for case study analysis.
- Visual Output Generation: Generates visual mind maps and flowcharts from case studies using Mermaid/Graphviz.
- User Authentication: Handles user signup, login with JWT and refresh tokens, and password hashing using bcrypt.

## Style Guidelines:

- Primary color: Deep navy blue (#1A237E), evoking trust and professionalism, reminiscent of classic legal aesthetics.
- Background color: Very light grayish-blue (#F0F4FF), providing a clean and modern canvas.
- Accent color: Muted gold (#BDBDBD), used sparingly for highlighting key actions and information, subtly symbolizing wisdom.
- Headline font: 'Belleza', a sans-serif suitable for fashion, art, and design, offering a blend of style and readability; use 'Alegreya' for body text (serif).
- Use minimalist icons related to law, justice, and document management. Simple, professional icons for key navigation items.
- Clean and structured layout with a clear separation of content areas. Consistent use of spacing and padding.
- Subtle transitions and animations for loading states and user interactions. Smooth transitions between pages and sections to enhance the user experience.