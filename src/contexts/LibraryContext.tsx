import { Song } from "@/types/Song";
import {
  createContext,
  Dispatch,
  ReactNode,
  SetStateAction,
  useContext,
  useState,
} from "react";

const LibraryContext = createContext<{
  songs: Song[];
  setSongs: Dispatch<SetStateAction<Song[]>>;
  selectedAlbum: string | null;
  setSelectedAlbum: Dispatch<SetStateAction<string | null>>;
  getSongsByAlbum: () => Record<string, Song[]>;
}>({
  songs: [],
  setSongs: () => {},
  selectedAlbum: null,
  setSelectedAlbum: () => {},
  getSongsByAlbum: () => ({}),
});

export function useLibrary() {
  const context = useContext(LibraryContext);
  if (context === null)
    throw new Error("useLibrary must used in a LibraryProvider");
  return context;
}

export function LibraryProvider({ children }: { children: ReactNode }) {
  const [songs, setSongs] = useState<Song[]>([]);
  const [selectedAlbum, setSelectedAlbum] = useState<string | null>(null);

  return (
    <LibraryContext.Provider
      value={{
        songs,
        setSongs,
        selectedAlbum,
        setSelectedAlbum,
        getSongsByAlbum: () => {
          const songsByAlbum = {} as Record<string, Song[]>;
          songs.map((song) => {
            const album = song.tag_data?.album ?? "<no album>";
            if (!(album in songsByAlbum)) songsByAlbum[album] = [];
            songsByAlbum[album].push(song);
          });
          return songsByAlbum;
        },
      }}
    >
      {children}
    </LibraryContext.Provider>
  );
}
