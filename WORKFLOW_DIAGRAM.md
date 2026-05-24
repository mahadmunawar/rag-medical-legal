# Workflow Architecture Diagram

## Complete Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ CHAT INPUT                                                          │
│ "What is chemotherapy?"                                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 1. SANITIZE INPUT                                                   │
│    • Remove injection attempts                                      │
│    • Lowercase                                                      │
│    • Output: clean_query = "what is chemotherapy?"                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. RULE CLASSIFIER (KEYWORD CHECK)                                  │
│    Regex: \bcancer\b|\btumor\b|\bchemotherapy\b|...               │
│                                                                     │
│    Question: Does text match medical keywords?                     │
└──────────────────┬──────────────────────────┬───────────────────────┘
                   │ YES                      │ NO
         ┌─────────▼──────────┐    ┌─────────▼──────────┐
         │ SET MEDICAL ROUTE  │    │ LEGAL RULE CHECK   │
         │ route = "medical"  │    │ (Check for law,    │
         │                    │    │  contract, sue,    │
         │                    │    │  court, attorney)  │
         └─────────┬──────────┘    └────┬──────────┬────┘
                   │                    │ YES      │ NO
                   │         ┌──────────▼────┐    │
                   │         │SET LEGAL ROUTE│    │
                   │         │route="legal"  │    │
                   │         └────────┬───────┘    │
                   │                  │           │
                   │                  │    ┌──────▼────────────┐
                   │                  │    │TEXT CLASSIFIER    │
                   │                  │    │(LLM-based)        │
                   │                  │    │ Query Groq:       │
                   │                  │    │ medical/legal/    │
                   │                  │    │ other?            │
                   │                  │    └────────┬──────────┘
                   │                  │             │
                   │                  │    ┌────────▼───────────┐
                   │                  │    │NORMALIZE CLASSIFIER│
                   │                  │    │Extract category    │
                   │                  │    └────────┬───────────┘
                   │                  │             │
                   └──────────────┬───┴─────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ ROUTE SWITCH (3 OUTPUTS)│
                    └──┬────────────┬──────────┬┘
        ┌──────────────┘            │          └──────────────┐
        │                           │                          │
   MEDICAL                      LEGAL                      OTHER
        │                           │                          │
        ▼                           ▼                          ▼
   ┌─────────────┐        ┌──────────────┐        ┌──────────────────┐
   │GET MEDICAL  │        │ GET LEGAL    │        │NO RAG NEEDED     │
   │CONTEXT      │        │ CONTEXT      │        │ (Skip to LLM)    │
   │             │        │              │        │                  │
   │ • Embed     │        │ • Embed      │        │ Question only    │
   │   query    │        │   query      │        │                  │
   │ • Search    │        │ • Search     │        │                  │
   │   Qdrant    │        │   Qdrant     │        │                  │
   │ • Get top-3 │        │ • Get top-3  │        │                  │
   │   results   │        │   results    │        │                  │
   └──────┬──────┘        └──────┬───────┘        └────────┬─────────┘
          │                      │                        │
          ▼                      ▼                        ▼
   ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────┐
   │BASIC LLM CHAIN   │  │ BASIC LLM CHAIN   │  │ BASIC LLM CHAIN    │
   │MEDICAL           │  │ LEGAL             │  │ GENERAL            │
   │                  │  │                   │  │                    │
   │System Prompt:    │  │System Prompt:     │  │System Prompt:      │
   │ "You are medical │  │ "You are legal    │  │ "Answer clearly    │
   │  assistant.      │  │  assistant.       │  │  and concisely."   │
   │  Use ONLY this   │  │  General info     │  │                    │
   │  context.        │  │  only. No legal   │  │ Context: NONE      │
   │  Do NOT diagnose │  │  advice.          │  │ Query only         │
   │  or prescribe."  │  │  End with legal   │  │                    │
   │                  │  │  disclaimer."     │  │                    │
   │Context: From RAG │  │Context: From RAG  │  │                    │
   │ search           │  │ search            │  │                    │
   │                  │  │                   │  │                    │
   │ ▲               │  │ ▲                 │  │ ▲                  │
   │ │               │  │ │                 │  │ │                  │
   │ └─── Groq       │  │ └─── Groq         │  │ └─── Groq          │
   │    Chat Model  │  │    Chat Model    │  │    Chat Model      │
   │                  │  │                   │  │                    │
   └──────┬───────────┘  └────┬──────────────┘  └─────┬──────────────┘
          │                   │                       │
          └───────────┬───────┴───────────────────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │ OUTPUT FILTER           │
          │                         │
          │ Check for blocked words:│
          │ • "system prompt"       │
          │ • "ignore all"          │
          │ • "jailbreak"           │
          │ • "act as"              │
          │                         │
          │ If blocked → reply      │
          │ "Response blocked."     │
          └────────┬────────────────┘
                   │
                   ▼
          ┌─────────────────────────┐
          │ SEND RESPONSE           │
          │                         │
          │ Output: safe_output     │
          └────────┬────────────────┘
                   │
                   ▼
          ┌─────────────────────────┐
          │ USER RECEIVES ANSWER    │
          │                         │
          │ "Chemotherapy is a      │
          │  treatment using drugs  │
          │  to kill cancer cells." │
          │                         │
          │ "This is not medical    │
          │  advice."               │
          └─────────────────────────┘
```

---

## Token Flow Per Query

```
REQUEST TOKENS (Input)
├─ Sanitize Input:        ~10 tokens
├─ Rule Classifier:       ~5 tokens (regex check)
├─ Legal Rule Check:      ~5 tokens (regex check)
├─ Text Classifier:       ~50 tokens (Groq classify)
└─ Get Context:
   ├─ Embed query:        ~50 tokens (Gemini)
   └─ Qdrant search:      0 tokens (vector DB)

RESPONSE TOKENS (Output)
├─ Groq answer gen:       ~400 tokens
└─ Output Filter:         ~5 tokens

TOTAL: ~525 tokens per request
= 26% of Groq daily free quota
= 35% of Gemini embeddings daily quota

✅ Safe to run 27 queries/hour continuously
```

---

## Data Flow for Medical Query

```
Input JSON:
{
  "chatInput": "What are chemo side effects?"
}
              ↓
              │ Sanitize Input
              ▼
{
  "clean_query": "what are chemo side effects?",
  "original": "What are chemo side effects?"
}
              ↓
              │ Rule Classifier (matches "chemo" + "effects")
              ▼
{
  "clean_query": "...",
  "route": "medical"  ← keyword match
}
              ↓
              │ Get Medical Context (Code node)
              ▼
{
  "context_text": "Chemotherapy side effects include nausea, hair loss, fatigue... [from Qdrant]",
  "clean_query": "what are chemo side effects?"
}
              ↓
              │ Basic LLM Chain Medical
              ▼
{
  "text": "Chemotherapy side effects vary by person... This is not medical advice.",
  "category": "medical",
  "context_text": "..."
}
              ↓
              │ Output Filter
              ▼
{
  "safe_output": "Chemotherapy side effects vary by person... This is not medical advice."
}
              ↓
              │ Send Response (Webhook)
              ▼
HTTP 200 Response:
{
  "output": "Chemotherapy side effects vary by person... This is not medical advice."
}
```

---

## Decision Tree

```
                    USER QUERY
                        │
                ┌───────┴───────┐
                │               │
            Contains        No Medical
          Medical Words     Keywords
            (Regex)         (Regex)
                │               │
                │ YES           │ NO
                ▼               │
          ┌──────────┐         │
          │route =   │         │
          │"medical" │         │
          └──────────┘         │
                                │
                        ┌───────┴────────┐
                        │                │
                    Contains         No Legal
                   Legal Words       Keywords
                     (Regex)          (Regex)
                        │                │
                        │ YES            │ NO
                        ▼                │
                    ┌──────────┐        │
                    │route =   │        │
                    │"legal"   │        │
                    └──────────┘        │
                                        │
                                ┌───────▼──────────┐
                                │                  │
                          LLM CLASSIFY             │
                          (Groq Text              │
                           Classifier)            │
                                │                  │
                    ┌───────┬───┴───┬──────────┐   │
                    │       │       │          │   │
               medical  legal  other    ???    │   │
                    │       │       │          │   │
                    └─┬─────┴───┬──┴──────────┘   │
                      │         │                  │
                    route =   route = or        other
                  "medical"   "legal"
                      │         │
                      ▼         ▼
                  Medical    Legal
                  Embedding  Embedding
                      │         │
                      ▼         ▼
                  Qdrant      Qdrant
                  Search      Search
                      │         │
                      ▼         ▼
                    Get         Get
                   Medical     Legal
                   Context    Context
                      │         │
                      └────┬────┘
                           │
                    ┌──────▼─────┐
                    │            │
                Medical Gen  Legal Gen  Other Gen
                   LLM          LLM         LLM
                    │            │          │
                    └────────┬────┴──────────┘
                             │
                       Output Filter
                             │
                          User Gets
                          Response
```

---

## Node Dependencies

```
Chat Trigger
    ↓
    └─→ Sanitize Input
        ↓
        └─→ Rule Classifier
            ├─→ Set Medical Route ──┐
            │                       │
            ├─→ Legal Rule Check   │
            │   ├─→ Set Legal Route │
            │   │                   │
            │   └─→ Text Classifier ─→ Normalize Classifier
            │                                   │
            └─────────────────────────→ Route Switch
                                        ├─ output[0] → Get Medical Context
                                        ├─ output[1] → Get Legal Context
                                        └─ output[2] → Basic LLM Chain General

Get Medical Context ──→ Basic LLM Chain Medical ──┐
Get Legal Context ───→ Basic LLM Chain Legal    ──→ Output Filter
Basic LLM Chain General (connected above) ────────┘

Output Filter ──→ Send Response
```

---

**Note:** All Groq Chat Model nodes (Medical, Legal, General) are connected to their respective LLM Chain nodes via the `ai_languageModel` connection type (shown on bottom port).
