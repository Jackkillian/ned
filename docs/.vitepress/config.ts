import { defineConfig } from "vitepress";
import typedocSidebar from "../api/typedoc-sidebar.json";

export default defineConfig({
  title: "Ned",
  description: "Documentation and API Reference",
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Guides", link: "/guides/getting-started" },
      { text: "API Reference", link: "/api/" },
    ],
    sidebar: {
      "/guides/": [
        {
          text: "Guides",
          items: [{ text: "Getting Started", link: "/guides/getting-started" }],
        },
      ],
      "/api/": typedocSidebar,
    },
  },
});
