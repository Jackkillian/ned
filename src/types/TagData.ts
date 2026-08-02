export interface TagData {
  /** Song title */
  title?: string;
  /** Song artist */
  artist?: string;
  /** Song album */
  album?: string;
  /** Song genre */
  genre?: string;
  /** Song album art; encoded as a base64 string */
  picture?: string;
  /** Song year */
  year?: number;
  /** Song disc number */
  disc_number?: number;
  /** Song track number */
  track_number?: number;
}
