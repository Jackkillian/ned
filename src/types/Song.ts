import { TagData } from "./TagData";

export interface Song {
  /** Optional tag data */
  tag_data?: TagData;
  /** File path to song on disk */
  path: string;
}
