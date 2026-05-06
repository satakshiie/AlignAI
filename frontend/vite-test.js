import { build } from 'vite';
await build({
  root: '.',
  logLevel: 'silent',
  build: {
    write: false,
    rollupOptions: {
      input: 'src/main.jsx',
    }
  }
});
