# 🧠 MindMarket – A Marketplace for Micro-Ideas

**MindMarket** is a platform where creativity meets commerce. It enables anyone to submit, discover, buy, or expand **micro-ideas** like app names, UI prompts, product hooks, and taglines — all ranked and enriched by AI.

> ✨ **Think: Fiverr, but for tiny bursts of imagination.**

🌐 **Live Demo:** [MindMarket on Replit](https://fe005164-c056-42f7-9c62-09f84bbada85-00-qfhr0rgb1aif.spock.replit.dev/)

---

## 💡 Why MindMarket?

Every day, people have flashes of brilliance — a great name for a product, a killer slogan, a fresh UI idea — but they go unused. MindMarket turns these sparks into shareable, sellable assets. With a little help from AI, creativity becomes a currency.

---

## 🚀 What It Does

- Users submit short ideas (e.g., _"app name: BrewLoop"_)
- AI ranks, tags, and clusters them by theme or industry
- Others can browse or buy ideas, or request custom ones
- Generative AI expands or remixes ideas on request

---

## 🛠️ Tech Stack

| Layer           | Tools & Libraries                                                                 |
|------------------|------------------------------------------------------------------------------------|
| **Language**       | Python 3.11+                                                                       |
| **Web Framework**  | Flask, Flask-Login, Flask-SQLAlchemy                                                |
| **AI Integration** | OpenAI GPT-4o for idea evaluation, clustering, and generation                      |
| **Database**       | PostgreSQL (via SQLAlchemy ORM)                                                    |
| **Frontend**       | Jinja2 Templates (server-rendered HTML via Flask)                                  |
| **Authentication** | Session-based using Flask-Login                                                    |
| **Deployment**     | Gunicorn (prod-ready WSGI server)                                                  |
| **Environment**    | `.replit` config for Replit integration                                            |
| **Other Libraries**| Werkzeug, psycopg2-binary, email-validator                                         |

---

## 🧪 Setup Instructions (For Local Dev)

1. Clone the repo
   ```bash
   git clone https://github.com/yourusername/mindmarket.git
   cd mindmarket
