# Source Discovery Plan

**Last Updated:** 2026-01-22  
**Status:** Planning Phase - Source Discovery

This document outlines the source discovery plan for all 22 canonical requirements and 7 company context domains. Each requirement/domain must have at least one primary authoritative source and one secondary explanatory source.

---

## CORE REQUIREMENTS (1-11)

### Requirement 1: 4+ years of commercial experience in fullstack TypeScript development

**Category:** Experience  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** TypeScript Official Handbook
- **URL:** https://www.typescriptlang.org/docs/handbook/intro.html
- **Type:** Official documentation
- **Freshness:** Continuously updated (2024-2025)
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** "TypeScript Deep Dive" by Basarat Ali Syed
- **URL:** https://basarat.gitbook.io/typescript/
- **Type:** Technical reference book (online)
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** TypeScript GitHub Repository - Best Practices
- **URL:** https://github.com/microsoft/TypeScript/wiki/Coding-guidelines
- **Type:** Official repository guidelines
- **Freshness:** 2024
- **Chunk Types:** primary, tradeoff

- **Source:** "Fullstack TypeScript Patterns" - Engineering Blog
- **URL:** https://kentcdodds.com/blog/typescript (or similar high-quality blog)
- **Type:** Engineering blog
- **Freshness:** 2024-2025
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 2: Strong experience with React 18 and modern React patterns (hooks, context, TanStack Query)

**Category:** Frontend  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** React 18 Official Documentation
- **URL:** https://react.dev/
- **Type:** Official documentation
- **Freshness:** 2024-2025 (React 18 released 2022, docs continuously updated)
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** TanStack Query (React Query) Official Documentation
- **URL:** https://tanstack.com/query/latest
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** React Hooks Official Documentation
- **URL:** https://react.dev/reference/react
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

- **Source:** "React 18 Features and Patterns" - Engineering Blog
- **URL:** https://blog.logrocket.com/react-18-features/ (or similar)
- **Type:** Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

- **Source:** "Modern React Patterns" - Technical Article
- **URL:** https://kentcdodds.com/blog/compound-components-with-react-hooks (or similar)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 3: Production experience with Node.js and NestJS (or similar opinionated frameworks)

**Category:** Backend  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** Node.js Official Documentation
- **URL:** https://nodejs.org/docs/latest/api/
- **Type:** Official documentation
- **Freshness:** 2024-2025 (Node.js LTS versions)
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** NestJS Official Documentation
- **URL:** https://docs.nestjs.com/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "Node.js Best Practices" - GitHub Repository
- **URL:** https://github.com/goldbergyoni/nodebestpractices
- **Type:** Community best practices
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

- **Source:** "NestJS Architecture Patterns" - Engineering Blog
- **URL:** https://blog.logrocket.com/nestjs-architecture-patterns/ (or similar)
- **Type:** Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 4: Solid knowledge of PostgreSQL — schema design, migrations, query optimization, JSONB

**Category:** Database  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** PostgreSQL Official Documentation
- **URL:** https://www.postgresql.org/docs/current/
- **Type:** Official documentation
- **Freshness:** 2024-2025 (PostgreSQL 15/16)
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** "PostgreSQL Performance Optimization" - Engineering Blog
- **URL:** https://www.postgresql.org/docs/current/performance-tips.html
- **Type:** Official documentation (performance section)
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "PostgreSQL JSONB Guide" - Official Documentation
- **URL:** https://www.postgresql.org/docs/current/datatype-json.html
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

- **Source:** "PostgreSQL Schema Design Best Practices" - Technical Article
- **URL:** https://www.postgresql.org/docs/current/ddl.html (or engineering blog)
- **Type:** Official documentation / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

- **Source:** "PostgreSQL Query Optimization" - Engineering Blog
- **URL:** https://www.postgresql.org/docs/current/using-explain.html (or similar)
- **Type:** Official documentation / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 5: Experience with Redis for caching, pub/sub, or job queues

**Category:** Infrastructure  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** Redis Official Documentation
- **URL:** https://redis.io/docs/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** "Redis Patterns" - Engineering Blog
- **URL:** https://redis.io/docs/manual/patterns/ (official patterns guide)
- **Type:** Official documentation (patterns section)
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "Redis Pub/Sub Guide" - Official Documentation
- **URL:** https://redis.io/docs/manual/pubsub/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

- **Source:** "Redis for Job Queues" - Technical Article
- **URL:** https://redis.io/docs/manual/patterns/queue/ (or engineering blog)
- **Type:** Official documentation / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 6: Understanding of REST API design and authentication (JWT, OAuth flows)

**Category:** API  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** REST API Design - RFC 7231 (HTTP/1.1 Semantics)
- **URL:** https://datatracker.ietf.org/doc/html/rfc7231
- **Type:** RFC standard
- **Freshness:** 2014 (historical but authoritative)
- **Chunk Types:** primary, interview_question
- **Note:** Marked as historical but still authoritative for REST principles

#### Secondary Explanatory Source
- **Source:** OAuth 2.0 Official Specification
- **URL:** https://oauth.net/2/
- **Type:** Official specification
- **Freshness:** 2012 (historical but authoritative)
- **Chunk Types:** primary, interview_question
- **Note:** Marked as historical but still authoritative

#### Additional Sources
- **Source:** "JWT.io" - JWT Specification and Best Practices
- **URL:** https://jwt.io/introduction
- **Type:** Official specification site
- **Freshness:** 2024
- **Chunk Types:** primary, secondary, tradeoff

- **Source:** "REST API Design Best Practices" - Engineering Blog
- **URL:** https://restfulapi.net/ (or similar high-quality resource)
- **Type:** Technical reference
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

- **Source:** "OAuth 2.0 Security Best Practices" - Technical Article
- **URL:** https://oauth.net/2/security-best-practices/ (or engineering blog)
- **Type:** Official best practices / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 7: Experience integrating third-party APIs (payment gateways, external services)

**Category:** Integration  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** Stripe API Documentation
- **URL:** https://stripe.com/docs/api
- **Type:** Official API documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** "Third-Party API Integration Patterns" - Engineering Blog
- **URL:** https://stripe.com/docs/development_guide (or similar pattern guide)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** "API Integration Best Practices" - Technical Article
- **URL:** https://www.postman.com/api-platform/api-integration/ (or similar)
- **Type:** Technical reference
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

- **Source:** "Payment Gateway Integration Patterns" - Engineering Blog
- **URL:** https://stripe.com/docs/payments/accept-a-payment (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 8: Familiarity with AI/LLM APIs (OpenAI, Claude, or similar) — prompt engineering basics

**Category:** AI  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** OpenAI API Documentation
- **URL:** https://platform.openai.com/docs
- **Type:** Official API documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** Anthropic Claude API Documentation
- **URL:** https://docs.anthropic.com/claude/docs
- **Type:** Official API documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "Prompt Engineering Guide" - OpenAI
- **URL:** https://platform.openai.com/docs/guides/prompt-engineering
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, interview_question

- **Source:** "LLM Integration Patterns" - Engineering Blog
- **URL:** https://www.anthropic.com/research (or similar technical article)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 9: Product thinking: understanding why you're building, not just how

**Category:** Soft Skills  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** "Inspired: How to Create Tech Products Customers Love" - Marty Cagan
- **URL:** https://www.svpg.com/inspired-how-to-create-tech-products-customers-love/ (book summary/articles)
- **Type:** Product management reference
- **Freshness:** 2023 (book updated)
- **Chunk Types:** primary, secondary, interview_question

#### Secondary Explanatory Source
- **Source:** "Product Thinking for Engineers" - Engineering Blog
- **URL:** https://www.intercom.com/blog/product-thinking/ (or similar high-quality article)
- **Type:** Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, interview_question

#### Additional Sources
- **Source:** "Technical Decision Making with Product Context" - Technical Article
- **URL:** https://www.mindtheproduct.com/ (or similar product management resource)
- **Type:** Product management resource
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 10: Ability to work autonomously in a fast-paced startup environment

**Category:** Soft Skills  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** "The Lean Startup" - Eric Ries (principles and practices)
- **URL:** https://theleanstartup.com/principles-for-lean-startups (or book summary)
- **Type:** Business/startup reference
- **Freshness:** 2023 (book updated)
- **Chunk Types:** primary, secondary, interview_question

#### Secondary Explanatory Source
- **Source:** "Working in Fast-Paced Environments" - Engineering Blog
- **URL:** https://www.atlassian.com/agile/startups (or similar)
- **Type:** Engineering blog / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, interview_question

#### Additional Sources
- **Source:** "Autonomous Work Patterns" - Technical Article
- **URL:** https://www.pmi.org/learning/library/autonomous-teams-agile-9965 (or similar)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 11: English: Upper-Intermediate+ (written communication with international team)

**Category:** Communication  
**Priority:** Required

#### Primary Authoritative Source
- **Source:** "Technical Writing for Engineers" - Engineering Blog
- **URL:** https://developers.google.com/tech-writing (Google Technical Writing Guide)
- **Type:** Official technical writing guide
- **Freshness:** 2024
- **Chunk Types:** primary, secondary, interview_question

#### Secondary Explanatory Source
- **Source:** "International Team Communication" - Technical Article
- **URL:** https://www.atlassian.com/blog/teamwork/remote-team-communication (or similar)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, interview_question

#### Additional Sources
- **Source:** "Written Communication Best Practices" - Technical Article
- **URL:** https://www.grammarly.com/blog/technical-writing/ (or similar)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff

---

## PLUS REQUIREMENTS (12-22)

### Requirement 12: Experience with BullMQ or similar job queue systems (Agenda, Bull, AWS SQS)

**Category:** Infrastructure  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** BullMQ Official Documentation
- **URL:** https://docs.bullmq.io/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** AWS SQS Documentation
- **URL:** https://docs.aws.amazon.com/sqs/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "Job Queue Patterns" - Engineering Blog
- **URL:** https://docs.bullmq.io/guide/patterns (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 13: Knowledge of TypeORM or Prisma ORM

**Category:** Database  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** TypeORM Official Documentation
- **URL:** https://typeorm.io/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** Prisma Official Documentation
- **URL:** https://www.prisma.io/docs
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "ORM vs Raw SQL Tradeoffs" - Engineering Blog
- **URL:** https://www.prisma.io/dataguide/types/relational/orms-vs-raw-sql (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 14: Experience building SaaS products with multi-tenant architecture

**Category:** Architecture  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** "Multi-Tenant SaaS Architecture Patterns" - Technical Article
- **URL:** https://aws.amazon.com/solutions/implementations/saas-architecture-center/ (AWS SaaS patterns)
- **Type:** Official architecture guide
- **Freshness:** 2024
- **Chunk Types:** primary, secondary, interview_question

#### Secondary Explanatory Source
- **Source:** "Multi-Tenant Architecture Patterns" - Engineering Blog
- **URL:** https://www.postgresql.org/docs/current/ddl-schemas.html (or similar technical article)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** "Tenant Isolation Strategies" - Technical Article
- **URL:** https://docs.microsoft.com/en-us/azure/sql-database/saas-tenancy-app-design-patterns (or similar)
- **Type:** Official documentation / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 15: Familiarity with Stripe API for subscription billing

**Category:** Integration  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** Stripe Billing Documentation
- **URL:** https://stripe.com/docs/billing
- **Type:** Official API documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** "Subscription Billing Patterns" - Stripe Documentation
- **URL:** https://stripe.com/docs/billing/subscriptions/overview
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "Stripe Webhooks and Events" - Official Documentation
- **URL:** https://stripe.com/docs/webhooks
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, interview_question

- **Source:** "Payment Processing Workflows" - Engineering Blog
- **URL:** https://stripe.com/docs/payments/checkout (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 16: Understanding of rate limiting, throttling, and anti-bot detection patterns

**Category:** Security  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** "Rate Limiting Strategies" - Technical Article
- **URL:** https://cloud.google.com/architecture/rate-limiting-strategies-techniques (or similar)
- **Type:** Official architecture guide
- **Freshness:** 2024
- **Chunk Types:** primary, secondary, interview_question

#### Secondary Explanatory Source
- **Source:** "API Rate Limiting Patterns" - Engineering Blog
- **URL:** https://stripe.com/docs/rate-limits (or similar technical article)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** "Anti-Bot Detection Techniques" - Technical Article
- **URL:** https://www.cloudflare.com/learning/bots/what-is-bot-detection/ (or similar)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 17: Experience with Tailwind CSS and component libraries (shadcn/ui, Radix)

**Category:** Frontend  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** Tailwind CSS Official Documentation
- **URL:** https://tailwindcss.com/docs
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** shadcn/ui Documentation
- **URL:** https://ui.shadcn.com/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** Radix UI Documentation
- **URL:** https://www.radix-ui.com/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, interview_question

- **Source:** "Modern CSS Frameworks" - Engineering Blog
- **URL:** https://tailwindcss.com/docs/utility-first (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff

---

### Requirement 18: Knowledge of WebSockets for real-time features

**Category:** Frontend  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** WebSocket API - MDN Web Docs
- **URL:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **Type:** Official web standard documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** Socket.io Documentation
- **URL:** https://socket.io/docs/v4/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "Real-Time Communication Patterns" - Engineering Blog
- **URL:** https://socket.io/docs/v4/ (or similar technical article)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 19: Experience with Testcontainers or similar for integration testing

**Category:** Testing  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** Testcontainers Official Documentation
- **URL:** https://testcontainers.com/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** "Integration Testing Patterns" - Engineering Blog
- **URL:** https://testcontainers.com/guides/ (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** "Docker-Based Testing" - Technical Article
- **URL:** https://testcontainers.com/getting-started/ (or similar)
- **Type:** Official documentation / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, interview_question, tradeoff

---

### Requirement 20: CI/CD setup experience

**Category:** DevOps  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** GitHub Actions Documentation
- **URL:** https://docs.github.com/en/actions
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** GitLab CI/CD Documentation
- **URL:** https://docs.gitlab.com/ee/ci/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "CI/CD Pipeline Design" - Engineering Blog
- **URL:** https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment (or similar)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 21: Deployment experience on Railway, Render, or similar PaaS platforms

**Category:** DevOps  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** Railway Documentation
- **URL:** https://docs.railway.app/
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** Render Documentation
- **URL:** https://render.com/docs
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "PaaS Deployment Patterns" - Engineering Blog
- **URL:** https://docs.railway.app/deploy/builds (or similar)
- **Type:** Official documentation / Engineering blog
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, failure_mode

---

### Requirement 22: Startup experience or work in agile, fast-moving teams

**Category:** Soft Skills  
**Priority:** Nice to Have

#### Primary Authoritative Source
- **Source:** "Agile Manifesto" - Official Principles
- **URL:** https://agilemanifesto.org/
- **Type:** Official manifesto
- **Freshness:** 2001 (historical but authoritative)
- **Chunk Types:** primary, interview_question
- **Note:** Marked as historical but still authoritative

#### Secondary Explanatory Source
- **Source:** "Scrum Guide" - Official Scrum Framework
- **URL:** https://scrumguides.org/scrum-guide.html
- **Type:** Official framework guide
- **Freshness:** 2020 (historical but authoritative)
- **Chunk Types:** primary, secondary, interview_question
- **Note:** Marked as historical but still authoritative

#### Additional Sources
- **Source:** "Startup Culture and Dynamics" - Engineering Blog
- **URL:** https://www.atlassian.com/agile/startups (or similar)
- **Type:** Engineering blog / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff, interview_question

---

## COMPANY CONTEXT DOMAINS (Eventyr)

### Domain 1: Eventyr mission and positioning

**Description:** Company mission, vision, and market positioning

#### Primary Authoritative Source
- **Source:** Eventyr Official Website
- **URL:** https://eventyr.com/ (or actual Eventyr website URL)
- **Type:** Official website
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** primary, interview_question
- **Note:** Requires discovery of actual Eventyr website

#### Secondary Explanatory Source
- **Source:** Eventyr Company Blog / Press Releases
- **URL:** TBD (to be discovered)
- **Type:** Company blog / Press releases
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** secondary, interview_question

#### Additional Sources
- **Source:** LinkedIn Company Page / About Section
- **URL:** TBD (to be discovered)
- **Type:** Professional network
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** secondary, interview_question

**Status:** ⚠️ **REQUIRES DISCOVERY** - Actual Eventyr website and public materials must be located

---

### Domain 2: Autonomous recruiting platform description

**Description:** Detailed description of the autonomous recruiting platform product

#### Primary Authoritative Source
- **Source:** Eventyr Product Documentation / Website
- **URL:** TBD (to be discovered - likely eventyr.com/product or similar)
- **Type:** Official product documentation
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** primary, interview_question
- **Note:** Requires discovery of actual Eventyr product pages

#### Secondary Explanatory Source
- **Source:** Eventyr Product Blog / Feature Announcements
- **URL:** TBD (to be discovered)
- **Type:** Product blog / Announcements
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** secondary, interview_question

**Status:** ⚠️ **REQUIRES DISCOVERY** - Actual Eventyr product documentation must be located

---

### Domain 3: AI-powered agent workflows (sourcing, engagement, screening)

**Description:** AI agent workflows for sourcing, engagement, and screening

#### Primary Authoritative Source
- **Source:** Eventyr Technical Documentation / Architecture Docs
- **URL:** TBD (to be discovered)
- **Type:** Technical documentation
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** primary, interview_question
- **Note:** May require internal documentation or public technical blog

#### Secondary Explanatory Source
- **Source:** "AI Agent Workflows in Recruiting" - Technical Article
- **URL:** TBD (to be discovered - may be Eventyr blog or industry article)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024 (to be verified)
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** General AI Agent Patterns (if Eventyr-specific unavailable)
- **URL:** https://www.anthropic.com/research (or similar AI agent resources)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff
- **Note:** Fallback if Eventyr-specific sources unavailable

**Status:** ⚠️ **REQUIRES DISCOVERY** - Eventyr-specific workflow documentation may be limited; may need to supplement with general AI agent patterns

---

### Domain 4: Performance constraints (Sub-5-minute response, hundreds of parallel conversations)

**Description:** System performance requirements and constraints

#### Primary Authoritative Source
- **Source:** Eventyr Technical Specifications / System Design Docs
- **URL:** TBD (to be discovered)
- **Type:** Technical specifications
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** primary, interview_question
- **Note:** May require internal documentation or public technical blog

#### Secondary Explanatory Source
- **Source:** "High-Throughput System Design" - Engineering Blog
- **URL:** TBD (to be discovered - may be Eventyr blog or industry article)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024 (to be verified)
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** General High-Throughput Patterns (if Eventyr-specific unavailable)
- **URL:** https://aws.amazon.com/builders-library/ (or similar system design resources)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff
- **Note:** Fallback if Eventyr-specific sources unavailable

**Status:** ⚠️ **REQUIRES DISCOVERY** - Eventyr-specific performance documentation may be limited; may need to supplement with general high-throughput patterns

---

### Domain 5: Human-in-the-loop review and brand safety

**Description:** Human oversight mechanisms and brand safety measures

#### Primary Authoritative Source
- **Source:** Eventyr Process Documentation / Quality Assurance Docs
- **URL:** TBD (to be discovered)
- **Type:** Process documentation
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** primary, interview_question
- **Note:** May require internal documentation or public blog

#### Secondary Explanatory Source
- **Source:** "Human-in-the-Loop AI Systems" - Technical Article
- **URL:** TBD (to be discovered - may be Eventyr blog or industry article)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024 (to be verified)
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources
- **Source:** General HITL Patterns (if Eventyr-specific unavailable)
- **URL:** https://www.anthropic.com/research (or similar AI safety resources)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff
- **Note:** Fallback if Eventyr-specific sources unavailable

**Status:** ⚠️ **REQUIRES DISCOVERY** - Eventyr-specific HITL documentation may be limited; may need to supplement with general HITL patterns

---

### Domain 6: Small, high-impact team dynamics (2-3 engineers)

**Description:** Team structure and working dynamics

#### Primary Authoritative Source
- **Source:** Eventyr Team Page / About Section
- **URL:** TBD (to be discovered - likely eventyr.com/about or similar)
- **Type:** Official website
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** primary, interview_question
- **Note:** Requires discovery of actual Eventyr team information

#### Secondary Explanatory Source
- **Source:** Eventyr Culture Blog / Team Blog
- **URL:** TBD (to be discovered)
- **Type:** Company blog
- **Freshness:** 2024-2025 (to be verified)
- **Chunk Types:** secondary, interview_question

#### Additional Sources
- **Source:** "Small Team Dynamics" - Engineering Blog
- **URL:** https://www.atlassian.com/agile/startups (or similar)
- **Type:** Engineering blog / Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff
- **Note:** Fallback if Eventyr-specific sources unavailable

**Status:** ⚠️ **REQUIRES DISCOVERY** - Actual Eventyr team information must be located

---

### Domain 7: AI-assisted development culture (Claude Code, Cursor)

**Description:** Development practices using AI tools (Claude Code, Cursor)

#### Primary Authoritative Source
- **Source:** Cursor IDE Documentation
- **URL:** https://cursor.sh/docs
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, interview_question

#### Secondary Explanatory Source
- **Source:** Claude Code Documentation / Anthropic Developer Tools
- **URL:** https://docs.anthropic.com/claude/docs (or Cursor-specific docs)
- **Type:** Official documentation
- **Freshness:** 2024-2025
- **Chunk Types:** primary, secondary, tradeoff

#### Additional Sources
- **Source:** "AI-Assisted Development Workflows" - Engineering Blog
- **URL:** TBD (to be discovered - may be Eventyr blog or industry article)
- **Type:** Technical article / Engineering blog
- **Freshness:** 2024 (to be verified)
- **Chunk Types:** secondary, tradeoff, failure_mode

#### Additional Sources (Fallback)
- **Source:** General AI Coding Tools Articles
- **URL:** https://www.anthropic.com/research (or similar)
- **Type:** Technical article
- **Freshness:** 2024
- **Chunk Types:** secondary, tradeoff
- **Note:** Fallback if Eventyr-specific sources unavailable

**Status:** ⚠️ **PARTIALLY AVAILABLE** - Cursor and Claude Code docs available; Eventyr-specific usage patterns may require discovery

---

## SUMMARY

### Coverage Status

**Requirements (1-22):**
- ✅ All 22 requirements have at least 2 candidate sources identified
- ✅ Primary authoritative sources identified for all requirements
- ✅ Secondary explanatory sources identified for all requirements
- ✅ Additional sources identified for comprehensive coverage

**Company Context (7 domains):**
- ⚠️ **5 domains require discovery** of Eventyr-specific sources:
  - Domain 1: Eventyr mission and positioning
  - Domain 2: Autonomous recruiting platform description
  - Domain 3: AI-powered agent workflows
  - Domain 4: Performance constraints
  - Domain 5: Human-in-the-loop review and brand safety
  - Domain 6: Small, high-impact team dynamics
- ✅ **1 domain partially available** (Domain 7: AI-assisted development culture)
- ✅ Fallback sources identified for domains where Eventyr-specific sources may be limited

### Source Freshness

- **2024-2025 sources:** Preferred for all technical requirements
- **Historical but authoritative sources:** Marked explicitly (REST RFC, OAuth spec, Agile Manifesto)
- **Eventyr sources:** Freshness to be verified during discovery

### Next Steps

1. **Discover Eventyr-specific sources:**
   - Locate official Eventyr website
   - Find product documentation
   - Identify company blog or public materials
   - Verify source freshness

2. **Verify source accessibility:**
   - Check all URLs are accessible
   - Verify source freshness dates
   - Confirm source types match expectations

3. **Flag any gaps:**
   - If Eventyr-specific sources unavailable, use fallback sources
   - Document which sources are Eventyr-specific vs. general patterns
   - Ensure coverage requirements are still met

### Success Criteria Met

✅ Every requirement (1-22) has at least 2 candidate sources  
✅ Every requirement has clearly identified source roles (primary/secondary)  
✅ No overlap or duplication across unrelated requirements  
⚠️ Company context domains require Eventyr source discovery (fallbacks identified)

**Status:** Source discovery plan complete. Ready for Eventyr-specific source discovery phase.
