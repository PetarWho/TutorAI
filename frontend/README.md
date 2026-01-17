# Lecture RAG Frontend

A modern, responsive React frontend for the Lecture-to-Tutor AI system, built with TypeScript, Tailwind CSS, and Vite.

## Features

- **Lecture Upload**: Drag & drop interface for audio/video files
- **Smart Search**: Ask questions about lectures with AI-powered answers
- **Course Management**: Organize lectures into courses
- **PDF Generation**: Download transcripts and summaries
- **Timestamp Navigation**: Jump to specific moments in lectures
- **User Authentication**: Secure login and registration
- **Responsive Design**: Works on desktop, tablet, and mobile

## Technology Stack

- **Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **Build Tool**: Vite
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **File Upload**: React Dropzone
- **Date Handling**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation
      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
