use chlorine::{scan_dir, Song};
use std::path::Path;
use tauri::{WebviewUrl, WebviewWindowBuilder};

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn scan(path: String) -> Result<Vec<Song>, String> {
    let target_path = Path::new(&path);

    if !target_path.exists() {
        return Err("Directory does not exist".to_string());
    }

    tokio::task::spawn_blocking(move || scan_dir(&path).map_err(|e| e.to_string()))
        .await
        .map_err(|e| e.to_string())?
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_sql::Builder::new().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, scan])
        .setup(|app| {
            let builder = WebviewWindowBuilder::new(
                app.handle(),
                "player",
                WebviewUrl::App("/player".into()),
            )
            .title("Player")
            .always_on_top(true)
            .transparent(true)
            .decorations(false)
            .accept_first_mouse(true)
            .min_inner_size(440.0, 112.0)
            .max_inner_size(600.0, 112.0)
            .inner_size(440.0, 112.0);
            builder.build().expect("Could not create player window");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
