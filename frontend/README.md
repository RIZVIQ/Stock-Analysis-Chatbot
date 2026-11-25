# Stock Analysis Frontend

Modern React 19 single-page application built with **TypeScript**, **Vite**, **@thesysai/genui-sdk**, and **@crayonai/react-ui**.

---

## Features

- **Generative UI Rendering**: Connects to the backend via Server-Sent Events and dynamically renders charts, metric cards, financial balance sheet tables, and news widgets.
- **C1Chat Component**: Built-in chat interface handling user prompts, session state, thread IDs, and token streaming.
- **Dark Theme**: Unified styling using `<ThemeProvider mode="dark">` and Roboto typography.
- **Built-in Reverse Proxy**: Proxies `/api` requests to the FastAPI backend (`http://localhost:8888`) during development.

---

## Tech Stack

- **React 19**
- **TypeScript 5.9**
- **Vite 7**
- **@thesysai/genui-sdk** (`v0.8.4`): GenUI client runtime and `C1Chat` interface.
- **@crayonai/react-ui** (`v0.9.16`): Generative component library and design system.

---

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Development Server

```bash
npm run dev
```

The app will start at `http://localhost:3000`.

### 3. Build for Production

```bash
npm run build
```

Build outputs are generated in the `dist/` directory.

### 4. Linting

```bash
npm run lint
```
