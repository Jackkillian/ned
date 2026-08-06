import { NavLink, Stack } from "@mantine/core";
import { Link, RouteObject, useLocation } from "react-router";

export function NavBar({ routes }: { routes: RouteObject[] }) {
  const { pathname } = useLocation();

  return (
    <Stack>
      {routes[0]?.children?.map((child) => {
        if (child.handle?.hidden) return;
        const Icon = child.handle?.icon;
        const active = child.index
          ? pathname === "/"
          : pathname.includes(child.path ?? "");
        return (
          <NavLink
            key={child.path}
            label={child.handle.label}
            leftSection={Icon ? <Icon size={16} /> : undefined}
            active={active}
            component={Link}
            to={child.index ? "/" : (child.path ?? "/")}
          />
        );
      })}
    </Stack>
  );
}
