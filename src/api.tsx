import { QueryClient } from "@tanstack/react-query";
import { invoke } from "@tauri-apps/api/core";
import { Song } from "@/types/Song";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 30,
    },
  },
});

export const songsQuery = (path: string) => ({
  queryKey: ["songs", path],
  queryFn: async () => {
    return await invoke<Song[]>("scan", { path });
  },
});
