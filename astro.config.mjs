import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://www.giusepperomanelli.it',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
