use audiotags::{MimeType, Tag};
use base64::{Engine as _, engine::general_purpose::STANDARD};
use serde::{Deserialize, Serialize};
use std::{
    fs::{self, DirEntry, ReadDir},
    io,
    path::{Path, PathBuf},
};

#[derive(Serialize, Deserialize)]
pub struct TagData {
    pub title: Option<String>,
    pub artist: Option<String>,
    pub album: Option<String>,
    pub genre: Option<String>,
    pub year: Option<i32>,
    pub disc_number: Option<u16>,
    pub track_number: Option<u16>,
    pub picture: Option<String>,
}

#[derive(Serialize, Deserialize)]
pub struct Song {
    pub tag_data: Option<TagData>,
    pub path: PathBuf,
}

impl Song {
    fn read_from_path(entry: DirEntry) -> Self {
        let path = entry.path();
        let tag_data = match Tag::new().read_from_path(&path) {
            Ok(tag) => {
                let to_str = |s: &str| s.to_string();
                Some(TagData {
                    title: tag.title().map(to_str),
                    artist: tag.artist().map(to_str),
                    album: match tag.album() {
                        Some(album) => Some(album.title.to_string()),
                        _ => None,
                    },
                    genre: tag.genre().map(to_str),
                    year: tag.year(),
                    disc_number: tag.disc_number(),
                    track_number: tag.track_number(),
                    picture: tag.album_cover().map(|pic| {
                        let mime_str = match pic.mime_type {
                            MimeType::Png => "png",
                            MimeType::Jpeg => "jpeg",
                            MimeType::Tiff => "tiff",
                            MimeType::Bmp => "bmp",
                            MimeType::Gif => "gif",
                        };
                        let base64_data = STANDARD.encode(pic.data);
                        format!("data:image/{};base64,{}", mime_str, base64_data)
                    }),
                })
            }
            _ => None,
        };
        Song { tag_data, path }
    }
}

fn is_audio_file(path: &Path) -> bool {
    let ext = match path.extension().and_then(|s| s.to_str()) {
        Some(ext) => ext.to_ascii_lowercase(),
        None => return false,
    };

    matches!(
        ext.as_str(),
        "mp3" | "flac" | "wav" | "m4a" | "aac" | "ogg" | "opus" | "wma"
    )
}

fn iter_dir(dir: ReadDir) -> Vec<Song> {
    let mut filtered = vec![];

    for entry in dir.flatten() {
        let path = entry.path();

        if let Ok(file_type) = entry.file_type() {
            if file_type.is_dir() {
                if let Ok(sub_dir) = fs::read_dir(path) {
                    let mut children = iter_dir(sub_dir);
                    filtered.append(&mut children);
                }
            } else if is_audio_file(&path) {
                filtered.push(Song::read_from_path(entry));
            }
        }
    }

    filtered
}

pub fn scan_dir(path: &str) -> io::Result<Vec<Song>> {
    let dir = fs::read_dir(path)?;
    Ok(iter_dir(dir))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use tempfile::tempdir;

    #[test]
    fn test_scan_dir_with_meta() {
        let results = scan_dir("./examples").unwrap();

        let _found_names: Vec<String> = results
            .into_iter()
            .map(|song| {
                if let Some(tag) = song.tag_data {
                    println!(
                        "{} - {} - {}",
                        tag.title.unwrap(),
                        tag.artist.unwrap(),
                        tag.album.unwrap()
                    );
                }
                song.path
                    .file_name()
                    .unwrap()
                    .to_string_lossy()
                    .into_owned()
            })
            .collect();
    }

    #[test]
    fn test_scan_dir_finds_nested_audio_files() {
        let dir = tempdir().unwrap();
        let root_path = dir.path();

        let sub_dir = root_path.join("album");
        fs::create_dir_all(&sub_dir).unwrap();

        let file_mp3 = root_path.join("track1.mp3");
        let file_flac = sub_dir.join("track2.flac");
        let file_txt = root_path.join("notes.txt");
        let file_cover = sub_dir.join("cover.jpg");

        File::create(&file_mp3).unwrap();
        File::create(&file_flac).unwrap();
        File::create(&file_txt).unwrap();
        File::create(&file_cover).unwrap();

        let results = scan_dir(root_path.to_str().unwrap()).unwrap();
        let found_names: Vec<String> = results
            .into_iter()
            .map(|song| {
                if let Some(tag) = song.tag_data {
                    println!(
                        "{} - {} - {}",
                        tag.title.unwrap(),
                        tag.artist.unwrap(),
                        tag.album.unwrap()
                    );
                }
                song.path
                    .file_name()
                    .unwrap()
                    .to_string_lossy()
                    .into_owned()
            })
            .collect();

        assert_eq!(found_names.len(), 2);
        assert!(found_names.contains(&"track1.mp3".to_string()));
        assert!(found_names.contains(&"track2.flac".to_string()));
        assert!(!found_names.contains(&"notes.txt".to_string()));
        assert!(!found_names.contains(&"cover.jpg".to_string()));
    }

    #[test]
    fn test_scan_dir_empty_directory() {
        let dir = tempdir().unwrap();
        let results = scan_dir(dir.path().to_str().unwrap()).unwrap();
        assert!(results.is_empty());
    }
}
