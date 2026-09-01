import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  // ./ prefix required, a bare 'a/b' string is read as a Hey API registry shorthand.
  input: "./frontend/openapi.json", // Dumped from the app by `bun run codegen`.
  output: "frontend/generated",
  // baseUrl: false so the client fetches relative urls, the app serves its own frontend.
  plugins: [{ name: "@hey-api/client-fetch", baseUrl: false }],
});
