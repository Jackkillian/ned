import "@mantine/core/styles.css";
import "mantine-datatable/styles.layer.css";
import "@gfazioli/mantine-audio/styles.css";
import "./App.css";
import { AppShell, MantineProvider } from "@mantine/core";
import { createBrowserRouter, Outlet } from "react-router";
import { useDisclosure } from "@mantine/hooks";
import { LibraryProvider } from "@/contexts/LibraryContext.tsx";
import { TitleBar } from "@/components/navigation/TitleBar.tsx";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, lazy: () => import("./pages/Root.jsx") },
      {
        path: "/album/:album",
        lazy: () => import("./pages/Album.tsx"),
      },
    ],
  },
]);

function Root() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <MantineProvider>
      <LibraryProvider>
        <AppShell
          padding="md"
          header={{ height: { base: 44 } }}
          navbar={{
            width: { base: 200, md: 300, lg: 400 },
            breakpoint: "sm",
            collapsed: { mobile: !opened, desktop: !opened },
          }}
          style={{ height: "100vh", overflow: "hidden" }}
        >
          <AppShell.Header>
            <TitleBar opened={opened} toggle={toggle} />
          </AppShell.Header>
          <AppShell.Navbar p="md">Navbar</AppShell.Navbar>
          <AppShell.Main
            h="calc(100vh - 44px)"
            pt="calc(var(--app-shell-header-offset, 0rem))"
            style={{ overflowY: "auto" }}
          >
            <Outlet />
          </AppShell.Main>
        </AppShell>
      </LibraryProvider>
    </MantineProvider>
  );
}
